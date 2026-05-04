"""Quote pricing domain implemented with small immutable value objects."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Iterable, Tuple


Money = Decimal


@dataclass(frozen=True)
class LineItem:
    """An immutable line item for one product line."""

    quantity: int
    unit_price: Money

    def total(self) -> Money:
        return (self.unit_price * Decimal(self.quantity)).quantize(Money("0.01"))


@dataclass(frozen=True)
class Discount:
    """An immutable percentage discount represented as a rate from 0 to 100."""

    percentage: Money

    def percentage_amount(self, amount: Money) -> Money:
        return (amount * self.percentage / Money("100")).quantize(Money("0.01"), rounding=ROUND_HALF_UP)

    def apply(self, amount: Money) -> Money:
        return (amount - self.percentage_amount(amount)).quantize(Money("0.01"), rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class Quote:
    """An immutable quote with line items and a percentage discount."""

    items: Tuple[LineItem, ...]
    discount: Discount

    def __init__(self, items: Iterable[LineItem], discount: Discount):
        object.__setattr__(self, "items", tuple(items))
        object.__setattr__(self, "discount", discount)

    def subtotal(self) -> Money:
        subtotal = sum((item.total() for item in self.items), Money("0.00"))
        return subtotal.quantize(Money("0.01"))

    def discounted_subtotal(self) -> Money:
        return self.discount.apply(self.subtotal())

    def total(self, tax_rate: Money) -> Money:
        before_tax = self.discounted_subtotal()
        tax = (before_tax * tax_rate).quantize(Money("0.01"), rounding=ROUND_HALF_UP)
        return (before_tax + tax).quantize(Money("0.01"))


def price_quote(lines, discount_percent: Money, tax_rate: Money) -> Money:
    items = tuple(LineItem(quantity=line["quantity"], unit_price=line["unit_price"]) for line in lines)
    return Quote(items, Discount(discount_percent)).total(tax_rate)
