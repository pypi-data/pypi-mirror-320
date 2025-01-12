from __future__ import annotations

from typing import TYPE_CHECKING

from skfolio.optimization import EqualWeighted
from sklearn.base import BaseEstimator

from ..mixins import OptimizerPipeMixin

if TYPE_CHECKING:
    from ..data import DataPlaceHolder


class EqualWeightOptimizer(OptimizerPipeMixin, BaseEstimator):
    """Optimizer that uses the EqualWeighted optimization model from skfolio.

    This optimizer will use the EqualWeighted optimization model from skfolio to
    optimize the weights of the input data. The optimization model is initialized
    in the constructor and fit to the data using the `fit` method.
    """

    def __init__(self) -> None:
        """Initializes the EqualWeightOptimizer with an EqualWeighted model."""
        self.model = EqualWeighted()

    def fit(self, X: DataPlaceHolder, y=None) -> EqualWeighted:
        """Fits the EqualWeighted model to the provided data.

        Args:
            X (DataPlaceHolder): The input data to fit the model.
            y: Optional additional data (unused).

        Returns:
            EqualWeighted: The fitted EqualWeighted model.
        """
        return self.model.fit(X.price, y)

    def predict(self, X: DataPlaceHolder):
        """Predicts using the EqualWeighted model with the provided data.

        Args:
            X (DataPlaceHolder): The input data for making predictions.

        Returns:
            The predictions made by the EqualWeighted model.
        """
        return self.model.predict(X.price)
