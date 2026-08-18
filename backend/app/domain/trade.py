from dataclasses import dataclass, field
from datetime import date
from uuid import uuid4
from app.strategies.base import SignalAction

@dataclass(frozen=True)
class Trade:
    stock_name: str
    trade_date: date
    side: SignalAction
    quantity: float
    price: float
    trade_detail: str
    trade_id: str = field(default_factory=lambda: str(uuid4()))


    @property
    def value(self) -> float:
        return self.quantity * self.price
