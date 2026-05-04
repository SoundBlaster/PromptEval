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
