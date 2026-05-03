from billing.api import render_invoice, render_refund


def test_render_invoice():
    invoice = render_invoice("acct-7", "pro", 2, "2026-05")
    assert "Account: acct-7" in invoice
    assert "Plan: Pro" in invoice
    assert "Subtotal: $98.00" in invoice
    assert "Total: $98.00" in invoice


def test_render_refund():
    assert render_refund("acct-7", 3000, 10) == "Refund for acct-7: $10.00"
