from dataclasses import dataclass, field


@dataclass
class Portfolio:
    initial_capital: float
    cash: float | None = None
    positions: dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.cash is None:
            self.cash = self.initial_capital

    def add_position(self, symbol: str, quantity: float) -> None:
        self.positions[symbol] = self.positions.get(symbol, 0.0) + quantity
