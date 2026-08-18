from datetime import date
from operator import ge, le
from typing import Callable

from app.strategies.base import BaseStrategy, Signal, SignalAction


class BuyAndHoldStrategy(BaseStrategy):
    strategy_name = "buy_and_hold"

    def _buy_signal(self, stock_name, signal_date, price, quantity, reason: str) -> Signal:
        return Signal(
            stock_name=stock_name,
            signal_date=signal_date,
            action=SignalAction.BUY,
            price=price,
            quantity=quantity,
            reason=reason,
        )

    # def _hold_signal(self, stock_name, signal_date, price, quantity, reason: str = "No buy trigger.") -> Signal:
    #     return Signal(
    #         stock_name=stock_name,
    #         signal_date=signal_date,
    #         action=SignalAction.HOLD,
    #         price=price,
    #         quantity=quantity,
    #         reason=reason,
    #     )


class BuyAndHoldByDateStrategy(BuyAndHoldStrategy):
    strategy_name = "buy_and_hold_by_date"

    def __init__(
        self,
        stock,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> None:
        super().__init__(
            stock=stock,
            start_date=start_date,
            end_date=end_date,
            parameters={
                "start_date": start_date,
                "end_date": end_date,
            },
        )

    def generate_signals(self) -> list[Signal]:
        if self.stock.data.empty:
            return []

        strategy_start_date = self.start_date or self.stock.data.iloc[0].date.date()
        has_bought = False
        signals = []

        for row in self.stock.data.itertuples(index=False):
            row_date = row.date.date()
            if not has_bought and row_date >= strategy_start_date:
                signals.append(
                    self._buy_signal(
                        self.stock.stock_name,
                        row_date,
                        row.close,
                        1,
                        f"Buy on or after strategy start date {strategy_start_date.isoformat()}.",
                    )
                )
                has_bought = True

        return signals


class BuyAndHoldByPriceStrategy(BuyAndHoldStrategy):
    strategy_name = "buy_and_hold_by_price"

    OPERATORS: dict[str, Callable[[float, float], bool]] = {
        "below_or_equal": le,
        "above_or_equal": ge,
    }

    def __init__(
        self,
        stock,
        trigger_price: float,
        comparison: str = "below_or_equal",
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> None:
        if comparison not in self.OPERATORS:
            supported = ", ".join(sorted(self.OPERATORS))
            raise ValueError(f"Unsupported price comparison '{comparison}'. Use one of: {supported}.")

        super().__init__(
            stock=stock,
            start_date=start_date,
            end_date=end_date,
            parameters={
                "trigger_price": trigger_price,
                "comparison": comparison,
                "start_date": start_date,
                "end_date": end_date,
            }
        )
        self.trigger_price = trigger_price
        self.comparison = comparison

    def generate_signals(self) -> list[Signal]:
        compare = self.OPERATORS[self.comparison]
        has_bought = False
        signals = []

        for row in self.stock.data.itertuples(index=False):
            close_price = float(row.close)
            if not has_bought and compare(close_price, self.trigger_price):
                signals.append(
                    self._buy_signal(
                    self.stock.stock_name, row.date.date(), row.close, 1, 
                        f"Buy when close is {self.comparison} {self.trigger_price}.",
                    )
                )
                has_bought = True

        return signals


BuyAndHoldStrategy_TriggerByDate = BuyAndHoldByDateStrategy
