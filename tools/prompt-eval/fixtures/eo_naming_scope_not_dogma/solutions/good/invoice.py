from dataclasses import dataclass


@dataclass
class Line:
    name: str
    price: float
    qty: int


class Invoice:
    def __init__(self, items):
        self._items = list(items)

    def subtotal(self):
        total = 0
        for item in self._items:
            total = total + item.total()
        return total


class Totals:
    def __init__(self, invoice, discount_percent, tax_percent):
        self._invoice = invoice
        self._discount = discount_percent
        self._tax = tax_percent

    def discounted(self):
        return self._invoice.subtotal() * (100 - self._discount) / 100

    def taxed(self, value):
        return value * (100 + self._tax) / 100

    def total(self):
        after = self.discounted()
        return self.taxed(after)


def calculate(lines, discount_percent, tax_percent):
    invoice = Invoice(lines)
    return Totals(invoice, discount_percent, tax_percent).total()


@dataclass
class _Line:
    name: str
    price: float
    qty: int

    def total(self):
        return self.price * self.qty


__all__ = ["Line", "_Line", "calculate", "Invoice", "Totals"]
