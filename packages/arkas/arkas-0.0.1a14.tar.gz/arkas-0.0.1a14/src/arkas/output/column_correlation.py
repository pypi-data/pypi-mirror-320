r"""Implement an output to analyze the correlation between columns."""

from __future__ import annotations

__all__ = ["ColumnCorrelationOutput"]

from typing import TYPE_CHECKING, Any

from coola.utils import repr_indent, repr_mapping, str_indent, str_mapping

from arkas.content.column_correlation import ColumnCorrelationContentGenerator
from arkas.evaluator2.column_correlation import ColumnCorrelationEvaluator
from arkas.output.lazy import BaseLazyOutput
from arkas.plotter.vanilla import Plotter

if TYPE_CHECKING:
    from arkas.state.target_dataframe import TargetDataFrameState


class ColumnCorrelationOutput(BaseLazyOutput):
    r"""Implement an output to summarize the numeric columns of a
    DataFrame.

    Args:
        state: The state containing the DataFrame to analyze.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from arkas.output import ColumnCorrelationOutput
    >>> from arkas.state import TargetDataFrameState
    >>> frame = pl.DataFrame(
    ...     {
    ...         "col1": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0],
    ...         "col2": [7.0, 6.0, 5.0, 4.0, 3.0, 2.0, 1.0],
    ...         "col3": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0],
    ...     },
    ... )
    >>> output = ColumnCorrelationOutput(TargetDataFrameState(frame, target_column="col3"))
    >>> output
    ColumnCorrelationOutput(
      (state): TargetDataFrameState(dataframe=(7, 3), target_column='col3', nan_policy='propagate', figure_config=MatplotlibFigureConfig())
    )
    >>> output.get_content_generator()
    ColumnCorrelationContentGenerator(
      (state): TargetDataFrameState(dataframe=(7, 3), target_column='col3', nan_policy='propagate', figure_config=MatplotlibFigureConfig())
    )
    >>> output.get_evaluator()
    ColumnCorrelationEvaluator(
      (state): TargetDataFrameState(dataframe=(7, 3), target_column='col3', nan_policy='propagate', figure_config=MatplotlibFigureConfig())
    )
    >>> output.get_plotter()
    Plotter(count=0)

    ```
    """

    def __init__(self, state: TargetDataFrameState) -> None:
        self._state = state

    def __repr__(self) -> str:
        args = repr_indent(repr_mapping({"state": self._state}))
        return f"{self.__class__.__qualname__}(\n  {args}\n)"

    def __str__(self) -> str:
        args = str_indent(str_mapping({"state": self._state}))
        return f"{self.__class__.__qualname__}(\n  {args}\n)"

    def equal(self, other: Any, equal_nan: bool = False) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._state.equal(other._state, equal_nan=equal_nan)

    def _get_content_generator(self) -> ColumnCorrelationContentGenerator:
        return ColumnCorrelationContentGenerator(self._state)

    def _get_evaluator(self) -> ColumnCorrelationEvaluator:
        return ColumnCorrelationEvaluator(self._state)

    def _get_plotter(self) -> Plotter:
        return Plotter()
