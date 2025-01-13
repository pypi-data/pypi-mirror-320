r"""Contain a simple evaluation runner implementation."""

from __future__ import annotations

__all__ = ["EvaluationRunner"]

import logging
from typing import TYPE_CHECKING, Any

from coola.nested import to_flat_dict
from coola.utils import str_indent, str_mapping
from coola.utils.path import sanitize_path
from grizz.ingestor import BaseIngestor, setup_ingestor
from grizz.transformer import BaseTransformer, setup_transformer
from iden.io import BaseSaver, setup_saver

from arkas.evaluator import BaseEvaluator, setup_evaluator
from arkas.runner.base import BaseRunner

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)


class EvaluationRunner(BaseRunner):
    r"""Implement a simple evaluation runner.

    Args:
        ingestor: The data ingestor or its configuration.
        transformer: The data transformer or its configuration.
        evaluator: The evaluator or its configuration.
        saver: The metric saver or its configuration.
        path: The path where to save the metrics.
        show_metrics: If ``True``, the metrics are shown in the
            logging output.

    Example usage:

    ```pycon

    >>> import tempfile
    >>> import polars as pl
    >>> from pathlib import Path
    >>> from iden.io import PickleSaver
    >>> from grizz.ingestor import Ingestor
    >>> from grizz.transformer import SequentialTransformer
    >>> from arkas.evaluator import AccuracyEvaluator
    >>> from arkas.runner import EvaluationRunner
    >>> with tempfile.TemporaryDirectory() as tmpdir:
    ...     path = Path(tmpdir).joinpath("metrics.pkl")
    ...     runner = EvaluationRunner(
    ...         ingestor=Ingestor(
    ...             pl.DataFrame(
    ...                 {
    ...                     "pred": [3, 2, 0, 1, 0],
    ...                     "target": [3, 2, 0, 1, 0],
    ...                 }
    ...             )
    ...         ),
    ...         transformer=SequentialTransformer(transformers=[]),
    ...         evaluator=AccuracyEvaluator(y_true="target", y_pred="pred"),
    ...         saver=PickleSaver(),
    ...         path=path,
    ...     )
    ...     print(runner)
    ...     runner.run()
    ...
    EvaluationRunner(
      (ingestor): Ingestor(shape=(5, 2))
      (transformer): SequentialTransformer()
      (evaluator): AccuracyEvaluator(y_true='target', y_pred='pred', drop_nulls=True, nan_policy='propagate')
      (saver): PickleSaver(protocol=5)
      (path): .../metrics.pkl
      (show_metrics): True
    )

    ```
    """

    def __init__(
        self,
        ingestor: BaseIngestor | dict,
        transformer: BaseTransformer | dict,
        evaluator: BaseEvaluator | dict,
        saver: BaseSaver | dict,
        path: Path | str,
        show_metrics: bool = True,
    ) -> None:
        self._ingestor = setup_ingestor(ingestor)
        self._transformer = setup_transformer(transformer)
        self._evaluator = setup_evaluator(evaluator)
        self._saver = setup_saver(saver)
        self._path = sanitize_path(path)
        self._show_metrics = bool(show_metrics)

    def __repr__(self) -> str:
        args = str_indent(
            str_mapping(
                {
                    "ingestor": self._ingestor,
                    "transformer": self._transformer,
                    "evaluator": self._evaluator,
                    "saver": self._saver,
                    "path": self._path,
                    "show_metrics": self._show_metrics,
                }
            )
        )
        return f"{self.__class__.__qualname__}(\n  {args}\n)"

    def run(self) -> Any:
        logger.info("Ingesting data...")
        raw_data = self._ingestor.ingest()
        logger.info("Transforming data...")
        data = self._transformer.transform(raw_data)
        logger.info("Evaluating...")
        result = self._evaluator.evaluate(data)
        logger.info(f"result:\n{result}")
        logger.info("Computing metrics...")
        metrics = result.compute_metrics()
        logger.info(f"Saving metrics at {self._path}...")
        self._saver.save(metrics, path=self._path, exist_ok=True)

        if self._show_metrics:
            logger.info(f"metrics:\n{str_mapping(to_flat_dict(metrics), sorted_keys=True)}")
