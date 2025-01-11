r"""Contain an analyzer that processes a mapping of analyzers."""

from __future__ import annotations

__all__ = ["MappingAnalyzer"]

import logging
from typing import TYPE_CHECKING

from coola.utils import repr_indent, repr_mapping

from arkas.analyzer.base import BaseAnalyzer
from arkas.output.mapping import OutputDict

if TYPE_CHECKING:
    from collections.abc import Mapping

    import polars as pl


logger = logging.getLogger(__name__)


class MappingAnalyzer(BaseAnalyzer):
    r"""Implement an analyzer that processes a mapping of analyzers.

    Args:
        analyzers: The mapping of analyzers.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from arkas.analyzer import (
    ...     MappingAnalyzer,
    ...     AccuracyAnalyzer,
    ...     BalancedAccuracyAnalyzer,
    ... )
    >>> analyzer = MappingAnalyzer(
    ...     {
    ...         "one": AccuracyAnalyzer(y_true="target", y_pred="pred"),
    ...         "two": BalancedAccuracyAnalyzer(y_true="target", y_pred="pred"),
    ...     }
    ... )
    >>> analyzer
    MappingAnalyzer(
      (one): AccuracyAnalyzer(y_true='target', y_pred='pred', drop_nulls=True, missing_policy='raise', nan_policy='propagate')
      (two): BalancedAccuracyAnalyzer(y_true='target', y_pred='pred', drop_nulls=True, missing_policy='raise', nan_policy='propagate')
    )
    >>> frame = pl.DataFrame({"pred": [1, 0, 0, 1, 1], "target": [1, 0, 0, 1, 1]})
    >>> output = analyzer.analyze(frame)
    >>> output
    OutputDict(count=2)

    ```
    """

    def __init__(self, analyzers: Mapping[str, BaseAnalyzer]) -> None:
        self._analyzers = analyzers

    def __repr__(self) -> str:
        args = repr_indent(repr_mapping(self._analyzers))
        return f"{self.__class__.__qualname__}(\n  {args}\n)"

    def analyze(self, frame: pl.DataFrame, lazy: bool = True) -> OutputDict:
        return OutputDict(
            {
                key: analyzer.analyze(frame=frame, lazy=lazy)
                for key, analyzer in self._analyzers.items()
            }
        )
