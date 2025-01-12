from __future__ import annotations

from typing import TYPE_CHECKING, Self

import numpy as np
import numpy.typing as npt
from sklearn.base import BaseEstimator, TransformerMixin

from ..mixins import AdaptorPipeMixin

if TYPE_CHECKING:
    from skfolio.optimization._base import BaseOptimization


class WeightArrayAdaptor(AdaptorPipeMixin, TransformerMixin, BaseEstimator):
    """Adaptor to convert optimization result's weights to a numpy array.

    This adaptor is useful when the weights of the optimization result are
    needed as a numpy array for further processing.

    Attributes:
        None
    """

    def fit(self, X: BaseOptimization, y=None) -> Self:
        """Fit the WeightArrayAdaptor.

        Args:
            X: The optimization result.
            y: Unused.

        Returns:
            Self.
        """
        return self

    def transform(self, X: BaseOptimization) -> npt.NDArray[np.float64]:
        """Transform the optimization result's weights to a numpy array.

        Args:
            X: The optimization result.

        Returns:
            A numpy array of shape (n_features,) containing the weights.
        """
        return X.weights_
