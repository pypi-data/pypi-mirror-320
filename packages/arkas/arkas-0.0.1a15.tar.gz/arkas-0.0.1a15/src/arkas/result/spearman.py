r"""Implement the Spearman correlation result."""

from __future__ import annotations

__all__ = ["SpearmanCorrelationResult"]

from typing import TYPE_CHECKING, Any

from coola import objects_are_equal
from coola.utils.format import repr_mapping_line

from arkas.metric.correlation.spearman import spearmanr
from arkas.metric.utils import check_nan_policy, check_same_shape
from arkas.result.base import BaseResult

if TYPE_CHECKING:
    import numpy as np


class SpearmanCorrelationResult(BaseResult):
    r"""Implement the Spearman correlation result.

    Args:
        x: The first input array.
        y: The second input array.
        alternative: The alternative hypothesis. Default is 'two-sided'.
            The following options are available:
            - 'two-sided': the correlation is nonzero
            - 'less': the correlation is negative (less than zero)
            - 'greater': the correlation is positive (greater than zero)
        nan_policy: The policy on how to handle NaN values in the input
            arrays. The following options are available: ``'omit'``,
            ``'propagate'``, and ``'raise'``.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.result import SpearmanCorrelationResult
    >>> result = SpearmanCorrelationResult(
    ...     x=np.array([1, 2, 3, 4, 5, 6, 7, 8, 9]),
    ...     y=np.array([1, 2, 3, 4, 5, 6, 7, 8, 9]),
    ... )
    >>> result
    SpearmanCorrelationResult(x=(9,), y=(9,), alternative='two-sided', nan_policy='propagate')
    >>> result.compute_metrics()
    {'count': 9, 'spearman_coeff': 1.0, 'spearman_pvalue': 0.0}

    ```
    """

    def __init__(
        self,
        x: np.ndarray,
        y: np.ndarray,
        alternative: str = "two-sided",
        nan_policy: str = "propagate",
    ) -> None:
        self._x = x.ravel()
        self._y = y.ravel()
        self._alternative = alternative

        check_same_shape([self._x, self._y])

        check_nan_policy(nan_policy)
        self._nan_policy = nan_policy

    def __repr__(self) -> str:
        args = repr_mapping_line(
            {
                "x": self._x.shape,
                "y": self._y.shape,
                "alternative": self._alternative,
                "nan_policy": self._nan_policy,
            }
        )
        return f"{self.__class__.__qualname__}({args})"

    @property
    def nan_policy(self) -> str:
        return self._nan_policy

    @property
    def x(self) -> np.ndarray:
        return self._x

    @property
    def y(self) -> np.ndarray:
        return self._y

    @property
    def alternative(self) -> str:
        return self._alternative

    def compute_metrics(self, prefix: str = "", suffix: str = "") -> dict[str, float]:
        return spearmanr(
            x=self._x,
            y=self._y,
            alternative=self._alternative,
            prefix=prefix,
            suffix=suffix,
            nan_policy=self._nan_policy,
        )

    def equal(self, other: Any, equal_nan: bool = False) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return (
            objects_are_equal(self.x, other.x, equal_nan=equal_nan)
            and objects_are_equal(self.y, other.y, equal_nan=equal_nan)
            and self.alternative == other.alternative
            and self.nan_policy == other.nan_policy
        )

    def generate_figures(
        self, prefix: str = "", suffix: str = ""  # noqa: ARG002
    ) -> dict[str, float]:
        return {}
