from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from bookstore import place_order, quote_order


CATALOG = {
    "eo": {"title": "Elegant Objects", "price": 4200, "tags": ["oop"]},
    "clean": {"title": "Clean Code", "price": 3500, "tags": ["craft"]},
    "ddd": {"title": "Domain-Driven Design", "price": 5000, "tags": ["architecture"]},
}


def test_quote_applies_loyalty_and_bundle_discounts():
    cart = [{"isbn": "eo", "quantity": 2}, {"isbn": "clean", "quantity": 1}]
    inventory = {"eo": 3, "clean": 4, "ddd": 1}
    customer = {"loyal": True}

    quote = quote_order(CATALOG, cart, inventory, customer)

    assert quote == {
        "subtotal": 11900,
        "discount": 1785,
        "total": 10115,
        "unavailable": [],
    }


def test_order_reserves_available_books_and_rejects_missing_stock():
    cart = [{"isbn": "eo", "quantity": 1}, {"isbn": "ddd", "quantity": 2}]
    inventory = {"eo": 2, "clean": 4, "ddd": 1}
    customer = {"loyal": False}
    payment = {"authorized": True}

    order = place_order(CATALOG, cart, inventory, customer, payment)

    assert order["status"] == "rejected"
    assert order["unavailable"] == ["ddd"]
    assert order["remaining_inventory"] == inventory


def test_order_reserves_stock_after_payment_authorization():
    cart = [{"isbn": "eo", "quantity": 1}, {"isbn": "clean", "quantity": 1}]
    inventory = {"eo": 2, "clean": 1, "ddd": 1}
    customer = {"loyal": False}
    payment = {"authorized": True}

    order = place_order(CATALOG, cart, inventory, customer, payment)

    assert order["status"] == "placed"
    assert order["total"] == 7315
    assert order["remaining_inventory"] == {"eo": 1, "clean": 0, "ddd": 1}
    assert inventory == {"eo": 2, "clean": 1, "ddd": 1}
