from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class TrainerStats:  # noqa: D101
    epoch: int
    train_iter_losses: List[float] = field(default_factory=list)
    train_iter_tokens: List[int] = field(default_factory=list)
    train_iter_times: List[float] = field(default_factory=list)
    train_iter_gpus: List[float] = field(default_factory=list)
    train_epoch_time: float = 0.0

    val_loss: Optional[float] = None

    @property
    def train_iter_tokens_per_sec(self) -> List[float]:
        """Compute the tokens per second for each training iteration

        Returns:
            List[float]: tokens per second for each training iteration
        """
        return [tokens / time for tokens, time in zip(self.train_iter_tokens, self.train_iter_times)]
