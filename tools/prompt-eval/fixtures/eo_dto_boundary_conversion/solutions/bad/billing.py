from __future__ import annotations

from typing import Any, Mapping


OrderInput = dict[str, Any]


def decode_order(payload: Mapping[str, Any]) -> OrderInput:
    """Boundary still returns a mapping and domain logic keeps using it."""
    return {
        "id": payload["id"],
        "customer_tier": payload["customer_tier"],
        "items": list(payload["items"]),
    }


def load_order(payload: Mapping[str, Any]) -> OrderInput:
    return decode_order(payload)


def is_eligible_for_free_shipping(order: OrderInput, minimum_cents: int) -> bool:
    subtotal = sum(item["unit_price_cents"] for item in order["items"])
    return order["customer_tier"] == "gold" and subtotal >= minimum_cents
