import json
from typing import Dict, List, Optional

from transformers import PreTrainedTokenizer


class Dataset:
    """Base class for datasets.

    Args:
        data_path (str): path to the data file.
        data_key (str): key of the data in the file. Defaults to "text".
        n_samples (int): number of samples to load for debugging. Defaults to 100.
    """

    def __init__(self, data_path: str, data_key: str = "text", n_samples: Optional[int] = None) -> None:
        with open(data_path, "r") as r:
            self.data = [json.loads(l) for l in r]
            if n_samples:
                self.data = self.data[:n_samples]
        self.data_key = data_key

    def __getitem__(self, idx: int) -> str:
        return self.data[idx][self.data_key]

    def __len__(self) -> int:
        return len(self.data)


class ChatDataset(Dataset):
    """Dataset for chat data.

    Args:
        data_path (str): path to the data file.
        tokenizer (PreTrainedTokenizer): tokenizer to use.
        n_samples (int): number of samples to load for debugging. Defaults to 100.
    """

    def __init__(self, data_path: str, tokenizer: PreTrainedTokenizer, n_samples: Optional[int] = None) -> None:
        super().__init__(data_path, n_samples=n_samples)
        self.tokenizer = tokenizer

    def __getitem__(self, idx: int) -> str:
        messages = self.data[idx]["messages"]
        text = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        return text
