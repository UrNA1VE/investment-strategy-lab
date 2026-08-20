from datetime import date
from types import SimpleNamespace

import pandas as pd

from app.domain.portfolio import Portfolio
from app.strategies.base import SignalAction
from app.strategies.conditions import DateGapCondition, PriceCondition
from app.strategies.strategy import RuleStrategy


def fake_stock():
    return SimpleNamespace(
        stock_name="AAPL",
        data=pd.DataFrame(
            {
                "date": pd.to_datetime(["2024-01-02"]),
                "close": [100.0],
            }
        ),
    )


def fake_stock_with_dates(dates: list[str], prices: list[float]):
    return SimpleNamespace(
        stock_name="AAPL",
        data=pd.DataFrame(
            {
                "date": pd.to_datetime(dates),
                "close": prices,
            }
        ),
    )


def test_portfolio_strategy_adds_user_strategy_name_to_signals() -> None:
    portfolio = Portfolio(initial_capital=1000, cash=1000)
    strategy = RuleStrategy(
        fake_stock(),
        portfolio,
        condition=DateGapCondition(gap=1),
        parameters={
            "action": "BUY",
            "type": "fixed_shares",
            "unit": 1,
        },
    )

    portfolio.add_strategy("strategy1", strategy)

    signals = portfolio.strategies["strategy1"].generate_signal(date(2024, 1, 2))

    assert signals[0].strategy_name == "strategy1"
    assert signals[0].action == SignalAction.BUY


def test_portfolio_action_uses_signal_strategy_name() -> None:
    portfolio = Portfolio(initial_capital=1000, cash=1000)
    strategy = RuleStrategy(
        fake_stock(),
        portfolio,
        condition=DateGapCondition(gap=1),
        parameters={
            "action": "BUY",
            "type": "fixed_shares",
            "unit": 1,
        },
    )
    portfolio.add_strategy("strategy1", strategy)
    signal = portfolio.strategies["strategy1"].generate_signal(date(2024, 1, 2))[0]

    trade = portfolio.action(signal)

    assert trade.side == SignalAction.BUY
    assert portfolio.cash == 900
    assert portfolio.positions["AAPL"] == 1

def test_portfolio_run_records_daily_value_even_without_daily_signals() -> None:
    portfolio = Portfolio(initial_capital=1000, cash=1000)
    strategy = RuleStrategy(
        fake_stock_with_dates(
            ["2024-01-02", "2024-01-03", "2024-01-04"],
            [100.0, 110.0, 90.0],
        ),
        portfolio,
        condition=DateGapCondition(gap=10),
        parameters={
            "action": "BUY",
            "type": "fixed_shares",
            "unit": 1,
        },
    )

    portfolio.add_strategy("strategy1", strategy)

    daily_values = portfolio.run()

    assert list(daily_values["date"]) == [
        date(2024, 1, 2),
        date(2024, 1, 3),
        date(2024, 1, 4),
    ]
    assert list(daily_values["cash"]) == [900.0, 900.0, 900.0]
    assert list(daily_values["positions_value"]) == [100.0, 110.0, 90.0]
    assert list(daily_values["total_value"]) == [1000.0, 1010.0, 990.0]
    assert len(portfolio.trades) == 1


def test_portfolio_summary_returns_performance_metrics() -> None:
    portfolio = Portfolio(initial_capital=1000, cash=1000)
    strategy = RuleStrategy(
        fake_stock_with_dates(
            ["2024-01-02", "2024-01-03", "2024-01-04"],
            [100.0, 110.0, 90.0],
        ),
        portfolio,
        condition=DateGapCondition(gap=10),
        parameters={
            "action": "BUY",
            "type": "fixed_shares",
            "unit": 1,
        },
    )
    portfolio.add_strategy("strategy1", strategy)
    portfolio.run()

    summary = portfolio.summary()

    assert summary["initial_capital"] == 1000
    assert summary["final_value"] == 990.0
    assert summary["total_pnl"] == -10.0
    assert summary["total_return"] == -0.01
    assert summary["trade_count"] == 1
    assert summary["start_date"] == date(2024, 1, 2)
    assert summary["end_date"] == date(2024, 1, 4)


def test_portfolio_run_calculates_cash_percent_from_current_cash_each_day() -> None:
    portfolio = Portfolio(initial_capital=1000, cash=1000)
    strategy = RuleStrategy(
        fake_stock_with_dates(
            ["2024-01-02", "2024-01-03"],
            [100.0, 100.0],
        ),
        portfolio,
        condition=PriceCondition(trigger_price=100.0),
        parameters={
            "action": "BUY",
            "type": "cash_percent",
            "unit": 0.5,
        },
    )
    portfolio.add_strategy("buy_half_cash", strategy)

    portfolio.run()

    assert [trade.quantity for trade in portfolio.trades] == [5, 2]
    assert portfolio.cash == 300.0
    assert portfolio.positions["AAPL"] == 7


def test_portfolio_run_calculates_position_percent_from_current_position_each_day() -> None:
    portfolio = Portfolio(initial_capital=1000, cash=1000)
    stock = fake_stock_with_dates(
        ["2024-01-02", "2024-01-03"],
        [100.0, 100.0],
    )
    buy_strategy = RuleStrategy(
        stock,
        portfolio,
        condition=DateGapCondition(gap=10),
        start_date=date(2024, 1, 2),
        parameters={
            "action": "BUY",
            "type": "fixed_shares",
            "unit": 10,
        },
    )
    sell_strategy = RuleStrategy(
        stock,
        portfolio,
        condition=PriceCondition(trigger_price=100.0, comparison="above_or_equal"),
        start_date=date(2024, 1, 3),
        parameters={
            "action": "SELL",
            "type": "position_percent",
            "unit": 0.5,
        },
    )
    portfolio.add_strategy("buy_ten", buy_strategy)
    portfolio.add_strategy("sell_half_position", sell_strategy)

    portfolio.run()

    assert [trade.quantity for trade in portfolio.trades] == [10, 5]
    assert portfolio.cash == 500.0
    assert portfolio.positions["AAPL"] == 5
