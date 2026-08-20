from datetime import date

import pytest

from app.strategies.conditions import DateGapCondition, PriceCondition


def test_price_condition_is_met_when_price_is_below_or_equal_trigger() -> None:
    condition = PriceCondition(trigger_price=100.0, comparison="below_or_equal")

    assert condition.is_met(date(2024, 1, 2), price=95.0) is True
    assert condition.is_met(date(2024, 1, 2), price=105.0) is False


def test_price_condition_is_met_when_price_is_above_or_equal_trigger() -> None:
    condition = PriceCondition(trigger_price=100.0, comparison="above_or_equal")

    assert condition.is_met(date(2024, 1, 2), price=105.0) is True
    assert condition.is_met(date(2024, 1, 2), price=95.0) is False


def test_price_condition_requires_positive_trigger_price() -> None:
    with pytest.raises(ValueError, match="positive number"):
        PriceCondition(trigger_price=0)


def test_price_condition_requires_supported_comparison() -> None:
    with pytest.raises(ValueError, match="Unsupported price comparison"):
        PriceCondition(trigger_price=100.0, comparison="equal")


def test_date_gap_condition_is_met_after_gap_days() -> None:
    condition = DateGapCondition(gap=2)

    assert condition.is_met(date(2024, 1, 2)) is True

    condition.record_trigger(date(2024, 1, 2))

    assert condition.is_met(date(2024, 1, 3)) is False
    assert condition.is_met(date(2024, 1, 4)) is True


def test_date_gap_condition_can_reset_state() -> None:
    condition = DateGapCondition(gap=2)
    condition.record_trigger(date(2024, 1, 2))
    condition.reset_state()

    assert condition.is_met(date(2024, 1, 3)) is True
