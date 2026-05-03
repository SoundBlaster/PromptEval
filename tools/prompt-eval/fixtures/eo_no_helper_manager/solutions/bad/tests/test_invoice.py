import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.invoice import OrderManager, create_standard_invoice

def test_standard_invoice_total_rounds_with_manager_and_helper():
    invoice, manager = create_standard_invoice()
    assert manager.process(invoice) == 143


def test_standard_invoice_items_keep_structure():
    invoice, _ = create_standard_invoice()
    assert len(invoice.items) == 2
    assert invoice.items[0][0] == "book"
