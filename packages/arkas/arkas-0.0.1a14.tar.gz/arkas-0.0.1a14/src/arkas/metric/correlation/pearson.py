r"""Implement the Pearson correlation metrics."""

from __future__ import annotations

__all__ = ["pearsonr"]


from typing import TYPE_CHECKING

from arkas.metric.utils import contains_nan, preprocess_same_shape_arrays
from arkas.utils.imports import check_scipy, is_scipy_available

if is_scipy_available():
    from scipy import stats

if TYPE_CHECKING:
    import numpy as np


def pearsonr(
    x: np.ndarray,
    y: np.ndarray,
    *,
    alternative: str = "two-sided",
    prefix: str = "",
    suffix: str = "",
    nan_policy: str = "propagate",
) -> dict[str, float]:
    r"""Return the Pearson correlation coefficient and p-value for
    testing non-correlation.

    Args:
        x: The first input array.
        y: The second input array.
        alternative: The alternative hypothesis. Default is 'two-sided'.
            The following options are available:
            - 'two-sided': the correlation is nonzero
            - 'less': the correlation is negative (less than zero)
            - 'greater': the correlation is positive (greater than zero)
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
    >>> from arkas.metric import pearsonr
    >>> pearsonr(x=np.array([1, 2, 3, 4, 5]), y=np.array([1, 2, 3, 4, 5]))
    {'count': 5, 'pearson_coeff': 1.0, 'pearson_pvalue': 0.0}

    ```
    """
    check_scipy()
    x, y = preprocess_same_shape_arrays(
        arrays=[x.ravel(), y.ravel()], drop_nan=nan_policy == "omit"
    )
    x_nan = contains_nan(arr=x, nan_policy=nan_policy, name="'x'")
    y_nan = contains_nan(arr=y, nan_policy=nan_policy, name="'y'")

    count = x.size
    coeff, pvalue = float("nan"), float("nan")
    if count > 1 and not x_nan and not y_nan:
        result = stats.pearsonr(x=x, y=y, alternative=alternative)
        coeff, pvalue = float(result.statistic), float(result.pvalue)
    return {
        f"{prefix}count{suffix}": count,
        f"{prefix}pearson_coeff{suffix}": coeff,
        f"{prefix}pearson_pvalue{suffix}": pvalue,
    }
