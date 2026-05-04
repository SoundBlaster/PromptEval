from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from library_app import lend_books, return_books


CATALOG = {
    "eo-1": {"title": "Elegant Objects", "available": 2},
    "ddd-1": {"title": "Domain-Driven Design", "available": 1},
}

PATRONS = {
    "ada": {"tier": "adult", "active_loans": 1, "blocked": False},
    "tim": {"tier": "child", "active_loans": 2, "blocked": False},
    "max": {"tier": "adult", "active_loans": 0, "blocked": True},
}


def test_lending_approves_requests_with_due_dates_and_remaining_stock():
    requests = [
        {"patron": "ada", "copy": "eo-1"},
        {"patron": "ada", "copy": "ddd-1"},
    ]

    result = lend_books(CATALOG, PATRONS, requests, today=10)

    assert result["approved"] == [
        {"patron": "ada", "copy": "eo-1", "due": 24},
        {"patron": "ada", "copy": "ddd-1", "due": 24},
    ]
    assert result["denied"] == []
    assert result["remaining"] == {"eo-1": 1, "ddd-1": 0}


def test_lending_denies_blocked_patrons_limits_and_missing_stock():
    requests = [
        {"patron": "max", "copy": "eo-1"},
        {"patron": "tim", "copy": "eo-1"},
        {"patron": "ada", "copy": "missing"},
    ]

    result = lend_books(CATALOG, PATRONS, requests, today=10)

    assert result["approved"] == []
    assert result["denied"] == [
        {"patron": "max", "copy": "eo-1", "reason": "blocked"},
        {"patron": "tim", "copy": "eo-1", "reason": "loan_limit"},
        {"patron": "ada", "copy": "missing", "reason": "unavailable"},
    ]
    assert result["remaining"] == {"eo-1": 2, "ddd-1": 1}


def test_returns_report_fines_for_late_loans():
    loans = [
        {"patron": "ada", "copy": "eo-1", "due": 12},
        {"patron": "tim", "copy": "ddd-1", "due": 15},
    ]
    returns = [{"patron": "ada", "copy": "eo-1"}, {"patron": "tim", "copy": "ddd-1"}]

    result = return_books(loans, returns, today=17)

    assert result == {
        "closed": [{"patron": "ada", "copy": "eo-1"}, {"patron": "tim", "copy": "ddd-1"}],
        "fines": [
            {"patron": "ada", "copy": "eo-1", "amount": 5},
            {"patron": "tim", "copy": "ddd-1", "amount": 2},
        ],
    }
