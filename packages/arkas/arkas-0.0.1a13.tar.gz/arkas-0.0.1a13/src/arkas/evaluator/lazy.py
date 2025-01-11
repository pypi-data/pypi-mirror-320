r"""Contain the base class to implement a lazy evaluator."""

from __future__ import annotations

__all__ = ["BaseLazyEvaluator"]

import logging
from abc import abstractmethod
from typing import TYPE_CHECKING, Generic, TypeVar

from grizz.utils.format import str_row_diff
from polars import selectors as cs

from arkas.evaluator.base import BaseEvaluator
from arkas.result import BaseResult, EmptyResult, Result
from arkas.utils.data import find_missing_keys

if TYPE_CHECKING:
    import polars as pl


logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseResult)


class BaseLazyEvaluator(BaseEvaluator, Generic[T]):
    r"""Define the base class to evaluate the result lazily.

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

    def __init__(self, drop_nulls: bool) -> None:
        self._drop_nulls = bool(drop_nulls)

    def _evaluate(self, data: pl.DataFrame, lazy: bool = True) -> T | Result:
        r"""Evaluate the result.

        Args:
            data: The data to evaluate.
            lazy: If ``True``, it forces the computation of the
                result, otherwise it returns a result object that
                delays the evaluation of the result.

        Returns:
            The generated result.
        """
        if missing_cols := find_missing_keys(keys=set(data.columns), queries=self._get_columns()):
            logger.warning(
                "Skipping the evaluation because some columns are missing: "
                f"{sorted(missing_cols)}"
            )
            return EmptyResult()

        data = self._prepare_data(data)
        out = self._compute_result(data)
        if lazy or isinstance(out, EmptyResult):
            return out
        return Result(metrics=out.compute_metrics(), figures=out.generate_figures())

    def _prepare_data(self, data: pl.DataFrame) -> pl.DataFrame:
        if self._drop_nulls:
            cols = self._get_columns()
            logger.info(f"Dropping rows that have at least one null value in the columns: {cols}")
            initial_shape = data.shape
            data = data.drop_nulls(cs.by_name(cols))
            logger.info(
                f"DataFrame shape: {initial_shape} -> {data.shape} | "
                f"{str_row_diff(orig=initial_shape[0], final=data.shape[0])}"
            )
        return data

    @abstractmethod
    def _compute_result(self, data: pl.DataFrame) -> T:
        r"""Compute and return the result.

        Args:
            data: The data to evaluate.

        Returns:
            The generated result.
        """

    @abstractmethod
    def _get_columns(self) -> tuple[str, ...]:
        r"""Get the columns used to compute the result.

        Returns:
            The column names.
        """
