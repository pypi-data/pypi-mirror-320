r"""Contain the implementation of a section that shows the results in a
HTML format."""

from __future__ import annotations

__all__ = ["ResultSection", "create_section_template"]

import logging
from typing import TYPE_CHECKING, Any

from coola.nested import to_flat_dict
from coola.utils import repr_indent, repr_mapping, str_indent, str_mapping
from jinja2 import Template

from arkas.section.base import BaseSection
from arkas.utils.figure import figure2html
from arkas.utils.html import GO_TO_TOP, render_toc, tags2id, tags2title, valid_h_tag

if TYPE_CHECKING:
    from collections.abc import Sequence

    from arkas.result import BaseResult


logger = logging.getLogger(__name__)


class ResultSection(BaseSection):
    r"""Implement a section that show the results in a HTML format.

    Args:
        result: The data structure containing the results.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.section import ResultSection
    >>> from arkas.result import AccuracyResult
    >>> section = ResultSection(
    ...     result=AccuracyResult(
    ...         y_true=np.array([1, 0, 0, 1, 1]), y_pred=np.array([1, 0, 0, 1, 1])
    ...     )
    ... )
    >>> section
    ResultSection(
      (result): AccuracyResult(y_true=(5,), y_pred=(5,), nan_policy='propagate')
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
        logger.info("Generating the accuracy section...")
        metrics = self._result.compute_metrics()
        figures = self._result.generate_figures()
        return Template(create_section_template()).render(
            {
                "go_to_top": GO_TO_TOP,
                "id": tags2id(tags),
                "depth": valid_h_tag(depth + 1),
                "title": tags2title(tags),
                "section": number,
                "metrics": create_table_metrics(metrics),
                "figures": create_figures(figures),
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

{{metrics}}

{{figures}}

<p style="margin-top: 1rem;">
"""


def create_table_metrics(metrics: dict) -> str:
    r"""Return the HTML code of a table with the metrics.

    Args:
        metrics: The metrics.

    Returns:
        The HTML code of the table.

    Example usage:

    ```pycon

    >>> from arkas.section.result import create_table_metrics
    >>> row = create_table_metrics({"accuracy": 0.42, "f1": 0.57})

    ```
    """
    metrics = to_flat_dict(metrics)
    rows = [create_table_metrics_row(name=name, value=value) for name, value in metrics.items()]
    return Template(
        """<table class="table table-hover table-responsive w-auto" >
    <thead class="thead table-group-divider">
        <tr>
            <th>name</th>
            <th>value</th>
        </tr>
    </thead>
    <tbody class="tbody table-group-divider">
        {{rows}}
        <tr class="table-group-divider"></tr>
    </tbody>
</table>
"""
    ).render({"rows": "\n".join(rows)})


def create_table_metrics_row(name: str, value: Any) -> str:
    r"""Return the HTML code of a table row.

    Args:
        name: The metric name.
        value: The metric value.

    Returns:
        The HTML code of a row.

    Example usage:

    ```pycon

    >>> from arkas.section.result import create_table_metrics_row
    >>> row = create_table_metrics_row(name="accuracy", value=42.0)

    ```
    """
    return f'<tr><th>{name}</th><td style="text-align: right;">{value}</td></tr>'


def create_figures(figures: dict) -> str:
    r"""Return the HTML code of the figures.

    Args:
        figures: The figures.

    Returns:
        The HTML code of the figures.

    Example usage:

    ```pycon

    >>> from arkas.section.result import create_figures
    >>> from matplotlib import pyplot as plt
    >>> fig, _ = plt.subplots()
    >>> out = create_figures({"pr": fig})

    ```
    """
    figures = to_flat_dict(figures)
    rows = "\n".join(
        [
            f"<li>{name}</li>\n{figure2html(value, reactive=False, close_fig=True)}"
            for name, value in figures.items()
        ]
    )
    return f"<ul>\n{rows}\n</ul>"
