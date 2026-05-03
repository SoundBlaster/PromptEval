import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
from reporting import render_monthly_report


def test_before_normalizes_and_mutates_rows():
    payload = {
        "title": "June",
        "rows": [
            {"name": "Widget", "amount": 2},
            {"name": "Gadget", "amount": 5, "tax": 1},
        ],
    }

    output = render_monthly_report(payload)

    assert "June" in output
    assert "Widget: 2 + 0" in output
    assert payload["rows"][0]["net"] == 2
    assert payload["rows"][0]["tax"] == 0
