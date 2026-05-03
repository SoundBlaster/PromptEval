from dataclasses import dataclass


@dataclass
class CustomerInvoiceLineItem:
    product_name: str
    price_each: float
    number_of_units: int


def calculate_total(lines, discount_percentage, tax_percentage):
    subtotal_for_all_items = 0
    for item in lines:
        subtotal_for_each_item = item.price_each * item.number_of_units
        subtotal_for_all_items = subtotal_for_all_items + subtotal_for_each_item

    total_discount_amount_for_customer = subtotal_for_all_items * discount_percentage / 100
    subtotal_for_customer_invoice = subtotal_for_all_items - total_discount_amount_for_customer
    sales_tax_for_customer_invoice = subtotal_for_customer_invoice * tax_percentage / 100
    return subtotal_for_customer_invoice + sales_tax_for_customer_invoice


def calculate_invoice_total_with_discounts_and_taxes_for_customer(invoice_lines, customer_discount_percentage, sales_tax_percentage):
    return calculate_total(invoice_lines, customer_discount_percentage, sales_tax_percentage)
