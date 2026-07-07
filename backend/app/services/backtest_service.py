from typing import Any

from app.backtesting.engine import BacktestEngine
from app.backtesting.metrics import MetricsCalculator
from app.strategies.base import BaseStrategy


class BacktestService:
    def __init__(
        self,
        engine: BacktestEngine | None = None,
        metrics_calculator: MetricsCalculator | None = None,
    ) -> None:
        self.engine = engine or BacktestEngine()
        self.metrics_calculator = metrics_calculator or MetricsCalculator()

    def run_backtest(
        self,
        price_data: Any,
        strategy: BaseStrategy,
        initial_capital: float,
    ) -> dict[str, Any]:
        signals = strategy.generate_signals(price_data)
        result = self.engine.run(price_data, signals, initial_capital)
        return {
            "result": result,
            "metrics": self.metrics_calculator.calculate(result),
        }
