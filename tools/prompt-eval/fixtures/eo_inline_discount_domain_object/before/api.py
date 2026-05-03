from dataclasses import dataclass
from typing import Iterable, Dict, List


def render_invoice(lines: Iterable[Dict[str, int]], discount_rate: int) -> Dict[str, int]:
    """Render invoice payload with inline discount math."""
    normalized_lines = list(lines)
    subtotal_cents = sum(line["price_cents"] * line["quantity"] for line in normalized_lines)
    discount_cents = (subtotal_cents * discount_rate) // 100
    total_cents = subtotal_cents - discount_cents

    return {
        "subtotal_cents": subtotal_cents,
        "discount_cents": discount_cents,
        "total_cents": total_cents,
    }
