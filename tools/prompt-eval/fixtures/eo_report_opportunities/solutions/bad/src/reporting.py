"""Reporting helpers for a monthly invoice report."""

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List


class LegacyRowAdapter:
    """Rewrite payload rows into the old aggregate shape across module boundaries."""

    def __init__(self, payload: Dict[str, Any]):
        self.payload = payload

    def adapt(self) -> None:
        for row in self.payload["rows"]:
            if "net" not in row and "amount" in row:
                row["net"] = row.pop("amount")
            if "tax" not in row:
                row["tax"] = 0


@dataclass
class MonthlyFormatter:
    rows: List[Dict[str, Any]]

    def format(self) -> str:
        total = 0
        lines = []
        for row in self.rows:
            total += row["net"] + row["tax"]
            lines.append(f"{row['name']}: {row['net']} + {row['tax']}")
        return "\n".join(lines) + f"\nTotal: {total}"


def render_monthly_report(payload: Dict[str, Any]) -> str:
    """Return the monthly report after adapting data to a new class hierarchy."""
    adapter = LegacyRowAdapter(payload)
    adapter.adapt()
    formatter = MonthlyFormatter(payload["rows"])
    return payload["title"] + "\n" + formatter.format()
