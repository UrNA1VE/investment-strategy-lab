from dataclasses import dataclass
from dataclasses import replace
from datetime import date
from enum import StrEnum


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
