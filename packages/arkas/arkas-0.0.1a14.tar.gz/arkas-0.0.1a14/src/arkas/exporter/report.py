r"""Contain the implementation of a report exporter."""

from __future__ import annotations

__all__ = ["ReportExporter"]

import logging
from typing import TYPE_CHECKING

from coola.utils import str_indent, str_mapping
from coola.utils.path import sanitize_path
from iden.io import BaseSaver, TextSaver, setup_saver

from arkas.exporter.base import BaseExporter
from arkas.reporter.utils import create_html_report

if TYPE_CHECKING:
    from pathlib import Path

    from arkas.output.base import BaseOutput

logger = logging.getLogger(__name__)


class ReportExporter(BaseExporter):
    r"""Implement a simple report exporter.

    Args:
        path: The path where to save the reports.
        saver: The report saver or its configuration.
        exist_ok: If ``exist_ok`` is ``False`` (the default),
            an exception is raised if the path already exists.
        max_toc_depth: The maximum level to show in the
            table of content.

    Example usage:

    ```pycon

    >>> import tempfile
    >>> from pathlib import Path
    >>> import numpy as np
    >>> from arkas.output import AccuracyOutput
    >>> from arkas.state import AccuracyState
    >>> from arkas.exporter import ReportExporter
    >>> output = AccuracyOutput(
    ...     state=AccuracyState(
    ...         y_true=np.array([1, 0, 0, 1, 1]),
    ...         y_pred=np.array([1, 0, 0, 1, 1]),
    ...         y_true_name="target",
    ...         y_pred_name="pred",
    ...     )
    ... )
    >>> with tempfile.TemporaryDirectory() as tmpdir:
    ...     exporter = ReportExporter(path=Path(tmpdir).joinpath("report.html"))
    ...     exporter.export(output)
    ...

    ```
    """

    def __init__(
        self,
        path: Path | str,
        saver: BaseSaver | dict | None = None,
        exist_ok: bool = False,
        max_toc_depth: int = 6,
    ) -> None:
        self._path = sanitize_path(path)
        self._saver = setup_saver(saver or TextSaver())
        self._exist_ok = exist_ok
        self._max_toc_depth = int(max_toc_depth)

    def __repr__(self) -> str:
        args = str_indent(
            str_mapping(
                {
                    "path": self._path,
                    "saver": self._saver,
                    "exist_ok": self._exist_ok,
                    "max_toc_depth": self._max_toc_depth,
                }
            )
        )
        return f"{self.__class__.__qualname__}(\n  {args}\n)"

    def export(self, output: BaseOutput) -> None:
        logger.info("Exporting reports...")
        logger.info("Creating the HTML report...")
        generator = output.get_content_generator()
        report = create_html_report(
            toc=generator.generate_toc(max_depth=self._max_toc_depth),
            body=generator.generate_body(),
        )
        logger.info(f"Saving the HTML report at {self._path}...")
        self._saver.save(report, self._path, exist_ok=self._exist_ok)
