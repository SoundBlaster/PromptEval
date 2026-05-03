import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.invoice import InvoiceManager, create_standard_invoice

def test_subtotal_is_sum_of_items():
    invoice = InvoiceManager()
    invoice.add_item("book", 2, 50)
    invoice.add_item("pen", 3, 10)
    assert invoice.subtotal() == 130


def test_total_applies_discount_and_tax_on_subtotal():
    invoice = create_standard_invoice()
    assert invoice.total() == 143


def test_invoice_can_add_duplicate_skus():
    invoice = InvoiceManager()
    invoice.add_item("book", 1, 30)
    invoice.add_item("book", 2, 30)
    assert invoice.subtotal() == 90
