r"""Implement the accuracy state."""

from __future__ import annotations

__all__ = ["AccuracyState"]

from typing import TYPE_CHECKING, Any

from arkas.metric.utils import check_nan_policy, check_same_shape_pred
from arkas.state.arg import BaseArgState

if TYPE_CHECKING:
    import numpy as np


class AccuracyState(BaseArgState):
    r"""Implement the accuracy state.

    Args:
        y_true: The ground truth target labels. This input must
            be an array of shape ``(n_samples,)`` where the values
            are in ``{0, ..., n_classes-1}``.
        y_pred: The predicted labels. This input must be an
            array of shape ``(n_samples,)`` where the values are
            in ``{0, ..., n_classes-1}``.
        y_true_name: The name associated to the ground truth target
            labels.
        y_pred_name: The name associated to the predicted labels.
        nan_policy: The policy on how to handle NaN values in the input
            arrays. The following options are available: ``'omit'``,
            ``'propagate'``, and ``'raise'``.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.state import AccuracyState
    >>> state = AccuracyState(
    ...     y_true=np.array([1, 0, 0, 1, 1]),
    ...     y_pred=np.array([1, 0, 0, 1, 1]),
    ...     y_true_name="target",
    ...     y_pred_name="pred",
    ... )
    >>> state
    AccuracyState(y_true=(5,), y_pred=(5,), y_true_name='target', y_pred_name='pred', nan_policy='propagate')

    ```
    """

    def __init__(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_true_name: str,
        y_pred_name: str,
        nan_policy: str = "propagate",
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._y_true = y_true.ravel()
        self._y_pred = y_pred.ravel()
        check_same_shape_pred(y_true=self._y_true, y_pred=self._y_pred)

        self._y_true_name = y_true_name
        self._y_pred_name = y_pred_name

        check_nan_policy(nan_policy)
        self._nan_policy = nan_policy

    @property
    def y_true(self) -> np.ndarray:
        return self._y_true

    @property
    def y_pred(self) -> np.ndarray:
        return self._y_pred

    @property
    def y_true_name(self) -> str:
        return self._y_true_name

    @property
    def y_pred_name(self) -> str:
        return self._y_pred_name

    @property
    def nan_policy(self) -> str:
        return self._nan_policy

    def get_args(self) -> dict:
        return {
            "y_true": self._y_true,
            "y_pred": self._y_pred,
            "y_true_name": self._y_true_name,
            "y_pred_name": self._y_pred_name,
            "nan_policy": self._nan_policy,
        } | super().get_args()
