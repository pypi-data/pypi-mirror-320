r"""Contain precision-recall curve plotting functionalities."""

from __future__ import annotations

__all__ = ["binary_precision_recall_curve"]

from typing import TYPE_CHECKING, Any

from sklearn.metrics import PrecisionRecallDisplay

from arkas.metric.utils import preprocess_pred

if TYPE_CHECKING:
    import numpy as np
    from matplotlib.axes import Axes


def binary_precision_recall_curve(
    ax: Axes, y_true: np.ndarray, y_pred: np.ndarray, **kwargs: Any
) -> None:
    r"""Plot the precision-recall curve for binary labels.

    Args:
        ax: The axes of the matplotlib figure to update.
        y_true: The ground truth target labels. This input must
            be an array of shape ``(n_samples,)`` with ``0`` and
            ``1`` values.
        y_pred: The predicted labels. This input must be an array of
            shape ``(n_samples,)`` with ``0`` and ``1`` values.
        **kwargs: Arbitrary keyword arguments that are passed to
            ``PrecisionRecallDisplay.from_predictions``.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from matplotlib import pyplot as plt
    >>> from arkas.plot import binary_precision_recall_curve
    >>> fig, ax = plt.subplots()
    >>> binary_precision_recall_curve(
    ...     ax=ax, y_true=np.array([1, 0, 0, 1, 1]), y_pred=np.array([1, 0, 0, 1, 1])
    ... )

    ```
    """
    y_true, y_pred = preprocess_pred(y_true=y_true.ravel(), y_pred=y_pred.ravel(), drop_nan=True)
    PrecisionRecallDisplay.from_predictions(y_true=y_true, y_pred=y_pred, ax=ax, **kwargs)
