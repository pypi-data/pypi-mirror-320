r"""Contain the implementation of a plotter to analyze a Series with
continuous values."""

from __future__ import annotations

__all__ = ["BaseFigureCreator", "ContinuousSeriesPlotter", "MatplotlibFigureCreator"]

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

import matplotlib.pyplot as plt
from coola.utils import repr_indent, repr_mapping, str_indent, str_mapping

from arkas.figure.creator import FigureCreatorRegistry
from arkas.figure.html import HtmlFigure
from arkas.figure.matplotlib import MatplotlibFigure, MatplotlibFigureConfig
from arkas.figure.utils import MISSING_FIGURE_MESSAGE
from arkas.plot.continuous import hist_continuous
from arkas.plot.utils.hist import adjust_nbins
from arkas.plotter.base import BasePlotter
from arkas.plotter.vanilla import Plotter
from arkas.utils.array import filter_range, nonnan, to_array
from arkas.utils.range import find_range

if TYPE_CHECKING:
    from arkas.figure.base import BaseFigure
    from arkas.state.series import SeriesState


class BaseFigureCreator(ABC):
    r"""Define the base class to create a figure with the content of the
    column."""

    @abstractmethod
    def create(self, state: SeriesState) -> BaseFigure:
        r"""Create a figure with the content of the column.

        Args:
            state: The state containing the Series to analyze.

        Returns:
            The generated figure.

        Example usage:

        ```pycon

        >>> import polars as pl
        >>> from arkas.figure import MatplotlibFigureConfig
        >>> from arkas.state import SeriesState
        >>> creator = MatplotlibFigureCreator()
        >>> fig = creator.create(SeriesState(pl.Series("col1", [1, 2, 3, 4, 5, 6, 7])))

        ```
        """


class MatplotlibFigureCreator(BaseFigureCreator):
    r"""Create a matplotlib figure with the content of each column.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from arkas.figure import MatplotlibFigureConfig
    >>> from arkas.state import SeriesState
    >>> creator = MatplotlibFigureCreator()
    >>> fig = creator.create(SeriesState(pl.Series("col1", [1, 2, 3, 4, 5, 6, 7])))

    ```
    """

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}()"

    def create(self, state: SeriesState) -> BaseFigure:
        array = nonnan(to_array(state.series))
        if array.size == 0:
            return HtmlFigure(MISSING_FIGURE_MESSAGE)

        fig, ax = plt.subplots(**state.figure_config.get_arg("init", {}))
        xmin, xmax = find_range(
            array,
            xmin=state.figure_config.get_arg("xmin"),
            xmax=state.figure_config.get_arg("xmax"),
        )
        nbins = adjust_nbins(
            nbins=state.figure_config.get_arg("nbins"),
            array=filter_range(array, xmin=xmin, xmax=xmax),
        )
        hist_continuous(
            ax=ax,
            array=array,
            nbins=nbins,
            xmin=xmin,
            xmax=xmax,
            yscale=state.figure_config.get_arg("yscale", default="linear"),
        )
        ax.set_title(f"data distribution for column {state.series.name!r}")
        fig.tight_layout()
        return MatplotlibFigure(fig)


class ContinuousSeriesPlotter(BasePlotter):
    r"""Implement a plotter that analyzes a column with continuous
    values.

    Args:
        state: The state containing the Series to analyze.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from arkas.plotter import ContinuousSeriesPlotter
    >>> from arkas.state import SeriesState
    >>> plotter = ContinuousSeriesPlotter(SeriesState(pl.Series("col1", [1, 2, 3, 4, 5, 6, 7])))
    >>> plotter
    ContinuousSeriesPlotter(
      (state): SeriesState(name='col1', values=(7,), figure_config=MatplotlibFigureConfig())
    )

    ```
    """

    registry = FigureCreatorRegistry[BaseFigureCreator](
        {MatplotlibFigureConfig.backend(): MatplotlibFigureCreator()}
    )

    def __init__(self, state: SeriesState) -> None:
        self._state = state

    def __repr__(self) -> str:
        args = repr_indent(repr_mapping({"state": self._state}))
        return f"{self.__class__.__qualname__}(\n  {args}\n)"

    def __str__(self) -> str:
        args = str_indent(str_mapping({"state": self._state}))
        return f"{self.__class__.__qualname__}(\n  {args}\n)"

    def compute(self) -> Plotter:
        return Plotter(self.plot())

    def equal(self, other: Any, equal_nan: bool = False) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._state.equal(other._state, equal_nan=equal_nan)

    def plot(self, prefix: str = "", suffix: str = "") -> dict:
        figure = self.registry.find_creator(self._state.figure_config.backend()).create(self._state)
        return {f"{prefix}continuous_histogram{suffix}": figure}
