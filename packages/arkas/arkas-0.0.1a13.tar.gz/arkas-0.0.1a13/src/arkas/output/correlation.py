r"""Implement an output to analyze the correlation between columns."""

from __future__ import annotations

__all__ = ["CorrelationOutput"]

from typing import TYPE_CHECKING, Any

from coola.utils import repr_indent, repr_mapping, str_indent, str_mapping

from arkas.content.correlation import CorrelationContentGenerator
from arkas.evaluator2.correlation import CorrelationEvaluator
from arkas.output.lazy import BaseLazyOutput
from arkas.plotter.correlation import CorrelationPlotter
from arkas.utils.dataframe import check_num_columns

if TYPE_CHECKING:
    from arkas.state.dataframe import DataFrameState


class CorrelationOutput(BaseLazyOutput):
    r"""Implement an output to summarize the numeric columns of a
    DataFrame.

    Args:
        state: The state containing the DataFrame to analyze.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from arkas.output import CorrelationOutput
    >>> from arkas.state import DataFrameState
    >>> frame = pl.DataFrame(
    ...     {
    ...         "col1": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0],
    ...         "col2": [7.0, 6.0, 5.0, 4.0, 3.0, 2.0, 1.0],
    ...     },
    ... )
    >>> output = CorrelationOutput(DataFrameState(frame))
    >>> output
    CorrelationOutput(
      (state): DataFrameState(dataframe=(7, 2), nan_policy='propagate', figure_config=MatplotlibFigureConfig())
    )
    >>> output.get_content_generator()
    CorrelationContentGenerator(
      (state): DataFrameState(dataframe=(7, 2), nan_policy='propagate', figure_config=MatplotlibFigureConfig())
    )
    >>> output.get_evaluator()
    CorrelationEvaluator(
      (state): DataFrameState(dataframe=(7, 2), nan_policy='propagate', figure_config=MatplotlibFigureConfig())
    )
    >>> output.get_plotter()
    CorrelationPlotter(
      (state): DataFrameState(dataframe=(7, 2), nan_policy='propagate', figure_config=MatplotlibFigureConfig())
    )

    ```
    """

    def __init__(self, state: DataFrameState) -> None:
        check_num_columns(state.dataframe, num_columns=2)
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

    def _get_content_generator(self) -> CorrelationContentGenerator:
        return CorrelationContentGenerator(self._state)

    def _get_evaluator(self) -> CorrelationEvaluator:
        return CorrelationEvaluator(self._state)

    def _get_plotter(self) -> CorrelationPlotter:
        return CorrelationPlotter(self._state)
