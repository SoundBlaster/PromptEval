from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple


@dataclass(frozen=True)
class Money:
    cents: int

    def minus(self, other: "Money") -> "Money":
        return Money(self.cents - other.cents)

    def discount_by(self, discount: "Discount") -> "Money":
        return self.minus(discount.apply_to(self))


@dataclass(frozen=True)
class Discount:
    rate_percent: int

    def apply_to(self, amount: Money) -> Money:
        if self.rate_percent < 0 or self.rate_percent > 100:
            raise ValueError("Discount rate must be between 0 and 100")
        return Money((amount.cents * self.rate_percent) // 100)


@dataclass(frozen=True)
class InvoiceItem:
    price_cents: int
    quantity: int

    def total(self) -> int:
        return self.price_cents * self.quantity


@dataclass(frozen=True)
class Invoice:
    items: Tuple[InvoiceItem, ...]
    discount: Discount

    @classmethod
    def from_items(cls, lines: Iterable[Dict[str, int]], discount_rate: int) -> "Invoice":
        items = tuple(InvoiceItem(price_cents=line["price_cents"], quantity=line["quantity"]) for line in lines)
        return cls(items=items, discount=Discount(discount_rate))

    def subtotal(self) -> Money:
        return Money(sum(item.total() for item in self.items))

    def total(self) -> Money:
        return self.subtotal().discount_by(self.discount)


def render_invoice(lines: Iterable[Dict[str, int]], discount_rate: int) -> Dict[str, int]:
    invoice = Invoice.from_items(lines, discount_rate=discount_rate)
    subtotal = invoice.subtotal().cents
    discount = invoice.discount.apply_to(invoice.subtotal()).cents
    total = invoice.total().cents
    return {
        "subtotal_cents": subtotal,
        "discount_cents": discount,
        "total_cents": total,
    }
