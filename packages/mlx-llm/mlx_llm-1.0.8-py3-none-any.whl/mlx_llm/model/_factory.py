import glob
import os
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import mlx.core as mx
import mlx.nn as nn
from transformers import AutoTokenizer

from ..utils.hf import download_from_hf
from ._registry import MODEL_ENTRYPOINTS
from ._utils import apply_weights, load_weights, quantize

__all__ = ["list_models", "create_model"]


def list_models() -> List[str]:
    """List all available LLM models."""
    all_models = list(MODEL_ENTRYPOINTS.keys())
    return all_models


def create_model(
    model_name: str,
    weights: Union[List[str], str, bool] = True,
    strict: bool = False,
    converter: Optional[Callable] = None,
    verbose: bool = False,
    model_config: Optional[Dict[str, Any]] = None,
) -> nn.Module:
    """Create a LLM model.

    Example:

    ```
    >>> from mlx_llm.model import create_model

    >>> # Create a LLaMA 3 8B model with pretrained weights from HF.
    >>> model = create_model('llama_3_8b_instruct')

    >>> # Create a LLaMA 3 8B model with pretrained weights from HF from another repository.
    >>> model = create_model(
            model_name="llama_3_8b_instruct", # it's the base model
            weights="hf://gradientai/Llama-3-8B-Instruct-262k", # new weights from HuggingFace
            model_config={ "rope_theta": 207112184.0 }
    >>> )

    >>> # Create a LLaMA 3 8B model model with custom local weights.
    >>> model = create_model('llama_2_8b_instruct', weights="path/to/model.safetensors")
    ```

    Args:
        model_name (str): model name
        weights (Union[str, List[str], bool]): if True, load pretrained weights from HF. If str or List[str], load weights from the given paths. Defaults to True.
        strict (bool, optional): whether to strictly enforce that the keys in weights match the keys of the model. Defaults to False.
        converter (Optional[Callable], optional): a function to convert the weights to the model format. Defaults to None.
        verbose (bool, optional): whether to print the model summary. Defaults to False.
        model_config (Dict[str, Any], optional): model configuration. Defaults to {}.

    Returns:
        nn.Module: a LLM model

    Raises:
        ValueError: Unknown model name
    """

    if model_name not in MODEL_ENTRYPOINTS:
        raise ValueError(f"Unknown model name: {model_name}.")

    if model_config is None:
        model_config = {}
    model, config = MODEL_ENTRYPOINTS[model_name](**model_config)

    if config.quantize is not None:
        model = quantize(model, group_size=config.quantize.group_size, bits=config.quantize.bits)

    if isinstance(weights, str) and weights.endswith(".safetensors"):
        model = load_weights(model=model, weights=weights, strict=strict, verbose=verbose)
    elif isinstance(weights, str) and weights.startswith("hf://"):
        model_path = download_from_hf(
            repo_id=weights.replace("hf://", ""),
        )
        weights = glob.glob(os.path.join(model_path, "*.safetensors"))  # type: ignore
        if len(weights) == 0:
            raise ValueError(f"No safetensors weights found in {model_path}.")
        converter = config.converter if converter is None else converter
        weights = converter(weights)
        model = apply_weights(model, weights)  # type: ignore

    elif isinstance(weights, bool) and weights is True:
        model_path = download_from_hf(
            repo_id=config.hf.repo_id, revision=config.hf.revision, filename=config.hf.filename
        )
        if os.path.isfile(model_path):
            weights = model_path
        else:
            weights = glob.glob(os.path.join(model_path, "*.safetensors"))  # type: ignore
        if config.converter is not None:
            weights = config.converter(weights)
            model = apply_weights(model, weights)  # type: ignore

    return model


def create_tokenizer(model_name: Optional[str] = None, path: Optional[str] = None) -> AutoTokenizer:
    """Create a tokenizer for a LLM model.

    Args:
        model_name (Optional[str], optional): model name. Defaults to None.
        path (Optional[str], optional): path to local tokenizer. Defaults to None.

    Raises:
        ValueError: Unknown model name

    Returns:
        AutoTokenizer: tokenizer
    """
    # if both model_name and path are None, raise an error
    if model_name is None and path is None:
        raise ValueError("Either model_name or path must be provided.")

    # if path is given, load the tokenizer from the path
    if path is not None and os.path.isdir(path):
        return AutoTokenizer.from_pretrained(path, legacy=True)

    if model_name is not None:
        if model_name.startswith("hf://"):
            repo_id = model_name.replace("hf://", "")
        elif model_name in MODEL_ENTRYPOINTS:
            _, config = MODEL_ENTRYPOINTS[model_name]()
            repo_id = config.tokenizer.repo_id if config.tokenizer else config.hf.repo_id
        else:
            raise ValueError(f"Unknown model name: {model_name}.")

        return AutoTokenizer.from_pretrained(repo_id, legacy=True)

    raise ValueError("Invalid arguments: model_name or path must be provided.")
