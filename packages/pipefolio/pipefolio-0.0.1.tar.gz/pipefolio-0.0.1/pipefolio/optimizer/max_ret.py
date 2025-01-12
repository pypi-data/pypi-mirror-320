from __future__ import annotations

from typing import TYPE_CHECKING

from skfolio.optimization import MeanRisk
from sklearn.base import BaseEstimator

from ..enums import OptimizeObjective
from ..mixins import OptimizerPipeMixin

if TYPE_CHECKING:
    from ..data import DataPlaceHolder


class MaxReturnOptimizer(OptimizerPipeMixin, BaseEstimator):
    """Optimizer that uses the MeanRisk optimization model to maximize return.

    The optimization model is initialized in the constructor and fit to the data
    using the `fit` method.

    Attributes:
        model: The MeanRisk optimization model.
    """

    def __init__(
        self,
        min_weights: float | dict[str, float] = 0.0,
        max_weights: float | dict[str, float] = 1.0,
    ) -> None:
        """Initializes the MaxReturnOptimizer with a MeanRisk model.

        Args:
            min_weights: The minimum weights for the optimization.
            max_weights: The maximum weights for the optimization.
        """
        self.model = MeanRisk(
            objective_function=OptimizeObjective.MAXIMIZE_RETURN.value,
            min_weights=min_weights,
            max_weights=max_weights,
        )

    def fit(self, X: DataPlaceHolder, y=None) -> MeanRisk:
        """Fits the MeanRisk model to the provided data.

        Args:
            X: The input data to fit the model.
            y: Optional additional data (unused).

        Returns:
            The fitted MaxReturnOptimizer model.
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
