r"""Contain figures to show precision-recall curves."""

from __future__ import annotations

__all__ = ["binary_precision_recall_curve"]

from typing import TYPE_CHECKING, Any

import matplotlib.pyplot as plt

from arkas import plot
from arkas.metric.utils import check_same_shape_pred

if TYPE_CHECKING:
    import numpy as np


def binary_precision_recall_curve(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    name: str = "model",
    plot_chance_level: bool = True,
    **kwargs: Any,
) -> plt.Figure | None:
    r"""Return a figure with the precision-recall curve for binary
    labels.

    Args:
        y_true: The ground truth target labels. This input must
            be an array of shape ``(n_samples,)`` with ``0`` and
            ``1`` values.
        y_pred: The predicted labels. This input must be an array of
            shape ``(n_samples,)`` with ``0`` and ``1`` values.
        name: The name for labeling curve.
        plot_chance_level: Whether to plot the chance level.
            The chance level is the prevalence of the positive label
            computed from the data.
        **kwargs: Arbitrary keyword arguments that are passed to
            ``PrecisionRecallDisplay.from_predictions``.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.metric.figure import binary_precision_recall_curve
    >>> fig = binary_precision_recall_curve(
    ...     y_true=np.array([1, 0, 0, 1, 1]), y_pred=np.array([1, 0, 0, 1, 1])
    ... )

    ```
    """
    check_same_shape_pred(y_true, y_pred)
    if y_true.size == 0:
        return None

    fig, ax = plt.subplots()
    plot.binary_precision_recall_curve(
        ax=ax,
        y_true=y_true,
        y_pred=y_pred,
        name=name,
        plot_chance_level=plot_chance_level,
        **kwargs,
    )
    return fig
