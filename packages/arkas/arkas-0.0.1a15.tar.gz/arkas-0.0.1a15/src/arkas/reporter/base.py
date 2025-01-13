r"""Contain the base class to implement a reporter."""

from __future__ import annotations

__all__ = ["BaseReporter", "is_reporter_config", "setup_reporter"]

import logging
from abc import ABC, abstractmethod

from objectory import AbstractFactory
from objectory.utils import is_object_config

logger = logging.getLogger(__name__)


class BaseReporter(ABC, metaclass=AbstractFactory):
    r"""Define the base class to generate a HTML report.

    Example usage:

    ```pycon

    >>> import tempfile
    >>> from pathlib import Path
    >>> import polars as pl
    >>> from arkas.evaluator import AccuracyEvaluator
    >>> from grizz.ingestor import Ingestor
    >>> from grizz.transformer import SequentialTransformer
    >>> from arkas.reporter import EvalReporter
    >>> with tempfile.TemporaryDirectory() as tmpdir:
    ...     reporter = EvalReporter(
    ...         ingestor=Ingestor(
    ...             pl.DataFrame({"pred": [3, 2, 0, 1, 0, 1], "target": [3, 2, 0, 1, 0, 1]})
    ...         ),
    ...         transformer=SequentialTransformer(transformers=[]),
    ...         evaluator=AccuracyEvaluator(y_true="target", y_pred="pred"),
    ...         report_path=Path(tmpdir).joinpath("report.html"),
    ...     )
    ...     reporter.generate()
    ...

    ```
    """

    @abstractmethod
    def generate(self) -> None:
        r"""Generate a HTML report.

        Example usage:

        ```pycon

        >>> import tempfile
        >>> from pathlib import Path
        >>> import polars as pl
        >>> from arkas.evaluator import AccuracyEvaluator
        >>> from grizz.ingestor import Ingestor
        >>> from grizz.transformer import SequentialTransformer
        >>> from arkas.reporter import EvalReporter
        >>> with tempfile.TemporaryDirectory() as tmpdir:
        ...     reporter = EvalReporter(
        ...         ingestor=Ingestor(
        ...             pl.DataFrame({"pred": [3, 2, 0, 1, 0, 1], "target": [3, 2, 0, 1, 0, 1]})
        ...         ),
        ...         transformer=SequentialTransformer(transformers=[]),
        ...         evaluator=AccuracyEvaluator(y_true="target", y_pred="pred"),
        ...         report_path=Path(tmpdir).joinpath("report.html"),
        ...     )
        ...     reporter.generate()
        ...

        ```
        """


def is_reporter_config(config: dict) -> bool:
    r"""Indicate if the input configuration is a configuration for a
    ``BaseReporter``.

    This function only checks if the value of the key  ``_target_``
    is valid. It does not check the other values. If ``_target_``
    indicates a function, the returned type hint is used to check
    the class.

    Args:
        config: The configuration to check.

    Returns:
        bool: ``True`` if the input configuration is a configuration
            for a ``BaseReporter`` object.

    Example usage:

    ```pycon

    >>> from arkas.reporter import is_reporter_config
    >>> is_reporter_config(
    ...     {
    ...         "_target_": "arkas.reporter.EvalReporter",
    ...         "ingestor": {
    ...             "_target_": "grizz.ingestor.CsvIngestor",
    ...             "path": "/path/to/data.csv",
    ...         },
    ...         "transformer": {"_target_": "grizz.transformer.DropDuplicate"},
    ...         "evaluator": {
    ...             "_target_": "arkas.evaluator.AccuracyEvaluator",
    ...             "y_true": "target",
    ...             "y_pred": "pred",
    ...         },
    ...         "report_path": "/path/to/report.html",
    ...     }
    ... )
    True

    ```
    """
    return is_object_config(config, BaseReporter)


def setup_reporter(
    reporter: BaseReporter | dict,
) -> BaseReporter:
    r"""Set up a reporter.

    The reporter is instantiated from its configuration
    by using the ``BaseReporter`` factory function.

    Args:
        reporter: A reporter or its configuration.

    Returns:
        An instantiated reporter.

    Example usage:

    ```pycon

    >>> from arkas.reporter import setup_reporter
    >>> reporter = setup_reporter(
    ...     {
    ...         "_target_": "arkas.reporter.EvalReporter",
    ...         "ingestor": {
    ...             "_target_": "grizz.ingestor.CsvIngestor",
    ...             "path": "/path/to/data.csv",
    ...         },
    ...         "transformer": {"_target_": "grizz.transformer.DropDuplicate"},
    ...         "evaluator": {
    ...             "_target_": "arkas.evaluator.AccuracyEvaluator",
    ...             "y_true": "target",
    ...             "y_pred": "pred",
    ...         },
    ...         "report_path": "/path/to/report.html",
    ...     }
    ... )
    >>> reporter
    EvalReporter(
      (ingestor): CsvIngestor(path=/path/to/data.csv)
      (transformer): DropDuplicateTransformer(columns=None, exclude_columns=(), missing_policy='raise')
      (evaluator): AccuracyEvaluator(y_true='target', y_pred='pred', drop_nulls=True, nan_policy='propagate')
      (report_path): /path/to/report.html
      (max_toc_depth): 6
    )

    ```
    """
    if isinstance(reporter, dict):
        logger.info("Initializing a reporter from its configuration... ")
        reporter = BaseReporter.factory(**reporter)
    if not isinstance(reporter, BaseReporter):
        logger.warning(f"reporter is not a `BaseReporter` (received: {type(reporter)})")
    return reporter
