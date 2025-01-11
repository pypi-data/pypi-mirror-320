r"""Contain the implementation of a correlation plotter."""

from __future__ import annotations

__all__ = ["BaseFigureCreator", "CorrelationPlotter", "MatplotlibFigureCreator"]

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

import matplotlib.pyplot as plt
from coola.utils import repr_indent, repr_mapping, str_indent, str_mapping

from arkas.figure.creator import FigureCreatorRegistry
from arkas.figure.html import HtmlFigure
from arkas.figure.matplotlib import MatplotlibFigure, MatplotlibFigureConfig
from arkas.figure.utils import MISSING_FIGURE_MESSAGE
from arkas.plotter.base import BasePlotter
from arkas.plotter.vanilla import Plotter
from arkas.utils.dataframe import check_num_columns
from arkas.utils.range import find_range

if TYPE_CHECKING:
    from arkas.figure.base import BaseFigure
    from arkas.state.dataframe import DataFrameState


class BaseFigureCreator(ABC):
    r"""Define the base class to create a figure with the content of
    each column."""

    @abstractmethod
    def create(self, state: DataFrameState) -> BaseFigure:
        r"""Create a figure with the content of each column.

        Args:
            state: The state containing the DataFrame to analyze.
                The DataFrame must have only 2 columns, which are the
                two columns to analyze.

        Returns:
            The generated figure.

        Example usage:

        ```pycon

        >>> import polars as pl
        >>> from arkas.figure import MatplotlibFigureConfig
        >>> from arkas.state import DataFrameState
        >>> from arkas.plotter.correlation import MatplotlibFigureCreator
        >>> creator = MatplotlibFigureCreator()
        >>> frame = pl.DataFrame(
        ...     {
        ...         "col1": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0],
        ...         "col3": [2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0],
        ...     },
        ... )
        >>> fig = creator.create(DataFrameState(frame))

        ```
        """


class MatplotlibFigureCreator(BaseFigureCreator):
    r"""Create a matplotlib figure with the content of each column.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from arkas.figure import MatplotlibFigureConfig
    >>> from arkas.state import DataFrameState
    >>> from arkas.plotter.correlation import MatplotlibFigureCreator
    >>> creator = MatplotlibFigureCreator()
    >>> frame = pl.DataFrame(
    ...     {
    ...         "col1": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0],
    ...         "col3": [2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0],
    ...     },
    ... )
    >>> fig = creator.create(DataFrameState(frame))

    ```
    """

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}()"

    def create(self, state: DataFrameState) -> BaseFigure:
        if state.dataframe.shape[0] == 0:
            return HtmlFigure(MISSING_FIGURE_MESSAGE)

        check_num_columns(state.dataframe, num_columns=2)
        xcol, ycol = state.dataframe.columns

        fig, ax = plt.subplots(**state.figure_config.get_arg("init", {}))
        x = state.dataframe[xcol].to_numpy()
        y = state.dataframe[ycol].to_numpy()
        ax.scatter(x=x, y=y)

        xmin, xmax = find_range(
            x,
            xmin=state.figure_config.get_arg("xmin"),
            xmax=state.figure_config.get_arg("xmax"),
        )
        if xmin < xmax:
            ax.set_xlim(xmin, xmax)
        ymin, ymax = find_range(
            y,
            xmin=state.figure_config.get_arg("ymin"),
            xmax=state.figure_config.get_arg("ymax"),
        )
        if ymin < ymax:
            ax.set_ylim(ymin, ymax)
        ax.set_xlabel(xcol)
        ax.set_ylabel(ycol)
        if xscale := state.figure_config.get_arg("xscale"):
            ax.set_xscale(xscale)
        if yscale := state.figure_config.get_arg("yscale"):
            ax.set_yscale(yscale)
        fig.tight_layout()
        return MatplotlibFigure(fig)


class CorrelationPlotter(BasePlotter):
    r"""Implement a DataFrame column plotter.

    Args:
        state: The state containing the DataFrame to analyze.
            The DataFrame must have only 2 columns, which are the two
            columns to analyze.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from arkas.plotter import CorrelationPlotter
    >>> from arkas.state import DataFrameState
    >>> frame = pl.DataFrame(
    ...     {
    ...         "col1": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0],
    ...         "col3": [2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0],
    ...     },
    ... )
    >>> plotter = CorrelationPlotter(DataFrameState(frame))
    >>> plotter
    CorrelationPlotter(
      (state): DataFrameState(dataframe=(7, 2), nan_policy='propagate', figure_config=MatplotlibFigureConfig())
    )

    ```
    """

    registry = FigureCreatorRegistry[BaseFigureCreator](
        {MatplotlibFigureConfig.backend(): MatplotlibFigureCreator()}
    )

    def __init__(self, state: DataFrameState) -> None:
        check_num_columns(state.dataframe, num_columns=2)
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
        return {f"{prefix}correlation{suffix}": figure}
