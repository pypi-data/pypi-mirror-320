from __future__ import annotations

from typing import TYPE_CHECKING, Self

import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

from ..enums import SelectMode
from ..mixins import SelectorPipeMixin

if TYPE_CHECKING:
    from ..data import DataPlaceHolder


class AverageTradeValueSelector(SelectorPipeMixin, TransformerMixin, BaseEstimator):
    """Selector to choose assets based on their average trade value.

    This selector computes the average trade value of asset returns and selects
    the top or bottom `n` assets based on the specified selection mode.

    Attributes:
        n (int): Number of assets to select.
        mode (SelectMode): Selection mode to determine whether to select the largest or smallest average trade values.
    """

    def __init__(self, n: int, mode: SelectMode = SelectMode.LARGEST) -> None:
        self.n = n
        self.mode = mode

    def _select(self, data: DataPlaceHolder) -> pd.Series:
        """Select assets based on average trade value.

        Args:
            data (DataPlaceHolder): Input data containing price information.

        Returns:
            pd.Series: Selected assets indexed by asset identifiers.
        """
        trade_val = data.close * data.volume
        avg_trade_val = trade_val.mean(axis=0)
        assert isinstance(avg_trade_val, pd.Series)

        match self.mode:
            case SelectMode.LARGEST:
                return avg_trade_val.nlargest(self.n)
            case SelectMode.SMALLEST:
                return avg_trade_val.nsmallest(self.n)

    def fit(self, X: DataPlaceHolder, y=None) -> Self:
        """Fit the selector.

        Args:
            X (DataPlaceHolder): The input data to fit.
            y: Optional additional data (unused).

        Returns:
            Self: The fitted selector.
        """
        return self

    def transform(self, X: DataPlaceHolder, y=None) -> DataPlaceHolder:
        """Transform the input data by selecting based on average trade value.

        Args:
            X (DataPlaceHolder): The input data to transform.
            y: Optional additional data (unused).

        Returns:
            DataPlaceHolder: The transformed data with selected assets.
        """
        selected = self._select(X)
        data_ = X.select_symbols(selected.index.to_list())
        X_ = X.copy_with_new_data(data_)
        return X_
