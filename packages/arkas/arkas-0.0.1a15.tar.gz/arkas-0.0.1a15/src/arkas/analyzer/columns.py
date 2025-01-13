r"""Define some template classes to implement some analyzers."""

from __future__ import annotations

__all__ = ["BaseTruePredAnalyzer"]

import logging
from abc import abstractmethod
from typing import TYPE_CHECKING

import polars as pl
from grizz.utils.column import check_column_missing_policy, check_missing_column
from grizz.utils.format import str_shape_diff
from polars import selectors as cs

from arkas.analyzer.base import BaseAnalyzer
from arkas.output.empty import EmptyOutput

if TYPE_CHECKING:
    from arkas.output.base import BaseOutput

logger = logging.getLogger(__name__)


class BaseTruePredAnalyzer(BaseAnalyzer):
    r"""Define a base class to implement ``polars.DataFrame``
    analyzer that takes two input columns: ``y_true`` and ``y_pred``.

    Args:
        y_true: The column name of the ground truth target
            labels.
        y_pred: The column name of the predicted labels.
        drop_nulls: If ``True``, the rows with null values in
            ``y_true`` or ``y_pred`` columns are dropped.
        missing_policy: The policy on how to handle missing columns.
            The following options are available: ``'ignore'``,
            ``'warn'``, and ``'raise'``. If ``'raise'``, an exception
            is raised if at least one column is missing.
            If ``'warn'``, a warning is raised if at least one column
            is missing and the missing columns are ignored.
            If ``'ignore'``, the missing columns are ignored and
            no warning message appears.
    """

    def __init__(
        self,
        y_true: str,
        y_pred: str,
        drop_nulls: bool,
        missing_policy: str,
    ) -> None:
        self._y_true = y_true
        self._y_pred = y_pred
        self._drop_nulls = bool(drop_nulls)

        check_column_missing_policy(missing_policy)
        self._missing_policy = missing_policy

    # def __repr__(self) -> str:
    #     args = repr_mapping_line(
    #         {
    #             "y_true": self._y_true,
    #             "y_pred": self._y_pred,
    #             "drop_nulls": self._drop_nulls,
    #             "missing_policy": self._missing_policy,
    #         }
    #     )
    #     return f"{self.__class__.__qualname__}({args})"

    def analyze(self, frame: pl.DataFrame, lazy: bool = True) -> BaseOutput:
        self._check_input_column(frame)
        for col in [self._y_true, self._y_pred]:
            if col not in frame:
                logger.info(
                    f"Skipping '{self.__class__.__qualname__}.analyze' "
                    f"because the input column {col!r} is missing"
                )
                return EmptyOutput()
        output = self._analyze(self._prepare_data(frame))
        if not lazy:
            output = output.compute()
        return output

    def _prepare_data(self, data: pl.DataFrame) -> pl.DataFrame:
        if self._drop_nulls:
            cols = [self._y_true, self._y_pred]
            logger.info(f"Dropping rows that have at least one null value in the columns: {cols}")
            initial_shape = data.shape
            data = data.drop_nulls(cs.by_name(cols))
            logger.info(str_shape_diff(orig=initial_shape, final=data.shape))
        return data

    def _check_input_column(self, frame: pl.DataFrame) -> None:
        r"""Check if the input column is missing.

        Args:
            frame: The input DataFrame to check.
        """
        check_missing_column(frame, column=self._y_true, missing_policy=self._missing_policy)
        check_missing_column(frame, column=self._y_pred, missing_policy=self._missing_policy)

    @abstractmethod
    def _analyze(self, frame: pl.DataFrame) -> BaseOutput:
        r"""Analyze the DataFrame.

        Args:
            frame: The DataFrame to analyze.

        Returns:
            The generated output.
        """
