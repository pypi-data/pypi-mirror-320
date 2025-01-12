from __future__ import annotations

from typing import TYPE_CHECKING

from deprecated import deprecated
from skfolio.optimization import MeanRisk
from sklearn.base import BaseEstimator

from ..enums import OptimizeObjective, RiskMetric
from ..mixins import OptimizerPipeMixin

if TYPE_CHECKING:
    from ..data import DataPlaceHolder


@deprecated(
    version="0.0.1",
    reason="Use MaxReturnOptimizer, MinRiskOptimizer or RiskAverseOptimizer instead",
)
class MeanRiskOptimizer(OptimizerPipeMixin, BaseEstimator):
    """Optimizer using the MeanRisk model.

    This class is deprecated. Use MaxReturnOptimizer, MinRiskOptimizer, or
    RiskAverseOptimizer instead.

    Attributes:
        model: The MeanRisk optimization model.

    Args:
        objective: The optimization objective.
        risk_metric: The risk metric to use.
        risk_aversion: The level of risk aversion.
        min_weights: The minimum weights for the optimization.
        max_weights: The maximum weights for the optimization.
    """

    def __init__(
        self,
        objective: OptimizeObjective = OptimizeObjective.MINIMIZE_RISK,
        risk_metric: RiskMetric = RiskMetric.VARIANCE,
        risk_aversion: float = 1.0,
        min_weights: float | dict[str, float] = 0.0,
        max_weights: float | dict[str, float] = 1.0,
    ) -> None:
        self.model = MeanRisk(
            objective_function=objective.value,
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
            The fitted MeanRisk model.
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
