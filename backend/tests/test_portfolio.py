from datetime import date
from types import SimpleNamespace

import pandas as pd

from app.domain.portfolio import Portfolio
from app.strategies.base import SignalAction
from app.strategies.buy_and_hold import BuyAndHoldByDateStrategy


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
    strategy = BuyAndHoldByDateStrategy(fake_stock())

    portfolio.add_strategy("strategy1", strategy)

    signals = portfolio.generate_signals()["signal"].tolist()

    assert signals[0].strategy_name == "strategy1"
    assert signals[0].action == SignalAction.BUY


def test_portfolio_action_uses_signal_strategy_name() -> None:
    portfolio = Portfolio(initial_capital=1000, cash=1000)
    strategy = BuyAndHoldByDateStrategy(fake_stock())
    portfolio.add_strategy("strategy1", strategy)
    signal = portfolio.generate_signals().iloc[0]["signal"]

    trade = portfolio.action(signal)

    assert trade.side == SignalAction.BUY
    assert portfolio.cash == 900
    assert portfolio.positions["AAPL"] == 1


def test_portfolio_generate_signals_returns_sorted_signal_list() -> None:
    portfolio = Portfolio(initial_capital=1000, cash=1000)
    later_strategy = BuyAndHoldByDateStrategy(
        fake_stock_with_dates(["2024-01-04"], [110.0])
    )
    earlier_strategy = BuyAndHoldByDateStrategy(
        fake_stock_with_dates(["2024-01-02"], [100.0])
    )

    portfolio.add_strategy("later_strategy", later_strategy)
    portfolio.add_strategy("earlier_strategy", earlier_strategy)

    signals = portfolio.generate_signals()
    signal_list = signals["signal"].tolist()

    assert list(signals["date"]) == [
        date(2024, 1, 2),
        date(2024, 1, 4),
    ]
    assert [signal.strategy_name for signal in signal_list] == [
        "earlier_strategy",
        "later_strategy",
    ]


def test_portfolio_run_records_daily_value_even_without_daily_signals() -> None:
    portfolio = Portfolio(initial_capital=1000, cash=1000)
    strategy = BuyAndHoldByDateStrategy(
        fake_stock_with_dates(
            ["2024-01-02", "2024-01-03", "2024-01-04"],
            [100.0, 110.0, 90.0],
        )
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
    strategy = BuyAndHoldByDateStrategy(
        fake_stock_with_dates(
            ["2024-01-02", "2024-01-03", "2024-01-04"],
            [100.0, 110.0, 90.0],
        )
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
