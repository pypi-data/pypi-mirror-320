r"""Implement the Area Under the Receiver Operating Characteristic Curve
(ROC AUC) result."""

from __future__ import annotations

__all__ = [
    "BaseRocAucResult",
    "BinaryRocAucResult",
    "MulticlassRocAucResult",
    "MultilabelRocAucResult",
]

from typing import TYPE_CHECKING, Any

from coola import objects_are_equal
from coola.utils.format import repr_mapping_line

from arkas.metric.classification.roc_auc import (
    binary_roc_auc,
    multiclass_roc_auc,
    multilabel_roc_auc,
)
from arkas.metric.utils import check_nan_policy, check_same_shape_score
from arkas.result.base import BaseResult

if TYPE_CHECKING:
    import matplotlib.pyplot as plt
    import numpy as np


class BaseRocAucResult(BaseResult):
    r"""Implement the base class to implement the Area Under the Receiver
    Operating Characteristic Curve (ROC AUC) results.

    Args:
        y_true: The ground truth target labels.
        y_score: The target scores, can either be probability
            estimates of the positive class, confidence values,
            or non-thresholded measure of decisions.
        nan_policy: The policy on how to handle NaN values in the input
            arrays. The following options are available: ``'omit'``,
            ``'propagate'``, and ``'raise'``.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.result import BinaryRocAucResult
    >>> result = BinaryRocAucResult(
    ...     y_true=np.array([1, 0, 0, 1, 1]), y_score=np.array([1, 0, 0, 1, 1])
    ... )
    >>> result
    BinaryRocAucResult(y_true=(5,), y_score=(5,), nan_policy='propagate')
    >>> result.compute_metrics()
    {'count': 5, 'roc_auc': 1.0}

    ```
    """

    def __init__(
        self,
        y_true: np.ndarray,
        y_score: np.ndarray,
        nan_policy: str = "propagate",
    ) -> None:
        self._y_true = y_true
        self._y_score = y_score

        check_nan_policy(nan_policy)
        self._nan_policy = nan_policy

    def __repr__(self) -> str:
        args = repr_mapping_line(
            {
                "y_true": self._y_true.shape,
                "y_score": self._y_score.shape,
                "nan_policy": self._nan_policy,
            }
        )
        return f"{self.__class__.__qualname__}({args})"

    @property
    def nan_policy(self) -> str:
        return self._nan_policy

    @property
    def y_true(self) -> np.ndarray:
        return self._y_true

    @property
    def y_score(self) -> np.ndarray:
        return self._y_score

    def equal(self, other: Any, equal_nan: bool = False) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return (
            objects_are_equal(self.y_true, other.y_true, equal_nan=equal_nan)
            and objects_are_equal(self.y_score, other.y_score, equal_nan=equal_nan)
            and self.nan_policy == other.nan_policy
        )


class BinaryRocAucResult(BaseRocAucResult):
    r"""Implement the Area Under the Receiver Operating Characteristic
    Curve (ROC AUC) result for binary labels.

    Args:
        y_true: The ground truth target labels. This input must
            be an array of shape ``(n_samples, *)`` with ``0`` and
            ``1`` values.
        y_score: The target scores, can either be probability
            estimates of the positive class, confidence values,
            or non-thresholded measure of decisions. This input must
            be an array of shape ``(n_samples, *)``.
        nan_policy: The policy on how to handle NaN values in the input
            arrays. The following options are available: ``'omit'``,
            ``'propagate'``, and ``'raise'``.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.result import BinaryRocAucResult
    >>> result = BinaryRocAucResult(
    ...     y_true=np.array([1, 0, 0, 1, 1]), y_score=np.array([2, -1, 0, 3, 1])
    ... )
    >>> result
    BinaryRocAucResult(y_true=(5,), y_score=(5,), nan_policy='propagate')
    >>> result.compute_metrics()
    {'count': 5, 'roc_auc': 1.0}

    ```
    """

    def __init__(
        self,
        y_true: np.ndarray,
        y_score: np.ndarray,
        nan_policy: str = "propagate",
    ) -> None:
        check_same_shape_score(y_true, y_score)
        super().__init__(y_true=y_true.ravel(), y_score=y_score.ravel(), nan_policy=nan_policy)

    def compute_metrics(self, prefix: str = "", suffix: str = "") -> dict[str, float]:
        return binary_roc_auc(
            y_true=self._y_true,
            y_score=self._y_score,
            prefix=prefix,
            suffix=suffix,
            nan_policy=self._nan_policy,
        )

    def generate_figures(
        self, prefix: str = "", suffix: str = ""  # noqa: ARG002
    ) -> dict[str, plt.Figure]:
        return {}


class MulticlassRocAucResult(BaseRocAucResult):
    r"""Implement the Area Under the Receiver Operating Characteristic
    Curve (ROC AUC) result for multiclass labels.

    Args:
        y_true: The ground truth target labels. This input must
            be an array of shape ``(n_samples,)`` with ``0`` and
            ``1`` values.
        y_score: The target scores, can either be probability
            estimates of the positive class, confidence values,
            or non-thresholded measure of decisions. This input must
            be an array of shape ``(n_samples, n_classes)``.
        nan_policy: The policy on how to handle NaN values in the input
            arrays. The following options are available: ``'omit'``,
            ``'propagate'``, and ``'raise'``.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.result import MulticlassRocAucResult
    >>> result = MulticlassRocAucResult(
    ...     y_true=np.array([0, 0, 1, 1, 2, 2]),
    ...     y_score=np.array(
    ...         [
    ...             [0.7, 0.2, 0.1],
    ...             [0.4, 0.3, 0.3],
    ...             [0.1, 0.8, 0.1],
    ...             [0.2, 0.5, 0.3],
    ...             [0.3, 0.3, 0.4],
    ...             [0.1, 0.2, 0.7],
    ...         ]
    ...     ),
    ... )
    >>> result
    MulticlassRocAucResult(y_true=(6,), y_score=(6, 3), nan_policy='propagate')
    >>> result.compute_metrics()
    {'count': 6,
     'macro_roc_auc': 1.0,
     'micro_roc_auc': 1.0,
     'roc_auc': array([1., 1., 1.]),
     'weighted_roc_auc': 1.0}

    ```
    """

    def __init__(
        self,
        y_true: np.ndarray,
        y_score: np.ndarray,
        nan_policy: str = "propagate",
    ) -> None:
        y_true = y_true.ravel()
        if y_true.shape[0] != y_score.shape[0]:
            msg = (
                f"'y_true' and 'y_score' have different first dimension: {y_true.shape} vs "
                f"{y_score.shape}"
            )
            raise RuntimeError(msg)
        super().__init__(y_true=y_true, y_score=y_score, nan_policy=nan_policy)

    def compute_metrics(self, prefix: str = "", suffix: str = "") -> dict[str, float]:
        return multiclass_roc_auc(
            y_true=self._y_true,
            y_score=self._y_score,
            prefix=prefix,
            suffix=suffix,
            nan_policy=self._nan_policy,
        )

    def generate_figures(
        self, prefix: str = "", suffix: str = ""  # noqa: ARG002
    ) -> dict[str, plt.Figure]:
        return {}


class MultilabelRocAucResult(BaseRocAucResult):
    r"""Implement the Area Under the Receiver Operating Characteristic
    Curve (ROC AUC) result for multilabel labels.

    Args:
        y_true: The ground truth target labels. This input must
            be an array of shape ``(n_samples, n_classes)`` with ``0``
            and ``1`` values.
        y_score: The target scores, can either be probability
            estimates of the positive class, confidence values,
            or non-thresholded measure of decisions. This input must
            be an array of shape ``(n_samples, n_classes)``.
        nan_policy: The policy on how to handle NaN values in the input
            arrays. The following options are available: ``'omit'``,
            ``'propagate'``, and ``'raise'``.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.result import MultilabelRocAucResult
    >>> result = MultilabelRocAucResult(
    ...     y_true=np.array([[1, 0, 1], [0, 1, 0], [0, 1, 0], [1, 0, 1], [1, 0, 1]]),
    ...     y_score=np.array([[2, -1, 1], [-1, 1, -2], [0, 2, -3], [3, -2, 4], [1, -3, 5]]),
    ... )
    >>> result
    MultilabelRocAucResult(y_true=(5, 3), y_score=(5, 3), nan_policy='propagate')
    >>> result.compute_metrics()
    {'count': 5,
     'macro_roc_auc': 1.0,
     'micro_roc_auc': 1.0,
     'roc_auc': array([1., 1., 1.]),
     'weighted_roc_auc': 1.0}

    ```
    """

    def __init__(
        self,
        y_true: np.ndarray,
        y_score: np.ndarray,
        nan_policy: str = "propagate",
    ) -> None:
        check_same_shape_score(y_true, y_score)
        super().__init__(y_true=y_true, y_score=y_score, nan_policy=nan_policy)

    def compute_metrics(self, prefix: str = "", suffix: str = "") -> dict[str, float]:
        return multilabel_roc_auc(
            y_true=self._y_true,
            y_score=self._y_score,
            prefix=prefix,
            suffix=suffix,
            nan_policy=self._nan_policy,
        )

    def generate_figures(
        self, prefix: str = "", suffix: str = ""  # noqa: ARG002
    ) -> dict[str, plt.Figure]:
        return {}
