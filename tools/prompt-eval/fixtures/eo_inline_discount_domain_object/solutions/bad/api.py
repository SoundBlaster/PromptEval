from typing import Dict, Iterable


def calculate_discount_amount(subtotal_cents: int, discount_rate: int) -> int:
    return (subtotal_cents * discount_rate) // 100


def render_invoice(lines: Iterable[Dict[str, int]], discount_rate: int) -> Dict[str, int]:
    normalized_lines = list(lines)
    subtotal_cents = sum(line["price_cents"] * line["quantity"] for line in normalized_lines)
    discount_cents = calculate_discount_amount(subtotal_cents, discount_rate)
    total_cents = subtotal_cents - discount_cents
    return {
        "subtotal_cents": subtotal_cents,
        "discount_cents": discount_cents,
        "total_cents": total_cents,
    }
