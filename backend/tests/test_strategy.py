from datetime import date
from types import SimpleNamespace

import pandas as pd
import pytest

from app.strategies.base import SignalAction
from app.strategies.conditions import DateGapCondition, PriceCondition
from app.strategies.strategy import RuleStrategy, StrategyFactory


def fake_portfolio():
    return SimpleNamespace(cash=1000.0, positions={"AAPL": 10})


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


def test_rule_strategy_generates_buy_signal_when_date_condition_is_met() -> None:
    strategy = RuleStrategy(
        fake_stock(),
        fake_portfolio(),
        condition=DateGapCondition(gap=10),
        start_date=date(2024, 1, 3),
        parameters={
            "action": "BUY",
            "type": "fixed_shares",
            "unit": 1,
        },
    )

    signals = strategy.generate_signal(date(2024, 1, 3))

    assert len(signals) == 1
    assert signals[0].action == SignalAction.BUY
    assert signals[0].signal_date == date(2024, 1, 3)
    assert signals[0].price == 95.0


def test_rule_strategy_generates_sell_signal_when_date_condition_is_met() -> None:
    strategy = RuleStrategy(
        fake_stock(),
        fake_portfolio(),
        condition=DateGapCondition(gap=10),
        start_date=date(2024, 1, 3),
        parameters={
            "action": "SELL",
            "type": "fixed_shares",
            "unit": 2,
        },
    )

    signals = strategy.generate_signal(date(2024, 1, 3))

    assert len(signals) == 1
    assert signals[0].action == SignalAction.SELL
    assert signals[0].quantity == 2


def test_rule_strategy_uses_date_gap_condition_between_signals() -> None:
    strategy = RuleStrategy(
        fake_stock(),
        fake_portfolio(),
        condition=DateGapCondition(gap=2),
        parameters={
            "action": "BUY",
            "type": "fixed_shares",
            "unit": 1,
        },
    )

    signals = []
    for current_date in [date(2024, 1, 2), date(2024, 1, 3), date(2024, 1, 4)]:
        signals.extend(strategy.generate_signal(current_date))

    assert [signal.signal_date for signal in signals] == [
        date(2024, 1, 2),
        date(2024, 1, 4),
    ]


def test_date_gap_condition_requires_positive_integer_gap() -> None:
    with pytest.raises(ValueError, match="positive integer"):
        DateGapCondition(gap=0)


def test_rule_strategy_generates_buy_signal_when_price_condition_is_met() -> None:
    strategy = RuleStrategy(
        fake_stock(),
        fake_portfolio(),
        condition=PriceCondition(trigger_price=96.0),
        parameters={
            "action": "BUY",
            "type": "fixed_shares",
            "unit": 1,
        },
    )

    signals = strategy.generate_signal(date(2024, 1, 3))

    assert len(signals) == 1
    assert signals[0].action == SignalAction.BUY
    assert signals[0].signal_date == date(2024, 1, 3)
    assert signals[0].price == 95.0


def test_rule_strategy_generates_sell_signal_when_price_condition_is_met() -> None:
    strategy = RuleStrategy(
        fake_stock(),
        fake_portfolio(),
        condition=PriceCondition(trigger_price=105.0, comparison="above_or_equal"),
        parameters={
            "action": "SELL",
            "type": "fixed_shares",
            "unit": 3,
        },
    )

    signals = strategy.generate_signal(date(2024, 1, 4))

    assert len(signals) == 1
    assert signals[0].action == SignalAction.SELL
    assert signals[0].quantity == 3
    assert signals[0].price == 110.0


def test_cash_percent_uses_portfolio_cash_to_calculate_buy_quantity() -> None:
    strategy = RuleStrategy(
        fake_stock(),
        fake_portfolio(),
        condition=PriceCondition(trigger_price=100.0),
        parameters={
            "action": "BUY",
            "type": "cash_percent",
            "unit": 0.5,
        },
    )

    signals = strategy.generate_signal(date(2024, 1, 2))

    assert signals[0].quantity == 5


def test_position_percent_uses_portfolio_position_to_calculate_sell_quantity() -> None:
    strategy = RuleStrategy(
        fake_stock(),
        fake_portfolio(),
        condition=PriceCondition(trigger_price=105.0, comparison="above_or_equal"),
        parameters={
            "action": "SELL",
            "type": "position_percent",
            "unit": 0.5,
        },
    )

    signals = strategy.generate_signal(date(2024, 1, 4))

    assert signals[0].quantity == 5


def test_buy_action_cannot_use_position_percent() -> None:
    with pytest.raises(ValueError, match="BUY action cannot use position_percent"):
        RuleStrategy(
            fake_stock(),
            fake_portfolio(),
            condition=PriceCondition(trigger_price=100.0),
            parameters={
                "action": "BUY",
                "type": "position_percent",
                "unit": 0.5,
            },
        )


def test_sell_action_cannot_use_cash_percent() -> None:
    with pytest.raises(ValueError, match="SELL action cannot use cash_percent"):
        RuleStrategy(
            fake_stock(),
            fake_portfolio(),
            condition=PriceCondition(trigger_price=100.0),
            parameters={
                "action": "SELL",
                "type": "cash_percent",
                "unit": 0.5,
            },
        )


def test_strategy_factory_creates_rule_strategy_with_date_gap_condition() -> None:
    strategy = StrategyFactory.create(
        stock=fake_stock(),
        portfolio=fake_portfolio(),
        config={
            "condition": {
                "type": "date_gap",
                "gap": 10,
            },
            "action": "BUY",
            "sizing": {
                "type": "fixed_shares",
                "unit": 1,
            },
            "start_date": date(2024, 1, 3),
        },
    )

    signals = strategy.generate_signal(date(2024, 1, 3))

    assert isinstance(strategy, RuleStrategy)
    assert isinstance(strategy.condition, DateGapCondition)
    assert signals[0].action == SignalAction.BUY
    assert signals[0].signal_date == date(2024, 1, 3)


def test_strategy_factory_creates_rule_strategy_with_price_condition() -> None:
    strategy = StrategyFactory.create(
        stock=fake_stock(),
        portfolio=fake_portfolio(),
        config={
            "condition": {
                "type": "price",
                "trigger_price": 105.0,
                "comparison": "above_or_equal",
            },
            "action": "SELL",
            "sizing": {
                "type": "position_percent",
                "unit": 0.5,
            },
        },
    )

    signals = strategy.generate_signal(date(2024, 1, 4))

    assert isinstance(strategy.condition, PriceCondition)
    assert signals[0].action == SignalAction.SELL
    assert signals[0].quantity == 5


def test_strategy_factory_rejects_unknown_condition_type() -> None:
    with pytest.raises(ValueError, match="Unsupported condition type"):
        StrategyFactory.create(
            stock=fake_stock(),
            portfolio=fake_portfolio(),
            config={
                "condition": {
                    "type": "unknown",
                },
                "action": "BUY",
                "sizing": {
                    "type": "fixed_shares",
                    "unit": 1,
                },
            },
        )
