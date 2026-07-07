from typing import Any


class BacktestEngine:
    def run(self, price_data: Any, signals: Any, initial_capital: float) -> dict[str, Any]:
        return {
            "initial_capital": initial_capital,
            "price_data": price_data,
            "signals": signals,
            "equity_curve": [],
            "trades": [],
        }
