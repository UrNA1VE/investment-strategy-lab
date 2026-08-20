from datetime import date
from typing import Any


def calculate_quantity(strategy: Any, current_date: date) -> int:
    sizing_type = strategy.parameters["type"]
    unit = strategy.parameters["unit"]

    if sizing_type == "fixed_shares":
        return unit

    if sizing_type == "cash_percent":
        unit_price = strategy.stock.data.loc[
            strategy.stock.data["date"].dt.date == current_date,
            "close",
        ].iloc[0]
        budget = strategy.portfolio.cash * unit
        return int(budget // unit_price)

    if sizing_type == "position_percent":
        current_position = strategy.portfolio.positions.get(strategy.stock.stock_name, 0)
        return int(current_position * unit)

    return 0
