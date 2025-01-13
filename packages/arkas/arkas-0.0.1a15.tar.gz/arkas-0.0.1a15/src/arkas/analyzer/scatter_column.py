r"""Implement an analyzer that plots the content of each column."""

from __future__ import annotations

__all__ = ["ScatterColumnAnalyzer"]

import logging
from typing import TYPE_CHECKING, Any

from coola import objects_are_equal
from coola.utils.format import repr_mapping_line
from grizz.utils.format import str_shape_diff

from arkas.analyzer.lazy import BaseLazyAnalyzer
from arkas.output.scatter_column import ScatterColumnOutput
from arkas.state.scatter_dataframe import ScatterDataFrameState

if TYPE_CHECKING:
    import polars as pl

    from arkas.figure import BaseFigureConfig

logger = logging.getLogger(__name__)


class ScatterColumnAnalyzer(BaseLazyAnalyzer):
    r"""Implement an analyzer that plots the content of each column.

    Args:
        x: The x-axis data column.
        y: The y-axis data column.
        color: An optional color axis data column.
        figure_config: The figure configuration.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from arkas.analyzer import ScatterColumnAnalyzer
    >>> analyzer = ScatterColumnAnalyzer(x="col1", y="col2")
    >>> analyzer
    ScatterColumnAnalyzer(x='col1', y='col2', color=None, figure_config=None)
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
    ScatterColumnOutput(
      (state): ScatterDataFrameState(dataframe=(4, 2), x='col1', y='col2', color=None, nan_policy='propagate', figure_config=MatplotlibFigureConfig())
    )

    ```
    """

    def __init__(
        self,
        x: str,
        y: str,
        color: str | None = None,
        figure_config: BaseFigureConfig | None = None,
    ) -> None:
        self._x = x
        self._y = y
        self._color = color
        self._figure_config = figure_config

    def __repr__(self) -> str:
        args = repr_mapping_line(self.get_args())
        return f"{self.__class__.__qualname__}({args})"

    def equal(self, other: Any, equal_nan: bool = False) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return objects_are_equal(self.get_args(), other.get_args(), equal_nan=equal_nan)

    def get_args(self) -> dict:
        return {
            "x": self._x,
            "y": self._y,
            "color": self._color,
            "figure_config": self._figure_config,
        }

    def _analyze(self, frame: pl.DataFrame) -> ScatterColumnOutput:
        logger.info(f"Plotting the content of {self._x!r}, {self._y!r}, and {self._color!r}...")
        dataframe = frame.select([self._x, self._y] + ([self._color] if self._color else []))
        logger.info(str_shape_diff(orig=frame.shape, final=dataframe.shape))
        return ScatterColumnOutput(
            state=ScatterDataFrameState(
                dataframe=dataframe,
                x=self._x,
                y=self._y,
                color=self._color,
                figure_config=self._figure_config,
            )
        )
