r"""Contain the base class to implement an analyzer."""

from __future__ import annotations

__all__ = ["BaseAnalyzer", "is_analyzer_config", "setup_analyzer"]

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from objectory import AbstractFactory
from objectory.utils import is_object_config

if TYPE_CHECKING:
    import polars as pl

    from arkas.output import BaseOutput

logger = logging.getLogger(__name__)


class BaseAnalyzer(ABC, metaclass=AbstractFactory):
    r"""Define the base class to analyze a DataFrame.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from arkas.analyzer import AccuracyAnalyzer
    >>> analyzer = AccuracyAnalyzer(y_true="target", y_pred="pred")
    >>> analyzer
    AccuracyAnalyzer(y_true='target', y_pred='pred', drop_nulls=True, missing_policy='raise', nan_policy='propagate')
    >>> data = pl.DataFrame({"pred": [3, 2, 0, 1, 0, 1], "target": [3, 2, 0, 1, 0, 1]})
    >>> output = analyzer.analyze(data)
    >>> output
    AccuracyOutput(
      (state): AccuracyState(y_true=(6,), y_pred=(6,), y_true_name='target', y_pred_name='pred', nan_policy='propagate')
    )

    ```
    """

    @abstractmethod
    def analyze(self, frame: pl.DataFrame, lazy: bool = True) -> BaseOutput:
        r"""Analyze the DataFrame.

        Args:
            frame: The DataFrame to analyze.
            lazy: If ``True``, it forces the computation of the output,
                otherwise it returns an output object that contains the
                logic.

        Returns:
            The generated output.

        Example usage:

        ```pycon

        >>> import polars as pl
        >>> from arkas.analyzer import AccuracyAnalyzer
        >>> analyzer = AccuracyAnalyzer(y_true="target", y_pred="pred")
        >>> data = pl.DataFrame({"pred": [3, 2, 0, 1, 0, 1], "target": [3, 2, 0, 1, 0, 1]})
        >>> output = analyzer.analyze(data)
        >>> output
        AccuracyOutput(
          (state): AccuracyState(y_true=(6,), y_pred=(6,), y_true_name='target', y_pred_name='pred', nan_policy='propagate')
        )

        ```
        """


def is_analyzer_config(config: dict) -> bool:
    r"""Indicate if the input configuration is a configuration for a
    ``BaseAnalyzer``.

    This function only checks if the value of the key  ``_target_``
    is valid. It does not check the other values. If ``_target_``
    indicates a function, the returned type hint is used to check
    the class.

    Args:
        config: The configuration to check.

    Returns:
        ``True`` if the input configuration is a configuration
            for a ``BaseAnalyzer`` object.

    Example usage:

    ```pycon

    >>> from arkas.analyzer import is_analyzer_config
    >>> is_analyzer_config({"_target_": "arkas.analyzer.AccuracyAnalyzer"})
    True

    ```
    """
    return is_object_config(config, BaseAnalyzer)


def setup_analyzer(
    analyzer: BaseAnalyzer | dict,
) -> BaseAnalyzer:
    r"""Set up an analyzer.

    The analyzer is instantiated from its configuration
    by using the ``BaseAnalyzer`` factory function.

    Args:
        analyzer: An analyzer or its configuration.

    Returns:
        An instantiated analyzer.

    Example usage:

    ```pycon

    >>> from arkas.analyzer import setup_analyzer
    >>> analyzer = setup_analyzer(
    ...     {
    ...         "_target_": "arkas.analyzer.AccuracyAnalyzer",
    ...         "y_true": "target",
    ...         "y_pred": "pred",
    ...     }
    ... )
    >>> analyzer
    AccuracyAnalyzer(y_true='target', y_pred='pred', drop_nulls=True, missing_policy='raise', nan_policy='propagate')

    ```
    """
    if isinstance(analyzer, dict):
        logger.info("Initializing an analyzer from its configuration... ")
        analyzer = BaseAnalyzer.factory(**analyzer)
    if not isinstance(analyzer, BaseAnalyzer):
        logger.warning(f"analyzer is not a `BaseAnalyzer` (received: {type(analyzer)})")
    return analyzer
