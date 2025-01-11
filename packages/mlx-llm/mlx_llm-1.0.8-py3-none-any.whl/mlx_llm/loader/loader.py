from queue import Queue
from threading import Thread
from typing import Any, Callable

import mlx.core as mx
import numpy as np
from transformers import PreTrainedTokenizer

from ..dataset import Dataset


# TODO: must be improved: add sampler support and other features
class DataLoader:
    """Custom DataLoader (similar to PyTorch but easier to read).

    Args:
        dataset (Dataset): the dataset to be loaded.
        tokenizer (PreTrainedTokenizer): the tokenizer to use.
        batch_size (int): the batch size. Defaults to 1.
        shuffle (bool): whether to shuffle the dataset. Defaults to False.
        collate_fn (Callable): the function to use to collate the data. Defaults to _default_collate_fn.
        drop_last (bool): whether to drop the last batch if it's smaller than the batch size. Defaults to False.
    """

    def __init__(
        self,
        dataset: Dataset,
        tokenizer: PreTrainedTokenizer,
        batch_size: int = 1,
        max_length: int = 2048,
        shuffle: bool = False,
        drop_last: bool = False,
    ):
        self.dataset = dataset
        self.tokenizer = tokenizer
        self.batch_size = batch_size
        self.max_length = max_length
        self.shuffle = shuffle
        self.indices = list(range(len(self.dataset)))

        # if drop_last is true, we need to make sure that the last batch is not smaller than the batch size
        if drop_last:
            self.indices = self.indices[: len(self.indices) - len(self.indices) % self.batch_size]

    def __iter__(self) -> Any:
        if self.shuffle:
            np.random.shuffle(self.indices)
        for idx in range(0, len(self.indices), self.batch_size):
            batch_indices = self.indices[idx : idx + self.batch_size]
            batch = self.tokenizer(
                [self.dataset[i] for i in batch_indices],
                max_length=self.max_length + 1,
                truncation=True,
                padding="max_length",
            )
            batch = mx.array(batch["input_ids"])
            lengths = mx.array([len(self.dataset[i]) for i in batch_indices])
            # yielding :
            # * batch[:, :-1] -> the input sequence (all but the last token)
            # * batch[:, 1:] -> the target sequence (all but the first token)
            # * lengths -> the length of each sequence
            yield batch[:, :-1], batch[:, 1:], mx.array(lengths)

    def __len__(self) -> int:
        return len(self.indices) // self.batch_size
