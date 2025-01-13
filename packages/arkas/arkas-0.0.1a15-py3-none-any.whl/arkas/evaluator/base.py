r"""Contain the base class to implement an evaluator."""

from __future__ import annotations

__all__ = ["BaseEvaluator", "is_evaluator_config", "setup_evaluator"]

import logging
from abc import ABC
from typing import TYPE_CHECKING

from objectory import AbstractFactory
from objectory.utils import is_object_config

if TYPE_CHECKING:
    import polars as pl

    from arkas.result import BaseResult

logger = logging.getLogger(__name__)


class BaseEvaluator(ABC, metaclass=AbstractFactory):
    r"""Define the base class to evaluate a DataFrame.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from arkas.evaluator import AccuracyEvaluator
    >>> evaluator = AccuracyEvaluator(y_true="target", y_pred="pred")
    >>> evaluator
    AccuracyEvaluator(y_true='target', y_pred='pred', drop_nulls=True, nan_policy='propagate')
    >>> data = pl.DataFrame({"pred": [3, 2, 0, 1, 0, 1], "target": [3, 2, 0, 1, 0, 1]})
    >>> result = evaluator.evaluate(data)
    >>> result
    AccuracyResult(y_true=(6,), y_pred=(6,), nan_policy='propagate')

    ```
    """

    def evaluate(self, data: pl.DataFrame, lazy: bool = True) -> BaseResult:
        r"""Evaluate the result.

        Args:
            data: The data to evaluate.
            lazy: If ``True``, it forces the computation of the
                result, otherwise it returns a result object that
                delays the evaluation of the result.

        Returns:
            The generated result.

        Example usage:

        ```pycon

        >>> import polars as pl
        >>> from arkas.evaluator import AccuracyEvaluator
        >>> evaluator = AccuracyEvaluator(y_true="target", y_pred="pred")
        >>> data = pl.DataFrame({"pred": [3, 2, 0, 1, 0, 1], "target": [3, 2, 0, 1, 0, 1]})
        >>> result = evaluator.evaluate(data)
        >>> result
        AccuracyResult(y_true=(6,), y_pred=(6,), nan_policy='propagate')

        ```
        """


def is_evaluator_config(config: dict) -> bool:
    r"""Indicate if the input configuration is a configuration for a
    ``BaseEvaluator``.

    This function only checks if the value of the key  ``_target_``
    is valid. It does not check the other values. If ``_target_``
    indicates a function, the returned type hint is used to check
    the class.

    Args:
        config: The configuration to check.

    Returns:
        ``True`` if the input configuration is a configuration
            for a ``BaseEvaluator`` object.

    Example usage:

    ```pycon

    >>> from arkas.evaluator import is_evaluator_config
    >>> is_evaluator_config({"_target_": "arkas.evaluator.AccuracyEvaluator"})
    True

    ```
    """
    return is_object_config(config, BaseEvaluator)


def setup_evaluator(
    evaluator: BaseEvaluator | dict,
) -> BaseEvaluator:
    r"""Set up an evaluator.

    The evaluator is instantiated from its configuration
    by using the ``BaseEvaluator`` factory function.

    Args:
        evaluator: An evaluator or its configuration.

    Returns:
        An instantiated evaluator.

    Example usage:

    ```pycon

    >>> from arkas.evaluator import setup_evaluator
    >>> evaluator = setup_evaluator(
    ...     {
    ...         "_target_": "arkas.evaluator.AccuracyEvaluator",
    ...         "y_true": "target",
    ...         "y_pred": "pred",
    ...     }
    ... )
    >>> evaluator
    AccuracyEvaluator(y_true='target', y_pred='pred', drop_nulls=True, nan_policy='propagate')

    ```
    """
    if isinstance(evaluator, dict):
        logger.info("Initializing an evaluator from its configuration... ")
        evaluator = BaseEvaluator.factory(**evaluator)
    if not isinstance(evaluator, BaseEvaluator):
        logger.warning(f"evaluator is not a `BaseEvaluator` (received: {type(evaluator)})")
    return evaluator
