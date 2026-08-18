from datetime import date

import pandas as pd
import pytest

from app.domain.stock import DailyStock, HourlyStock, StockDataError, StockFactory


def fake_yfinance_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Date": pd.to_datetime(["2024-01-02", "2024-01-03"]),
            "Open": [100.0, 101.0],
            "High": [102.0, 103.0],
            "Low": [99.0, 100.0],
            "Close": [101.0, 102.0],
            "Adj Close": [100.5, 101.5],
            "Volume": [1000000, 1100000],
        }
    ).set_index("Date")


def test_daily_stock_loads_and_standardizes_yfinance_data(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = {}

    def fake_download(**kwargs):
        calls.update(kwargs)
        return fake_yfinance_data()

    monkeypatch.setattr("app.domain.stock.yf.download", fake_download)

    stock = DailyStock(
        stock_name="aapl",
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 5),
    )

    assert stock.stock_name == "AAPL"
    assert stock.data_type == "daily"
    assert calls["tickers"] == "AAPL"
    assert calls["interval"] == "1d"
    assert stock.to_records()[0] == {
        "date": "2024-01-02",
        "open": 100.0,
        "high": 102.0,
        "low": 99.0,
        "close": 101.0,
        "adjusted_close": 100.5,
        "volume": 1000000,
    }


def test_stock_factory_creates_hourly_stock(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.domain.stock.yf.download", lambda **kwargs: fake_yfinance_data())

    stock = StockFactory.create(
        stock_name="MSFT",
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 5),
        data_type="hourly",
    )

    assert isinstance(stock, HourlyStock)
    assert stock.yfinance_interval == "1h"


def test_stock_rejects_invalid_date_range(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.domain.stock.yf.download", lambda **kwargs: fake_yfinance_data())

    with pytest.raises(ValueError, match="Start date must be before end date"):
        DailyStock(
            stock_name="AAPL",
            start_date=date(2024, 1, 5),
            end_date=date(2024, 1, 1),
        )


def test_stock_rejects_empty_yfinance_data(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.domain.stock.yf.download", lambda **kwargs: pd.DataFrame())

    with pytest.raises(StockDataError, match="No daily data found"):
        DailyStock(
            stock_name="AAPL",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 5),
        )
