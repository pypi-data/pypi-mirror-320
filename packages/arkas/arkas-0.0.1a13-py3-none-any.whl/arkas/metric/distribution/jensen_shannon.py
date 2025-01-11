r"""Implement the Jensen-Shannon (JS) divergence between two
distributions."""

from __future__ import annotations

__all__ = ["jensen_shannon_divergence"]


from typing import TYPE_CHECKING

from arkas.metric.distribution.kl import _kl_divergence
from arkas.metric.utils import preprocess_same_shape_arrays
from arkas.utils.imports import check_scipy, is_scipy_available

if is_scipy_available():
    pass

if TYPE_CHECKING:
    import numpy as np


def jensen_shannon_divergence(
    p: np.ndarray,
    q: np.ndarray,
    *,
    prefix: str = "",
    suffix: str = "",
) -> dict[str, float]:
    r"""Return the Jensen-Shannon (JS) divergence between two
    distributions.

    Args:
        p: The true probability distribution.
        q: The model probability distribution.
        prefix: The key prefix in the returned dictionary.
        suffix: The key suffix in the returned dictionary.

    Returns:
        The computed metrics.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.metric import jensen_shannon_divergence
    >>> jensen_shannon_divergence(
    ...     p=np.array([0.1, 0.6, 0.1, 0.2]), q=np.array([0.2, 0.5, 0.2, 0.1])
    ... )
    {'size': 4, 'jensen_shannon_divergence': 0.027...}

    ```
    """
    check_scipy()
    p, q = preprocess_same_shape_arrays(arrays=[p.ravel(), q.ravel()])

    size = p.size
    div = float("nan")
    if size > 0:
        m = 0.5 * (p + q)
        div = 0.5 * (_kl_divergence(p, m) + _kl_divergence(q, m))
    return {f"{prefix}size{suffix}": size, f"{prefix}jensen_shannon_divergence{suffix}": div}
