r"""Contain the implementation of a section that analyze precision
results."""

from __future__ import annotations

__all__ = ["BinaryPrecisionSection", "create_section_template"]

import logging
from typing import TYPE_CHECKING, Any

from coola.utils import repr_indent, repr_mapping, str_indent, str_mapping
from jinja2 import Template

from arkas.section.base import BaseSection
from arkas.utils.html import GO_TO_TOP, render_toc, tags2id, tags2title, valid_h_tag

if TYPE_CHECKING:
    from collections.abc import Sequence

    from arkas.result import BaseResult


logger = logging.getLogger(__name__)


class BinaryPrecisionSection(BaseSection):
    r"""Implement a section that analyze precision results.

    Args:
        result: The data structure containing the results.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.section import BinaryPrecisionSection
    >>> from arkas.result import BinaryPrecisionResult
    >>> section = BinaryPrecisionSection(
    ...     result=BinaryPrecisionResult(
    ...         y_true=np.array([1, 0, 0, 1, 1]), y_pred=np.array([1, 0, 0, 1, 1])
    ...     )
    ... )
    >>> section
    BinaryPrecisionSection(
      (result): BinaryPrecisionResult(y_true=(5,), y_pred=(5,), nan_policy='propagate')
    )
    >>> section.generate_html_body()

    ```
    """

    def __init__(self, result: BaseResult) -> None:
        self._result = result

    def __repr__(self) -> str:
        args = repr_indent(repr_mapping({"result": self._result}))
        return f"{self.__class__.__qualname__}(\n  {args}\n)"

    def __str__(self) -> str:
        args = str_indent(str_mapping({"result": self._result}))
        return f"{self.__class__.__qualname__}(\n  {args}\n)"

    def equal(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._result.equal(other._result)

    def generate_html_body(self, number: str = "", tags: Sequence[str] = (), depth: int = 0) -> str:
        logger.info("Generating the binary precision section...")
        metrics = self._result.compute_metrics()
        return Template(create_section_template()).render(
            {
                "go_to_top": GO_TO_TOP,
                "id": tags2id(tags),
                "depth": valid_h_tag(depth + 1),
                "title": tags2title(tags),
                "section": number,
                "precision": f"{metrics.get('precision', float('nan')):.4f}",
                "count": f"{metrics.get('count', 0):,}",
            }
        )

    def generate_html_toc(
        self, number: str = "", tags: Sequence[str] = (), depth: int = 0, max_depth: int = 1
    ) -> str:
        return render_toc(number=number, tags=tags, depth=depth, max_depth=max_depth)


def create_section_template() -> str:
    r"""Return the template of the section.

    Returns:
        The section template.

    Example usage:

    ```pycon

    >>> from arkas.section.accuracy import create_section_template
    >>> template = create_section_template()

    ```
    """
    return """<h{{depth}} id="{{id}}">{{section}} {{title}} </h{{depth}}>

{{go_to_top}}

<p style="margin-top: 1rem;">

<ul>
  <li>precision: {{precision}}</li>
  <li>count: {{count}}</li>
</ul>

<p style="margin-top: 1rem;">
"""
