from api import Invoice, Discount, InvoiceItem, render_invoice


def test_render_invoice_applies_discount_via_domain_objects():
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


def test_invoice_total_uses_discount_domain_object():
    invoice = Invoice(
        items=(
            InvoiceItem(price_cents=500, quantity=2),
            InvoiceItem(price_cents=250, quantity=2),
        ),
        discount=Discount(rate_percent=25),
    )
    assert invoice.subtotal().cents == 1500
    assert invoice.total().cents == 1125
