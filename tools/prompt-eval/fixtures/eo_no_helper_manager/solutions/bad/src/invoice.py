class Invoice:
    def __init__(self):
        self.items = []

    def add_item(self, sku, quantity, unit_price):
        self.items.append((sku, quantity, unit_price))


class InvoiceHelper:
    @staticmethod
    def subtotal(items):
        return sum(quantity * unit_price for _, quantity, unit_price in items)

    @staticmethod
    def apply_discount(amount):
        return amount * 0.9

    @staticmethod
    def apply_tax(amount):
        return amount * 1.2


class OrderManager:
    def __init__(self):
        self.discount_percent = 10
        self.tax_rate = 20

    def process(self, invoice):
        base = InvoiceHelper.subtotal(invoice.items)
        discount = base * self.discount_percent / 100
        tax = base * self.tax_rate / 100
        return base - discount + tax


def create_standard_invoice():
    invoice = Invoice()
    invoice.add_item("book", 2, 50)
    invoice.add_item("pen", 3, 10)
    return invoice, OrderManager()
