from __future__ import annotations

from billing import is_eligible_for_free_shipping, load_order


def _payload() -> dict:
    return {
        "id": "ord-77",
        "customer_tier": "gold",
        "items": [
            {"sku": "A", "unit_price_cents": 1200},
            {"sku": "B", "unit_price_cents": 1900},
        ],
    }


def test_gold_customer_reaches_threshold() -> None:
    order = load_order(_payload())
    assert is_eligible_for_free_shipping(order, minimum_cents=3000)


def test_gold_customer_below_threshold() -> None:
    order = load_order(_payload())
    assert not is_eligible_for_free_shipping(order, minimum_cents=4000)
