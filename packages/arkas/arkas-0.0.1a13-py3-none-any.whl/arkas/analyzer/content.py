r"""Contain an analyzer that generates an output with the given custom
content."""

from __future__ import annotations

__all__ = ["ContentAnalyzer"]

import logging
from typing import TYPE_CHECKING

from arkas.analyzer.lazy import BaseLazyAnalyzer
from arkas.output.content import ContentOutput

if TYPE_CHECKING:
    import polars as pl


logger = logging.getLogger(__name__)


class ContentAnalyzer(BaseLazyAnalyzer):
    r"""Implement an analyzer that generates an output with the given
    custom content.

    Args:
        content: The content to use in the HTML code.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from arkas.analyzer import ContentAnalyzer
    >>> analyzer = ContentAnalyzer(content="meow")
    >>> analyzer
    ContentAnalyzer()
    >>> frame = pl.DataFrame({"pred": [3, 2, 0, 1, 0, 1], "target": [3, 2, 0, 1, 0, 1]})
    >>> output = analyzer.analyze(frame)
    >>> output
    ContentOutput(
      (content): ContentGenerator()
      (evaluator): Evaluator(count=0)
      (plotter): Plotter(count=0)
    )

    ```
    """

    def __init__(self, content: str) -> None:
        self._content = content

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}()"

    def _analyze(self, frame: pl.DataFrame) -> ContentOutput:  # noqa: ARG002
        return ContentOutput(self._content)
