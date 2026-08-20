from datetime import date

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str


class PriceBarResponse(BaseModel):
    date: date
    open: float
    high: float
    low: float
    close: float
    adjusted_close: float
    volume: int


class PriceDataResponse(BaseModel):
    stock_name: str
    start_date: date
    end_date: date
    data_type: str
    row_count: int
    prices: list[PriceBarResponse]


class DailyValueResponse(BaseModel):
    date: date
    cash: float
    positions_value: float
    total_value: float


class TradeResponse(BaseModel):
    stock_name: str
    trade_date: date
    side: str
    quantity: int
    price: float
    trade_detail: str


class BacktestResponse(BaseModel):
    # Response returned after the API runs the portfolio backtest.
    summary: dict
    daily_values: list[DailyValueResponse]
    trades: list[TradeResponse]
