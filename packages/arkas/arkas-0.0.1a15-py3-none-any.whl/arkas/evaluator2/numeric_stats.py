r"""Implement an evaluator to compute statistics of numerical column."""

from __future__ import annotations

__all__ = ["NumericStatisticsEvaluator"]


from typing import TYPE_CHECKING, Any

from coola.utils import repr_indent, repr_mapping, str_indent, str_mapping

from arkas.evaluator2.base import BaseEvaluator
from arkas.evaluator2.vanilla import Evaluator
from arkas.utils.stats import compute_statistics_continuous

if TYPE_CHECKING:
    from arkas.state.dataframe import DataFrameState


class NumericStatisticsEvaluator(BaseEvaluator):
    r"""Implement an evaluator to compute statistics of numerical
    columns.

    Args:
        state: The state containing the DataFrame to analyze.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from arkas.evaluator2 import NumericStatisticsEvaluator
    >>> from arkas.state import DataFrameState
    >>> dataframe = pl.DataFrame(
    ...     {
    ...         "col1": [0, 1, 1, 0, 0, 1, 0],
    ...         "col2": [0, 1, 0, 1, 0, 1, 0],
    ...         "col3": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0],
    ...     }
    ... )
    >>> evaluator = NumericStatisticsEvaluator(DataFrameState(dataframe))
    >>> evaluator
    NumericStatisticsEvaluator(
      (state): DataFrameState(dataframe=(7, 3), nan_policy='propagate', figure_config=MatplotlibFigureConfig())
    )
    >>> evaluator.evaluate()
    {'col1': {'count': 7, ...}, 'col2': {'count': 7, ...}}

    ```
    """

    def __init__(self, state: DataFrameState) -> None:
        self._state = state

    def __repr__(self) -> str:
        args = repr_indent(repr_mapping({"state": self._state}))
        return f"{self.__class__.__qualname__}(\n  {args}\n)"

    def __str__(self) -> str:
        args = str_indent(str_mapping({"state": self._state}))
        return f"{self.__class__.__qualname__}(\n  {args}\n)"

    def compute(self) -> Evaluator:
        return Evaluator(metrics=self.evaluate())

    def equal(self, other: Any, equal_nan: bool = False) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._state.equal(other._state, equal_nan=equal_nan)

    def evaluate(self, prefix: str = "", suffix: str = "") -> dict[str, dict[str, float]]:
        return {
            f"{prefix}{series.name}{suffix}": compute_statistics_continuous(series)
            for series in self._state.dataframe
        }
