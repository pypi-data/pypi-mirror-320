from __future__ import annotations

from typing import TYPE_CHECKING, Self

import empyrical as emp
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

from ..enums import SelectMode, DataPeriod
from ..mixins import SelectorPipeMixin

if TYPE_CHECKING:
    from ..data import DataPlaceHolder


class AnnualVolatilitySelector(SelectorPipeMixin, TransformerMixin, BaseEstimator):
    """Selector to choose assets based on their annualized volatility.

    This selector computes the annualized volatility of asset returns and selects
    the top or bottom `n` assets based on the specified selection mode.

    Attributes:
        n (int): Number of assets to select.
        mode (SelectMode): Selection mode to determine whether to select the largest or smallest volatilities.
    """

    def __init__(
        self,
        n: int,
        mode: SelectMode = SelectMode.SMALLEST,
    ) -> None:
        self.n = n
        self.mode = mode

    def _select(self, data: pd.DataFrame, period: DataPeriod) -> pd.Series:
        """Select assets based on annualized volatility.

        Args:
            data (pd.DataFrame): Input data containing price information.

        Returns:
            pd.Series: Selected assets indexed by asset identifiers.
        """
        ret = emp.simple_returns(data)
        ann_vol = emp.annual_volatility(returns=ret, period=period.value)
        assert isinstance(ann_vol, np.ndarray)
        ann_vol = pd.Series(data=ann_vol, index=data.columns)
        assert isinstance(ann_vol, pd.Series)

        match self.mode:
            case SelectMode.LARGEST:
                return ann_vol.nlargest(self.n)
            case SelectMode.SMALLEST:
                return ann_vol.nsmallest(self.n)

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
        """Transform the input data by selecting based on annual volatility.

        Args:
            X (DataPlaceHolder): The input data to transform.
            y: Optional additional data (unused).

        Returns:
            DataPlaceHolder: The transformed data with selected assets.
        """
        selected = self._select(X.price, X.period)
        data_ = X.select_symbols(selected.index.to_list())
        X_ = X.copy_with_new_data(data_)
        return X_
