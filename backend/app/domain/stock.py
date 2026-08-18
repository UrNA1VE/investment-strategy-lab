from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date
from typing import ClassVar

import pandas as pd
import yfinance as yf


class StockDataError(Exception):
    pass


@dataclass
class Stock(ABC):
    stock_name: str
    start_date: date
    end_date: date
    data_type: str = "daily"
    data: pd.DataFrame = field(init=False, repr=False)

    REQUIRED_COLUMNS: ClassVar[set[str]] = {
        "date",
        "open",
        "high",
        "low",
        "close",
        "adjusted_close",
        "volume",
    }

    def __post_init__(self) -> None:
        self.stock_name = self.stock_name.strip().upper()
        self._validate_inputs()
        self.data = self._load_data()

    @property
    @abstractmethod
    def yfinance_interval(self) -> str:
        raise NotImplementedError

    def to_records(self) -> list[dict]:
        records = []
        for row in self.data.itertuples(index=False):
            records.append(
                {
                    "date": row.date.date().isoformat(),
                    "open": float(row.open),
                    "high": float(row.high),
                    "low": float(row.low),
                    "close": float(row.close),
                    "adjusted_close": float(row.adjusted_close),
                    "volume": int(row.volume),
                }
            )
        return records

    def _validate_inputs(self) -> None:
        if not self.stock_name:
            raise ValueError("Stock name cannot be empty.")

        if self.start_date >= self.end_date:
            raise ValueError("Start date must be before end date.")

    def _load_data(self) -> pd.DataFrame:
        raw_data = yf.download(
            tickers=self.stock_name,
            start=self.start_date.isoformat(),
            end=self.end_date.isoformat(),
            interval=self.yfinance_interval,
            auto_adjust=False,
            progress=False,
            threads=False,
        )
        return self._clean_data(raw_data)

    def _clean_data(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        if raw_data.empty:
            raise StockDataError(f"No {self.data_type} data found for {self.stock_name}.")

        data = raw_data.copy()

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        data = data.reset_index()
        data.columns = [str(column).strip().lower().replace(" ", "_") for column in data.columns]
        data = data.rename(columns={"datetime": "date", "adj_close": "adjusted_close"})

        if "date" not in data.columns and "index" in data.columns:
            data = data.rename(columns={"index": "date"})

        missing_columns = self.REQUIRED_COLUMNS.difference(data.columns)
        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise StockDataError(f"Stock data is missing required columns: {missing}.")

        data["date"] = pd.to_datetime(data["date"])
        data = (
            data.drop_duplicates(subset=["date"])
            .sort_values("date")
            .dropna(subset=["open", "high", "low", "close", "adjusted_close"])
        )

        if data.empty:
            raise StockDataError(f"No valid {self.data_type} rows found for {self.stock_name}.")

        return data


class DailyStock(Stock):
    @property
    def yfinance_interval(self) -> str:
        return "1d"


class HourlyStock(Stock):
    @property
    def yfinance_interval(self) -> str:
        return "1h"


class StockFactory:
    STOCK_TYPES = {
        "daily": DailyStock,
        "hourly": HourlyStock,
    }

    @classmethod
    def create(
        cls,
        stock_name: str,
        start_date: date,
        end_date: date,
        data_type: str = "daily",
    ) -> Stock:
        normalized_type = data_type.strip().lower()
        stock_class = cls.STOCK_TYPES.get(normalized_type)

        if stock_class is None:
            supported_types = ", ".join(sorted(cls.STOCK_TYPES))
            raise ValueError(f"Unsupported stock data type '{data_type}'. Use one of: {supported_types}.")

        return stock_class(
            stock_name=stock_name,
            start_date=start_date,
            end_date=end_date,
            data_type=normalized_type,
        )
