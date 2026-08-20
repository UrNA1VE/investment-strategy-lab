from datetime import date
from operator import ge, le
from typing import Callable
from abc import ABC, abstractmethod


class Condition(ABC):
    @abstractmethod
    def __init__(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def is_met(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def record_trigger(self) -> None:
        raise NotImplementedError
    
    @abstractmethod
    def reset_state(self) -> None:
        raise NotImplementedError
    
    @abstractmethod
    def describe(self) -> None:
        raise NotImplementedError    


class DateGapCondition(Condition):
    def __init__(self, gap: int = 1) -> None:
        if not isinstance(gap, int) or gap <= 0:
            raise ValueError("'gap' must be a positive integer.")

        self.gap = gap
        self.last_triggered_date = None

    def is_met(self, current_date: date, price: float | None = None) -> bool:
        if self.last_triggered_date is None:
            return True

        return (current_date - self.last_triggered_date).days >= self.gap

    def record_trigger(self, current_date: date) -> None:
        self.last_triggered_date = current_date

    def reset_state(self) -> None:
        self.last_triggered_date = None

    def describe(self) -> str:
        return f"date gap is at least {self.gap} day(s)"


class PriceCondition(Condition):
    OPERATORS: dict[str, Callable[[float, float], bool]] = {
        "below_or_equal": le,
        "above_or_equal": ge,
    }

    def __init__(self, trigger_price: float, comparison: str = "below_or_equal") -> None:
        if not isinstance(trigger_price, int | float) or trigger_price <= 0:
            raise ValueError("'trigger_price' must be a positive number.")

        if comparison not in self.OPERATORS:
            supported = ", ".join(sorted(self.OPERATORS))
            raise ValueError(f"Unsupported price comparison '{comparison}'. Use one of: {supported}.")

        self.trigger_price = trigger_price
        self.comparison = comparison

    def is_met(self, current_date: date, price: float | None = None) -> bool:
        if price is None:
            return False

        compare = self.OPERATORS[self.comparison]
        return compare(price, self.trigger_price)

    def record_trigger(self, current_date: date) -> None:
        return

    def reset_state(self) -> None:
        return

    def describe(self) -> str:
        return f"close is {self.comparison} {self.trigger_price}"
