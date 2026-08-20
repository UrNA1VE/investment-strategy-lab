from app.domain.account import Account
from app.domain.portfolio import Portfolio


def test_account_summary_aggregates_portfolio_summaries() -> None:
    account = Account(name="Demo")
    growth = Portfolio(cash=1000)
    income = Portfolio(cash=2000)
    growth.daily_values = [
        {
            "date": "2024-01-02",
            "cash": 900,
            "positions_value": 200,
            "total_value": 1100,
        }
    ]
    income.daily_values = [
        {
            "date": "2024-01-02",
            "cash": 1800,
            "positions_value": 100,
            "total_value": 1900,
        }
    ]
    account.portfolios["growth"] = growth
    account.portfolios["income"] = income

    summary = account.summary()

    assert summary["name"] == "Demo"
    assert summary["portfolio_count"] == 2
    assert summary["total_initial_capital"] == 3000
    assert summary["total_final_value"] == 3000
    assert summary["total_pnl"] == 0
    assert summary["total_return"] == 0
    assert set(summary["portfolios"]) == {"growth", "income"}


def test_account_assign_initial_capital_updates_existing_portfolio() -> None:
    account = Account(name="Demo")
    account.create_portfolio("main", cash=1000)

    account.assign_initial_capital("main", 1500)

    assert account.portfolios["main"].cash == 1500
    assert account.portfolios["main"].initial_capital == 1500
