r"""Implement the F-beta metrics."""

from __future__ import annotations

__all__ = [
    "binary_fbeta_score",
    "fbeta_score",
    "multiclass_fbeta_score",
    "multilabel_fbeta_score",
]

from typing import TYPE_CHECKING

import numpy as np
from sklearn import metrics

from arkas.metric.classification.precision import find_label_type
from arkas.metric.utils import (
    check_label_type,
    contains_nan,
    preprocess_pred,
    preprocess_pred_multilabel,
)

if TYPE_CHECKING:
    from collections.abc import Sequence


def fbeta_score(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    *,
    betas: Sequence[float] = (1,),
    label_type: str = "auto",
    prefix: str = "",
    suffix: str = "",
    nan_policy: str = "propagate",
) -> dict[str, float | np.ndarray]:
    r"""Return the F-beta metrics.

    Args:
        y_true: The ground truth target labels. This input must
            be an array of shape ``(n_samples,)`` or
            ``(n_samples, n_classes)``.
        y_pred: The predicted labels. This input must be an array of
            shape ``(n_samples,)`` or ``(n_samples, n_classes)``.
        betas: The betas used to compute the F-beta scores.
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
    >>> from arkas.metric import fbeta_score
    >>> # auto
    >>> fbeta_score(y_true=np.array([1, 0, 0, 1, 1]), y_pred=np.array([1, 0, 0, 1, 1]))
    {'count': 5, 'f1': 1.0}
    >>> # binary
    >>> fbeta_score(
    ...     y_true=np.array([1, 0, 0, 1, 1]),
    ...     y_pred=np.array([1, 0, 0, 1, 1]),
    ...     label_type="binary",
    ... )
    {'count': 5, 'f1': 1.0}
    >>> # multiclass
    >>> fbeta_score(
    ...     y_true=np.array([0, 0, 1, 1, 2, 2]),
    ...     y_pred=np.array([0, 0, 1, 1, 2, 2]),
    ...     label_type="multiclass",
    ... )
    {'count': 6,
     'f1': array([1., 1., 1.]),
     'macro_f1': 1.0,
     'micro_f1': 1.0,
     'weighted_f1': 1.0}
    >>> # multilabel
    >>> fbeta_score(
    ...     y_true=np.array([[1, 0, 1], [0, 1, 0], [0, 1, 0], [1, 0, 1], [1, 0, 1]]),
    ...     y_pred=np.array([[1, 0, 1], [0, 1, 0], [0, 1, 0], [1, 0, 1], [1, 0, 1]]),
    ...     label_type="multilabel",
    ... )
    {'count': 5,
     'f1': array([1., 1., 1.]),
     'macro_f1': 1.0,
     'micro_f1': 1.0,
     'weighted_f1': 1.0}

    ```
    """
    check_label_type(label_type)
    if label_type == "auto":
        label_type = find_label_type(y_true=y_true, y_pred=y_pred)
    if label_type == "binary":
        return binary_fbeta_score(
            y_true=y_true.ravel(),
            y_pred=y_pred.ravel(),
            betas=betas,
            prefix=prefix,
            suffix=suffix,
            nan_policy=nan_policy,
        )
    if label_type == "multilabel":
        return multilabel_fbeta_score(
            y_true=y_true,
            y_pred=y_pred,
            betas=betas,
            prefix=prefix,
            suffix=suffix,
            nan_policy=nan_policy,
        )
    return multiclass_fbeta_score(
        y_true=y_true.ravel(),
        y_pred=y_pred.ravel(),
        betas=betas,
        prefix=prefix,
        suffix=suffix,
        nan_policy=nan_policy,
    )


def binary_fbeta_score(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    *,
    betas: Sequence[float] = (1,),
    prefix: str = "",
    suffix: str = "",
    nan_policy: str = "propagate",
) -> dict[str, float]:
    r"""Return the F-beta metrics for binary labels.

    Args:
        y_true: The ground truth target labels. This input must
            be an array of shape ``(n_samples,)``.
        y_pred: The predicted labels. This input must
            be an array of shape ``(n_samples,)``.
        betas: The betas used to compute the F-beta scores.
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
    >>> from arkas.metric import binary_fbeta_score
    >>> binary_fbeta_score(
    ...     y_true=np.array([1, 0, 0, 1, 1]),
    ...     y_pred=np.array([1, 0, 0, 1, 1]),
    ... )
    {'count': 5, 'f1': 1.0}

    ```
    """
    y_true, y_pred = preprocess_pred(
        y_true=y_true.ravel(), y_pred=y_pred.ravel(), drop_nan=nan_policy == "omit"
    )
    y_true_nan = contains_nan(arr=y_true, nan_policy=nan_policy, name="'y_true'")
    y_pred_nan = contains_nan(arr=y_pred, nan_policy=nan_policy, name="'y_pred'")

    count = y_true.size
    out = {f"{prefix}count{suffix}": count}
    for beta in betas:
        score = float("nan")
        if count > 0 and not y_true_nan and not y_pred_nan:
            score = float(metrics.fbeta_score(y_true=y_true, y_pred=y_pred, beta=beta))
        out[f"{prefix}f{beta}{suffix}"] = score
    return out


def multiclass_fbeta_score(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    *,
    betas: Sequence[float] = (1,),
    prefix: str = "",
    suffix: str = "",
    nan_policy: str = "propagate",
) -> dict[str, float]:
    r"""Return the F-beta metrics for multiclass labels.

    Args:
        y_true: The ground truth target labels. This input must
            be an array of shape ``(n_samples,)``.
        y_pred: The predicted labels. This input must
            be an array of shape ``(n_samples,)``.
        betas: The betas used to compute the F-beta scores.
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
    >>> from arkas.metric import multiclass_fbeta_score
    >>> multiclass_fbeta_score(
    ...     y_true=np.array([0, 0, 1, 1, 2, 2]),
    ...     y_pred=np.array([0, 0, 1, 1, 2, 2]),
    ... )
    {'count': 6,
     'f1': array([1., 1., 1.]),
     'macro_f1': 1.0,
     'micro_f1': 1.0,
     'weighted_f1': 1.0}

    ```
    """
    y_true, y_pred = preprocess_pred(
        y_true=y_true.ravel(), y_pred=y_pred.ravel(), drop_nan=nan_policy == "omit"
    )
    y_true_nan = contains_nan(arr=y_true, nan_policy=nan_policy, name="'y_true'")
    y_pred_nan = contains_nan(arr=y_pred, nan_policy=nan_policy, name="'y_pred'")

    n_samples = y_true.shape[0]
    out = {f"{prefix}count{suffix}": n_samples}
    for beta in betas:
        fbeta = np.array([])
        macro, micro, weighted = float("nan"), float("nan"), float("nan")
        if n_samples > 0 and not y_true_nan and not y_pred_nan:
            macro = metrics.fbeta_score(
                y_true=y_true, y_pred=y_pred, beta=beta, average="macro", zero_division=0.0
            )
            micro = metrics.fbeta_score(
                y_true=y_true, y_pred=y_pred, beta=beta, average="micro", zero_division=0.0
            )
            weighted = metrics.fbeta_score(
                y_true=y_true, y_pred=y_pred, beta=beta, average="weighted", zero_division=0.0
            )
            fbeta = np.asarray(
                metrics.fbeta_score(
                    y_true=y_true, y_pred=y_pred, beta=beta, average=None, zero_division=0.0
                )
            ).ravel()
        out |= {
            f"{prefix}f{beta}{suffix}": fbeta,
            f"{prefix}macro_f{beta}{suffix}": float(macro),
            f"{prefix}micro_f{beta}{suffix}": float(micro),
            f"{prefix}weighted_f{beta}{suffix}": float(weighted),
        }
    return out


def multilabel_fbeta_score(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    *,
    betas: Sequence[float] = (1,),
    prefix: str = "",
    suffix: str = "",
    nan_policy: str = "propagate",
) -> dict[str, float]:
    r"""Return the F-beta metrics for multilabel labels.

    Args:
        y_true: The ground truth target labels. This input must
            be an array of shape ``(n_samples,)``.
        y_pred: The predicted labels. This input must
            be an array of shape ``(n_samples,)``.
        betas: The betas used to compute the F-beta scores.
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
    >>> from arkas.metric import multilabel_fbeta_score
    >>> multilabel_fbeta_score(
    ...     y_true=np.array([[1, 0, 1], [0, 1, 0], [0, 1, 0], [1, 0, 1], [1, 0, 1]]),
    ...     y_pred=np.array([[1, 0, 1], [0, 1, 0], [0, 1, 0], [1, 0, 1], [1, 0, 1]]),
    ... )
    {'count': 5,
     'f1': array([1., 1., 1.]),
     'macro_f1': 1.0,
     'micro_f1': 1.0,
     'weighted_f1': 1.0}

    ```
    """
    y_true, y_pred = preprocess_pred_multilabel(y_true, y_pred, drop_nan=nan_policy == "omit")
    y_true_nan = contains_nan(arr=y_true, nan_policy=nan_policy, name="'y_true'")
    y_pred_nan = contains_nan(arr=y_pred, nan_policy=nan_policy, name="'y_pred'")

    n_samples = y_true.shape[0]
    out = {f"{prefix}count{suffix}": n_samples}
    for beta in betas:
        fbeta = np.array([])
        macro, micro, weighted = float("nan"), float("nan"), float("nan")
        if n_samples > 0 and not y_true_nan and not y_pred_nan:
            fbeta = np.array(
                metrics.fbeta_score(
                    y_true=y_true,
                    y_pred=y_pred,
                    beta=beta,
                    average="binary" if y_pred.shape[1] == 1 else None,
                )
            ).ravel()
            macro = metrics.fbeta_score(y_true=y_true, y_pred=y_pred, beta=beta, average="macro")
            micro = metrics.fbeta_score(y_true=y_true, y_pred=y_pred, beta=beta, average="micro")
            weighted = metrics.fbeta_score(
                y_true=y_true, y_pred=y_pred, beta=beta, average="weighted"
            )
        out |= {
            f"{prefix}f{beta}{suffix}": fbeta,
            f"{prefix}macro_f{beta}{suffix}": float(macro),
            f"{prefix}micro_f{beta}{suffix}": float(micro),
            f"{prefix}weighted_f{beta}{suffix}": float(weighted),
        }
    return out
