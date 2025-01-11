r"""Implement a simple content output."""

from __future__ import annotations

__all__ = ["ContentOutput"]


from arkas.content.vanilla import ContentGenerator
from arkas.evaluator2.vanilla import Evaluator
from arkas.output.vanilla import Output
from arkas.plotter.vanilla import Plotter


class ContentOutput(Output):
    r"""Implement a simple content output.

    Args:
        content: The HTML content.

    Example usage:

    ```pycon

    >>> from arkas.output import ContentOutput
    >>> output = ContentOutput("meow")
    >>> output
    ContentOutput(
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

    def __init__(self, content: str) -> None:
        super().__init__(
            content=ContentGenerator(content), evaluator=Evaluator(), plotter=Plotter()
        )
