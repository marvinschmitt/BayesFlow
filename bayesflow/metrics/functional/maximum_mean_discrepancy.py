import keras

from bayesflow.types import Tensor
from bayesflow.utils import issue_url


def gaussian_kernel(x1: Tensor, x2: Tensor, scales: Tensor = keras.ops.logspace(-6, 6, 11)) -> Tensor:
    residuals = x1[:, None] - x2[None, :]
    norms = keras.ops.norm(residuals, axis=tuple(range(2, keras.ops.ndim(residuals))))
    exponent = norms[:, :, None] / (2.0 * scales[None, None, :])
    return keras.ops.mean(keras.ops.exp(-exponent), axis=2)


def maximum_mean_discrepancy(x1: Tensor, x2: Tensor, kernel: str = "gaussian", **kwargs) -> Tensor:
    """Computes the maximum mean discrepancy between samples x1 and x2.

    :param x1: Tensor of shape (n, ...)

    :param x2: Tensor of shape (m, ...)

    :param kernel: Name of the kernel to use.
        Default: 'gaussian'

    :param kwargs: Additional keyword arguments to pass to the kernel function.

    :return: Tensor of shape (n, m)
        Pairwise maximum mean discrepancy between samples in x1 and x2.
    """
    if kernel != "gaussian":
        raise ValueError(
            "For now, we only support the Gaussian kernel. "
            f"If you need a different kernel, please open an issue at {issue_url}"
        )
    else:
        kernel_fn = gaussian_kernel

    if keras.ops.shape(x1)[1:] != keras.ops.shape(x2)[1:]:
        raise ValueError(
            f"Expected x1 and x2 to live in the same feature space, "
            f"but got {keras.ops.shape(x1)[1:]} != {keras.ops.shape(x2)[1:]}."
        )

    # use flattened versions
    x1 = keras.ops.reshape(x1, (keras.ops.shape(x1)[0], -1))
    x2 = keras.ops.reshape(x2, (keras.ops.shape(x2)[0], -1))

    k1 = kernel_fn(x1, x1, **kwargs)
    k2 = kernel_fn(x2, x2, **kwargs)
    k3 = kernel_fn(x1, x2, **kwargs)

    return k1 + k2 - 2.0 * k3
