r"""Implement the F-beta result."""

from __future__ import annotations

__all__ = [
    "BaseFbetaScoreResult",
    "BinaryFbetaScoreResult",
    "MulticlassFbetaScoreResult",
    "MultilabelFbetaScoreResult",
]

from typing import TYPE_CHECKING, Any

from coola import objects_are_equal
from coola.utils.format import repr_mapping_line

from arkas.metric.classification.fbeta import (
    binary_fbeta_score,
    multiclass_fbeta_score,
    multilabel_fbeta_score,
)
from arkas.metric.utils import check_nan_policy, check_same_shape_pred
from arkas.result.base import BaseResult

if TYPE_CHECKING:
    from collections.abc import Sequence

    import numpy as np


class BaseFbetaScoreResult(BaseResult):
    r"""Implement the base class to implement the F-beta results.

    Args:
        y_true: The ground truth target labels.
        y_pred: The predicted labels.
        betas: The betas used to compute the F-beta scores.
        nan_policy: The policy on how to handle NaN values in the input
            arrays. The following options are available: ``'omit'``,
            ``'propagate'``, and ``'raise'``.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.result import BinaryFbetaScoreResult
    >>> result = BinaryFbetaScoreResult(
    ...     y_true=np.array([1, 0, 0, 1, 1]), y_pred=np.array([1, 0, 0, 1, 1])
    ... )
    >>> result
    BinaryFbetaScoreResult(y_true=(5,), y_pred=(5,), betas=(1,), nan_policy='propagate')
    >>> result.compute_metrics()
    {'count': 5, 'f1': 1.0}

    ```
    """

    def __init__(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        betas: Sequence[float] = (1,),
        nan_policy: str = "propagate",
    ) -> None:
        self._y_true = y_true
        self._y_pred = y_pred
        self._betas = tuple(betas)

        check_nan_policy(nan_policy)
        self._nan_policy = nan_policy

    def __repr__(self) -> str:
        args = repr_mapping_line(
            {
                "y_true": self._y_true.shape,
                "y_pred": self._y_pred.shape,
                "betas": self._betas,
                "nan_policy": self._nan_policy,
            }
        )
        return f"{self.__class__.__qualname__}({args})"

    @property
    def nan_policy(self) -> str:
        return self._nan_policy

    @property
    def betas(self) -> tuple[float, ...]:
        return self._betas

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
            and objects_are_equal(self.betas, other.betas, equal_nan=equal_nan)
            and self.nan_policy == other.nan_policy
        )


class BinaryFbetaScoreResult(BaseFbetaScoreResult):
    r"""Implement the F-beta result for binary labels.

    Args:
        y_true: The ground truth target labels. This input must
            be an array of shape ``(n_samples, *)`` with ``0`` and
            ``1`` values.
        y_pred: The predicted labels. This input must be an array of
            shape ``(n_samples, *)`` with ``0`` and ``1`` values.
        betas: The betas used to compute the F-beta scores.
        nan_policy: The policy on how to handle NaN values in the input
            arrays. The following options are available: ``'omit'``,
            ``'propagate'``, and ``'raise'``.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.result import BinaryFbetaScoreResult
    >>> result = BinaryFbetaScoreResult(
    ...     y_true=np.array([1, 0, 0, 1, 1]), y_pred=np.array([1, 0, 0, 1, 1])
    ... )
    >>> result
    BinaryFbetaScoreResult(y_true=(5,), y_pred=(5,), betas=(1,), nan_policy='propagate')
    >>> result.compute_metrics()
    {'count': 5, 'f1': 1.0}

    ```
    """

    def __init__(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        betas: Sequence[float] = (1,),
        nan_policy: str = "propagate",
    ) -> None:
        check_same_shape_pred(y_true, y_pred)
        super().__init__(
            y_true=y_true.ravel(), y_pred=y_pred.ravel(), betas=betas, nan_policy=nan_policy
        )

    def compute_metrics(self, prefix: str = "", suffix: str = "") -> dict[str, float]:
        return binary_fbeta_score(
            y_true=self._y_true,
            y_pred=self._y_pred,
            prefix=prefix,
            suffix=suffix,
            betas=self._betas,
            nan_policy=self._nan_policy,
        )

    def generate_figures(
        self, prefix: str = "", suffix: str = ""  # noqa: ARG002
    ) -> dict[str, float]:
        return {}


class MulticlassFbetaScoreResult(BaseFbetaScoreResult):
    r"""Implement the F-beta result for multiclass labels.

    Args:
        y_true: The ground truth target labels. This input must
            be an array of shape ``(n_samples, *)`` with values in
            ``{0, ..., n_classes-1}``.
        y_pred: The predicted labels. This input must be an array of
            shape ``(n_samples, *)`` with values in
            ``{0, ..., n_classes-1}``.
        betas: The betas used to compute the F-beta scores.
        nan_policy: The policy on how to handle NaN values in the input
            arrays. The following options are available: ``'omit'``,
            ``'propagate'``, and ``'raise'``.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.result import MulticlassFbetaScoreResult
    >>> result = MulticlassFbetaScoreResult(
    ...     y_true=np.array([0, 0, 1, 1, 2, 2]),
    ...     y_pred=np.array([0, 0, 1, 1, 2, 2]),
    ... )
    >>> result
    MulticlassFbetaScoreResult(y_true=(6,), y_pred=(6,), betas=(1,), nan_policy='propagate')
    >>> result.compute_metrics()
    {'count': 6,
     'f1': array([1., 1., 1.]),
     'macro_f1': 1.0,
     'micro_f1': 1.0,
     'weighted_f1': 1.0}

    ```
    """

    def __init__(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        betas: Sequence[float] = (1,),
        nan_policy: str = "propagate",
    ) -> None:
        check_same_shape_pred(y_true, y_pred)
        super().__init__(
            y_true=y_true.ravel(), y_pred=y_pred.ravel(), betas=betas, nan_policy=nan_policy
        )

    def compute_metrics(self, prefix: str = "", suffix: str = "") -> dict[str, float]:
        return multiclass_fbeta_score(
            y_true=self._y_true,
            y_pred=self._y_pred,
            prefix=prefix,
            suffix=suffix,
            betas=self._betas,
            nan_policy=self._nan_policy,
        )

    def generate_figures(
        self, prefix: str = "", suffix: str = ""  # noqa: ARG002
    ) -> dict[str, float]:
        return {}


class MultilabelFbetaScoreResult(BaseFbetaScoreResult):
    r"""Implement the F-beta result for multilabel labels.

    Args:
        y_true: The ground truth target labels. This input must
            be an array of shape ``(n_samples, n_classes)`` with ``0``
            and ``1`` values.
        y_pred: The predicted labels. This input must be an array of
            shape ``(n_samples, n_classes)`` with ``0`` and ``1``
            values.
        betas: The betas used to compute the F-beta scores.
        nan_policy: The policy on how to handle NaN values in the input
            arrays. The following options are available: ``'omit'``,
            ``'propagate'``, and ``'raise'``.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.result import MultilabelFbetaScoreResult
    >>> result = MultilabelFbetaScoreResult(
    ...     y_true=np.array([[1, 0, 1], [0, 1, 0], [0, 1, 0], [1, 0, 1], [1, 0, 1]]),
    ...     y_pred=np.array([[1, 0, 1], [0, 1, 0], [0, 1, 0], [1, 0, 1], [1, 0, 1]]),
    ... )
    >>> result
    MultilabelFbetaScoreResult(y_true=(5, 3), y_pred=(5, 3), betas=(1,), nan_policy='propagate')
    >>> result.compute_metrics()
    {'count': 5,
     'f1': array([1., 1., 1.]),
     'macro_f1': 1.0,
     'micro_f1': 1.0,
     'weighted_f1': 1.0}

    ```
    """

    def __init__(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        betas: Sequence[float] = (1,),
        nan_policy: str = "propagate",
    ) -> None:
        check_same_shape_pred(y_true, y_pred)
        super().__init__(y_true=y_true, y_pred=y_pred, betas=betas, nan_policy=nan_policy)

    def compute_metrics(self, prefix: str = "", suffix: str = "") -> dict[str, float]:
        return multilabel_fbeta_score(
            y_true=self._y_true,
            y_pred=self._y_pred,
            prefix=prefix,
            suffix=suffix,
            betas=self._betas,
            nan_policy=self._nan_policy,
        )

    def generate_figures(
        self, prefix: str = "", suffix: str = ""  # noqa: ARG002
    ) -> dict[str, float]:
        return {}
