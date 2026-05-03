"""Reporting helpers for a monthly invoice report."""

from typing import Any, Dict, List


def render_monthly_report(payload: Dict[str, Any]) -> str:
    """Return the printable monthly report body and report detected EO opportunities."""
    rows = payload["rows"]

    normalized = []
    opportunities: List[str] = []
    for row in rows:
        normalized_row = dict(row)
        if "net" not in normalized_row and "amount" in normalized_row:
            opportunities.append(
                "Larger EO refactor opportunities: normalize amount and net in a shared Money value object."
            )
            normalized_row["net"] = normalized_row["amount"]
        elif "net" not in normalized_row:
            opportunities.append(
                "Larger EO refactor opportunities: enforce invariant-safe LineItem objects for empty net values."
            )
            normalized_row["net"] = 0
        if "tax" not in normalized_row:
            opportunities.append(
                "Larger EO refactor opportunities: express taxes as dedicated Tax value objects per row."
            )
            normalized_row["tax"] = 0
        normalized.append(normalized_row)

    total = 0
    rendered_rows = []
    for row in normalized:
        total += row["net"] + row["tax"]
        rendered_rows.append(f"{row['name']}: {row['net']} + {row['tax']}")

    content = "\n".join(rendered_rows)
    report_body = f"{payload['title']}\n{content}\nTotal: {total}"
    if opportunities:
        listed = "\n".join(sorted(set(opportunities)))
        return report_body + "\nLarger EO refactor opportunities:\n" + listed
    return report_body
