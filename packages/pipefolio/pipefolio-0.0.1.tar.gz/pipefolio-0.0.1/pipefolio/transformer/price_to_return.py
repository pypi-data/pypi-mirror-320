from __future__ import annotations

from typing import TYPE_CHECKING, Self

import pandas as pd
from skfolio.preprocessing import prices_to_returns
from sklearn.base import BaseEstimator, TransformerMixin

from ..mixins import TransformerPipeMixin

if TYPE_CHECKING:
    from ..data import DataPlaceHolder


class PriceToReturnTransformer(TransformerPipeMixin, TransformerMixin, BaseEstimator):
    def __init__(self, log_returns: bool = False) -> None:
        """Initializes the transformer.

        Args:
            log_returns (bool): Whether to calculate log returns. Defaults to False.
        """
        self.log_returns = log_returns

    def fit(self, X: DataPlaceHolder, y=None) -> Self:
        """Fit the transformer.

        Args:
            X (DataPlaceHolder): The input data to fit.
            y: Optional additional data (unused).

        Returns:
            Self: The fitted transformer.
        """
        return self

    def transform(self, X: DataPlaceHolder) -> DataPlaceHolder:
        """Transform input data from prices to returns.

        Args:
            X (DataPlaceHolder): The input data to transform.

        Returns:
            DataPlaceHolder: The transformed data with returns instead of prices.
        """
        rets = prices_to_returns(X.data, log_returns=self.log_returns)
        assert isinstance(rets, pd.DataFrame)
        rets[X.ohlcv.volume] = X.volume  # revert volume
        return X.copy_with_new_data(rets)
