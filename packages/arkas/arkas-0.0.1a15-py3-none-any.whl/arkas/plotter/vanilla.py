r"""Contain the implementation of a simple plotter."""

from __future__ import annotations

__all__ = ["Plotter"]

from typing import Any

from coola import objects_are_equal

from arkas.plotter.base import BasePlotter


class Plotter(BasePlotter):
    r"""Implement a simple plotter.

    Args:
        figures: The dictionary of figures.

    Example usage:

    ```pycon

    >>> from arkas.plotter import Plotter
    >>> plotter = Plotter()
    >>> plotter
    Plotter(count=0)
    >>> plotter.plot()
    {}

    ```
    """

    def __init__(self, figures: dict | None = None) -> None:
        self._figures = figures or {}

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(count={len(self._figures):,})"

    def compute(self) -> Plotter:
        return Plotter(self._figures)

    def equal(self, other: Any, equal_nan: bool = False) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return objects_are_equal(self._figures, other._figures, equal_nan=equal_nan)

    def plot(self, prefix: str = "", suffix: str = "") -> dict:
        return {f"{prefix}{key}{suffix}": value for key, value in self._figures.items()}
