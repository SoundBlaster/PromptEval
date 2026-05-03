from dataclasses import dataclass


@dataclass
class InvoiceLine:
    product_name: str
    unit_price: float
    units: int


def calculate_invoice_total_with_discounts_and_taxes_for_customer(
    invoice_lines,
    customer_discount_percentage,
    sales_tax_percentage,
):
    invoice_line_items_total = 0
    for invoice_line in invoice_lines:
        invoice_line_subtotal = invoice_line.unit_price * invoice_line.units
        invoice_line_items_total = invoice_line_items_total + invoice_line_subtotal

    customer_discount_amount = invoice_line_items_total * customer_discount_percentage / 100
    invoice_total_after_discount = invoice_line_items_total - customer_discount_amount
    sales_tax_amount = invoice_total_after_discount * sales_tax_percentage / 100
    return invoice_total_after_discount + sales_tax_amount
