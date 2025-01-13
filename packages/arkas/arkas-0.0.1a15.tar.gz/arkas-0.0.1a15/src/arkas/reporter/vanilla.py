r"""Contain the implementation of a simple reporter that generates a
HTML file and save it."""

from __future__ import annotations

__all__ = ["Reporter"]

import logging
from typing import TYPE_CHECKING

from coola.utils import str_indent, str_mapping
from coola.utils.path import sanitize_path
from iden.io import save_text

from arkas.reporter.base import BaseReporter
from arkas.reporter.utils import create_html_report

if TYPE_CHECKING:
    from pathlib import Path

    from arkas.content import BaseContentGenerator

logger = logging.getLogger(__name__)


class Reporter(BaseReporter):
    r"""Implement a simple reporter that generates a HTML file and save
    it.

    Args:
        report_path: The path where to save the HTML report.
        max_toc_depth: The maximum level to show in the
            table of content.

    Example usage:

    ```pycon

    >>> import tempfile
    >>> from pathlib import Path
    >>> import numpy as np
    >>> from arkas.content import AccuracyContentGenerator
    >>> from arkas.state import AccuracyState
    >>> from arkas.reporter import Reporter
    >>> generator = AccuracyContentGenerator(
    ...     state=AccuracyState(
    ...         y_true=np.array([1, 0, 0, 1, 1]),
    ...         y_pred=np.array([1, 0, 0, 1, 1]),
    ...         y_true_name="target",
    ...         y_pred_name="pred",
    ...     )
    ... )
    >>> with tempfile.TemporaryDirectory() as tmpdir:
    ...     reporter = Reporter(
    ...         report_path=Path(tmpdir).joinpath("report.html"),
    ...     )
    ...     reporter.generate(generator)
    ...

    ```
    """

    def __init__(self, report_path: Path | str, max_toc_depth: int = 6) -> None:
        self._report_path = sanitize_path(report_path)
        self._max_toc_depth = int(max_toc_depth)

    def __repr__(self) -> str:
        args = str_indent(
            str_mapping(
                {
                    "report_path": self._report_path,
                    "max_toc_depth": self._max_toc_depth,
                }
            )
        )
        return f"{self.__class__.__qualname__}(\n  {args}\n)"

    def generate(self, generator: BaseContentGenerator) -> None:
        logger.info("Creating the HTML report with the results...")
        report = create_html_report(
            toc=generator.generate_body(),
            body=generator.generate_toc(max_depth=self._max_toc_depth),
        )
        logger.info(f"Saving the HTML report at {self._report_path}...")
        save_text(report, self._report_path, exist_ok=True)
