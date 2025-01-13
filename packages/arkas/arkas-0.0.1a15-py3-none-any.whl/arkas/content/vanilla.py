r"""Contain the implementation of a simple HTML content generator."""

from __future__ import annotations

__all__ = ["ContentGenerator"]

import logging
from typing import Any

from arkas.content.section import BaseSectionContentGenerator

logger = logging.getLogger(__name__)


class ContentGenerator(BaseSectionContentGenerator):
    r"""Implement a section that analyze accuracy states.

    Args:
        content: The HTML content.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.content import ContentGenerator
    >>> generator = ContentGenerator("meow")
    >>> generator
    ContentGenerator()
    >>> generator.generate_content()
    'meow'

    ```
    """

    def __init__(self, content: str = "") -> None:
        self._content = str(content)

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}()"

    def __str__(self) -> str:
        return f"{self.__class__.__qualname__}()"

    def equal(self, other: Any, equal_nan: bool = False) -> bool:  # noqa: ARG002
        if not isinstance(other, self.__class__):
            return False
        return self._content == other._content

    def generate_content(self) -> str:
        return self._content
