r"""Contain the Wasserstein distance between two 1D distributions
evaluator."""

from __future__ import annotations

__all__ = ["WassersteinDistanceEvaluator"]

import logging
from typing import TYPE_CHECKING

from coola.utils.format import repr_mapping_line

from arkas.evaluator.lazy import BaseLazyEvaluator
from arkas.metric.utils import check_nan_policy
from arkas.result import Result, WassersteinDistanceResult
from arkas.utils.array import to_array

if TYPE_CHECKING:
    import polars as pl


logger = logging.getLogger(__name__)


class WassersteinDistanceEvaluator(BaseLazyEvaluator[WassersteinDistanceResult]):
    r"""Implement the Wasserstein distance between two 1D distributions
    evaluator.

    Args:
        u_values: The values observed in the (empirical) distribution.
        v_values: The values observed in the (empirical) distribution.
        drop_nulls: If ``True``, the rows with null values in
            ``x`` or ``y`` columns are dropped.
        nan_policy: The policy on how to handle NaN values in the input
            arrays. The following options are available: ``'omit'``,
            ``'propagate'``, and ``'raise'``.

    Example usage:

    ```pycon

    >>> import polars as pl
    >>> from arkas.evaluator import WassersteinDistanceEvaluator
    >>> evaluator = WassersteinDistanceEvaluator(u_values="target", v_values="pred")
    >>> evaluator
    WassersteinDistanceEvaluator(u_values='target', v_values='pred', drop_nulls=True, nan_policy='propagate')
    >>> data = pl.DataFrame({"pred": [1, 2, 3, 4, 5], "target": [1, 2, 3, 4, 5]})
    >>> result = evaluator.evaluate(data)
    >>> result
    WassersteinDistanceResult(u_values=(5,), v_values=(5,), nan_policy='propagate')

    ```
    """

    def __init__(
        self,
        u_values: str,
        v_values: str,
        drop_nulls: bool = True,
        nan_policy: str = "propagate",
    ) -> None:
        super().__init__(drop_nulls=drop_nulls)
        self._u_values = u_values
        self._v_values = v_values

        check_nan_policy(nan_policy)
        self._nan_policy = nan_policy

    def __repr__(self) -> str:
        args = repr_mapping_line(
            {
                "u_values": self._u_values,
                "v_values": self._v_values,
                "drop_nulls": self._drop_nulls,
                "nan_policy": self._nan_policy,
            }
        )
        return f"{self.__class__.__qualname__}({args})"

    def evaluate(self, data: pl.DataFrame, lazy: bool = True) -> WassersteinDistanceResult | Result:
        logger.info(
            f"Evaluating the Wasserstein distance | u_values={self._u_values!r} | "
            f"v_values={self._v_values!r} | drop_nulls={self._drop_nulls} | "
            f"nan_policy={self._nan_policy!r}"
        )
        return self._evaluate(data, lazy)

    def _compute_result(self, data: pl.DataFrame) -> WassersteinDistanceResult:
        return WassersteinDistanceResult(
            u_values=to_array(data[self._u_values]).ravel(),
            v_values=to_array(data[self._v_values]).ravel(),
            nan_policy=self._nan_policy,
        )

    def _get_columns(self) -> tuple[str, ...]:
        return (self._u_values, self._v_values)
