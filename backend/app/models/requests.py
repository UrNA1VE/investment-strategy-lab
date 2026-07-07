from datetime import date

from pydantic import BaseModel, Field


class BacktestRequest(BaseModel):
    ticker: str = Field(min_length=1, examples=["AAPL"])
    start_date: date
    end_date: date
    initial_capital: float = Field(gt=0, examples=[10000])
    strategy_name: str = Field(default="buy_and_hold")
    parameters: dict = Field(default_factory=dict)
