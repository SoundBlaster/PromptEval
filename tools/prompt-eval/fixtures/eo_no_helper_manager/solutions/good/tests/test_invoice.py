import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.invoice import Invoice, LineItem, DiscountPolicy, TaxPolicy, create_standard_invoice

def test_line_item_calculates_subtotal():
    item = LineItem("book", 2, 50)
    assert item.subtotal() == 100


def test_invoice_has_focused_model_objects():
    invoice = Invoice(DiscountPolicy(10), TaxPolicy(20))
    assert hasattr(invoice, "discount")
    assert hasattr(invoice, "tax")
    invoice.add_item("book", 2, 50)
    invoice.add_item("pen", 3, 10)
    assert invoice.subtotal() == 130


def test_standard_invoice_total_is_discounted_and_taxed_on_subtotal():
    invoice = create_standard_invoice()
    assert invoice.total() == 143
