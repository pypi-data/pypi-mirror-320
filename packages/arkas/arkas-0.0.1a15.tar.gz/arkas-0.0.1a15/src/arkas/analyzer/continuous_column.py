r"""Implement an analyzer that  analyzes a column with continuous
values."""

from __future__ import annotations

__all__ = ["ContinuousColumnAnalyzer"]

import logging
from typing import TYPE_CHECKING, Any

from coola import objects_are_equal
from coola.utils.format import repr_mapping_line

from arkas.analyzer.lazy import BaseLazyAnalyzer
from arkas.output.continuous_series import ContinuousSeriesOutput
from arkas.state.series import SeriesState

if TYPE_CHECKING:
    import polars as pl

    from arkas.figure import BaseFigureConfig

logger = logging.getLogger(__name__)


class ContinuousColumnAnalyzer(BaseLazyAnalyzer):
    r"""Implement an analyzer that analyzes a column with continuous
    values.

    Args:
        column: The column to analyze.
        figure_config: The figure configuration.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from arkas.analyzer import ContinuousColumnAnalyzer
    >>> analyzer = ContinuousColumnAnalyzer(column="col1")
    >>> analyzer
    ContinuousColumnAnalyzer(column='col1', figure_config=None)
    >>> frame = pl.DataFrame(
    ...     {
    ...         "col1": [0, 1, 0, 1],
    ...         "col2": [1, 0, 1, 0],
    ...         "col3": [1, 1, 1, 1],
    ...     },
    ...     schema={"col1": pl.Int64, "col2": pl.Int64, "col3": pl.Int64},
    ... )
    >>> output = analyzer.analyze(frame)
    >>> output
    ContinuousSeriesOutput(
      (state): SeriesState(name='col1', values=(4,), figure_config=MatplotlibFigureConfig())
    )

    ```
    """

    def __init__(self, column: str, figure_config: BaseFigureConfig | None = None) -> None:
        self._column = column
        self._figure_config = figure_config

    def __repr__(self) -> str:
        args = repr_mapping_line(self.get_args())
        return f"{self.__class__.__qualname__}({args})"

    def equal(self, other: Any, equal_nan: bool = False) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return objects_are_equal(self.get_args(), other.get_args(), equal_nan=equal_nan)

    def get_args(self) -> dict:
        return {"column": self._column, "figure_config": self._figure_config}

    def _analyze(self, frame: pl.DataFrame) -> ContinuousSeriesOutput:
        logger.info(f"Analyzing the continuous distribution of column {self._column!r}...")
        return ContinuousSeriesOutput(
            state=SeriesState(
                series=frame[self._column],
                figure_config=self._figure_config,
            )
        )
