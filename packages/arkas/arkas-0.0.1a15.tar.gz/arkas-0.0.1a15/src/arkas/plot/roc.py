r"""Contain Receiver Operating Characteristic Curve (ROC) plotting
functionalities."""

from __future__ import annotations

__all__ = ["binary_roc_curve"]

from typing import TYPE_CHECKING, Any

from sklearn.metrics import RocCurveDisplay

from arkas.metric.utils import preprocess_score_binary

if TYPE_CHECKING:
    import numpy as np
    from matplotlib.axes import Axes


def binary_roc_curve(ax: Axes, y_true: np.ndarray, y_score: np.ndarray, **kwargs: Any) -> None:
    r"""Plot the Receiver Operating Characteristic Curve (ROC) for binary
    labels.

    Args:
        ax: The axes of the matplotlib figure to update.
        y_true: The ground truth target labels. This input must
            be an array of shape ``(n_samples,)``.
        y_score: The target scores, can either be probability
            estimates of the positive class, confidence values,
            or non-thresholded measure of decisions. This input must
            be an array of shape ``(n_samples,)``.
        **kwargs: Arbitrary keyword arguments that are passed to
            ``RocCurveDisplay.from_predictions``.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from matplotlib import pyplot as plt
    >>> from arkas.plot import binary_roc_curve
    >>> fig, ax = plt.subplots()
    >>> binary_roc_curve(
    ...     ax=ax, y_true=np.array([1, 0, 0, 1, 1]), y_score=np.array([2, -1, 0, 3, 1])
    ... )

    ```
    """
    y_true, y_score = preprocess_score_binary(
        y_true=y_true.ravel(), y_score=y_score.ravel(), drop_nan=True
    )
    RocCurveDisplay.from_predictions(y_true=y_true, y_pred=y_score, ax=ax, **kwargs)
