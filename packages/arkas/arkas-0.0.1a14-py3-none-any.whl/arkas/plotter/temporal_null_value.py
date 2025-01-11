r"""Contain the implementation of a DataFrame column plotter."""

from __future__ import annotations

__all__ = ["BaseFigureCreator", "MatplotlibFigureCreator", "TemporalNullValuePlotter"]

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

import matplotlib.pyplot as plt
from coola.utils import repr_indent, repr_mapping, str_indent, str_mapping
from grizz.utils.null import compute_temporal_null_count

from arkas.figure.creator import FigureCreatorRegistry
from arkas.figure.html import HtmlFigure
from arkas.figure.matplotlib import MatplotlibFigure, MatplotlibFigureConfig
from arkas.figure.utils import MISSING_FIGURE_MESSAGE
from arkas.plot import plot_null_temporal
from arkas.plot.utils import readable_xticklabels
from arkas.plotter.base import BasePlotter
from arkas.plotter.vanilla import Plotter

if TYPE_CHECKING:
    from arkas.figure.base import BaseFigure
    from arkas.state.temporal_dataframe import TemporalDataFrameState


class BaseFigureCreator(ABC):
    r"""Define the base class to create a figure with the content of
    each column."""

    @abstractmethod
    def create(self, state: TemporalDataFrameState) -> BaseFigure:
        r"""Create a figure with the content of each column.

        Args:
        state: The state containing the DataFrame to analyze.

        Returns:
            The generated figure.

        Example usage:

        ```pycon

        >>> from datetime import datetime, timezone
        >>> import polars as pl
        >>> from arkas.plotter.temporal_null_value import MatplotlibFigureCreator
        >>> from arkas.state import TemporalDataFrameState
        >>> creator = MatplotlibFigureCreator()
        >>> frame = pl.DataFrame(
        ...     {
        ...         "col1": [0, 1, 1, 0],
        ...         "col2": [0, 1, 0, 1],
        ...         "col3": [1, 0, 0, 0],
        ...         "datetime": [
        ...             datetime(year=2020, month=1, day=3, tzinfo=timezone.utc),
        ...             datetime(year=2020, month=2, day=3, tzinfo=timezone.utc),
        ...             datetime(year=2020, month=3, day=3, tzinfo=timezone.utc),
        ...             datetime(year=2020, month=4, day=3, tzinfo=timezone.utc),
        ...         ],
        ...     },
        ...     schema={
        ...         "col1": pl.Int64,
        ...         "col2": pl.Int64,
        ...         "col3": pl.Int64,
        ...         "datetime": pl.Datetime(time_unit="us", time_zone="UTC"),
        ...     },
        ... )
        >>> fig = creator.create(
        ...     TemporalDataFrameState(frame, temporal_column="datetime", period="1d")
        ... )

        ```
        """


class MatplotlibFigureCreator(BaseFigureCreator):
    r"""Create a matplotlib figure with the content of each column.

    Example usage:

    ```pycon

    >>> from datetime import datetime, timezone
    >>> import polars as pl
    >>> from arkas.plotter.temporal_null_value import MatplotlibFigureCreator
    >>> from arkas.state import TemporalDataFrameState
    >>> creator = MatplotlibFigureCreator()
    >>> frame = pl.DataFrame(
    ...     {
    ...         "col1": [0, 1, 1, 0],
    ...         "col2": [0, 1, 0, 1],
    ...         "col3": [1, 0, 0, 0],
    ...         "datetime": [
    ...             datetime(year=2020, month=1, day=3, tzinfo=timezone.utc),
    ...             datetime(year=2020, month=2, day=3, tzinfo=timezone.utc),
    ...             datetime(year=2020, month=3, day=3, tzinfo=timezone.utc),
    ...             datetime(year=2020, month=4, day=3, tzinfo=timezone.utc),
    ...         ],
    ...     },
    ...     schema={
    ...         "col1": pl.Int64,
    ...         "col2": pl.Int64,
    ...         "col3": pl.Int64,
    ...         "datetime": pl.Datetime(time_unit="us", time_zone="UTC"),
    ...     },
    ... )
    >>> fig = creator.create(
    ...     TemporalDataFrameState(frame, temporal_column="datetime", period="1d")
    ... )

    ```
    """

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}()"

    def create(self, state: TemporalDataFrameState) -> BaseFigure:
        if state.dataframe.shape[0] == 0:
            return HtmlFigure(MISSING_FIGURE_MESSAGE)

        fig, ax = plt.subplots(**state.figure_config.get_arg("init", {}))
        columns = list(state.dataframe.columns)
        columns.remove(state.temporal_column)
        nulls, totals, labels = compute_temporal_null_count(
            frame=state.dataframe,
            columns=columns,
            temporal_column=state.temporal_column,
            period=state.period,
        )
        plot_null_temporal(ax=ax, labels=labels, nulls=nulls, totals=totals)
        readable_xticklabels(ax, max_num_xticks=100)

        fig.tight_layout()
        return MatplotlibFigure(fig)


class TemporalNullValuePlotter(BasePlotter):
    r"""Implement a DataFrame column plotter.

    Args:
        state: The state containing the DataFrame to analyze.

    Example usage:

    ```pycon

    >>> from datetime import datetime, timezone
    >>> import polars as pl
    >>> from arkas.plotter import TemporalNullValuePlotter
    >>> from arkas.state import TemporalDataFrameState
    >>> frame = pl.DataFrame(
    ...     {
    ...         "col1": [0, 1, 1, 0],
    ...         "col2": [0, 1, 0, 1],
    ...         "col3": [1, 0, 0, 0],
    ...         "datetime": [
    ...             datetime(year=2020, month=1, day=3, tzinfo=timezone.utc),
    ...             datetime(year=2020, month=2, day=3, tzinfo=timezone.utc),
    ...             datetime(year=2020, month=3, day=3, tzinfo=timezone.utc),
    ...             datetime(year=2020, month=4, day=3, tzinfo=timezone.utc),
    ...         ],
    ...     },
    ...     schema={
    ...         "col1": pl.Int64,
    ...         "col2": pl.Int64,
    ...         "col3": pl.Int64,
    ...         "datetime": pl.Datetime(time_unit="us", time_zone="UTC"),
    ...     },
    ... )
    >>> plotter = TemporalNullValuePlotter(
    ...     TemporalDataFrameState(frame, temporal_column="datetime", period="1d")
    ... )
    >>> plotter
    TemporalNullValuePlotter(
      (state): TemporalDataFrameState(dataframe=(4, 4), temporal_column='datetime', period='1d', nan_policy='propagate', figure_config=MatplotlibFigureConfig())
    )

    ```
    """

    registry = FigureCreatorRegistry[BaseFigureCreator](
        {MatplotlibFigureConfig.backend(): MatplotlibFigureCreator()}
    )

    def __init__(self, state: TemporalDataFrameState) -> None:
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
        return {f"{prefix}temporal_null_value{suffix}": figure}
