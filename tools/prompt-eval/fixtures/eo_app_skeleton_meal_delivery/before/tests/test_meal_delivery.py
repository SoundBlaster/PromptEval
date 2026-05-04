from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from meal_delivery import place_delivery_order, quote_delivery


MENU = {
    "ramen": {"price": 1200, "available": 2},
    "sushi": {"price": 1800, "available": 1},
    "tea": {"price": 300, "available": 10},
}


def test_quote_delivery_applies_zone_fee_and_loyalty_discount():
    cart = [{"item": "ramen", "quantity": 2}, {"item": "sushi", "quantity": 1}]
    address = {"zone": "near", "fees": {"near": 300, "far": 800}, "minimum": 1000}
    customer = {"loyal": True}

    quote = quote_delivery(MENU, cart, address, customer)

    assert quote == {
        "subtotal": 4200,
        "delivery_fee": 300,
        "discount": 420,
        "total": 4080,
        "unavailable": [],
        "minimum_missing": 0,
    }


def test_quote_delivery_reports_combined_item_shortage_and_minimum():
    cart = [{"item": "ramen", "quantity": 1}, {"item": "ramen", "quantity": 2}]
    address = {"zone": "far", "fees": {"near": 300, "far": 800}, "minimum": 5000}

    quote = quote_delivery(MENU, cart, address, {"loyal": False})

    assert quote["unavailable"] == [{"item": "ramen", "quantity": 1}]
    assert quote["minimum_missing"] == 1400
    assert MENU["ramen"]["available"] == 2


def test_place_delivery_order_reserves_items_only_after_open_kitchen_and_payment():
    cart = [{"item": "ramen", "quantity": 1}, {"item": "tea", "quantity": 2}]
    address = {"zone": "near", "fees": {"near": 300, "far": 800}, "minimum": 1000}

    rejected = place_delivery_order(MENU, cart, {"open": False}, address, {"loyal": False}, {"authorized": True})
    assert rejected == {
        "status": "rejected",
        "reason": "kitchen_closed",
        "remaining": {"ramen": 2, "sushi": 1, "tea": 10},
    }

    placed = place_delivery_order(MENU, cart, {"open": True}, address, {"loyal": False}, {"authorized": True})
    assert placed == {
        "status": "placed",
        "total": 2100,
        "remaining": {"ramen": 1, "sushi": 1, "tea": 8},
    }
    assert MENU["ramen"]["available"] == 2
