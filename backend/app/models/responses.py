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
