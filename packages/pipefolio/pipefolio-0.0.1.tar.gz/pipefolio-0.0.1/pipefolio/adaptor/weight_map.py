from __future__ import annotations

from typing import TYPE_CHECKING, Self

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.utils.validation import check_is_fitted

from ..mixins import AdaptorPipeMixin

if TYPE_CHECKING:
    from skfolio.optimization._base import BaseOptimization


class WeightMappingAdaptor(AdaptorPipeMixin, TransformerMixin, BaseEstimator):
    """Convert optimization result's weights to a dictionary mapping feature names to weights."""

    def fit(self, X: BaseOptimization, y=None) -> Self:
        """Fit the adaptor.

        Args:
            X: Optimization result.
            y: Unused.

        Returns:
            Self.
        """
        check_is_fitted(X, "feature_names_in_")
        return self

    def transform(self, X: BaseOptimization) -> dict[str, float]:
        """Transform the optimization result's weights to a dictionary mapping feature names to weights.

        Args:
            X: Optimization result.

        Returns:
            A dictionary mapping feature names to weights.
        """
        return dict(zip(X.feature_names_in_, X.weights_))  # type: ignore
