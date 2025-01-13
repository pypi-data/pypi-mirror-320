r"""Contain an analyzer that transforms the data before to analyze
them."""

from __future__ import annotations

__all__ = ["TransformAnalyzer"]

import logging
from typing import TYPE_CHECKING

from coola.utils.format import repr_indent, repr_mapping
from grizz.transformer import BaseTransformer, setup_transformer

from arkas.analyzer.base import BaseAnalyzer, setup_analyzer

if TYPE_CHECKING:
    import polars as pl

    from arkas.output.base import BaseOutput


logger = logging.getLogger(__name__)


class TransformAnalyzer(BaseAnalyzer):
    r"""Implement an analyzer that transforms the data before to analyze
    them.

    Args:
        transformer: The transformer or its configuration.
        analyzer: The analyzer or its configuration.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from arkas.analyzer import AccuracyAnalyzer, TransformAnalyzer
    >>> from grizz.transformer import DropNullRow
    >>> analyzer = TransformAnalyzer(
    ...     transformer=DropNullRow(), analyzer=AccuracyAnalyzer(y_true="target", y_pred="pred")
    ... )
    >>> analyzer
    TransformAnalyzer(
      (transformer): DropNullRowTransformer(columns=None, exclude_columns=(), missing_policy='raise')
      (analyzer): AccuracyAnalyzer(y_true='target', y_pred='pred', drop_nulls=True, missing_policy='raise', nan_policy='propagate')
    )
    >>> frame = pl.DataFrame(
    ...     {"pred": [3, 2, 0, 1, 0, 1, None], "target": [3, 2, 0, 1, 0, 1, None]}
    ... )
    >>> output = analyzer.analyze(frame)
    >>> output
    AccuracyOutput(
      (state): AccuracyState(y_true=(6,), y_pred=(6,), y_true_name='target', y_pred_name='pred', nan_policy='propagate')
    )

    ```
    """

    def __init__(
        self,
        transformer: BaseTransformer | dict,
        analyzer: BaseAnalyzer | dict,
    ) -> None:
        self._transformer = setup_transformer(transformer)
        self._analyzer = setup_analyzer(analyzer)

    def __repr__(self) -> str:
        args = repr_indent(
            repr_mapping({"transformer": self._transformer, "analyzer": self._analyzer})
        )
        return f"{self.__class__.__qualname__}(\n  {args}\n)"

    def analyze(self, frame: pl.DataFrame, lazy: bool = True) -> BaseOutput:
        frame = self._transformer.transform(frame)
        return self._analyzer.analyze(frame=frame, lazy=lazy)
