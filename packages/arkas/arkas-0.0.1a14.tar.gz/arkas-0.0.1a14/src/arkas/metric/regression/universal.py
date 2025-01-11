r"""Implement the regression error metrics."""

from __future__ import annotations

__all__ = ["regression_errors"]


from typing import TYPE_CHECKING

from arkas.metric.regression.abs_error import mean_absolute_error, median_absolute_error
from arkas.metric.regression.mse import mean_squared_error

if TYPE_CHECKING:
    import numpy as np


def regression_errors(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    *,
    prefix: str = "",
    suffix: str = "",
    nan_policy: str = "propagate",
) -> dict[str, float]:
    r"""Return the regression error metrics.

    Args:
        y_true: The ground truth target values.
        y_pred: The predicted values.
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
    >>> from arkas.metric import regression_errors
    >>> regression_errors(y_true=np.array([1, 2, 3, 4, 5]), y_pred=np.array([1, 2, 3, 4, 5]))
    {'count': 5,
     'mean_absolute_error': 0.0,
     'median_absolute_error': 0.0,
     'mean_squared_error': 0.0}

    ```
    """
    return (
        mean_absolute_error(
            y_true=y_true,
            y_pred=y_pred,
            prefix=prefix,
            suffix=suffix,
            nan_policy=nan_policy,
        )
        | median_absolute_error(
            y_true=y_true,
            y_pred=y_pred,
            prefix=prefix,
            suffix=suffix,
            nan_policy=nan_policy,
        )
        | mean_squared_error(
            y_true=y_true,
            y_pred=y_pred,
            prefix=prefix,
            suffix=suffix,
            nan_policy=nan_policy,
        )
    )
