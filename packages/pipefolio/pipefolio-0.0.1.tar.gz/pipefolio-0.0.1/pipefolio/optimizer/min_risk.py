from __future__ import annotations

from typing import TYPE_CHECKING

from skfolio.optimization import MeanRisk
from sklearn.base import BaseEstimator

from ..enums import OptimizeObjective, RiskMetric
from ..mixins import OptimizerPipeMixin

if TYPE_CHECKING:
    from ..data import DataPlaceHolder


class MinRiskOptimizer(OptimizerPipeMixin, BaseEstimator):
    """
    Optimizer that uses the MeanRisk optimization model from skfolio to minimize risk.

    The optimization model is initialized in the constructor and fit to the data
    using the `fit` method.

    Attributes:
        model: The MeanRisk optimization model.
    """

    def __init__(
        self,
        risk_metric: RiskMetric = RiskMetric.VARIANCE,
        min_weights: float | dict[str, float] = 0.0,
        max_weights: float | dict[str, float] = 1.0,
    ) -> None:
        """
        Initializes the MinRiskOptimizer with a MeanRisk model.

        Args:
            risk_metric: The risk metric to use.
            min_weights: The minimum weights for the optimization.
            max_weights: The maximum weights for the optimization.
        """
        self.model = MeanRisk(
            objective_function=OptimizeObjective.MINIMIZE_RISK.value,
            risk_measure=risk_metric.value,
            min_weights=min_weights,
            max_weights=max_weights,
        )

    def fit(self, X: DataPlaceHolder, y=None) -> MeanRisk:
        """
        Fits the MeanRisk model to the provided data.

        Args:
            X: The input data to fit the model.
            y: Optional additional data (unused).

        Returns:
            The fitted MinRiskOptimizer model.
        """
        return self.model.fit(X.price, y)

    def predict(self, X: DataPlaceHolder):
        """
        Predicts using the MeanRisk model with the provided data.

        Args:
            X: The input data for making predictions.

        Returns:
            The predictions made by the MeanRisk model.
        """
        return self.model.predict(X.price)
