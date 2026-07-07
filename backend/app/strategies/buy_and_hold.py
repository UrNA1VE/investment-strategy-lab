from typing import Any

from app.strategies.base import BaseStrategy


class BuyAndHoldStrategy(BaseStrategy):
    strategy_name = "buy_and_hold"

    def generate_signals(self, price_data: Any) -> Any:
        return price_data
