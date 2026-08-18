from abc import ABC, abstractmethod
from copy import copy
from dataclasses import dataclass
from dataclasses import replace
from datetime import date
from enum import StrEnum
from typing import Any


class SignalAction(StrEnum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    INVALID = "INVALID"


@dataclass(frozen=True)
class Signal:
    stock_name: str
    signal_date: date
    action: SignalAction
    price: float
    quantity: int
    reason: str
    strategy_name: str = ""

    @property
    def value(self) -> float:
        return self.quantity * self.price

    def with_strategy_name(self, strategy_name: str) -> "Signal":
        return replace(self, strategy_name=strategy_name)


class BaseStrategy(ABC):
    strategy_name: str

    def __init__(
        self,
        stock: Any,
        start_date: date | None = None,
        end_date: date | None = None,
        parameters: dict | None = None,
    ) -> None:
        self.stock = stock
        self.start_date = start_date
        self.end_date = end_date
        self.parameters = parameters or {}
        self.stock = self.filter_stock_by_strategy_dates(stock)

    def filter_stock_by_strategy_dates(self, stock: Any):
        filtered_stock = copy(stock)
        data = stock.data

        if self.start_date is not None:
            data = data[data["date"].dt.date >= self.start_date]

        if self.end_date is not None:
            data = data[data["date"].dt.date <= self.end_date]

        filtered_stock.data = data
        return filtered_stock

    @abstractmethod
    def generate_signals(self) -> list[Signal]:
        raise NotImplementedError
