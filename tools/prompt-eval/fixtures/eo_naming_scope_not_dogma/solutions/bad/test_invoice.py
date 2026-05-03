from invoice import CustomerInvoiceLineItem, calculate_invoice_total_with_discounts_and_taxes_for_customer


def test_invoice_with_one_line_honors_discount_and_tax():
    lines = [CustomerInvoiceLineItem("book", 10.0, 2)]
    total = calculate_invoice_total_with_discounts_and_taxes_for_customer(
        lines,
        customer_discount_percentage=10,
        sales_tax_percentage=20,
    )
    assert total == 21.6


def test_invoice_with_zero_discount_keeps_full_total():
    lines = [CustomerInvoiceLineItem("book", 5.0, 1), CustomerInvoiceLineItem("pen", 1.0, 3)]
    total = calculate_invoice_total_with_discounts_and_taxes_for_customer(
        lines,
        customer_discount_percentage=0,
        sales_tax_percentage=10,
    )
    assert total == 8.8


def test_empty_invoice_costs_nothing():
    total = calculate_invoice_total_with_discounts_and_taxes_for_customer([], 0, 20)
    assert total == 0
