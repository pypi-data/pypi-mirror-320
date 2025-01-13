r"""Contain the implementation for plotly figures."""

from __future__ import annotations

__all__ = ["PlotlyFigure", "PlotlyFigureConfig"]

import copy
import sys
from typing import Any

from coola import objects_are_equal
from coola.utils.format import repr_mapping_line

from arkas.figure.base import BaseFigure, BaseFigureConfig
from arkas.utils.imports import check_plotly, is_plotly_available

if sys.version_info >= (3, 11):
    from typing import Self
else:  # pragma: no cover
    from typing_extensions import (
        Self,  # use backport because it was added in python 3.11
    )

if is_plotly_available():
    from plotly.graph_objects import Figure
else:  # pragma: no cover
    from unittest.mock import Mock

    Figure = Mock()


class PlotlyFigure(BaseFigure):
    r"""Implement the plotly figure.

    Args:
        figure: The plotly figure.
        reactive: If ``True``, the generated is configured to be
            reactive to the screen size.

    Example usage:

    ```pycon

    >>> from arkas.figure import PlotlyFigure
    >>> fig = PlotlyFigure(None)
    >>> fig
    PlotlyFigure(reactive=True)

    ```
    """

    def __init__(self, figure: Figure, reactive: bool = True) -> None:
        check_plotly()
        self._figure = figure
        self._reactive = reactive

    def __repr__(self) -> str:
        args = repr_mapping_line({"reactive": self._reactive})
        return f"{self.__class__.__qualname__}({args})"

    @property
    def figure(self) -> Figure:
        return self._figure

    def close(self) -> None:
        pass

    def equal(self, other: Any, equal_nan: bool = False) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return (
            objects_are_equal(self.figure, other.figure, equal_nan=equal_nan)
            and self._reactive == other._reactive
        )

    def set_reactive(self, reactive: bool) -> Self:
        return self.__class__(figure=self.figure, reactive=reactive)

    def to_html(self) -> str:
        data = ""
        style = 'style="width:100%; height:auto;" ' if self._reactive else ""
        return f'<img {style}src="data:image/png;charset=utf-8;base64, {data}">'


class PlotlyFigureConfig(BaseFigureConfig):
    r"""Implement the plotly figure config.

    Args:
        **kwargs: Additional keyword arguments to pass to plotly
            functions. The valid arguments depend on the context.

    Example usage:

    ```pycon

    >>> from arkas.figure import PlotlyFigureConfig
    >>> config = PlotlyFigureConfig()
    >>> config
    PlotlyFigureConfig()

    ```
    """

    def __init__(self, **kwargs: Any) -> None:
        check_plotly()
        self._kwargs = kwargs

    def __repr__(self) -> str:
        args = repr_mapping_line(self._kwargs)
        return f"{self.__class__.__qualname__}({args})"

    @classmethod
    def backend(cls) -> str:
        return "plotly"

    def clone(self) -> Self:
        return self.__class__(**self._kwargs)

    def equal(self, other: Any, equal_nan: bool = False) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return objects_are_equal(self._kwargs, other._kwargs, equal_nan=equal_nan)

    def get_arg(self, name: str, default: Any = None) -> Any:
        return copy.copy(self._kwargs.get(name, default))
