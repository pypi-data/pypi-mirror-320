r"""Implement a simple output."""

from __future__ import annotations

__all__ = ["Output"]

from typing import TYPE_CHECKING, Any

from coola.utils import repr_indent, repr_mapping

from arkas.output.lazy import BaseLazyOutput

if TYPE_CHECKING:
    from arkas.content.base import BaseContentGenerator
    from arkas.evaluator2.base import BaseEvaluator
    from arkas.plotter.base import BasePlotter


class Output(BaseLazyOutput):
    r"""Implement a simple output.

    Args:
        content: The HTML content generator.
        evaluator: The evaluator.
        plotter: The plotter.

    Example usage:

    ```pycon

    >>> from arkas.output import Output
    >>> from arkas.content import ContentGenerator
    >>> from arkas.evaluator2 import Evaluator
    >>> from arkas.plotter import Plotter
    >>> output = Output(
    ...     content=ContentGenerator("meow"), evaluator=Evaluator(), plotter=Plotter()
    ... )
    >>> output
    Output(
      (content): ContentGenerator()
      (evaluator): Evaluator(count=0)
      (plotter): Plotter(count=0)
    )
    >>> output.get_content_generator()
    ContentGenerator()
    >>> output.get_evaluator()
    Evaluator(count=0)
    >>> output.get_plotter()
    Plotter(count=0)

    ```
    """

    def __init__(
        self,
        content: BaseContentGenerator,
        evaluator: BaseEvaluator,
        plotter: BasePlotter,
    ) -> None:
        self._content = content
        self._evaluator = evaluator
        self._plotter = plotter

    def __repr__(self) -> str:
        args = repr_indent(
            repr_mapping(
                {
                    "content": self._content,
                    "evaluator": self._evaluator,
                    "plotter": self._plotter,
                }
            )
        )
        return f"{self.__class__.__qualname__}(\n  {args}\n)"

    def equal(self, other: Any, equal_nan: bool = False) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return (
            self._content.equal(other._content, equal_nan=equal_nan)
            and self._evaluator.equal(other._evaluator, equal_nan=equal_nan)
            and self._plotter.equal(other._plotter, equal_nan=equal_nan)
        )

    def _get_content_generator(self) -> BaseContentGenerator:
        return self._content

    def _get_evaluator(self) -> BaseEvaluator:
        return self._evaluator

    def _get_plotter(self) -> BasePlotter:
        return self._plotter
