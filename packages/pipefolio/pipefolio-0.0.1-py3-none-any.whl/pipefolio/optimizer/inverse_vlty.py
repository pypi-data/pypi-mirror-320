from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from skfolio.optimization import InverseVolatility
from sklearn.base import BaseEstimator

from ..mixins import OptimizerPipeMixin

if TYPE_CHECKING:
    from ..data import DataPlaceHolder


class InverseVolatilityOptimizer(OptimizerPipeMixin, BaseEstimator):
    """Optimizer that uses the Inverse Volatility optimization model from skfolio.

    This optimizer utilizes the Inverse Volatility optimization model to
    allocate weights inversely proportional to the volatility of the assets.

    Attributes:
        model: An instance of the InverseVolatility optimization model.
    """

    def __init__(self) -> None:
        """Initializes the InverseVolatilityOptimizer with an InverseVolatility model."""
        self.model = InverseVolatility()

    def fit(self, X: DataPlaceHolder, y=None) -> InverseVolatility:
        """Fit the InverseVolatility model to the provided data.

        Args:
            X (DataPlaceHolder): The input data to fit the model.
            y: Optional additional data (unused).

        Returns:
            InverseVolatility: The fitted InverseVolatility model.
        """
        self.model.fit(X.price, y)
        setattr(self.model, "feature_names_in_", np.array(X.symbols, dtype=object))
        return self.model

    def predict(self, X: DataPlaceHolder):
        """Predict using the InverseVolatility model with the provided data.

        Args:
            X (DataPlaceHolder): The input data for making predictions.

        Returns:
            The predictions made by the InverseVolatility model.
        """
        return self.model.predict(X.price)
