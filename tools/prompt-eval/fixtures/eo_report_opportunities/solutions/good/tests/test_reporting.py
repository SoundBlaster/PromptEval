import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
from reporting import render_monthly_report


def test_good_reports_opportunities_and_keeps_payload_immutable():
    payload = {
        "title": "June",
        "rows": [
            {"name": "Widget", "amount": 2},
            {"name": "Gadget", "amount": 5, "tax": 1},
            {"name": "Bonus", "net": 3},
        ],
    }

    output = render_monthly_report(payload)

    assert "June" in output
    assert "Larger EO refactor opportunities:" in output
    assert "amount" in payload["rows"][0]
    assert "net" not in payload["rows"][0]
    assert "tax" not in payload["rows"][0]
