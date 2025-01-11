"""Contain the base class to implement a figure."""

from __future__ import annotations

__all__ = ["BaseFigure", "BaseFigureConfig"]

import sys
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from coola.equality.comparators import BaseEqualityComparator
from coola.equality.handlers import EqualNanHandler, SameObjectHandler, SameTypeHandler
from coola.equality.testers import EqualityTester

if TYPE_CHECKING:
    from coola.equality import EqualityConfig

if sys.version_info >= (3, 11):
    from typing import Self
else:  # pragma: no cover
    from typing_extensions import (
        Self,  # use backport because it was added in python 3.11
    )


class BaseFigure(ABC):
    r"""Define the base class to implement a figure.

    Example usage:

    ```pycon

    >>> from matplotlib import pyplot as plt
    >>> from arkas.figure import MatplotlibFigure
    >>> fig = MatplotlibFigure(plt.subplots()[0])
    >>> fig
    MatplotlibFigure(reactive=True)

    ```
    """

    @abstractmethod
    def close(self) -> None:
        r"""Close the figure.

        Example usage:

        ```pycon

        >>> from matplotlib import pyplot as plt
        >>> from arkas.figure import MatplotlibFigure
        >>> fig = MatplotlibFigure(plt.subplots()[0])
        >>> fig.close()

        ```
        """

    @abstractmethod
    def equal(self, other: Any, equal_nan: bool = False) -> bool:
        r"""Indicate if two figures are equal or not.

        Args:
            other: The other object to compare with.
            equal_nan: Whether to compare NaN's as equal. If ``True``,
                NaN's in both objects will be considered equal.

        Returns:
            ``True`` if the two objects are equal, otherwise ``False``.

        Example usage:

        ```pycon

        >>> from matplotlib import pyplot as plt
        >>> from arkas.figure import MatplotlibFigure
        >>> fig = plt.subplots()[0]
        >>> fig1 = MatplotlibFigure(fig)
        >>> fig2 = MatplotlibFigure(fig)
        >>> fig3 = MatplotlibFigure(fig, reactive=False)
        >>> fig1.equal(fig2)
        True
        >>> fig1.equal(fig3)
        False

        ```
        """

    @abstractmethod
    def set_reactive(self, reactive: bool) -> Self:
        r"""Set the figure reactive mode.

        Args:
            reactive: The reactive mode.

        Returns:
            A new figure object with the right reactive mode.

        Example usage:

        ```pycon

        >>> from matplotlib import pyplot as plt
        >>> from arkas.figure import MatplotlibFigure
        >>> fig = MatplotlibFigure(plt.subplots()[0])
        >>> fig
        MatplotlibFigure(reactive=True)
        >>> fig2 = fig.set_reactive(False)
        >>> fig2
        MatplotlibFigure(reactive=False)

        ```
        """

    @abstractmethod
    def to_html(self) -> str:
        r"""Export the figure to a HTML code.

        Returns:
            The HTML code of the figure.

        Example usage:

        ```pycon

        >>> from matplotlib import pyplot as plt
        >>> from arkas.figure import MatplotlibFigure
        >>> fig = MatplotlibFigure(plt.subplots()[0])
        >>> html = fig.to_html()

        ```
        """


class BaseFigureConfig(ABC):
    r"""Define the base class to implement a figure config.

    Example usage:

    ```pycon

    >>> from arkas.figure import MatplotlibFigureConfig
    >>> config = MatplotlibFigureConfig()
    >>> config
    MatplotlibFigureConfig()

    ```
    """

    @classmethod
    @abstractmethod
    def backend(cls) -> str:
        r"""Return the backend to generate the figure.

        Example usage:

        ```pycon

        >>> from arkas.figure import MatplotlibFigureConfig
        >>> backend = MatplotlibFigureConfig.backend()
        >>> backend
        matplotlib

        ```
        """

    @abstractmethod
    def clone(self) -> Self:
        r"""Return a copy of the config.

        Returns:
            A copy of the config.

        Example usage:

        ```pycon

        >>> from arkas.figure import MatplotlibFigureConfig
        >>> config = MatplotlibFigureConfig()
        >>> cloned_config = config.clone()

        ```
        """

    @abstractmethod
    def equal(self, other: Any, equal_nan: bool = False) -> bool:
        r"""Indicate if two configs are equal or not.

        Args:
            other: The other object to compare with.
            equal_nan: Whether to compare NaN's as equal. If ``True``,
                NaN's in both objects will be considered equal.

        Returns:
            ``True`` if the two objects are equal, otherwise ``False``.

        Example usage:

        ```pycon

        >>> from arkas.figure import MatplotlibFigureConfig
        >>> config1 = MatplotlibFigureConfig(dpi=300)
        >>> config2 = MatplotlibFigureConfig(dpi=300)
        >>> config3 = MatplotlibFigureConfig()
        >>> config1.equal(config2)
        True
        >>> config1.equal(config3)
        False

        ```
        """

    @abstractmethod
    def get_arg(self, name: str, default: Any = None) -> Any:
        r"""Get a given argument from the config.

        Args:
            name: The argument name to get.
            default: The default value to return if the argument is missing.

        Returns:
            The argument value or the default value.

        Example usage:

        ```pycon

        >>> from arkas.figure import MatplotlibFigureConfig
        >>> config = MatplotlibFigureConfig(dpi=42)
        >>> config.get_arg("dpi")
        42

        ```
        """


class FigureEqualityComparator(BaseEqualityComparator[BaseFigure]):
    r"""Implement an equality comparator for ``BaseFigure`` and
    ``BaseFigureConfig`` objects."""

    def __init__(self) -> None:
        self._handler = SameObjectHandler()
        self._handler.chain(SameTypeHandler()).chain(EqualNanHandler())

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__)

    def clone(self) -> FigureEqualityComparator:
        return self.__class__()

    def equal(
        self, actual: BaseFigure | BaseFigureConfig, expected: Any, config: EqualityConfig
    ) -> bool:
        return self._handler.handle(actual, expected, config=config)


if not EqualityTester.has_comparator(BaseFigure):  # pragma: no cover
    EqualityTester.add_comparator(BaseFigure, FigureEqualityComparator())
    EqualityTester.add_comparator(BaseFigureConfig, FigureEqualityComparator())
