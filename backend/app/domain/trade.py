from dataclasses import dataclass, field
from datetime import date
from uuid import uuid4


@dataclass(frozen=True)
class Trade:
    asset_symbol: str
    trade_date: date
    side: str
    quantity: float
    price: float
    trade_id: str = field(default_factory=lambda: str(uuid4()))

    @property
    def value(self) -> float:
        return self.quantity * self.price
