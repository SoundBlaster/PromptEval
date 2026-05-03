from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence


@dataclass(frozen=True)
class ItemDto:
    sku: str
    unit_price_cents: int


@dataclass(frozen=True)
class OrderDto:
    id: str
    customer_tier: str
    items: tuple[ItemDto, ...]


@dataclass(frozen=True)
class Item:
    sku: str
    unit_price_cents: int


@dataclass(frozen=True)
class Order:
    id: str
    customer_tier: str
    items: tuple[Item, ...]

    @property
    def subtotal_cents(self) -> int:
        return sum(item.unit_price_cents for item in self.items)


def decode_order(payload: Mapping[str, Any]) -> OrderDto:
    return OrderDto(
        id=payload["id"],
        customer_tier=payload["customer_tier"],
        items=tuple(ItemDto(**item) for item in payload["items"]),
    )


def to_domain(dto: OrderDto) -> Order:
    return Order(
        id=dto.id,
        customer_tier=dto.customer_tier,
        items=tuple(Item(sku=item.sku, unit_price_cents=item.unit_price_cents) for item in dto.items),
    )


def load_order(payload: Mapping[str, Any]) -> Order:
    dto = decode_order(payload)
    return to_domain(dto)


def is_eligible_for_free_shipping(order: Order, minimum_cents: int) -> bool:
    return order.customer_tier == "gold" and order.subtotal_cents >= minimum_cents
