from __future__ import annotations

from typing import Any, Mapping


OrderInput = dict[str, Any]


def decode_order(payload: Mapping[str, Any]) -> OrderInput:
    """Decode API data and return a raw structure for downstream logic."""
    return {
        "id": payload["id"],
        "customer_tier": payload["customer_tier"],
        "items": list(payload["items"]),
    }


def is_eligible_for_free_shipping(order: OrderInput, minimum_cents: int) -> bool:
    """Business behavior directly consumes decoded payload."""
    subtotal = sum(item["unit_price_cents"] for item in order["items"])
    return order["customer_tier"] == "gold" and subtotal >= minimum_cents
