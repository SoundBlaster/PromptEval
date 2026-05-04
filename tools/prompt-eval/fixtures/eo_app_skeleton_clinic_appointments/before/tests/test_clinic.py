from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from clinic import check_in, schedule_visits


SLOTS = {
    "lee": {"specialties": ["cardiology"], "capacity": {5: 1}},
    "park": {"specialties": ["general"], "capacity": {5: 2}},
}

PATIENTS = {
    "ada": {"blocked": False, "referrals": ["cardiology"]},
    "max": {"blocked": False, "referrals": ["cardiology"]},
    "bob": {"blocked": True, "referrals": []},
    "cy": {"blocked": False, "referrals": []},
}


def test_schedule_visits_tracks_capacity_and_patient_rules():
    requests = [
        {"patient": "ada", "specialty": "cardiology", "day": 5},
        {"patient": "max", "specialty": "cardiology", "day": 5},
        {"patient": "bob", "specialty": "general", "day": 5},
        {"patient": "cy", "specialty": "cardiology", "day": 5},
    ]

    result = schedule_visits(SLOTS, PATIENTS, requests)

    assert result == {
        "scheduled": [{"patient": "ada", "doctor": "lee", "day": 5}],
        "denied": [
            {"patient": "max", "specialty": "cardiology", "reason": "unavailable"},
            {"patient": "bob", "specialty": "general", "reason": "blocked"},
            {"patient": "cy", "specialty": "cardiology", "reason": "referral_required"},
        ],
        "remaining": {"lee": {5: 0}, "park": {5: 2}},
    }


def test_schedule_general_visit_uses_matching_capacity():
    requests = [{"patient": "cy", "specialty": "general", "day": 5}]

    result = schedule_visits(SLOTS, PATIENTS, requests)

    assert result["scheduled"] == [{"patient": "cy", "doctor": "park", "day": 5}]
    assert result["remaining"] == {"lee": {5: 1}, "park": {5: 1}}


def test_check_in_reports_late_fee_and_unknown_appointments():
    appointments = [
        {"patient": "ada", "day": 5, "window_start": 540, "window_end": 570},
        {"patient": "cy", "day": 5, "window_start": 600, "window_end": 630},
    ]

    assert check_in(appointments, {"patient": "ada", "day": 5, "time": 565}) == {
        "status": "checked_in",
        "late_fee": 0,
    }
    assert check_in(appointments, {"patient": "cy", "day": 5, "time": 645}) == {
        "status": "late",
        "late_fee": 15,
    }
    assert check_in(appointments, {"patient": "max", "day": 5, "time": 600}) == {
        "status": "not_scheduled",
    }
