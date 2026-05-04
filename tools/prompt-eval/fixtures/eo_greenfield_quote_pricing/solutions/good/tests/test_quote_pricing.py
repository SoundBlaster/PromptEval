from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from quote_pricing import price_quote
from decimal import Decimal


def test_quote_total_with_discount_and_tax():
    lines = (
        {"quantity": 2, "unit_price": Decimal("10.00")},
        {"quantity": 1, "unit_price": Decimal("5.00")},
    )

    assert price_quote(lines, Decimal("10.00"), Decimal("0.20")) == Decimal("27.00")


def test_quote_total_rounds_money_to_two_places():
    lines = (
        {"quantity": 3, "unit_price": Decimal("7.50")},
    )

    assert price_quote(lines, Decimal("20.00"), Decimal("0.20")) == Decimal("21.60")


def test_discount_percent_and_tax_rate_use_different_units():
    lines = (
        {"quantity": 1, "unit_price": Decimal("100.00")},
    )

    assert price_quote(lines, Decimal("10.00"), Decimal("0.10")) == Decimal("99.00")
