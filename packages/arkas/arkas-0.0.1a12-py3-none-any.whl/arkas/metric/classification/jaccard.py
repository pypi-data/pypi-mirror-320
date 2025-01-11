r"""Implement the Jaccard metrics."""

from __future__ import annotations

__all__ = [
    "binary_jaccard",
    "jaccard",
    "multiclass_jaccard",
    "multilabel_jaccard",
]


import numpy as np
from sklearn import metrics

from arkas.metric.classification.precision import find_label_type
from arkas.metric.utils import (
    check_label_type,
    contains_nan,
    preprocess_pred,
    preprocess_pred_multilabel,
)


def jaccard(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    *,
    label_type: str = "auto",
    prefix: str = "",
    suffix: str = "",
    nan_policy: str = "propagate",
) -> dict[str, float | np.ndarray]:
    r"""Return the Jaccard metrics.

    Args:
        y_true: The ground truth target labels. This input must
            be an array of shape ``(n_samples,)`` or
            ``(n_samples, n_classes)``.
        y_pred: The predicted labels. This input must be an array of
            shape ``(n_samples,)`` or ``(n_samples, n_classes)``.
        label_type: The type of labels used to evaluate the metrics.
            The valid values are: ``'binary'``, ``'multiclass'``,
            and ``'multilabel'``. If ``'binary'`` or ``'multilabel'``,
            ``y_true`` values  must be ``0`` and ``1``.
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
    >>> from arkas.metric import jaccard
    >>> # auto
    >>> jaccard(y_true=np.array([1, 0, 0, 1, 1]), y_pred=np.array([1, 0, 0, 1, 1]))
    {'count': 5, 'jaccard': 1.0}
    >>> # binary
    >>> jaccard(
    ...     y_true=np.array([1, 0, 0, 1, 1]),
    ...     y_pred=np.array([1, 0, 0, 1, 1]),
    ...     label_type="binary",
    ... )
    {'count': 5, 'jaccard': 1.0}
    >>> # multiclass
    >>> jaccard(
    ...     y_true=np.array([0, 0, 1, 1, 2, 2]),
    ...     y_pred=np.array([0, 0, 1, 1, 2, 2]),
    ...     label_type="multiclass",
    ... )
    {'count': 6,
     'jaccard': array([1., 1., 1.]),
     'macro_jaccard': 1.0,
     'micro_jaccard': 1.0,
     'weighted_jaccard': 1.0}
    >>> # multilabel
    >>> jaccard(
    ...     y_true=np.array([[1, 0, 1], [0, 1, 0], [0, 1, 0], [1, 0, 1], [1, 0, 1]]),
    ...     y_pred=np.array([[1, 0, 1], [0, 1, 0], [0, 1, 0], [1, 0, 1], [1, 0, 1]]),
    ...     label_type="multilabel",
    ... )
    {'count': 5,
     'jaccard': array([1., 1., 1.]),
     'macro_jaccard': 1.0,
     'micro_jaccard': 1.0,
     'weighted_jaccard': 1.0}

    ```
    """
    check_label_type(label_type)
    if label_type == "auto":
        label_type = find_label_type(y_true=y_true, y_pred=y_pred)
    if label_type == "binary":
        return binary_jaccard(
            y_true=y_true, y_pred=y_pred, prefix=prefix, suffix=suffix, nan_policy=nan_policy
        )
    if label_type == "multilabel":
        return multilabel_jaccard(
            y_true=y_true, y_pred=y_pred, prefix=prefix, suffix=suffix, nan_policy=nan_policy
        )
    return multiclass_jaccard(
        y_true=y_true, y_pred=y_pred, prefix=prefix, suffix=suffix, nan_policy=nan_policy
    )


def binary_jaccard(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    *,
    prefix: str = "",
    suffix: str = "",
    nan_policy: str = "propagate",
) -> dict[str, float]:
    r"""Return the Jaccard metrics for binary labels.

    Args:
        y_true: The ground truth target labels. This input must
            be an array of shape ``(n_samples,)``.
        y_pred: The predicted labels. This input must
            be an array of shape ``(n_samples,)``.
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
    >>> from arkas.metric import binary_jaccard
    >>> binary_jaccard(y_true=np.array([1, 0, 0, 1, 1]), y_pred=np.array([1, 0, 0, 1, 1]))
    {'count': 5, 'jaccard': 1.0}

    ```
    """
    y_true, y_pred = preprocess_pred(
        y_true=y_true.ravel(), y_pred=y_pred.ravel(), drop_nan=nan_policy == "omit"
    )
    y_true_nan = contains_nan(arr=y_true, nan_policy=nan_policy, name="'y_true'")
    y_pred_nan = contains_nan(arr=y_pred, nan_policy=nan_policy, name="'y_pred'")

    count, score = y_true.size, float("nan")
    if count > 0 and not y_true_nan and not y_pred_nan:
        score = float(metrics.jaccard_score(y_true=y_true, y_pred=y_pred))
    return {f"{prefix}count{suffix}": count, f"{prefix}jaccard{suffix}": score}


def multiclass_jaccard(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    *,
    prefix: str = "",
    suffix: str = "",
    nan_policy: str = "propagate",
) -> dict[str, float | np.ndarray]:
    r"""Return the Jaccard metrics for multiclass labels.

    Args:
        y_true: The ground truth target labels. This input must
            be an array of shape ``(n_samples,)``.
        y_pred: The predicted labels. This input must
            be an array of shape ``(n_samples,)``.
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
    >>> from arkas.metric import multiclass_jaccard
    >>> multiclass_jaccard(
    ...     y_true=np.array([0, 0, 1, 1, 2, 2]), y_pred=np.array([0, 0, 1, 1, 2, 2])
    ... )
    {'count': 6,
     'jaccard': array([1., 1., 1.]),
     'macro_jaccard': 1.0,
     'micro_jaccard': 1.0,
     'weighted_jaccard': 1.0}

    ```
    """
    y_true, y_pred = preprocess_pred(
        y_true=y_true.ravel(), y_pred=y_pred.ravel(), drop_nan=nan_policy == "omit"
    )
    y_true_nan = contains_nan(arr=y_true, nan_policy=nan_policy, name="'y_true'")
    y_pred_nan = contains_nan(arr=y_pred, nan_policy=nan_policy, name="'y_pred'")

    per_class = np.array([])
    macro, micro, weighted = float("nan"), float("nan"), float("nan")
    n_samples = y_true.shape[0]
    if n_samples > 0 and not y_true_nan and not y_pred_nan:
        macro = metrics.jaccard_score(
            y_true=y_true, y_pred=y_pred, average="macro", zero_division=0.0
        )
        micro = metrics.jaccard_score(
            y_true=y_true, y_pred=y_pred, average="micro", zero_division=0.0
        )
        weighted = metrics.jaccard_score(
            y_true=y_true, y_pred=y_pred, average="weighted", zero_division=0.0
        )
        per_class = np.asarray(
            metrics.jaccard_score(y_true=y_true, y_pred=y_pred, average=None, zero_division=0.0)
        ).ravel()
    return {
        f"{prefix}count{suffix}": n_samples,
        f"{prefix}jaccard{suffix}": per_class,
        f"{prefix}macro_jaccard{suffix}": float(macro),
        f"{prefix}micro_jaccard{suffix}": float(micro),
        f"{prefix}weighted_jaccard{suffix}": float(weighted),
    }


def multilabel_jaccard(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    *,
    prefix: str = "",
    suffix: str = "",
    nan_policy: str = "propagate",
) -> dict[str, float | np.ndarray]:
    r"""Return the Jaccard metrics for multilabel labels.

    Args:
        y_true: The ground truth target labels. This input must
            be an array of shape ``(n_samples, n_classes)``.
        y_pred: The predicted labels. This input must
            be an array of shape ``(n_samples, n_classes)``.
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
    >>> from arkas.metric import multilabel_jaccard
    >>> multilabel_jaccard(
    ...     y_true=np.array([[1, 0, 1], [0, 1, 0], [0, 1, 0], [1, 0, 1], [1, 0, 1]]),
    ...     y_pred=np.array([[1, 0, 1], [0, 1, 0], [0, 1, 0], [1, 0, 1], [1, 0, 1]]),
    ... )
    {'count': 5,
     'jaccard': array([1., 1., 1.]),
     'macro_jaccard': 1.0,
     'micro_jaccard': 1.0,
     'weighted_jaccard': 1.0}

    ```
    """
    y_true, y_pred = preprocess_pred_multilabel(y_true, y_pred, drop_nan=nan_policy == "omit")
    y_true_nan = contains_nan(arr=y_true, nan_policy=nan_policy, name="'y_true'")
    y_pred_nan = contains_nan(arr=y_pred, nan_policy=nan_policy, name="'y_pred'")

    per_class = np.array([])
    macro, micro, weighted = float("nan"), float("nan"), float("nan")
    n_samples = y_true.shape[0]
    if n_samples > 0 and not y_true_nan and not y_pred_nan:
        per_class = np.array(
            metrics.jaccard_score(
                y_true=y_true,
                y_pred=y_pred,
                average="binary" if y_pred.shape[1] == 1 else None,
            )
        ).ravel()
        macro = metrics.jaccard_score(y_true=y_true, y_pred=y_pred, average="macro")
        micro = metrics.jaccard_score(y_true=y_true, y_pred=y_pred, average="micro")
        weighted = metrics.jaccard_score(y_true=y_true, y_pred=y_pred, average="weighted")

    return {
        f"{prefix}count{suffix}": n_samples,
        f"{prefix}jaccard{suffix}": per_class,
        f"{prefix}macro_jaccard{suffix}": float(macro),
        f"{prefix}micro_jaccard{suffix}": float(micro),
        f"{prefix}weighted_jaccard{suffix}": float(weighted),
    }
