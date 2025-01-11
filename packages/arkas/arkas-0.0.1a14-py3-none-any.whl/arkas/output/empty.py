r"""Implement an empty output."""

from __future__ import annotations

__all__ = ["EmptyOutput"]


from arkas.content.vanilla import ContentGenerator
from arkas.evaluator2.vanilla import Evaluator
from arkas.output.vanilla import Output
from arkas.plotter.vanilla import Plotter


class EmptyOutput(Output):
    r"""Implement the accuracy output.

    Example usage:

    ```pycon

    >>> from arkas.output import EmptyOutput
    >>> output = EmptyOutput()
    >>> output
    EmptyOutput()
    >>> output.get_evaluator()
    Evaluator(count=0)
    >>> output.get_plotter()
    Plotter(count=0)

    ```
    """

    def __init__(self) -> None:
        super().__init__(content=ContentGenerator(), evaluator=Evaluator(), plotter=Plotter())

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}()"
