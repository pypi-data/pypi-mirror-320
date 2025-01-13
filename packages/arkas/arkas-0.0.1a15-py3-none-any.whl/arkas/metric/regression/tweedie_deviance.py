r"""Implement the mean Tweedie deviance regression loss."""

from __future__ import annotations

__all__ = ["mean_tweedie_deviance"]

from typing import TYPE_CHECKING

from sklearn import metrics

from arkas.metric.utils import contains_nan, preprocess_pred

if TYPE_CHECKING:
    from collections.abc import Sequence

    import numpy as np


def mean_tweedie_deviance(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    *,
    powers: Sequence[float] = (0,),
    prefix: str = "",
    suffix: str = "",
    nan_policy: str = "propagate",
) -> dict[str, float]:
    r"""Return the mean Tweedie deviance regression loss.

    Args:
        y_true: The ground truth target values.
        y_pred: The predicted values.
        powers: The Tweedie power parameter. The higher power the less
            weight is given to extreme deviations between true and
            predicted targets.
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
    >>> from arkas.metric import mean_tweedie_deviance
    >>> mean_tweedie_deviance(
    ...     y_true=np.array([1, 2, 3, 4, 5]), y_pred=np.array([1, 2, 3, 4, 5])
    ... )
    {'count': 5, 'mean_tweedie_deviance_power_0': 0.0}

    ```
    """
    y_true, y_pred = preprocess_pred(
        y_true=y_true.ravel(), y_pred=y_pred.ravel(), drop_nan=nan_policy == "omit"
    )
    y_true_nan = contains_nan(arr=y_true, nan_policy=nan_policy, name="'y_true'")
    y_pred_nan = contains_nan(arr=y_pred, nan_policy=nan_policy, name="'y_pred'")

    count = y_true.size
    out = {f"{prefix}count{suffix}": count}
    for power in powers:
        score = float("nan")
        if count > 0 and not y_true_nan and not y_pred_nan:
            score = metrics.mean_tweedie_deviance(y_true=y_true, y_pred=y_pred, power=power)
        out[f"{prefix}mean_tweedie_deviance_power_{power}{suffix}"] = float(score)
    return out
