from datetime import date
from types import SimpleNamespace

import pandas as pd

from app.strategies.base import SignalAction
from app.strategies.buy_and_hold import BuyAndHoldByDateStrategy, BuyAndHoldByPriceStrategy


def fake_stock():
    return SimpleNamespace(
        stock_name="AAPL",
        data=pd.DataFrame(
            {
                "date": pd.to_datetime(["2024-01-02", "2024-01-03", "2024-01-04"]),
                "close": [100.0, 95.0, 110.0],
            }
        ),
    )


def test_buy_and_hold_by_date_buys_on_strategy_start_date() -> None:
    strategy = BuyAndHoldByDateStrategy(fake_stock(), start_date=date(2024, 1, 3))

    signals = strategy.generate_signals()

    assert len(signals) == 1
    assert signals[0].action == SignalAction.BUY
    assert signals[0].signal_date == date(2024, 1, 3)
    assert signals[0].price == 95.0


def test_buy_and_hold_by_date_buys_first_available_date_by_default() -> None:
    strategy = BuyAndHoldByDateStrategy(fake_stock())

    signals = strategy.generate_signals()

    assert signals[0].action == SignalAction.BUY
    assert signals[0].signal_date == date(2024, 1, 2)


def test_buy_and_hold_by_date_returns_no_signal_when_range_has_no_data() -> None:
    strategy = BuyAndHoldByDateStrategy(
        fake_stock(),
        start_date=date(2024, 2, 1),
        end_date=date(2024, 2, 28),
    )

    signals = strategy.generate_signals()

    assert signals == []


def test_buy_and_hold_by_price_buys_when_price_is_below_or_equal_trigger() -> None:
    strategy = BuyAndHoldByPriceStrategy(fake_stock(), trigger_price=96.0)

    signals = strategy.generate_signals()

    assert len(signals) == 1
    assert signals[0].action == SignalAction.BUY
    assert signals[0].signal_date == date(2024, 1, 3)
    assert signals[0].price == 95.0


def test_buy_and_hold_by_price_can_buy_when_price_is_above_or_equal_trigger() -> None:
    strategy = BuyAndHoldByPriceStrategy(fake_stock(), trigger_price=105.0, comparison="above_or_equal")

    signals = strategy.generate_signals()

    assert len(signals) == 1
    assert signals[0].action == SignalAction.BUY
    assert signals[0].signal_date == date(2024, 1, 4)
    assert signals[0].price == 110.0
