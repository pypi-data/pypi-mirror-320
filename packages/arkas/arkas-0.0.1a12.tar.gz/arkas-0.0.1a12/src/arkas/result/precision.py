r"""Implement the precision result."""

from __future__ import annotations

__all__ = [
    "BasePrecisionResult",
    "BinaryPrecisionResult",
    "MulticlassPrecisionResult",
    "MultilabelPrecisionResult",
    "PrecisionResult",
]

from typing import TYPE_CHECKING, Any

from coola import objects_are_equal
from coola.utils.format import repr_mapping_line

from arkas.metric.classification.precision import (
    binary_precision,
    find_label_type,
    multiclass_precision,
    multilabel_precision,
    precision,
)
from arkas.metric.figure import binary_precision_recall_curve
from arkas.metric.utils import check_label_type, check_nan_policy, check_same_shape_pred
from arkas.result.base import BaseResult

if TYPE_CHECKING:
    import matplotlib.pyplot as plt
    import numpy as np


class PrecisionResult(BaseResult):
    r"""Implement the precision result.

    This result can be used in 3 different settings:

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
        nan_policy: The policy on how to handle NaN values in the input
            arrays. The following options are available: ``'omit'``,
            ``'propagate'``, and ``'raise'``.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.result import PrecisionResult
    >>> # binary
    >>> result = PrecisionResult(
    ...     y_true=np.array([1, 0, 0, 1, 1]),
    ...     y_pred=np.array([1, 0, 0, 1, 1]),
    ...     label_type="binary",
    ... )
    >>> result
    PrecisionResult(y_true=(5,), y_pred=(5,), label_type='binary', nan_policy='propagate')
    >>> result.compute_metrics()
    {'count': 5, 'precision': 1.0}
    >>> # multilabel
    >>> result = PrecisionResult(
    ...     y_true=np.array([[1, 0, 1], [0, 1, 0], [0, 1, 0], [1, 0, 1], [1, 0, 1]]),
    ...     y_pred=np.array([[1, 0, 0], [0, 1, 1], [0, 1, 1], [1, 0, 0], [1, 0, 0]]),
    ...     label_type="multilabel",
    ... )
    >>> result
    PrecisionResult(y_true=(5, 3), y_pred=(5, 3), label_type='multilabel', nan_policy='propagate')
    >>> result.compute_metrics()
    {'count': 5,
     'macro_precision': 0.666...,
     'micro_precision': 0.714...,
     'precision': array([1., 1., 0.]),
     'weighted_precision': 0.625}
    >>> # multiclass
    >>> result = PrecisionResult(
    ...     y_true=np.array([0, 0, 1, 1, 2, 2]),
    ...     y_pred=np.array([0, 0, 1, 1, 2, 2]),
    ...     label_type="multiclass",
    ... )
    >>> result
    PrecisionResult(y_true=(6,), y_pred=(6,), label_type='multiclass', nan_policy='propagate')
    >>> result.compute_metrics()
    {'count': 6,
     'macro_precision': 1.0,
     'micro_precision': 1.0,
     'precision': array([1., 1., 1.]),
     'weighted_precision': 1.0}
    >>> # auto
    >>> result = PrecisionResult(
    ...     y_true=np.array([1, 0, 0, 1, 1]), y_pred=np.array([1, 0, 0, 1, 1])
    ... )
    >>> result
    PrecisionResult(y_true=(5,), y_pred=(5,), label_type='binary', nan_policy='propagate')
    >>> result.compute_metrics()
    {'count': 5, 'precision': 1.0}

    ```
    """

    def __init__(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        label_type: str = "auto",
        nan_policy: str = "propagate",
    ) -> None:
        self._y_true = y_true
        self._y_pred = y_pred
        self._label_type = (
            find_label_type(y_true=y_true, y_pred=y_pred) if label_type == "auto" else label_type
        )
        self._check_inputs()

        check_nan_policy(nan_policy)
        self._nan_policy = nan_policy

    def __repr__(self) -> str:
        args = repr_mapping_line(
            {
                "y_true": self._y_true.shape,
                "y_pred": self._y_pred.shape,
                "label_type": self._label_type,
                "nan_policy": self._nan_policy,
            }
        )
        return f"{self.__class__.__qualname__}({args})"

    @property
    def nan_policy(self) -> str:
        return self._nan_policy

    @property
    def label_type(self) -> str:
        return self._label_type

    @property
    def y_true(self) -> np.ndarray:
        return self._y_true

    @property
    def y_pred(self) -> np.ndarray:
        return self._y_pred

    def compute_metrics(self, prefix: str = "", suffix: str = "") -> dict[str, float]:
        return precision(
            y_true=self._y_true,
            y_pred=self._y_pred,
            label_type=self._label_type,
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
            and self.label_type == other.label_type
            and self.nan_policy == other.nan_policy
        )

    def generate_figures(
        self, prefix: str = "", suffix: str = ""  # noqa: ARG002
    ) -> dict[str, float]:
        return {}

    def _check_inputs(self) -> None:
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
        check_label_type(self._label_type)


class BasePrecisionResult(BaseResult):
    r"""Implement the base class to implement the precision results.

    Args:
        y_true: The ground truth target labels.
        y_pred: The predicted labels.
        nan_policy: The policy on how to handle NaN values in the input
            arrays. The following options are available: ``'omit'``,
            ``'propagate'``, and ``'raise'``.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.result import BinaryPrecisionResult
    >>> result = BinaryPrecisionResult(
    ...     y_true=np.array([1, 0, 0, 1, 1]), y_pred=np.array([1, 0, 0, 1, 1])
    ... )
    >>> result
    BinaryPrecisionResult(y_true=(5,), y_pred=(5,), nan_policy='propagate')
    >>> result.compute_metrics()
    {'count': 5, 'precision': 1.0}

    ```
    """

    def __init__(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        nan_policy: str = "propagate",
    ) -> None:
        self._y_true = y_true
        self._y_pred = y_pred

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
    def nan_policy(self) -> str:
        return self._nan_policy

    @property
    def y_true(self) -> np.ndarray:
        return self._y_true

    @property
    def y_pred(self) -> np.ndarray:
        return self._y_pred

    def equal(self, other: Any, equal_nan: bool = False) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return (
            objects_are_equal(self.y_true, other.y_true, equal_nan=equal_nan)
            and objects_are_equal(self.y_pred, other.y_pred, equal_nan=equal_nan)
            and self.nan_policy == other.nan_policy
        )


class BinaryPrecisionResult(BasePrecisionResult):
    r"""Implement the precision result for binary labels.

    Args:
        y_true: The ground truth target labels. This input must
            be an array of shape ``(n_samples, *)`` with ``0`` and
            ``1`` values.
        y_pred: The predicted labels. This input must be an array of
            shape ``(n_samples, *)`` with ``0`` and ``1`` values.
        nan_policy: The policy on how to handle NaN values in the input
            arrays. The following options are available: ``'omit'``,
            ``'propagate'``, and ``'raise'``.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.result import BinaryPrecisionResult
    >>> result = BinaryPrecisionResult(
    ...     y_true=np.array([1, 0, 0, 1, 1]), y_pred=np.array([1, 0, 0, 1, 1])
    ... )
    >>> result
    BinaryPrecisionResult(y_true=(5,), y_pred=(5,), nan_policy='propagate')
    >>> result.compute_metrics()
    {'count': 5, 'precision': 1.0}

    ```
    """

    def __init__(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        nan_policy: str = "propagate",
    ) -> None:
        check_same_shape_pred(y_true, y_pred)
        super().__init__(y_true=y_true.ravel(), y_pred=y_pred.ravel(), nan_policy=nan_policy)

    def compute_metrics(self, prefix: str = "", suffix: str = "") -> dict[str, float]:
        return binary_precision(
            y_true=self._y_true,
            y_pred=self._y_pred,
            prefix=prefix,
            suffix=suffix,
            nan_policy=self._nan_policy,
        )

    def generate_figures(self, prefix: str = "", suffix: str = "") -> dict[str, plt.Figure]:
        fig = binary_precision_recall_curve(
            y_true=self._y_true,
            y_pred=self._y_pred,
        )
        if fig is None:
            return {}
        return {f"{prefix}precision_recall{suffix}": fig}


class MulticlassPrecisionResult(BasePrecisionResult):
    r"""Implement the precision result for multiclass labels.

    Args:
        y_true: The ground truth target labels. This input must
            be an array of shape ``(n_samples, *)`` with values in
            ``{0, ..., n_classes-1}``.
        y_pred: The predicted labels. This input must be an array of
            shape ``(n_samples, *)`` with values in
            ``{0, ..., n_classes-1}``.
        nan_policy: The policy on how to handle NaN values in the input
            arrays. The following options are available: ``'omit'``,
            ``'propagate'``, and ``'raise'``.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.result import MulticlassPrecisionResult
    >>> result = MulticlassPrecisionResult(
    ...     y_true=np.array([0, 0, 1, 1, 2, 2]),
    ...     y_pred=np.array([0, 0, 1, 1, 2, 2]),
    ... )
    >>> result
    MulticlassPrecisionResult(y_true=(6,), y_pred=(6,), nan_policy='propagate')
    >>> result.compute_metrics()
    {'count': 6,
     'macro_precision': 1.0,
     'micro_precision': 1.0,
     'precision': array([1., 1., 1.]),
     'weighted_precision': 1.0}

    ```
    """

    def __init__(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        nan_policy: str = "propagate",
    ) -> None:
        check_same_shape_pred(y_true, y_pred)
        super().__init__(y_true=y_true.ravel(), y_pred=y_pred.ravel(), nan_policy=nan_policy)

    def compute_metrics(self, prefix: str = "", suffix: str = "") -> dict[str, float]:
        return multiclass_precision(
            y_true=self._y_true,
            y_pred=self._y_pred,
            prefix=prefix,
            suffix=suffix,
            nan_policy=self._nan_policy,
        )

    def generate_figures(
        self, prefix: str = "", suffix: str = ""  # noqa: ARG002
    ) -> dict[str, float]:
        return {}


class MultilabelPrecisionResult(BasePrecisionResult):
    r"""Implement the precision result for multilabel labels.

    Args:
        y_true: The ground truth target labels. This input must
            be an array of shape ``(n_samples, n_classes)`` with ``0``
            and ``1`` values.
        y_pred: The predicted labels. This input must be an array of
            shape ``(n_samples, n_classes)`` with ``0`` and ``1``
            values.
        nan_policy: The policy on how to handle NaN values in the input
            arrays. The following options are available: ``'omit'``,
            ``'propagate'``, and ``'raise'``.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.result import MultilabelPrecisionResult
    >>> result = MultilabelPrecisionResult(
    ...     y_true=np.array([[1, 0, 1], [0, 1, 0], [0, 1, 0], [1, 0, 1], [1, 0, 1]]),
    ...     y_pred=np.array([[1, 0, 1], [0, 1, 0], [0, 1, 0], [1, 0, 1], [1, 0, 1]]),
    ... )
    >>> result
    MultilabelPrecisionResult(y_true=(5, 3), y_pred=(5, 3), nan_policy='propagate')
    >>> result.compute_metrics()
    {'count': 5,
     'macro_precision': 1.0,
     'micro_precision': 1.0,
     'precision': array([1., 1., 1.]),
     'weighted_precision': 1.0}

    ```
    """

    def __init__(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        nan_policy: str = "propagate",
    ) -> None:
        check_same_shape_pred(y_true, y_pred)
        super().__init__(y_true=y_true, y_pred=y_pred, nan_policy=nan_policy)

    def compute_metrics(self, prefix: str = "", suffix: str = "") -> dict[str, float]:
        return multilabel_precision(
            y_true=self._y_true,
            y_pred=self._y_pred,
            prefix=prefix,
            suffix=suffix,
            nan_policy=self._nan_policy,
        )

    def generate_figures(
        self, prefix: str = "", suffix: str = ""  # noqa: ARG002
    ) -> dict[str, float]:
        return {}
