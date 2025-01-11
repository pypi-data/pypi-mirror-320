r"""Implement the accuracy result."""

from __future__ import annotations

__all__ = ["AccuracyResult"]

from typing import TYPE_CHECKING, Any

from coola import objects_are_equal
from coola.utils.format import repr_mapping_line

from arkas.metric.classification.accuracy import accuracy
from arkas.metric.utils import check_nan_policy, check_same_shape_pred
from arkas.result.base import BaseResult

if TYPE_CHECKING:
    import numpy as np


class AccuracyResult(BaseResult):
    r"""Implement the accuracy result.

    Args:
        y_true: The ground truth target labels. This input must
            be an array of shape ``(n_samples,)`` where the values
            are in ``{0, ..., n_classes-1}``.
        y_pred: The predicted labels. This input must be an
            array of shape ``(n_samples,)`` where the values are
            in ``{0, ..., n_classes-1}``.
        nan_policy: The policy on how to handle NaN values in the input
            arrays. The following options are available: ``'omit'``,
            ``'propagate'``, and ``'raise'``.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.result import AccuracyResult
    >>> result = AccuracyResult(
    ...     y_true=np.array([1, 0, 0, 1, 1]), y_pred=np.array([1, 0, 0, 1, 1])
    ... )
    >>> result
    AccuracyResult(y_true=(5,), y_pred=(5,), nan_policy='propagate')
    >>> result.compute_metrics()
    {'accuracy': 1.0, 'count_correct': 5, 'count_incorrect': 0, 'count': 5, 'error': 0.0}

    ```
    """

    def __init__(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        nan_policy: str = "propagate",
    ) -> None:
        self._y_true = y_true.ravel()
        self._y_pred = y_pred.ravel()
        check_same_shape_pred(y_true=self._y_true, y_pred=self._y_pred)

        check_nan_policy(nan_policy)
        self._nan_policy = nan_policy

    def __repr__(self) -> str:
        args = repr_mapping_line(
            {
                "y_true": self._y_true.shape,
                "y_pred": self._y_pred.shape,
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
    def nan_policy(self) -> str:
        return self._nan_policy

    def compute_metrics(self, prefix: str = "", suffix: str = "") -> dict[str, float]:
        return accuracy(
            y_true=self._y_true,
            y_pred=self._y_pred,
            prefix=prefix,
            suffix=suffix,
            nan_policy=self._nan_policy,
        )

    def equal(self, other: Any, equal_nan: bool = False) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return (
            objects_are_equal(self.y_true, other.y_true, equal_nan=equal_nan)
            and objects_are_equal(self.y_pred, other.y_pred, equal_nan=equal_nan)
            and self.nan_policy == other.nan_policy
        )

    def generate_figures(
        self, prefix: str = "", suffix: str = ""  # noqa: ARG002
    ) -> dict[str, float]:
        return {}
