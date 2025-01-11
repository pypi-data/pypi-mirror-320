import time
from typing import Callable, Dict, Optional, Tuple

import mlx.core as mx
import mlx.nn as nn
import numpy as np
from mlx.optimizers import Optimizer
from tqdm import tqdm

from ..callbacks import ModelCheckpoint, StatsMonitor, TrainerStats
from ..loader import DataLoader
from ..model import get_weights, params_stats


def grad_checkpoint(model: nn.Module):
    """Update all instances of type(layer) to use gradient checkpointing.

    Args:
        model (nn.Module): model
    """
    fn = type(model).__call__

    def checkpointed_fn(model, *args, **kwargs):
        def inner_fn(params, *args, **kwargs):
            model.update(params)
            return fn(model, *args, **kwargs)

        return mx.checkpoint(inner_fn)(model.trainable_parameters(), *args, **kwargs)

    type(model).__call__ = checkpointed_fn


class Trainer:
    """Trainer class to train a model

    Args:
        model (nn.Module): the model to train
        optimizer (Optimizer): the optimizer to use
        train_loader (Dataset): the training loader
        val_loader (Optional[Dataset]): the validation loader. Defaults to None.
        max_epochs (int): the maximum number of epochs. Defaults to 10.
        val_every_n_epoch (int): validation frequency. Defaults to 1.
        log_every_n_steps (int): logging frequency. Defaults to 10.
        grad_ckpt (bool): whether to checkpoint gradients. If True, enables gradient checkpoint (some activations will not be saved but computed during backprop). Pro: spare some memory. Con: increased training time.
        model_checkpoint (Optional[ModelCheckpoint]): model checkpoint callback. Defaults to None.
        stats_monitor (Optional[StatsMonitor]): stats monitor callback. Defaults to None.
    """

    def __init__(
        self,
        model: nn.Module,
        optimizer: Optimizer,
        train_loader: DataLoader,
        val_loader: Optional[DataLoader] = None,
        max_epochs: int = 10,
        val_every_n_epoch: int = 1,
        stats_every_n_epoch: int = 1,
        log_every_n_steps: int = 10,
        grad_ckpt: bool = False,
        model_checkpoint: Optional[ModelCheckpoint] = None,
        stats_monitor: Optional[StatsMonitor] = None,
    ) -> None:
        self.model = model
        self.optimizer = optimizer
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.max_epochs = max_epochs
        self.val_every_n_epoch = val_every_n_epoch
        self.stats_every_n_epoch = stats_every_n_epoch
        self.log_every_n_steps = log_every_n_steps
        self.grad_ckpt = grad_ckpt
        self.model_checkpoint = model_checkpoint
        self.stats_monitor = stats_monitor

        # define forward and backward step
        self.forward_pass = nn.value_and_grad(self.model, self._forward_pass)

        if self.grad_ckpt:
            grad_checkpoint(self.model)

        self._post_init()

    def _post_init(self) -> None:
        pass

    def _forward_pass(self, tokens: mx.array, target: mx.array, lengths: mx.array) -> Tuple[mx.array, int]:
        """Model forward pass

        Args:
            tokens (mx.array): input tokens
            target (mx.array): target tokens
            lengths (mx.array): lengths of the sequences

        Returns:
            Tuple[mx.array, int]: loss and number of tokens
        """
        # forward pass
        logits, _ = self.model(tokens)
        logits = logits.astype(mx.float32)

        # mask padding tokens
        length_mask = mx.arange(tokens.shape[1])[None, :] < lengths[:, None]

        # Cross entropy
        cross_entropy = nn.losses.cross_entropy(logits, tokens) * length_mask
        num_tokens = length_mask.sum()

        cross_entropy = cross_entropy.sum() / num_tokens
        return cross_entropy, num_tokens

    def train_epoch(self, trainer_stats: TrainerStats) -> TrainerStats:
        """Train the model for one epoch

        Args:
            trainer_stats (TrainerStats): stats of the epoch

        Returns:
            TrainerStats: stats of the epoch
        """
        self.model.train()
        for idx, (tokens, targets, lengths) in enumerate(self.train_loader):  # type: ignore
            iter_tic = time.perf_counter()
            # compute loss and gradients - forward pass
            (loss, num_tokens), gradients = self.forward_pass(tokens, targets, lengths)
            # update model - backward pass
            self.optimizer.update(self.model, gradients)
            mx.eval(self.model.parameters(), self.optimizer.state, loss)
            iter_toc = time.perf_counter()

            # update iter stats
            trainer_stats.train_iter_losses.append(loss.item())
            trainer_stats.train_iter_tokens.append(num_tokens.item())
            trainer_stats.train_iter_times.append(iter_toc - iter_tic)
            trainer_stats.train_iter_gpus.append(mx.metal.get_peak_memory() / 2**30)

            # log stats
            if idx % self.log_every_n_steps == 0:
                # log last iter stats
                log_loss = np.mean(trainer_stats.train_iter_losses[idx - self.log_every_n_steps :])
                log_tokens = np.mean(trainer_stats.train_iter_tokens[idx - self.log_every_n_steps :])
                log_time = np.sum(trainer_stats.train_iter_times[idx - self.log_every_n_steps :])
                np.mean(trainer_stats.train_iter_gpus[idx - self.log_every_n_steps :])
                print(
                    f"> Training Iter [{idx+1}/{len(self.train_loader)}] - loss: {log_loss:.4f} - tokens/s: {log_tokens/log_time:.2f}"
                )

        return trainer_stats

    def val_epoch(self, trainer_stats: Optional[TrainerStats] = None) -> Optional[TrainerStats]:  # type: ignore
        """Validation epoch

        Args:
            trainer_stats (Optional[TrainerStats]): stats of the epoch. Defaults to None.

        Returns:
            Optional[TrainerStats]: stats of the epoch
        """

        self.model.eval()
        val_loss, val_tokens = [], 0
        for _idx, (tokens, targets, lengths) in tqdm(
            enumerate(self.val_loader), total=len(self.val_loader), desc="> Running validation..."  # type: ignore
        ):
            # forward pass
            loss, num_tokens = self._forward_pass(tokens, targets, lengths)
            val_loss.append((loss * num_tokens).item())
            val_tokens += num_tokens.item()  # type: ignore

        val_loss = np.sum(val_loss) / val_tokens

        print(f"\n> Validation loss: {val_loss:.4f}")

        if trainer_stats is not None:
            trainer_stats.val_loss = val_loss  # type: ignore
            return trainer_stats

    # define a method that checks if it's time to run validation
    def _time_to_validate(self, epoch: int) -> bool:
        """Check if it's time to run validation

        Args:
            epoch (int): epoch number

        Returns:
            bool: True if it's time to run validation, False otherwise
        """
        return self.val_loader is not None and epoch % self.val_every_n_epoch == 0

    def _on_train_epoch_end(self, trainer_stats: TrainerStats) -> None:
        """Callbacks to run at the end of the training epoch

        Args:
            trainer_stats (TrainerStats): training stats
        """

        if self.model_checkpoint:
            self.model_checkpoint.step(trainer_stats=trainer_stats, weights=get_weights(self.model, trainable=True))

        if self.stats_monitor:
            self.stats_monitor.step(trainer_stats)

    def train(self) -> None:
        """Train the model"""
        for epoch in range(self.max_epochs):
            # init epoch stats
            trainer_stats = TrainerStats(epoch=epoch)

            print(f"\n******** Epoch {epoch}/{self.max_epochs} ********")

            epoch_tic = time.perf_counter()
            trainer_stats = self.train_epoch(trainer_stats=trainer_stats)
            time.perf_counter()

            trainer_stats.train_epoch_time = time.perf_counter() - epoch_tic
            print(f"> Epoch training time: {trainer_stats.train_epoch_time:.2f}s\n")

            # save epoch stats in output_dir
            if self._time_to_validate(epoch):
                trainer_stats = self.val_epoch(trainer_stats=trainer_stats)  # type: ignore

            self._on_train_epoch_end(trainer_stats)

    def eval(self) -> None:
        """Evaluate the model

        Raises:
            ValueError: Validation loader is required to evaluate the model
        """
        if self.val_loader is None:
            raise ValueError("Validation loader is required to evaluate the model")
        _ = self.val_epoch()
