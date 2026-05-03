"""Reporting helpers for a monthly invoice report."""

from typing import Any, Dict, List


def render_monthly_report(payload: Dict[str, Any]) -> str:
    """Return the printable monthly report body."""
    rows: List[Dict[str, Any]] = payload["rows"]
    _adapt_rows(rows)

    total = 0
    rendered_rows = []
    for row in rows:
        total += row["net"] + row.get("tax", 0)
        rendered_rows.append(f"{row['name']}: {row['net']} + {row.get('tax', 0)}")

    content = "\n".join(rendered_rows)
    return f"{payload['title']}\n{content}\nTotal: {total}"


def _adapt_rows(rows: List[Dict[str, Any]]) -> None:
    for row in rows:
        if "net" not in row and "amount" in row:
            row["net"] = row.pop("amount")
        if "tax" not in row:
            row["tax"] = 0
