r"""Contain utility functions to manage figures."""

from __future__ import annotations

__all__ = ["MISSING_FIGURE_MESSAGE", "figure2html", "get_default_config"]

from typing import TYPE_CHECKING

from arkas.figure.matplotlib import MatplotlibFigureConfig

if TYPE_CHECKING:
    from arkas.figure.base import BaseFigure, BaseFigureConfig

MISSING_FIGURE_MESSAGE = (
    "<span>&#9888;</span> No figure is generated because of missing or incorrect data"
)


def figure2html(figure: BaseFigure, reactive: bool = True, close_fig: bool = False) -> str:
    r"""Convert a figure to a HTML code.

    Args:
        figure: The figure to convert.
        reactive: If ``True``, the generated is configured to be
            reactive to the screen size.
        close_fig: If ``True``, the figure is closed after it is
            converted to HTML format.

    Returns:
        The HTML code of the input figure.

    Example usage:

    ```pycon

    >>> from matplotlib import pyplot as plt
    >>> from arkas.figure import figure2html, MatplotlibFigure
    >>> fig, _ = plt.subplots()
    >>> data = figure2html(MatplotlibFigure(fig))

    ```
    """
    data = figure.set_reactive(reactive).to_html()
    if close_fig:
        figure.close()
    return data


def get_default_config() -> BaseFigureConfig:
    r"""Get the default figure config.

    Returns:
        The default figure config.

    Example usage:

    ```pycon

    >>> from arkas.figure import get_default_config
    >>> config = get_default_config()
    >>> config
    MatplotlibFigureConfig()

    ```
    """
    return MatplotlibFigureConfig()
