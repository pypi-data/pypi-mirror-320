from __future__ import annotations

from collections import namedtuple
from collections.abc import Iterable
from typing import Self

import pandas as pd
from pydantic import ConfigDict, Field
from pydantic.dataclasses import dataclass

from .enums import DataColumn, DataPeriod

OHLCV = namedtuple("OHLCV", ["open", "high", "low", "close", "volume"])


@dataclass(config=ConfigDict(arbitrary_types_allowed=True, frozen=True))
class DataPlaceHolder:
    """A placeholder for financial data with OHLCV structure.

    Attributes:
        data: A pandas DataFrame containing financial data.
        symbols: A list of asset symbols.
        ohlcv: An OHLCV namedtuple mapping data columns.
        period: The data period (e.g., daily, weekly).
        start: The start timestamp of the data.
        end: The end timestamp of the data.
        price_col: The column to use as price data.
    """

    data: pd.DataFrame
    symbols: list[str]
    ohlcv: OHLCV
    period: DataPeriod
    start: pd.Timestamp
    end: pd.Timestamp
    price_col: DataColumn = Field(default=DataColumn.CLOSE)

    @classmethod
    def from_dataframe(
        cls,
        data: pd.DataFrame,
        ohlcv: OHLCV = OHLCV("Open", "High", "Low", "Close", "Volume"),
        period: DataPeriod = DataPeriod.DAILY,
        price_col: DataColumn = DataColumn.CLOSE,
    ) -> Self:
        """Create a DataPlaceHolder from a DataFrame.

        Args:
            data: A pandas DataFrame with a MultiIndex for columns.
            ohlcv: An OHLCV namedtuple to map data columns.
            period: The data period.
            price_col: The column to use as price data.

        Returns:
            A DataPlaceHolder instance.
        """
        assert isinstance(data.columns, pd.MultiIndex)
        return cls(
            data=data,
            symbols=data.columns.get_level_values(1).unique().to_list(),
            ohlcv=ohlcv,
            period=period,
            start=pd.Timestamp(data.index[0]),
            end=pd.Timestamp(data.index[-1]),
            price_col=price_col,
        )

    @property
    def open(self) -> pd.DataFrame:
        """Get the open prices."""
        return self.data[self.ohlcv.open]

    @property
    def high(self) -> pd.DataFrame:
        """Get the high prices."""
        return self.data[self.ohlcv.high]

    @property
    def low(self) -> pd.DataFrame:
        """Get the low prices."""
        return self.data[self.ohlcv.low]

    @property
    def close(self) -> pd.DataFrame:
        """Get the close prices."""
        return self.data[self.ohlcv.close]

    @property
    def volume(self) -> pd.DataFrame:
        """Get the volume data."""
        return self.data[self.ohlcv.volume]

    @property
    def price(self) -> pd.DataFrame:
        """Get the selected price column based on `price_col`.

        Returns:
            The DataFrame for the selected price column.
        """
        match self.price_col:
            case DataColumn.OPEN:
                return self.open
            case DataColumn.HIGH:
                return self.high
            case DataColumn.LOW:
                return self.low
            case DataColumn.CLOSE:
                return self.close
            case DataColumn.VOLUME:
                return self.volume
            case _:
                raise NotImplementedError

    def select_symbols(self, symbols: Iterable[str]) -> pd.DataFrame:
        """Select data for specific symbols.

        Args:
            symbols: An iterable of asset symbols.

        Returns:
            A DataFrame with data for the specified symbols.
        """
        idx = pd.IndexSlice[:, symbols]  # type: ignore
        return self.data.loc[:, idx]

    def copy_with_new_data(self, data: pd.DataFrame) -> DataPlaceHolder:
        """Create a copy of the instance with new data.

        Args:
            data: A pandas DataFrame with new data.

        Returns:
            A new DataPlaceHolder instance with the updated data.
        """
        return DataPlaceHolder.from_dataframe(
            data, ohlcv=self.ohlcv, period=self.period, price_col=self.price_col
        )
