"""Dictionary and helper-based quote pricing solution."""

from .quote_helper import QuoteHelper

__all__ = ["QuoteHelper", "line_item", "discount", "quote", "price_quote"]

def line_item(quantity, unit_price):
    return {"quantity": quantity, "unit_price": unit_price}


def discount(percentage):
    return {"percentage": percentage}


def quote(items, discount_obj):
    return {"items": list(items), "discount": discount_obj}


def price_quote(lines, discount_percent, tax_rate):
    helper = QuoteHelper()
    items = [line_item(line["quantity"], line["unit_price"]) for line in lines]
    return helper.quote_total(items, discount(discount_percent), tax_rate)
