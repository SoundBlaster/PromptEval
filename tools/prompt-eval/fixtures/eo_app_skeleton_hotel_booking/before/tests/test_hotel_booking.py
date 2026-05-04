from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from hotel_booking import quote_stay, reserve_stay


ROOMS = {
    "standard": {
        "base": 12000,
        "weekend_surcharge": 3000,
        "cleaning_fee": 2500,
        "availability": {1: 2, 2: 1, 3: 0},
    },
    "suite": {
        "base": 20000,
        "weekend_surcharge": 5000,
        "cleaning_fee": 5000,
        "availability": {1: 1, 2: 1, 3: 1},
    },
}


def test_quote_prices_nights_with_member_discount():
    request = {"room_type": "standard", "nights": [1, 2], "weekend_nights": [2]}
    guest = {"member": True}

    quote = quote_stay(ROOMS, request, guest)

    assert quote == {
        "subtotal": 29500,
        "discount": 2950,
        "total": 26550,
        "unavailable_nights": [],
    }


def test_quote_reports_unavailable_nights_without_reserving():
    request = {"room_type": "standard", "nights": [2, 3], "weekend_nights": []}
    guest = {"member": False}

    quote = quote_stay(ROOMS, request, guest)

    assert quote["unavailable_nights"] == [3]
    assert ROOMS["standard"]["availability"] == {1: 2, 2: 1, 3: 0}


def test_reservation_changes_inventory_only_after_payment_authorization():
    request = {"room_type": "standard", "nights": [1, 2], "weekend_nights": [2]}
    guest = {"member": False}

    rejected = reserve_stay(ROOMS, request, guest, {"authorized": False})
    assert rejected == {
        "status": "rejected",
        "reason": "payment_required",
        "remaining": ROOMS["standard"]["availability"],
    }

    placed = reserve_stay(ROOMS, request, guest, {"authorized": True})
    assert placed == {
        "status": "reserved",
        "total": 29500,
        "remaining": {1: 1, 2: 0, 3: 0},
    }
    assert ROOMS["standard"]["availability"] == {1: 2, 2: 1, 3: 0}
