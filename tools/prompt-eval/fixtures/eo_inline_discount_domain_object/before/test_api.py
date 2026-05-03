from api import render_invoice


def test_render_invoice_applies_percentage_discount():
    lines = [
        {"price_cents": 1200, "quantity": 2},
        {"price_cents": 450, "quantity": 3},
    ]
    result = render_invoice(lines, discount_rate=20)
    assert result == {
        "subtotal_cents": 3750,
        "discount_cents": 750,
        "total_cents": 3000,
    }


def test_render_invoice_no_discount_keeps_total_and_subtotal_in_sync():
    lines = [
        {"price_cents": 333, "quantity": 3},
    ]
    result = render_invoice(lines, discount_rate=0)
    assert result["discount_cents"] == 0
    assert result["total_cents"] == result["subtotal_cents"]
