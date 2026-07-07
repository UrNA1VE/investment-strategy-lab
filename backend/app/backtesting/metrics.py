from typing import Any


class MetricsCalculator:
    def calculate(self, backtest_result: dict[str, Any]) -> dict[str, Any]:
        return {
            "initial_capital": backtest_result.get("initial_capital"),
            "final_portfolio_value": None,
            "total_return": None,
            "max_drawdown": None,
            "trade_count": len(backtest_result.get("trades", [])),
        }
