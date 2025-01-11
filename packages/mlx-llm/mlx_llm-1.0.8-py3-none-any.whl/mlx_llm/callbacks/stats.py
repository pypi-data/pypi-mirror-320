import json
import os
from typing import Any, Dict, List, Optional

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from .data import TrainerStats

matplotlib.use("Agg")


class StatsMonitor:
    """Monitor the training statistics and save them to disk.

    Args:
        output_dir (str): output directory
        plots_every_n_epoch (int): generate plots every n epoch
    """

    def __init__(self, output_dir: str, plots_every_n_epoch: int = 1):
        self.data_dir = os.path.join(output_dir, "data")
        self.plots_dir = os.path.join(output_dir, "plots")

        self.plots_every_n_epoch = plots_every_n_epoch
        self.stats_history: List[TrainerStats] = []

        # Create the output directories if they don't exist
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.plots_dir, exist_ok=True)

    def step(self, trainer_stats: TrainerStats) -> None:
        """Step the monitor.

        Args:
            trainer_stats (TrainerStats): trainer statistics
        """
        # Append the current epoch's statistics to the history
        self.stats_history.append(trainer_stats)

        # Save the current epoch's statistics
        self._save_epoch_stats(trainer_stats)

        # Generate plots every `plots_every_n_epoch`
        if trainer_stats.epoch % self.plots_every_n_epoch == 0:
            print(f"> Generating plots for epoch {trainer_stats.epoch} at {self.plots_dir}")
            self._make_plots()

    def _save_epoch_stats(self, trainer_stats: TrainerStats) -> None:
        """Save the epoch statistics to disk.

        Args:
            trainer_stats (TrainerStats): trainer statistics
        """
        # Save the stats in a JSON file, named by the epoch number
        epoch_filename = os.path.join(self.data_dir, f"epoch_{trainer_stats.epoch}.json")
        with open(epoch_filename, "w") as f:
            json.dump(trainer_stats.__dict__, f, indent=4)

    def _make_plots(self) -> None:
        """Generate the plots."""
        # Generate the plots
        train_iter_losses = []
        train_tokens_per_sec = []
        train_epoch_losses, val_losses = [], []
        epochs = []
        for stats in self.stats_history:
            train_iter_losses.extend(stats.train_iter_losses)
            train_tokens_per_sec.extend(stats.train_iter_tokens_per_sec)
            if stats.val_loss is not None:
                train_epoch_losses.append(np.mean(stats.train_iter_losses))
                val_losses.append(stats.val_loss)
                epochs.append(stats.epoch)

        # Plotting the training losses
        plt.figure()
        plt.plot(train_iter_losses, marker="o", color="orange", linestyle="-", markersize=3.0)
        plt.title("Training Losses")
        plt.xlabel("Iteration")
        plt.ylabel("Loss")
        plt.ylim(bottom=0, top=max(train_iter_losses) * 1.3)
        plt.savefig(os.path.join(self.plots_dir, "train_loss.png"))
        plt.close()

        # Plotting tokens per second
        plt.figure()
        plt.plot(train_tokens_per_sec, marker="o", color="orange")
        plt.title("Training Tokens/Second")
        plt.xlabel("Iteration")
        plt.ylabel("Tokens/Second")
        plt.ylim(bottom=0, top=max(train_tokens_per_sec) * 1.3)
        plt.savefig(os.path.join(self.plots_dir, "train_tokens_second.png"))
        plt.close()

        # Plotting validation loss if available
        if any(val_losses):
            # Plotting the comparison between training loss mean and validation loss
            plt.figure()
            plt.plot(
                epochs,
                train_epoch_losses,
                label="Training Loss Mean",
                marker="o",
                linestyle="-",
                markersize=3.0,
                color="orange",
            )
            plt.plot(
                epochs, val_losses, label="Validation Loss", marker="o", linestyle="-", markersize=3.0, color="blue"
            )
            plt.title("Training Loss (Mean) vs Validation Loss per Epoch")
            plt.xlabel("Epoch")
            plt.ylabel("Loss")
            plt.legend()
            plt.grid(True)
            plt.savefig(os.path.join(self.plots_dir, "train_vs_val_loss.png"))
            plt.close()
