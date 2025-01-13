r"""Contain a content generator that combines a mapping of content
generators."""

from __future__ import annotations

__all__ = ["ContentGeneratorDict"]

import logging
from typing import TYPE_CHECKING, Any

from coola import objects_are_equal
from coola.utils import repr_indent, repr_mapping, str_indent

from arkas.content.base import BaseContentGenerator
from arkas.utils.html import GO_TO_TOP, render_toc, tags2id, tags2title, valid_h_tag

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

logger = logging.getLogger(__name__)


class ContentGeneratorDict(BaseContentGenerator):
    r"""Implement a content generator that combines a mapping of content
    generators.

    Args:
        generators: The mapping of content generators.

    Example usage:

    ```pycon

    >>> from arkas.content import ContentGeneratorDict, ContentGenerator
    >>> content = ContentGeneratorDict(
    ...     {
    ...         "one": ContentGenerator(),
    ...         "two": ContentGenerator("meow"),
    ...     }
    ... )
    >>> content
    ContentGeneratorDict(
      (one): ContentGenerator()
      (two): ContentGenerator()
    )

    ```
    """

    def __init__(
        self, generators: Mapping[str, BaseContentGenerator], max_toc_depth: int = 0
    ) -> None:
        self._generators = generators
        self._max_toc_depth = max_toc_depth

    def __repr__(self) -> str:
        args = repr_indent(repr_mapping(self._generators))
        return f"{self.__class__.__qualname__}(\n  {args}\n)"

    def compute(self) -> ContentGeneratorDict:
        return ContentGeneratorDict(
            generators={key: generator.compute() for key, generator in self._generators.items()},
            max_toc_depth=self._max_toc_depth,
        )

    def equal(self, other: Any, equal_nan: bool = False) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return objects_are_equal(self._generators, other._generators, equal_nan=equal_nan)

    def generate_body(self, number: str = "", tags: Sequence[str] = (), depth: int = 0) -> str:
        report = []
        if tags:
            report.extend(
                [
                    f'<h{valid_h_tag(depth + 1)} id="{tags2id(tags)}">{number} '
                    f"{tags2title(tags)} </h{valid_h_tag(depth + 1)}>",
                    GO_TO_TOP,
                    '<p style="margin-top: 1rem;">',
                ]
            )

        if self._max_toc_depth > 0:
            report.append(
                self._generate_toc_content(
                    number=number, tags=tags, depth=0, max_depth=self._max_toc_depth
                )
            )

        for i, (name, generator) in enumerate(self._generators.items()):
            report.append(
                generator.generate_body(
                    number=f"{number}{i + 1}.", tags=[*list(tags), name], depth=depth + 1
                )
            )
        return "\n".join(report)

    def generate_toc(
        self, number: str = "", tags: Sequence[str] = (), depth: int = 0, max_depth: int = 1
    ) -> str:
        if depth >= max_depth:
            return ""
        toc = []
        if tags:
            toc.append(render_toc(number=number, tags=tags, depth=depth, max_depth=max_depth))
        subtoc = self._generate_toc_content(tags=tags, depth=depth + 1, max_depth=max_depth)
        if subtoc:
            toc.append(subtoc)
        return "\n".join(toc)

    def _generate_toc_content(
        self, number: str = "", tags: Sequence[str] = (), depth: int = 0, max_depth: int = 1
    ) -> str:
        subtoc = []
        for i, (name, generator) in enumerate(self._generators.items()):
            line = generator.generate_toc(
                number=f"{number}{i + 1}.",
                tags=[*list(tags), name],
                depth=depth,
                max_depth=max_depth,
            )
            if line:
                subtoc.append(f"  {str_indent(line)}")
        if subtoc:
            subtoc.insert(0, "<ul>")
            subtoc.append("</ul>")
        return "\n".join(subtoc)
