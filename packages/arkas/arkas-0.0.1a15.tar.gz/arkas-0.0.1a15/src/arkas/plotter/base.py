r"""Contain the base class to implement a plotter."""

from __future__ import annotations

__all__ = ["BasePlotter"]

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from coola.equality.comparators import BaseEqualityComparator
from coola.equality.handlers import EqualNanHandler, SameObjectHandler, SameTypeHandler
from coola.equality.testers import EqualityTester

if TYPE_CHECKING:
    from coola.equality import EqualityConfig


class BasePlotter(ABC):
    r"""Define the base class to implement a plotter.

    Example usage:

    ```pycon

    >>> from arkas.plotter import Plotter
    >>> plotter = Plotter()
    >>> plotter
    Plotter(count=0)

    ```
    """

    @abstractmethod
    def compute(self) -> BasePlotter:
        r"""Compute the figures and return a new plotter.

        Returns:
            A new plotter with the computed figures.

        Example usage:

        ```pycon

        >>> from arkas.plotter import Plotter
        >>> plotter = Plotter({"fig": None})
        >>> plotter
        Plotter(count=1)
        >>> plotter2 = plotter.compute()
        >>> plotter2
        Plotter(count=1)

        ```
        """

    @abstractmethod
    def equal(self, other: Any, equal_nan: bool = False) -> bool:
        r"""Indicate if two plotters are equal or not.

        Args:
            other: The other plotter to compare.
            equal_nan: Whether to compare NaN's as equal. If ``True``,
                NaN's in both objects will be considered equal.

        Returns:
            ``True`` if the two plotters are equal, otherwise ``False``.

        Example usage:

        ```pycon

        >>> from arkas.plotter import Plotter
        >>> plotter1 = Plotter()
        >>> plotter2 = Plotter()
        >>> plotter3 = Plotter({"fig": None})
        >>> plotter1.equal(plotter2)
        True
        >>> plotter1.equal(plotter3)
        False

        ```
        """

    @abstractmethod
    def plot(self, prefix: str = "", suffix: str = "") -> dict:
        r"""Generate the figures.

        Args:
            prefix: The key prefix in the returned dictionary.
            suffix: The key suffix in the returned dictionary.

        Returns:
            A dictionary with the generated figures.

        Example usage:

        ```pycon

        >>> from arkas.plotter import Plotter
        >>> plotter = Plotter()
        >>> plotter.plot()
        {}

        ```
        """


class PlotterEqualityComparator(BaseEqualityComparator[BasePlotter]):
    r"""Implement an equality comparator for ``BasePlotter`` objects."""

    def __init__(self) -> None:
        self._handler = SameObjectHandler()
        self._handler.chain(SameTypeHandler()).chain(EqualNanHandler())

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__)

    def clone(self) -> PlotterEqualityComparator:
        return self.__class__()

    def equal(self, actual: BasePlotter, expected: Any, config: EqualityConfig) -> bool:
        return self._handler.handle(actual, expected, config=config)


if not EqualityTester.has_comparator(BasePlotter):  # pragma: no cover
    EqualityTester.add_comparator(BasePlotter, PlotterEqualityComparator())
