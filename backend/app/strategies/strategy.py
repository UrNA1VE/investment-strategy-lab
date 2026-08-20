from copy import copy
from datetime import date
from typing import Any

from app.strategies.base import Signal, SignalAction
from app.strategies.conditions import DateGapCondition, PriceCondition
from app.strategies.sizing import calculate_quantity


def validate_rule_parameters(parameters: dict | None) -> dict:
    if parameters is None:
        raise ValueError("RuleStrategy requires parameters.")

    if "action" not in parameters:
        raise ValueError("RuleStrategy requires 'action' in parameters.")

    try:
        action = SignalAction(parameters["action"])
    except ValueError as exc:
        raise ValueError("action must be 'BUY' or 'SELL'.") from exc

    if action not in {SignalAction.BUY, SignalAction.SELL}:
        raise ValueError("action must be 'BUY' or 'SELL'.")

    if "type" not in parameters:
        raise ValueError("RuleStrategy requires 'type' in parameters.")
    if parameters["type"] not in {"fixed_shares", "cash_percent", "position_percent"}:
        raise ValueError("type must be 'fixed_shares', 'cash_percent', or 'position_percent'.")

    unit = parameters.get("unit")
    if unit is None:
        raise ValueError("RuleStrategy requires 'unit' in parameters.")

    if parameters["type"] == "fixed_shares":
        if not isinstance(unit, int) or unit <= 0:
            raise ValueError("unit must be a positive integer for fixed_shares.")

    if parameters["type"] in {"cash_percent", "position_percent"}:
        if not isinstance(unit, int | float) or unit <= 0 or unit > 1:
            raise ValueError("unit must be a number between 0 and 1 for percent sizing.")

    if action is SignalAction.SELL and parameters["type"] == "cash_percent":
        raise ValueError("SELL action cannot use cash_percent sizing.")

    if action is SignalAction.BUY and parameters["type"] == "position_percent":
        raise ValueError("BUY action cannot use position_percent sizing.")

    return {**parameters, "action": action}


class RuleStrategy:
    strategy_name = "rule"

    def __init__(
        self,
        stock,
        portfolio,
        condition: Any,
        start_date: date | None = None,
        end_date: date | None = None,
        parameters: dict | None = None,
    ) -> None:
        parameters = validate_rule_parameters(parameters)
        self.portfolio = portfolio
        self.start_date = start_date
        self.end_date = end_date
        self.parameters = {
            **parameters,
            "start_date": start_date,
            "end_date": end_date,
        }
        self.stock = self.filter_stock_by_strategy_dates(stock)
        self.condition = condition
        self.action = self.parameters["action"]

    def filter_stock_by_strategy_dates(self, stock: Any):
        filtered_stock = copy(stock)
        data = stock.data

        if self.start_date is not None:
            data = data[data["date"].dt.date >= self.start_date]

        if self.end_date is not None:
            data = data[data["date"].dt.date <= self.end_date]

        filtered_stock.data = data
        return filtered_stock

    def reset_state(self) -> None:
        self.condition.reset_state()

    def generate_signal(self, current_date: date) -> list[Signal]:
        if self.stock.data.empty:
            return []

        today_data = self.stock.data[self.stock.data["date"].dt.date == current_date]
        if today_data.empty:
            return []

        row = today_data.iloc[-1]
        close_price = float(row.close)
        if not self.condition.is_met(current_date=current_date, price=close_price):
            return []

        quantity = calculate_quantity(self, current_date)
        if quantity <= 0:
            return []

        self.condition.record_trigger(current_date)
        return [
            Signal(
                stock_name=self.stock.stock_name,
                signal_date=current_date,
                action=self.action,
                price=row.close,
                quantity=quantity,
                reason=f"{self.action.value} when {self.condition.describe()}.",
            )
        ]


class StrategyFactory:
    CONDITION_TYPES = {"date_gap", "price"}

    @classmethod
    def create(
        cls,
        stock,
        portfolio,
        config: dict,
    ) -> RuleStrategy:
        condition_config = config.get("condition")
        if not isinstance(condition_config, dict):
            raise ValueError("Strategy config requires a 'condition' dictionary.")

        sizing_config = config.get("sizing")
        if not isinstance(sizing_config, dict):
            raise ValueError("Strategy config requires a 'sizing' dictionary.")

        condition = cls.create_condition(condition_config)
        parameters = {
            "action": config.get("action"),
            "type": sizing_config.get("type"),
            "unit": sizing_config.get("unit"),
        }

        return RuleStrategy(
            stock=stock,
            portfolio=portfolio,
            condition=condition,
            start_date=config.get("start_date"),
            end_date=config.get("end_date"),
            parameters=parameters,
        )

    @classmethod
    def create_condition(cls, config: dict):
        condition_type = config.get("type")
        if not isinstance(condition_type, str):
            raise ValueError("Condition config requires 'type'.")

        normalized_type = condition_type.strip().lower()
        if normalized_type not in cls.CONDITION_TYPES:
            supported_types = ", ".join(sorted(cls.CONDITION_TYPES))
            raise ValueError(f"Unsupported condition type '{condition_type}'. Use one of: {supported_types}.")

        if normalized_type == "date_gap":
            if "gap" not in config:
                raise ValueError("date_gap condition requires 'gap'.")
            return DateGapCondition(gap=config["gap"])

        comparison = config.get("comparison", "below_or_equal")
        if "trigger_price" not in config:
            raise ValueError("price condition requires 'trigger_price'.")

        return PriceCondition(
            trigger_price=config["trigger_price"],
            comparison=comparison,
        )
