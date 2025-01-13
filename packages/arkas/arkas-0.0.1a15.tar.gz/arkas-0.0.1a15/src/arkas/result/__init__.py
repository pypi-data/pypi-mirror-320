r"""Contain results."""

from __future__ import annotations

__all__ = [
    "AccuracyResult",
    "AveragePrecisionResult",
    "BalancedAccuracyResult",
    "BaseResult",
    "BinaryAveragePrecisionResult",
    "BinaryClassificationResult",
    "BinaryConfusionMatrixResult",
    "BinaryFbetaScoreResult",
    "BinaryJaccardResult",
    "BinaryPrecisionResult",
    "BinaryRecallResult",
    "BinaryRocAucResult",
    "EmptyResult",
    "EnergyDistanceResult",
    "JensenShannonDivergenceResult",
    "KLDivResult",
    "MappingResult",
    "MeanAbsoluteErrorResult",
    "MeanAbsolutePercentageErrorResult",
    "MeanSquaredErrorResult",
    "MeanSquaredLogErrorResult",
    "MeanTweedieDevianceResult",
    "MedianAbsoluteErrorResult",
    "MulticlassAveragePrecisionResult",
    "MulticlassConfusionMatrixResult",
    "MulticlassFbetaScoreResult",
    "MulticlassJaccardResult",
    "MulticlassPrecisionResult",
    "MulticlassRecallResult",
    "MulticlassRocAucResult",
    "MultilabelAveragePrecisionResult",
    "MultilabelConfusionMatrixResult",
    "MultilabelFbetaScoreResult",
    "MultilabelJaccardResult",
    "MultilabelPrecisionResult",
    "MultilabelRecallResult",
    "MultilabelRocAucResult",
    "PearsonCorrelationResult",
    "PrecisionResult",
    "R2ScoreResult",
    "RecallResult",
    "RegressionErrorResult",
    "Result",
    "RootMeanSquaredErrorResult",
    "SequentialResult",
    "SpearmanCorrelationResult",
    "WassersteinDistanceResult",
]

from arkas.result.accuracy import AccuracyResult
from arkas.result.ap import (
    AveragePrecisionResult,
    BinaryAveragePrecisionResult,
    MulticlassAveragePrecisionResult,
    MultilabelAveragePrecisionResult,
)
from arkas.result.balanced_accuracy import BalancedAccuracyResult
from arkas.result.base import BaseResult
from arkas.result.binary_classification import BinaryClassificationResult
from arkas.result.confmat import (
    BinaryConfusionMatrixResult,
    MulticlassConfusionMatrixResult,
    MultilabelConfusionMatrixResult,
)
from arkas.result.energy import EnergyDistanceResult
from arkas.result.fbeta import (
    BinaryFbetaScoreResult,
    MulticlassFbetaScoreResult,
    MultilabelFbetaScoreResult,
)
from arkas.result.jaccard import (
    BinaryJaccardResult,
    MulticlassJaccardResult,
    MultilabelJaccardResult,
)
from arkas.result.jensen_shannon import JensenShannonDivergenceResult
from arkas.result.kl import KLDivResult
from arkas.result.mae import MeanAbsoluteErrorResult
from arkas.result.mape import MeanAbsolutePercentageErrorResult
from arkas.result.mapping import MappingResult
from arkas.result.median_error import MedianAbsoluteErrorResult
from arkas.result.mse import MeanSquaredErrorResult
from arkas.result.msle import MeanSquaredLogErrorResult
from arkas.result.pearson import PearsonCorrelationResult
from arkas.result.precision import (
    BinaryPrecisionResult,
    MulticlassPrecisionResult,
    MultilabelPrecisionResult,
    PrecisionResult,
)
from arkas.result.r2 import R2ScoreResult
from arkas.result.recall import (
    BinaryRecallResult,
    MulticlassRecallResult,
    MultilabelRecallResult,
    RecallResult,
)
from arkas.result.regression import RegressionErrorResult
from arkas.result.rmse import RootMeanSquaredErrorResult
from arkas.result.roc_auc import (
    BinaryRocAucResult,
    MulticlassRocAucResult,
    MultilabelRocAucResult,
)
from arkas.result.sequential import SequentialResult
from arkas.result.spearman import SpearmanCorrelationResult
from arkas.result.tweedie_deviance import MeanTweedieDevianceResult
from arkas.result.vanilla import EmptyResult, Result
from arkas.result.wasserstein import WassersteinDistanceResult
