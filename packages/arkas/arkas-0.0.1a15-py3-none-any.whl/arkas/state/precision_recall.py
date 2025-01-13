r"""Implement the accuracy state."""

from __future__ import annotations

__all__ = ["PrecisionRecallState"]

import sys
from typing import TYPE_CHECKING, Any

from coola import objects_are_equal
from coola.utils.format import repr_mapping_line

from arkas.metric.classification.precision import find_label_type
from arkas.metric.utils import check_label_type, check_nan_policy, check_same_shape_pred
from arkas.state.base import BaseState

if sys.version_info >= (3, 11):
    from typing import Self
else:  # pragma: no cover
    from typing_extensions import (
        Self,  # use backport because it was added in python 3.11
    )

if TYPE_CHECKING:
    import numpy as np


class PrecisionRecallState(BaseState):
    r"""Implement a state for precision-recall-based metrics.

    This state can be used in 3 different settings:

    - binary: ``y_true`` must be an array of shape ``(n_samples,)``
        with ``0`` and ``1`` values, and ``y_pred`` must be an array
        of shape ``(n_samples,)``.
    - multiclass: ``y_true`` must be an array of shape ``(n_samples,)``
        with values in ``{0, ..., n_classes-1}``, and ``y_pred`` must
        be an array of shape ``(n_samples,)``.
    - multilabel: ``y_true`` must be an array of shape
        ``(n_samples, n_classes)`` with ``0`` and ``1`` values, and
        ``y_pred`` must be an array of shape
        ``(n_samples, n_classes)``.

    Args:
        y_true: The ground truth target labels. This input must
            be an array of shape ``(n_samples,)`` or
            ``(n_samples, n_classes)``.
        y_pred: The predicted labels. This input must
            be an array of shape ``(n_samples,)`` or
            ``(n_samples, n_classes)``.
        y_true_name: The name associated to the ground truth target
            labels.
        y_pred_name: The name associated to the predicted labels.
        label_type: The type of labels used to evaluate the metrics.
            The valid values are: ``'binary'``, ``'multiclass'``,
            and ``'multilabel'``. If ``'binary'`` or ``'multilabel'``,
            ``y_true`` values  must be ``0`` and ``1``.
        nan_policy: The policy on how to handle NaN values in the input
            arrays. The following options are available: ``'omit'``,
            ``'propagate'``, and ``'raise'``.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.state import PrecisionRecallState
    >>> state = PrecisionRecallState(
    ...     y_true=np.array([1, 0, 0, 1, 1]),
    ...     y_pred=np.array([1, 0, 0, 1, 1]),
    ...     y_true_name="target",
    ...     y_pred_name="pred",
    ... )
    >>> state
    PrecisionRecallState(y_true=(5,), y_pred=(5,), y_true_name='target', y_pred_name='pred', label_type='binary', nan_policy='propagate')

    ```
    """

    def __init__(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_true_name: str,
        y_pred_name: str,
        label_type: str = "auto",
        nan_policy: str = "propagate",
    ) -> None:
        self._y_true = y_true
        self._y_pred = y_pred
        self._y_true_name = y_true_name
        self._y_pred_name = y_pred_name
        self._label_type = (
            find_label_type(y_true=y_true, y_pred=y_pred) if label_type == "auto" else label_type
        )
        self._nan_policy = nan_policy
        self._check_args()

    def __repr__(self) -> str:
        args = repr_mapping_line(
            {
                "y_true": self._y_true.shape,
                "y_pred": self._y_pred.shape,
                "y_true_name": self._y_true_name,
                "y_pred_name": self._y_pred_name,
                "label_type": self._label_type,
                "nan_policy": self._nan_policy,
            }
        )
        return f"{self.__class__.__qualname__}({args})"

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
    def label_type(self) -> str:
        return self._label_type

    @property
    def nan_policy(self) -> str:
        return self._nan_policy

    def clone(self, deep: bool = True) -> Self:
        return self.__class__(
            y_true=self._y_true.copy() if deep else self._y_true,
            y_pred=self._y_pred.copy() if deep else self._y_pred,
            y_true_name=self._y_true_name,
            y_pred_name=self._y_pred_name,
            label_type=self._label_type,
            nan_policy=self._nan_policy,
        )

    def equal(self, other: Any, equal_nan: bool = False) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return (
            objects_are_equal(self.y_true, other.y_true, equal_nan=equal_nan)
            and objects_are_equal(self.y_pred, other.y_pred, equal_nan=equal_nan)
            and self.y_true_name == other.y_true_name
            and self.y_pred_name == other.y_pred_name
            and self.label_type == other.label_type
            and self.nan_policy == other.nan_policy
        )

    def _check_args(self) -> None:
        if self._y_true.ndim not in {1, 2}:
            msg = (
                f"'y_true' must be a 1d or 2d array but received an array of shape: "
                f"{self._y_true.shape}"
            )
            raise ValueError(msg)
        if self._y_pred.ndim not in {1, 2}:
            msg = (
                f"'y_pred' must be a 1d or 2d array but received an array of shape: "
                f"{self._y_pred.shape}"
            )
            raise ValueError(msg)
        check_same_shape_pred(y_true=self._y_true, y_pred=self._y_pred)
        check_label_type(self._label_type)
        check_nan_policy(self._nan_policy)
