from datetime import date
from types import SimpleNamespace

import pandas as pd

from app.strategies.sizing import calculate_quantity


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


def test_calculate_quantity_for_fixed_shares() -> None:
    strategy = SimpleNamespace(
        parameters={"type": "fixed_shares", "unit": 3},
        stock=fake_stock(),
        portfolio=SimpleNamespace(cash=1000.0, positions={}),
    )

    assert calculate_quantity(strategy, date(2024, 1, 2)) == 3


def test_calculate_quantity_for_cash_percent() -> None:
    strategy = SimpleNamespace(
        parameters={"type": "cash_percent", "unit": 0.5},
        stock=fake_stock(),
        portfolio=SimpleNamespace(cash=1000.0, positions={}),
    )

    assert calculate_quantity(strategy, date(2024, 1, 2)) == 5


def test_calculate_quantity_for_fixed_shares_with_position() -> None:
    strategy = SimpleNamespace(
        parameters={"type": "fixed_shares", "unit": 4},
        stock=fake_stock(),
        portfolio=SimpleNamespace(cash=1000.0, positions={"AAPL": 10}),
    )

    assert calculate_quantity(strategy, date(2024, 1, 2)) == 4


def test_calculate_quantity_for_position_percent() -> None:
    strategy = SimpleNamespace(
        parameters={"type": "position_percent", "unit": 0.5},
        stock=fake_stock(),
        portfolio=SimpleNamespace(cash=1000.0, positions={"AAPL": 10}),
    )

    assert calculate_quantity(strategy, date(2024, 1, 2)) == 5
