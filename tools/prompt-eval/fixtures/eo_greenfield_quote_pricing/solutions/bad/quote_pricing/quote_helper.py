"""A weaker helper-oriented implementation for contrast with the good model."""

from decimal import Decimal


TWO_PLACES = Decimal("0.01")


def _money(value):
    return Decimal(value).quantize(TWO_PLACES)


def _subtotal(items):
    total = Decimal("0.00")
    for item in items:
        total += _money(item["unit_price"]) * _money(item["quantity"])
    return total


def _apply_discount(amount, discount_value):
    rate = _money(discount_value)
    return amount - (amount * rate / Decimal("100")).quantize(TWO_PLACES)


def _with_tax(amount, tax_rate):
    return amount + (amount * _money(tax_rate)).quantize(TWO_PLACES)


class QuoteHelper:
    def quote_total(self, items, discount_obj, tax_rate):
        base = _subtotal(items)
        after_discount = _apply_discount(base, discount_obj["percentage"])
        return _with_tax(after_discount, tax_rate)
