r"""Contain an exporter that sequentially calls several exporters."""

from __future__ import annotations

__all__ = ["SequentialExporter"]

import logging
from typing import TYPE_CHECKING

from coola.utils import repr_indent, repr_sequence

from arkas.exporter import BaseExporter, setup_exporter

if TYPE_CHECKING:
    from collections.abc import Sequence

    from arkas.output import BaseOutput


logger = logging.getLogger(__name__)


class SequentialExporter(BaseExporter):
    r"""Implement an exporter that sequentially calls several exporters.

    Args:
        exporters: The sequence of exporters.

    Example usage:

    ```pycon


    >>> import tempfile
    >>> from pathlib import Path
    >>> import numpy as np
    >>> from arkas.output import AccuracyOutput
    >>> from arkas.state import AccuracyState
    >>> from arkas.exporter import (
    ...     SequentialExporter,
    ...     FigureExporter,
    ...     MetricExporter,
    ... )
    >>> output = AccuracyOutput(
    ...     state=AccuracyState(
    ...         y_true=np.array([1, 0, 0, 1, 1]),
    ...         y_pred=np.array([1, 0, 0, 1, 1]),
    ...         y_true_name="target",
    ...         y_pred_name="pred",
    ...     )
    ... )
    >>> with tempfile.TemporaryDirectory() as tmpdir:
    ...     path = Path(tmpdir)
    ...     exporter = SequentialExporter(
    ...         [
    ...             MetricExporter(path.joinpath("metrics.pkl")),
    ...             FigureExporter(path.joinpath("figures.pkl")),
    ...         ]
    ...     )
    ...     print(exporter)
    ...     exporter.export(output)
    ...
    SequentialExporter(
      (0): MetricExporter(
          (path): .../metrics.pkl
          (saver): PickleSaver(protocol=5)
          (exist_ok): False
          (show_metrics): False
        )
      (1): FigureExporter(
          (path): .../figures.pkl
          (saver): PickleSaver(protocol=5)
          (exist_ok): False
        )
    )

    ```
    """

    def __init__(self, exporters: Sequence[BaseExporter | dict]) -> None:
        self._exporters = tuple(setup_exporter(exporter) for exporter in exporters)

    def __repr__(self) -> str:
        args = repr_indent(repr_sequence(self._exporters))
        return f"{self.__class__.__qualname__}(\n  {args}\n)"

    def export(self, output: BaseOutput) -> None:
        for exporter in self._exporters:
            exporter.export(output)
