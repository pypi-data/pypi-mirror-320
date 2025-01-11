r"""Implement the Normalized Discounted Cumulative Gain (NDCG)
metrics."""

from __future__ import annotations

__all__ = ["ndcg"]


from typing import TYPE_CHECKING

from sklearn.metrics import ndcg_score

from arkas.metric.utils import (
    check_array_ndim,
    contains_nan,
    preprocess_score_multilabel,
)

if TYPE_CHECKING:
    import numpy as np


def ndcg(
    y_true: np.ndarray,
    y_score: np.ndarray,
    *,
    k: int | None = None,
    prefix: str = "",
    suffix: str = "",
    nan_policy: str = "propagate",
) -> dict[str, float]:
    r"""Return the Normalized Discounted Cumulative Gain (NDCG) metrics.

    Args:
        y_true: The ground truth target targets of multilabel
            classification, or true scores of entities to be ranked.
            Negative values in y_true may result in an output that is
            not between 0 and 1. This input must be an array of shape
            ``(n_samples, n_labels)``.
        y_score: The predicted scores, can either be probability
            estimates, confidence values, or non-thresholded measure
            of decisions. This input must be an array of shape
            ``(n_samples, n_labels)``.
        k: Only consider the highest ``k`` scores in the ranking.
            If ``None``, use all outputs.
        prefix: The key prefix in the returned dictionary.
        suffix: The key suffix in the returned dictionary.
        nan_policy: The policy on how to handle NaN values in the input
            arrays. The following options are available: ``'omit'``,
            ``'propagate'``, and ``'raise'``.

    Returns:
        The computed metrics.

    Example usage:

    ```pycon

    >>> import numpy as np
    >>> from arkas.metric import ndcg
    >>> ndcg(
    ...     y_true=np.array([[1, 0, 0], [1, 2, 0], [1, 1, 2], [0, 0, 1]]),
    ...     y_score=np.array(
    ...         [[2.0, 1.0, 0.0], [0.0, 1.0, -1.0], [0.0, 0.0, 1.0], [1.0, 2.0, 3.0]]
    ...     ),
    ... )
    {'count': 4, 'ndcg': 1.0}

    ```
    """
    check_array_ndim(y_true, ndim=2)
    y_true, y_score = preprocess_score_multilabel(
        y_true=y_true, y_score=y_score, drop_nan=nan_policy == "omit"
    )
    y_true_nan = contains_nan(arr=y_true, nan_policy=nan_policy, name="'y_true'")
    y_score_nan = contains_nan(arr=y_score, nan_policy=nan_policy, name="'y_score'")

    n_samples = y_true.shape[0]
    score = float("nan")
    if n_samples > 0 and not y_true_nan and not y_score_nan:
        score = float(ndcg_score(y_true=y_true, y_score=y_score, k=k))
    return {f"{prefix}count{suffix}": n_samples, f"{prefix}ndcg{suffix}": score}
