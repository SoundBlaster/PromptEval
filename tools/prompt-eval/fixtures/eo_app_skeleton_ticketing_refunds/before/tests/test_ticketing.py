from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from ticketing import price_tickets, refund_tickets


EVENT = {
    "prices": {"standard": 5000, "vip": 12000},
    "capacity": {"standard": 3, "vip": 1},
    "fee_per_ticket": 300,
}


def test_price_tickets_applies_fees_and_early_bird_discount():
    request = [{"tier": "standard", "quantity": 2}, {"tier": "vip", "quantity": 1}]
    buyer = {"early_bird": True}

    quote = price_tickets(EVENT, request, buyer)

    assert quote == {
        "subtotal": 22900,
        "discount": 2290,
        "total": 20610,
        "unavailable": [],
    }


def test_price_tickets_reports_combined_capacity_shortage():
    request = [{"tier": "standard", "quantity": 2}, {"tier": "standard", "quantity": 2}]

    quote = price_tickets(EVENT, request, {"early_bird": False})

    assert quote["unavailable"] == [{"tier": "standard", "quantity": 1}]
    assert EVENT["capacity"] == {"standard": 3, "vip": 1}


def test_refund_tickets_applies_policy_and_keeps_remaining_tickets():
    order = {
        "tickets": [
            {"tier": "standard", "quantity": 2, "unit_price": 5000},
            {"tier": "vip", "quantity": 1, "unit_price": 12000},
        ],
        "event_day": 10,
    }
    refund_request = {"tickets": [{"tier": "standard", "quantity": 1}], "today": 5}
    policy = {"full_refund_days": 7, "partial_percent": 50}

    refund = refund_tickets(order, refund_request, policy)

    assert refund == {
        "status": "partial_refund",
        "amount": 2500,
        "remaining_tickets": [
            {"tier": "standard", "quantity": 1},
            {"tier": "vip", "quantity": 1},
        ],
    }
