r"""Contain an plotter that generates figures from a mapping of
plotters."""

from __future__ import annotations

__all__ = ["PlotterDict"]

import logging
from typing import TYPE_CHECKING, Any

from coola import objects_are_equal
from coola.utils import repr_indent, repr_mapping

from arkas.plotter.base import BasePlotter
from arkas.plotter.vanilla import Plotter

if TYPE_CHECKING:
    from collections.abc import Hashable, Mapping

logger = logging.getLogger(__name__)


class PlotterDict(BasePlotter):
    r"""Implement a plotter that generates figures from a mapping of
    plotters.

    Args:
        plotters: The mapping of plotters.

    Example usage:

    ```pycon

    >>> from arkas.plotter import PlotterDict, Plotter
    >>> plotter = PlotterDict(
    ...     {
    ...         "one": Plotter(),
    ...         "two": Plotter({"fig": None}),
    ...     }
    ... )
    >>> plotter
    PlotterDict(
      (one): Plotter(count=0)
      (two): Plotter(count=1)
    )
    >>> figures = plotter.plot()
    >>> figures
    {'one': {}, 'two': {'fig': None}}

    ```
    """

    def __init__(self, plotters: Mapping[Hashable, BasePlotter]) -> None:
        self._plotters = plotters

    def __repr__(self) -> str:
        args = repr_indent(repr_mapping(self._plotters))
        return f"{self.__class__.__qualname__}(\n  {args}\n)"

    def compute(self) -> Plotter:
        return Plotter(figures=self.plot())

    def equal(self, other: Any, equal_nan: bool = False) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return objects_are_equal(self._plotters, other._plotters, equal_nan=equal_nan)

    def plot(self, prefix: str = "", suffix: str = "") -> dict:
        return {
            key: plotter.plot(prefix=prefix, suffix=suffix)
            for key, plotter in self._plotters.items()
        }
