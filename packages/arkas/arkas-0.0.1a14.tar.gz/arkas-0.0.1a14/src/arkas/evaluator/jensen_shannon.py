r"""Contain the Jensen-Shannon (JS) divergence between two distributions
evaluator."""

from __future__ import annotations

__all__ = ["JensenShannonDivergenceEvaluator"]

import logging
from typing import TYPE_CHECKING

from coola.utils.format import repr_mapping_line

from arkas.evaluator.lazy import BaseLazyEvaluator
from arkas.result import JensenShannonDivergenceResult, Result
from arkas.utils.array import to_array

if TYPE_CHECKING:
    import polars as pl


logger = logging.getLogger(__name__)


class JensenShannonDivergenceEvaluator(BaseLazyEvaluator[JensenShannonDivergenceResult]):
    r"""Implement the Jensen-Shannon (JS) divergence between two
    distributions evaluator.

    Args:
        p: The values observed in the (empirical) distribution.
        q: The values observed in the (empirical) distribution.
        drop_nulls: If ``True``, the rows with null values in
            ``x`` or ``y`` columns are dropped.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from arkas.evaluator import JensenShannonDivergenceEvaluator
    >>> evaluator = JensenShannonDivergenceEvaluator(p="target", q="pred")
    >>> evaluator
    JensenShannonDivergenceEvaluator(p='target', q='pred', drop_nulls=True)
    >>> data = pl.DataFrame({"pred": [1, 2, 3, 4, 5], "target": [1, 2, 3, 4, 5]})
    >>> result = evaluator.evaluate(data)
    >>> result
    JensenShannonDivergenceResult(p=(5,), q=(5,))

    ```
    """

    def __init__(self, p: str, q: str, drop_nulls: bool = True) -> None:
        super().__init__(drop_nulls=drop_nulls)
        self._p = p
        self._q = q

    def __repr__(self) -> str:
        args = repr_mapping_line(
            {
                "p": self._p,
                "q": self._q,
                "drop_nulls": self._drop_nulls,
            }
        )
        return f"{self.__class__.__qualname__}({args})"

    def evaluate(
        self, data: pl.DataFrame, lazy: bool = True
    ) -> JensenShannonDivergenceResult | Result:
        logger.info(
            f"Evaluating the Wasserstein distance | p={self._p!r} | "
            f"q={self._q!r} | drop_nulls={self._drop_nulls}"
        )
        return self._evaluate(data, lazy)

    def _compute_result(self, data: pl.DataFrame) -> JensenShannonDivergenceResult:
        return JensenShannonDivergenceResult(
            p=to_array(data[self._p]).ravel(),
            q=to_array(data[self._q]).ravel(),
        )

    def _get_columns(self) -> tuple[str, ...]:
        return (self._p, self._q)
