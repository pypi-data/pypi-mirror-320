r"""Contain the implementation of a plotter that plots the number of
null values for each column."""

from __future__ import annotations

__all__ = ["BaseFigureCreator", "MatplotlibFigureCreator", "NullValuePlotter"]

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

import matplotlib.pyplot as plt
from coola.utils import repr_indent, repr_mapping, str_indent, str_mapping

from arkas.figure.creator import FigureCreatorRegistry
from arkas.figure.html import HtmlFigure
from arkas.figure.matplotlib import MatplotlibFigure, MatplotlibFigureConfig
from arkas.figure.utils import MISSING_FIGURE_MESSAGE
from arkas.plot.utils import readable_xticklabels
from arkas.plotter.base import BasePlotter
from arkas.plotter.vanilla import Plotter

if TYPE_CHECKING:
    from arkas.figure.base import BaseFigure
    from arkas.state.null_value import NullValueState


class BaseFigureCreator(ABC):
    r"""Define the base class to create a bar plot figure with the
    number of null values for each column."""

    @abstractmethod
    def create(self, state: NullValueState) -> BaseFigure:
        r"""Create a bar plot figure with the number of null values for
        each column.

        Args:
            state: The state containing the number of null values per
                column.

        Returns:
            The generated figure.

        Example usage:

        ```pycon

        >>> import numpy as np
        >>> from arkas.figure import MatplotlibFigureConfig
        >>> from arkas.state import NullValueState
        >>> creator = MatplotlibFigureCreator()
        >>> fig = creator.create(
        ...     NullValueState(
        ...         null_count=np.array([0, 1, 2]),
        ...         total_count=np.array([5, 5, 5]),
        ...         columns=["col1", "col2", "col3"],
        ...     )
        ... )

        ```
        """


class MatplotlibFigureCreator(BaseFigureCreator):
    r"""Create a matplotlib figure with the number of null values for
    each column.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.figure import MatplotlibFigureConfig
    >>> from arkas.state import NullValueState
    >>> creator = MatplotlibFigureCreator()
    >>> fig = creator.create(
    ...     NullValueState(
    ...         null_count=np.array([0, 1, 2]),
    ...         total_count=np.array([5, 5, 5]),
    ...         columns=["col1", "col2", "col3"],
    ...     )
    ... )

    ```
    """

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}()"

    def create(self, state: NullValueState) -> BaseFigure:
        if state.null_count.shape[0] == 0:
            return HtmlFigure(MISSING_FIGURE_MESSAGE)

        fig, ax = plt.subplots(**state.figure_config.get_arg("init", {}))

        frame = state.to_dataframe().sort(by=["null", "column"])
        ax.bar(x=frame["column"].to_list(), height=frame["null"].to_numpy(), color="tab:blue")
        ax.set_xlim(-0.5, len(state.columns) - 0.5)
        readable_xticklabels(ax, max_num_xticks=100)
        ax.set_xlabel("column")
        ax.set_ylabel("number of null values")
        ax.set_title("number of null values per column")
        fig.tight_layout()
        return MatplotlibFigure(fig)


class NullValuePlotter(BasePlotter):
    r"""Implement a plotter that plots the number of null values for each
    column.

    Args:
        state: The state containing the number of null values per
            column.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.plotter import NullValuePlotter
    >>> from arkas.state import NullValueState
    >>> plotter = NullValuePlotter(
    ...     NullValueState(
    ...         null_count=np.array([0, 1, 2]),
    ...         total_count=np.array([5, 5, 5]),
    ...         columns=["col1", "col2", "col3"],
    ...     )
    ... )
    >>> plotter
    NullValuePlotter(
      (state): NullValueState(num_columns=3, figure_config=MatplotlibFigureConfig())
    )

    ```
    """

    registry = FigureCreatorRegistry[BaseFigureCreator](
        {MatplotlibFigureConfig.backend(): MatplotlibFigureCreator()}
    )

    def __init__(self, state: NullValueState) -> None:
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
        return {f"{prefix}null_values{suffix}": figure}
