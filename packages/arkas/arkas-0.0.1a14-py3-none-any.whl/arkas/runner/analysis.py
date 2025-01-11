r"""Contain a simple runner to analyze data."""

from __future__ import annotations

__all__ = ["AnalysisRunner"]

import logging

from coola.utils import str_indent, str_mapping
from grizz.ingestor import BaseIngestor, setup_ingestor
from grizz.transformer import BaseTransformer, setup_transformer
from iden.utils.time import timeblock

from arkas.analyzer.base import BaseAnalyzer, setup_analyzer
from arkas.exporter import BaseExporter, setup_exporter
from arkas.runner.base import BaseRunner

logger = logging.getLogger(__name__)


class AnalysisRunner(BaseRunner):
    r"""Implement a runner to analyze data.

    Args:
        ingestor: The data ingestor or its configuration.
        transformer: The data transformer or its configuration.
        analyzer: The analyzer or its configuration.
        exporter: The output exporter or its configuration.
        lazy: If ``True``, the analyzer computation is done lazily.

    Example usage:

    ```pycon

    >>> import tempfile
    >>> import polars as pl
    >>> from pathlib import Path
    >>> from grizz.ingestor import Ingestor
    >>> from grizz.transformer import SequentialTransformer
    >>> from arkas.analyzer import AccuracyAnalyzer
    >>> from arkas.exporter import MetricExporter
    >>> from arkas.runner import AnalysisRunner
    >>> with tempfile.TemporaryDirectory() as tmpdir:
    ...     runner = AnalysisRunner(
    ...         ingestor=Ingestor(
    ...             pl.DataFrame(
    ...                 {
    ...                     "pred": [3, 2, 0, 1, 0],
    ...                     "target": [3, 2, 0, 1, 0],
    ...                 }
    ...             )
    ...         ),
    ...         transformer=SequentialTransformer(transformers=[]),
    ...         analyzer=AccuracyAnalyzer(y_true="target", y_pred="pred"),
    ...         exporter=MetricExporter(Path(tmpdir).joinpath("metrics.pkl")),
    ...     )
    ...     print(runner)
    ...     runner.run()
    ...
    AnalysisRunner(
      (ingestor): Ingestor(shape=(5, 2))
      (transformer): SequentialTransformer()
      (analyzer): AccuracyAnalyzer(y_true='target', y_pred='pred', drop_nulls=True, missing_policy='raise', nan_policy='propagate')
      (exporter): MetricExporter(
          (path): .../metrics.pkl
          (saver): PickleSaver(protocol=5)
          (exist_ok): False
          (show_metrics): False
        )
      (lazy): True
    )

    ```
    """

    def __init__(
        self,
        ingestor: BaseIngestor | dict,
        transformer: BaseTransformer | dict,
        analyzer: BaseAnalyzer | dict,
        exporter: BaseExporter | dict,
        lazy: bool = True,
    ) -> None:
        self._ingestor = setup_ingestor(ingestor)
        self._transformer = setup_transformer(transformer)
        self._analyzer = setup_analyzer(analyzer)
        self._exporter = setup_exporter(exporter)
        self._lazy = lazy

    def __repr__(self) -> str:
        args = str_indent(
            str_mapping(
                {
                    "ingestor": self._ingestor,
                    "transformer": self._transformer,
                    "analyzer": self._analyzer,
                    "exporter": self._exporter,
                    "lazy": self._lazy,
                }
            )
        )
        return f"{self.__class__.__qualname__}(\n  {args}\n)"

    def run(self) -> None:
        with timeblock():
            self._run()

    def _run(self) -> None:
        logger.info("Ingesting data...")
        raw_data = self._ingestor.ingest()
        logger.info("Transforming data...")
        data = self._transformer.transform(raw_data)
        logger.info("Analyzing...")
        output = self._analyzer.analyze(data, lazy=self._lazy)
        logger.info(f"output:\n{output}")
        logger.info("Exporting the output...")
        self._exporter.export(output)
