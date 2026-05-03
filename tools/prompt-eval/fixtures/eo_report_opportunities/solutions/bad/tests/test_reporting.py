import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
from reporting import render_monthly_report


def test_bad_adds_refactor_notice_and_preserves_input_shape():
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
    assert "Tax policy" in output
