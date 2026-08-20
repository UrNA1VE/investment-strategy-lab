from datetime import date

from pydantic import BaseModel, Field


class ConditionConfig(BaseModel):
    # Defines when a strategy rule should trigger.
    type: str = Field(examples=["price", "date_gap"])
    trigger_price: float | None = Field(default=None, examples=[100.0])
    comparison: str | None = Field(default=None, examples=["below_or_equal"])
    gap: int | None = Field(default=None, examples=[10])


class SizingConfig(BaseModel):
    # Defines how many shares the strategy should buy or sell.
    type: str = Field(examples=["fixed_shares", "cash_percent", "position_percent"])
    unit: int | float = Field(examples=[1, 0.5])


class StrategyConfig(BaseModel):
    # A user-defined trading rule: condition + action + sizing.
    name: str = Field(min_length=1, examples=["buy_when_price_is_low"])
    condition: ConditionConfig
    action: str = Field(examples=["BUY", "SELL"])
    sizing: SizingConfig
    start_date: date | None = None
    end_date: date | None = None


class BacktestRequest(BaseModel):
    # Main request body for running one portfolio backtest.
    ticker: str = Field(min_length=1, examples=["AAPL"])
    start_date: date
    end_date: date
    initial_capital: float = Field(gt=0, examples=[10000])
    data_type: str = Field(default="daily", examples=["daily"])
    strategies: list[StrategyConfig] = Field(default_factory=list)
