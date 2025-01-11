import os
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import mlx.core as mx

from mlx_llm.utils.weights import save_weights

from .data import TrainerStats


class ModelCheckpoint:
    """Model checkpoint class to save checkpoints and monitoring them. Filename for each checkpoint will be filled with trainer_stats from Trainer.

    Args:
        output_dir (str): output dir where checkpoints folder will contain mlx files.
        monitor (str, optional): metric to monitor. Defaults to "loss".
        mode (str, optional): mode to check metric to monitor. Defaults to "min".
        save_top_k (int, optional): how many top mlx files to keep during training. Defaults to 5.
        patience (int, optional): how many epochs to wait before ending training if metric to monitor does not improve. Defaults to 10.
        weights_ext (str, optional): extension for weights file. Defaults to ".safetensors".
    """

    def __init__(
        self,
        output_dir: str,
        monitor: str = "val_loss",
        mode: str = "min",
        save_top_k: int = 5,
        patience: int = 10,
        weights_ext: str = ".safetensors",
    ) -> None:
        assert mode in ["max", "min"], f"Mode {mode} not supported. Choose between max or min."
        assert (
            monitor in TrainerStats.__dataclass_fields__
        ), f"Monitor {monitor} not in TrainerStats attributes. Valid attributes are {TrainerStats.__annotations__}"

        self.output_dir = os.path.join(output_dir, "adapters")
        os.makedirs(self.output_dir, exist_ok=True)
        self.monitor = monitor
        self.history: List[Tuple[float, int]] = []  # each el is a Tuple of (val, epoch)
        self.save_top_k = save_top_k
        self.mode = mode
        self.reverse = True if self.mode == "max" else False
        self.patience = patience
        self.weights_ext = weights_ext

        # support fields
        self.patience_count = 0
        self.to_remove = None  # an epoch will be saved here

    def _update_history_sequence(self, value: float, epoch: int, remove_last: bool) -> None:
        """Update history sequence

        Args:
            value (float): value to add
            epoch (int): current epoch
            remove_last (bool): remove last from history
        """

        if remove_last:
            self.to_remove = self.history[-1][1]  # type: ignore
            self.history = self.history[:-1]

        self.history.append((value, epoch))
        self.history = sorted(self.history, reverse=self.reverse, key=lambda x: x[0])
        self.patience_count = 0

    @property
    def best_value(self) -> Optional[float]:
        """Return best value of history sequence

        Returns:
            Optional[float]: best value
        """
        if len(self.history) == 0:
            return None
        return sorted(self.history, reverse=self.reverse, key=lambda x: x[0])[0][0]

    def _update_history(self, trainer_stats: TrainerStats) -> None:
        """Update history

        Args:
            trainer_stats (TrainerStats): TrainerStats instance
        """

        value = trainer_stats.__dict__[self.monitor]
        epoch = trainer_stats.epoch

        if len(self.history) < self.save_top_k:
            self._update_history_sequence(value=value, epoch=epoch, remove_last=False)
            print(
                f"> Epoch {epoch} with best model with {self.monitor}={value:.4f}. Best model is at {self.monitor}={self.best_value:.4f}"
            )
        else:
            # checking for history full
            to_update = True
            if self.mode == "max" and value < min(self.history, key=lambda x: x[0])[0]:
                to_update = False
            elif self.mode == "min" and value > max(self.history, key=lambda x: x[0])[0]:
                to_update = False

            if not to_update:
                print(
                    f"> Epoch {epoch} was not between best models with {self.monitor}={value:.4f}. Current best model interval is {self.monitor}={self.best_value:.4f}"
                )
                self.patience_count += 1
            else:
                self._update_history_sequence(value=value, epoch=epoch, remove_last=True)

    @property
    def patience_over(self) -> bool:
        """Check if patience is over

        Returns:
            bool: True if patience over, False otherwise
        """
        return self.patience_count >= self.patience

    def _create_filename(self, trainer_stats: TrainerStats) -> str:
        """Create mlx filename

        Args:
            trainer_stats (TrainerStats): TrainerStats instance

        Returns:
            str: model filename
        """

        filename = f"epoch={trainer_stats.epoch}-"
        value = trainer_stats.__dict__[self.monitor]
        filename += f"{self.monitor}={value:.4f}"
        return f"{filename}{self.weights_ext}"

    def save(self, weights: Dict, filename: str) -> None:
        """Save mlx file and removes old worst one if needed

        Args:
            weights (Dict): model weights
            filename (str): filename to save
        """

        if len(self.history) == self.save_top_k:
            for f in os.listdir(self.output_dir):
                if self.to_remove is not None:
                    if f.startswith(f"epoch={self.to_remove}"):  # type: ignore
                        os.remove(os.path.join(self.output_dir, f))
        try:
            save_weights(weights, os.path.join(self.output_dir, filename))
            print(f"> Saved model mlx file ({filename}) in checkpoints folder.")
        except Exception as e:
            print(f"[ERROR] Error while saving model. Error {e}.")

    def step(self, trainer_stats: TrainerStats, weights: Dict[str, mx.array]) -> None:
        """Update model checkpoint data and save mlx file if needed

        Args:
            epoch (int): current epoch
            trainer_stats (TrainerStats): trainer stats
            weights (Dict): model weights
        """

        trainer_stats.__dict__[self.monitor]

        self._update_history(trainer_stats=trainer_stats)
        # it means one of best models just added
        if self.patience_count == 0:
            filename = self._create_filename(trainer_stats=trainer_stats)
            self.save(weights=weights, filename=filename)
