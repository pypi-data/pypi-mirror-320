r"""Implement the Kullback-Leibler (KL) divergence between two
distributions."""

from __future__ import annotations

__all__ = ["kl_div"]


from typing import TYPE_CHECKING

from arkas.metric.utils import preprocess_same_shape_arrays
from arkas.utils.imports import check_scipy, is_scipy_available

if is_scipy_available():
    from scipy.special import rel_entr

if TYPE_CHECKING:
    import numpy as np


def kl_div(
    p: np.ndarray,
    q: np.ndarray,
    *,
    prefix: str = "",
    suffix: str = "",
) -> dict[str, float]:
    r"""Return the Kullback-Leibler (KL) divergence between two
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
    >>> from arkas.metric import kl_div
    >>> kl_div(p=np.array([0.1, 0.6, 0.1, 0.2]), q=np.array([0.2, 0.5, 0.2, 0.1]))
    {'size': 4, 'kl_pq': 0.109..., 'kl_qp': 0.116...}

    ```
    """
    check_scipy()
    p, q = preprocess_same_shape_arrays(arrays=[p.ravel(), q.ravel()])

    size = p.size
    kl_pq, kl_qp = float("nan"), float("nan")
    if size > 0:
        kl_pq = _kl_divergence(p, q)
        kl_qp = _kl_divergence(q, p)
    return {
        f"{prefix}size{suffix}": size,
        f"{prefix}kl_pq{suffix}": kl_pq,
        f"{prefix}kl_qp{suffix}": kl_qp,
    }


def _kl_divergence(p: np.ndarray, q: np.ndarray) -> float:
    r"""Return the Kullback-Leibler (KL) divergence between two
    distributions.

    Args:
        p: The true probability distribution.
        q: The model probability distribution.

    Returns:
        The KL divergence.
    """
    return float(rel_entr(p, q).sum())
