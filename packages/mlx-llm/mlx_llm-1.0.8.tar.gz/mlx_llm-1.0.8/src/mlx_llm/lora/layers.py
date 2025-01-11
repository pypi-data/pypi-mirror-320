import math
from typing import Optional

import mlx.core as mx
import mlx.nn as nn


class LoRALinear(nn.Module):
    """LoRA Linear layer.

    The output is calculated as:
    .. math::
        \text{Output} = (W_0 \times x) + \alpha \\cdot (A \times B \\times x)

    Where:
    - `x` is the input to the layer.
    - `W_0` is the original weight matrix from the pre-trained model.
    - `A` and `B` are the low-rank matrices used for the adaptation.
    - `alpha` is the scaling factor applied to the low-rank update.


    Args:
        layer (nn.Linear, optional): pre-trained linear layer. Defaults to None.
        input_dims (int): input dimensions. Defaults to None.
        output_dims (int): output dimensions. Defaults to None.
        r (int, optional): rank of the low-rank matrices used in LoRA. Defaults to 8.
        drop (float, optional): dropout rate. Defaults to 0.0.
        alpha (float, optional): scale factor. Defaults to 20.0.
        bias (bool, optional): use bias. Defaults to False.
    """

    def __init__(
        self,
        layer: Optional[nn.Linear] = None,
        input_dims: Optional[int] = None,
        output_dims: Optional[int] = None,
        r: int = 8,
        dropout: float = 0.2,
        alpha: float = 32.0,
        bias: bool = False,
    ):
        assert (layer is not None) or (
            input_dims is not None and output_dims is not None
        ), "Either layer or input_dims and output_dims must be provided."

        super().__init__()
        if layer is not None:
            output_dims, input_dims = layer.weight.shape
            self.layer = layer
        else:
            if input_dims is None or output_dims is None:
                raise ValueError("input_dims and output_dims must be provided.")
            self.layer = nn.Linear(input_dims, output_dims, bias=bias)  # type: ignore

        self.dropout = nn.Dropout(p=dropout)
        # scale for low-rank update
        self.alpha = alpha
        # A init values --> random uniform around 1/sqrt(input_dims) in (-val, val) -> shape is (input_dims, r)
        val = 1 / math.sqrt(input_dims)  # type: ignore
        self.a = mx.random.uniform(low=-val, high=val, shape=(input_dims, r))
        self.b = mx.zeros(shape=(r, output_dims))

    def to_linear(self):  # noqa: D102
        linear = self.layer
        bias = "bias" in linear
        weight = linear.weight
        is_quantized = isinstance(linear, nn.QuantizedLinear)

        # Use the same type as the linear weight if not quantized
        dtype = weight.dtype

        if is_quantized:
            dtype = mx.float16
            weight = mx.dequantize(
                weight,
                linear.scales,
                linear.biases,
                linear.group_size,
                linear.bits,
            )
        output_dims, input_dims = weight.shape
        fused_linear = nn.Linear(input_dims, output_dims, bias=bias)

        lora_b = (self.alpha * self.b.T).astype(dtype)
        lora_a = self.a.T.astype(dtype)
        fused_linear.weight = weight + lora_b @ lora_a
        if bias:
            fused_linear.bias = linear.bias

        if is_quantized:
            fused_linear = nn.QuantizedLinear.from_linear(
                fused_linear,
                linear.group_size,
                linear.bits,
            )

        return fused_linear

    def __call__(self, x: mx.array) -> mx.array:
        """Forward pass.

        Args:
            x (mx.array): input tensor

        Returns:
            mx.array: output tensor
        """
        # linear layer
        y = self.layer(x)
        # low-rank update
        z = (self.dropout(x) @ self.a) @ self.b
        out = y + (self.alpha * z).astype(x.dtype)
        return out
