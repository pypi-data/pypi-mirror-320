from typing import Any, Dict, Iterable

import mlx.core as mx
import mlx.nn as nn
from mlx.utils import tree_unflatten

from .layers import LoRALinear


def _to_lora(layer: nn.Module, lora_config: Dict[str, Any]) -> nn.Module:
    """Converts a layer to a LoRA layer.

    Args:
        layer (nn.Module): a layer to convert.
        lora_config (Dict[str, Any]): LoRA configuration.

    Raises:
        ValueError: if the layer is not supported.

    Returns:
        nn.Module: a LoRA layer.
    """
    if isinstance(layer, (nn.Linear, nn.QuantizedLinear)):
        return LoRALinear(layer, **lora_config)  # type: ignore
    else:
        raise ValueError(f"Layer {layer} is not supported for LoRA conversion.")


def convert_layers(
    model: nn.Module,
    lora_layers_keys: Iterable[str] = ("attention.q_proj", "attention.k_proj", "attention.v_proj"),
    num_lora_layers: int = 4,
    lora_config: Dict[str, Any] = {"r": 8, "dropout": 0.2, "alpha": 32, "bias": False},  # noqa: B006
) -> nn.Module:
    """Converts the last `num_lora_layers` layers of the model to LoRA layers.

    Args:
        model (nn.Module): a model to convert.
        lora_layers_keys (Iterable[str], optional): keys of the layers to convert. Defaults to ("attention.q_proj", "attention.k_proj", "attention.v_proj").
        num_lora_layers (int, optional): number of layers to convert. Defaults to 16.
        lora_config (Dict[str, Any], optional): LoRA configuration. Defaults to DEFAULT_LORA_CONFIG.

    Returns:
        nn.Module: a model with LoRA layers.
    """

    num_model_layers = len(model.layers)
    if num_lora_layers > num_model_layers or num_lora_layers < 0:
        raise ValueError(
            f"num_lora_layers ({num_lora_layers}) must be less than the number of layers in the model ({num_model_layers}) and >0."
        )

    start_from = num_model_layers - num_lora_layers
    applied = 0

    if isinstance(lora_layers_keys, str):
        lora_layers_keys = [lora_layers_keys]

    for layer in model.layers[start_from:]:
        lora_layers = [(k, _to_lora(m, lora_config)) for k, m in layer.named_modules() if k in lora_layers_keys]
        if lora_layers:
            applied += 1
            layer.update_modules(tree_unflatten(lora_layers))

    if applied == 0:
        raise ValueError(f"No LoRA layers found in the last {num_lora_layers} layers.")
    else:
        print(f"Converted last {applied} layers with keys ({lora_layers_keys}) for LoRA.")

    return model
