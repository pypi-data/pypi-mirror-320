r"""Contain the Spearman correlation evaluator."""

from __future__ import annotations

__all__ = ["SpearmanCorrelationEvaluator"]

import logging
from typing import TYPE_CHECKING

from coola.utils.format import repr_mapping_line

from arkas.evaluator.lazy import BaseLazyEvaluator
from arkas.metric.utils import check_nan_policy
from arkas.result import Result, SpearmanCorrelationResult
from arkas.utils.array import to_array

if TYPE_CHECKING:
    import polars as pl


logger = logging.getLogger(__name__)


class SpearmanCorrelationEvaluator(BaseLazyEvaluator[SpearmanCorrelationResult]):
    r"""Implement the Spearman correlation evaluator.

    Args:
        x: The key or column name of the ground truth target
            values.
        y: The key or column name of the predicted values.
        alternative: The alternative hypothesis. Default is 'two-sided'.
            The following options are available:
            - 'two-sided': the correlation is nonzero
            - 'less': the correlation is negative (less than zero)
            - 'greater': the correlation is positive (greater than zero)
        drop_nulls: If ``True``, the rows with null values in
            ``x`` or ``y`` columns are dropped.
        nan_policy: The policy on how to handle NaN values in the input
            arrays. The following options are available: ``'omit'``,
            ``'propagate'``, and ``'raise'``.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from arkas.evaluator import SpearmanCorrelationEvaluator
    >>> evaluator = SpearmanCorrelationEvaluator(x="target", y="pred")
    >>> evaluator
    SpearmanCorrelationEvaluator(x='target', y='pred', alternative='two-sided', drop_nulls=True, nan_policy='propagate')
    >>> data = pl.DataFrame({"pred": [1, 2, 3, 4, 5], "target": [1, 2, 3, 4, 5]})
    >>> result = evaluator.evaluate(data)
    >>> result
    SpearmanCorrelationResult(x=(5,), y=(5,), alternative='two-sided', nan_policy='propagate')

    ```
    """

    def __init__(
        self,
        x: str,
        y: str,
        alternative: str = "two-sided",
        drop_nulls: bool = True,
        nan_policy: str = "propagate",
    ) -> None:
        super().__init__(drop_nulls=drop_nulls)
        self._x = x
        self._y = y
        self._alternative = alternative

        check_nan_policy(nan_policy)
        self._nan_policy = nan_policy

    def __repr__(self) -> str:
        args = repr_mapping_line(
            {
                "x": self._x,
                "y": self._y,
                "alternative": self._alternative,
                "drop_nulls": self._drop_nulls,
                "nan_policy": self._nan_policy,
            }
        )
        return f"{self.__class__.__qualname__}({args})"

    def evaluate(self, data: pl.DataFrame, lazy: bool = True) -> SpearmanCorrelationResult | Result:
        logger.info(
            f"Evaluating the Spearman correlation | x={self._x} | "
            f"y={self._y} | drop_nulls={self._drop_nulls} | "
            f"nan_policy={self._nan_policy!r}"
        )
        return self._evaluate(data, lazy)

    def _compute_result(self, data: pl.DataFrame) -> SpearmanCorrelationResult:
        return SpearmanCorrelationResult(
            x=to_array(data[self._x]).ravel(),
            y=to_array(data[self._y]).ravel(),
            alternative=self._alternative,
            nan_policy=self._nan_policy,
        )

    def _get_columns(self) -> tuple[str, ...]:
        return (self._x, self._y)
