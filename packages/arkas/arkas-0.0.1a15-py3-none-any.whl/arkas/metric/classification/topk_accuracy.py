r"""Implement a function to compute the Top-k Accuracy classification
metrics."""

from __future__ import annotations

__all__ = ["binary_top_k_accuracy", "multiclass_top_k_accuracy", "top_k_accuracy"]

from typing import TYPE_CHECKING

from sklearn import metrics

from arkas.metric.utils import (
    contains_nan,
    preprocess_score_binary,
    preprocess_score_multiclass,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

    import numpy as np


def top_k_accuracy(
    y_true: np.ndarray,
    y_score: np.ndarray,
    *,
    k: Sequence[int] = (2,),
    prefix: str = "",
    suffix: str = "",
    nan_policy: str = "propagate",
) -> dict[str, float | np.ndarray]:
    r"""Return the Area Under the Top-k Accuracy classification metrics.

    Args:
        y_true: The ground truth target labels. This input must
            be an array of shape ``(n_samples,)``.
        y_score: The target scores, can either be probability
            estimates of the positive class, confidence values,
            or non-thresholded measure of decisions. The binary case
            expects scores with shape ``(n_samples,)`` while the
            multiclass case expects scores with shape
            ``(n_samples, n_classes)``.
        k: The numbers of most likely outcomes considered to find the
            correct label.
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
    >>> from arkas.metric import top_k_accuracy
    >>> # binary
    >>> metrics = top_k_accuracy(
    ...     y_true=np.array([1, 0, 0, 1, 1]), y_score=np.array([2, -1, 0, 3, 1]), k=[1, 2]
    ... )
    >>> metrics
    {'count': 5, 'top_1_accuracy': 1.0, 'top_2_accuracy': 1.0}
    >>> # multiclass
    >>> metrics = top_k_accuracy(
    ...     y_true=np.array([0, 1, 2, 2]),
    ...     y_score=np.array(
    ...         [[0.5, 0.2, 0.2], [0.3, 0.4, 0.2], [0.2, 0.4, 0.3], [0.7, 0.2, 0.1]]
    ...     ),
    ...     k=[1, 2, 3],
    ... )
    >>> metrics
    {'count': 4, 'top_1_accuracy': 0.5, 'top_2_accuracy': 0.75, 'top_3_accuracy': 1.0}

    ```
    """
    if y_score.ndim == 1:
        return binary_top_k_accuracy(
            y_true=y_true.ravel(),
            y_score=y_score.ravel(),
            k=k,
            prefix=prefix,
            suffix=suffix,
            nan_policy=nan_policy,
        )
    return multiclass_top_k_accuracy(
        y_true=y_true,
        y_score=y_score,
        k=k,
        prefix=prefix,
        suffix=suffix,
        nan_policy=nan_policy,
    )


def binary_top_k_accuracy(
    y_true: np.ndarray,
    y_score: np.ndarray,
    *,
    k: Sequence[int] = (2,),
    prefix: str = "",
    suffix: str = "",
    nan_policy: str = "propagate",
) -> dict[str, float]:
    r"""Return the Area Under the Top-k Accuracy classification metrics
    for binary labels.

    Args:
        y_true: The ground truth target labels. This input must
            be an array of shape ``(n_samples,)``.
        y_score: The target scores, can either be probability
            estimates of the positive class, confidence values,
            or non-thresholded measure of decisions. This input must
            be an array of shape ``(n_samples,)``.
        k: The numbers of most likely outcomes considered to find the
            correct label.
        prefix: The key prefix in the returned dictionary.
        suffix: The key suffix in the returned dictionary.
        nan_policy: The policy on how to handle NaN values in the input
            arrays. The following options are available: ``'omit'``,
            ``'propagate'``, and ``'raise'``.

    Returns:
        The computed metrics.
    """
    y_true, y_score = preprocess_score_binary(
        y_true=y_true, y_score=y_score, drop_nan=nan_policy == "omit"
    )
    return _top_k_accuracy(
        y_true=y_true,
        y_score=y_score,
        k=k,
        prefix=prefix,
        suffix=suffix,
        nan_policy=nan_policy,
    )


def multiclass_top_k_accuracy(
    y_true: np.ndarray,
    y_score: np.ndarray,
    *,
    k: Sequence[int] = (2,),
    prefix: str = "",
    suffix: str = "",
    nan_policy: str = "propagate",
) -> dict[str, float | np.ndarray]:
    r"""Return the Area Under the Top-k Accuracy classification metrics
    for multiclass labels.

    Args:
        y_true: The ground truth target labels. This input must
            be an array of shape ``(n_samples,)``.
        y_score: The target scores, can either be probability
            estimates of the positive class, confidence values,
            or non-thresholded measure of decisions. This input must
            be an array of shape ``(n_samples, n_classes)``.
        k: The numbers of most likely outcomes considered to find the
            correct label.
        prefix: The key prefix in the returned dictionary.
        suffix: The key suffix in the returned dictionary.
        nan_policy: The policy on how to handle NaN values in the input
            arrays. The following options are available: ``'omit'``,
            ``'propagate'``, and ``'raise'``.

    Returns:
        The computed metrics.
    """
    y_true, y_score = preprocess_score_multiclass(y_true, y_score, drop_nan=nan_policy == "omit")
    return _top_k_accuracy(
        y_true=y_true,
        y_score=y_score,
        k=k,
        prefix=prefix,
        suffix=suffix,
        nan_policy=nan_policy,
    )


def _top_k_accuracy(
    y_true: np.ndarray,
    y_score: np.ndarray,
    *,
    k: Sequence[int] = (2,),
    prefix: str = "",
    suffix: str = "",
    nan_policy: str = "propagate",
) -> dict[str, float | np.ndarray]:
    r"""Return the Area Under the Top-k Accuracy classification metrics
    for multiclass labels.

    Args:
        y_true: The ground truth target labels. This input must
            be an array of shape ``(n_samples,)``.
        y_score: The target scores, can either be probability
            estimates of the positive class, confidence values,
            or non-thresholded measure of decisions. This input must
            be an array of shape ``(n_samples, n_classes)``.
        k: The numbers of most likely outcomes considered to find the
            correct label.
        prefix: The key prefix in the returned dictionary.
        suffix: The key suffix in the returned dictionary.
        nan_policy: The policy on how to handle NaN values in the input
            arrays. The following options are available: ``'omit'``,
            ``'propagate'``, and ``'raise'``.

    Returns:
        The computed metrics.
    """
    y_true_nan = contains_nan(arr=y_true, nan_policy=nan_policy, name="'y_true'")
    y_score_nan = contains_nan(arr=y_score, nan_policy=nan_policy, name="'y_score'")

    count = y_true.size
    out = {}
    for _k in k:
        top_k_accuracy = float("nan")
        if count > 0 and not y_true_nan and not y_score_nan:
            top_k_accuracy = float(
                metrics.top_k_accuracy_score(y_true=y_true, y_score=y_score, k=_k)
            )
        out[f"{prefix}top_{_k}_accuracy{suffix}"] = top_k_accuracy
    return {f"{prefix}count{suffix}": count} | out
