from __future__ import annotations

from typing import TYPE_CHECKING

from skfolio.optimization import MeanRisk
from sklearn.base import BaseEstimator

from ..enums import OptimizeObjective, RiskMetric
from ..mixins import OptimizerPipeMixin

if TYPE_CHECKING:
    from ..data import DataPlaceHolder


class RiskAverseOptimizer(OptimizerPipeMixin, BaseEstimator):
    """
    Optimizer that uses the MeanRisk optimization model to maximize utility
    while considering risk aversion.

    The optimization model is initialized in the constructor and fit to the data
    using the `fit` method.

    Attributes:
        model: The MeanRisk optimization model.

    Args:
        risk_metric: The risk metric to use for optimization.
        risk_aversion: The level of risk aversion in the optimization.
        min_weights: The minimum weights for the optimization.
        max_weights: The maximum weights for the optimization.
    """

    def __init__(
        self,
        risk_metric: RiskMetric = RiskMetric.VARIANCE,
        risk_aversion: float = 1.0,
        min_weights: float | dict[str, float] = 0.0,
        max_weights: float | dict[str, float] = 1.0,
    ) -> None:
        self.model = MeanRisk(
            objective_function=OptimizeObjective.MAXIMIZE_UTILITY.value,
            risk_measure=risk_metric.value,
            risk_aversion=risk_aversion,
            min_weights=min_weights,
            max_weights=max_weights,
        )

    def fit(self, X: DataPlaceHolder, y=None) -> MeanRisk:
        """Fits the MeanRisk model to the provided data.

        Args:
            X: The input data to fit the model.
            y: Optional additional data (unused).

        Returns:
            The fitted RiskAverseOptimizer model.
        """
        return self.model.fit(X.price, y)

    def predict(self, X: DataPlaceHolder):
        """Predicts using the MeanRisk model with the provided data.

        Args:
            X: The input data for making predictions.

        Returns:
            The predictions made by the MeanRisk model.
        """
        return self.model.predict(X.price)
