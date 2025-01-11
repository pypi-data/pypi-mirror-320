r"""Implement the classification accuracy metrics."""

from __future__ import annotations

__all__ = ["balanced_accuracy"]


from typing import TYPE_CHECKING

from sklearn import metrics

from arkas.metric.utils import contains_nan, preprocess_pred

if TYPE_CHECKING:
    import numpy as np


def balanced_accuracy(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    *,
    prefix: str = "",
    suffix: str = "",
    nan_policy: str = "propagate",
) -> dict[str, float]:
    r"""Return the accuracy metrics.

    Args:
        y_true: The ground truth target labels.
        y_pred: The predicted labels.
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
    >>> from arkas.metric import balanced_accuracy
    >>> balanced_accuracy(y_true=np.array([1, 0, 0, 1, 1]), y_pred=np.array([1, 0, 0, 1, 1]))
    {'balanced_accuracy': 1.0, 'count': 5}

    ```
    """
    y_true, y_pred = preprocess_pred(
        y_true=y_true.ravel(), y_pred=y_pred.ravel(), drop_nan=nan_policy == "omit"
    )
    y_true_nan = contains_nan(arr=y_true, nan_policy=nan_policy, name="'y_true'")
    y_pred_nan = contains_nan(arr=y_pred, nan_policy=nan_policy, name="'y_pred'")

    count = y_true.size
    acc = float("nan")
    if count > 0 and not y_true_nan and not y_pred_nan:
        acc = float(metrics.balanced_accuracy_score(y_true=y_true, y_pred=y_pred))
    return {f"{prefix}balanced_accuracy{suffix}": acc, f"{prefix}count{suffix}": count}
