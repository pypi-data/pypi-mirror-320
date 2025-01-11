r"""Implement the Wasserstein distance between two 1D discrete
distributions."""

from __future__ import annotations

__all__ = ["wasserstein_distance"]


from typing import TYPE_CHECKING

from arkas.metric.utils import contains_nan, preprocess_same_shape_arrays
from arkas.utils.imports import check_scipy, is_scipy_available

if is_scipy_available():
    from scipy import stats

if TYPE_CHECKING:
    import numpy as np


def wasserstein_distance(
    u_values: np.ndarray,
    v_values: np.ndarray,
    *,
    prefix: str = "",
    suffix: str = "",
    nan_policy: str = "propagate",
) -> dict[str, float]:
    r"""Return the Wasserstein distance between two 1D discrete
    distributions.

    Args:
        u_values: An array that contains a sample from a probability
            distribution or the support (set of all possible values)
            of a probability distribution. Each element is an
            observation or possible value.
        v_values: An array that contains a sample from or the support
            of a second distribution.
        prefix: The key prefix in the returned dictionary.
        suffix: The key suffix in the returned dictionary.
        nan_policy: The policy on how to handle NaN values in the input
            arrays. The following options are available: ``'omit'``,
            ``'propagate'``, and ``'raise'``.

    Returns:
        The computed metrics.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.metric import wasserstein_distance
    >>> wasserstein_distance(
    ...     u_values=np.array([1, 2, 3, 4, 5]), v_values=np.array([1, 2, 3, 4, 5])
    ... )
    {'count': 5, 'wasserstein_distance': 0.0}

    ```
    """
    check_scipy()
    u_values, v_values = preprocess_same_shape_arrays(
        arrays=[u_values.ravel(), v_values.ravel()], drop_nan=nan_policy == "omit"
    )
    u_nan = contains_nan(arr=u_values, nan_policy=nan_policy, name="'u_values'")
    v_nan = contains_nan(arr=v_values, nan_policy=nan_policy, name="'v_values'")

    count = u_values.size
    dist = float("nan")
    if count > 0 and not u_nan and not v_nan:
        dist = float(stats.wasserstein_distance(u_values, v_values))
    return {
        f"{prefix}count{suffix}": count,
        f"{prefix}wasserstein_distance{suffix}": dist,
    }
