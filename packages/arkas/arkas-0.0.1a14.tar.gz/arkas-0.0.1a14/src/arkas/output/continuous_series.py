r"""Implement an output to analyze a series with continuous values."""

from __future__ import annotations

__all__ = ["ContinuousSeriesOutput"]

from typing import TYPE_CHECKING, Any

from coola.utils import repr_indent, repr_mapping, str_indent, str_mapping

from arkas.content.continuous_series import ContinuousSeriesContentGenerator
from arkas.evaluator2.vanilla import Evaluator
from arkas.output.lazy import BaseLazyOutput
from arkas.plotter.continuous_series import ContinuousSeriesPlotter

if TYPE_CHECKING:
    from arkas.state.series import SeriesState


class ContinuousSeriesOutput(BaseLazyOutput):
    r"""Implement an output to analyze a series with continuous values.

    Args:
        state: The state containing the Series to analyze.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from arkas.output import ContinuousSeriesOutput
    >>> from arkas.state import SeriesState
    >>> output = ContinuousSeriesOutput(SeriesState(pl.Series("col1", [1, 2, 3, 4, 5, 6, 7])))
    >>> output
    ContinuousSeriesOutput(
      (state): SeriesState(name='col1', values=(7,), figure_config=MatplotlibFigureConfig())
    )
    >>> output.get_content_generator()
    ContinuousSeriesContentGenerator(
      (state): SeriesState(name='col1', values=(7,), figure_config=MatplotlibFigureConfig())
    )
    >>> output.get_evaluator()
    Evaluator(count=0)
    >>> output.get_plotter()
    ContinuousSeriesPlotter(
      (state): SeriesState(name='col1', values=(7,), figure_config=MatplotlibFigureConfig())
    )

    ```
    """

    def __init__(self, state: SeriesState) -> None:
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

    def _get_content_generator(self) -> ContinuousSeriesContentGenerator:
        return ContinuousSeriesContentGenerator(self._state)

    def _get_evaluator(self) -> Evaluator:
        return Evaluator()

    def _get_plotter(self) -> ContinuousSeriesPlotter:
        return ContinuousSeriesPlotter(self._state)
