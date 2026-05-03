class LineItem:
    def __init__(self, sku, quantity, unit_price):
        self.sku = sku
        self.quantity = quantity
        self.unit_price = unit_price


class InvoiceManager:
    def __init__(self):
        self.items = []
        self.discount_percent = 0
        self.tax_rate = 0

    def add_item(self, sku, quantity, unit_price):
        self.items.append(LineItem(sku, quantity, unit_price))

    def set_discount_percent(self, discount_percent):
        self.discount_percent = discount_percent

    def set_tax_rate(self, tax_rate):
        self.tax_rate = tax_rate

    def subtotal(self):
        total = 0
        for item in self.items:
            total += item.quantity * item.unit_price
        return total

    def total(self):
        subtotal = self.subtotal()
        discount = subtotal * self.discount_percent / 100
        tax = subtotal * self.tax_rate / 100
        return subtotal - discount + tax


def create_standard_invoice():
    invoice = InvoiceManager()
    invoice.set_discount_percent(10)
    invoice.set_tax_rate(20)
    invoice.add_item("book", 2, 50)
    invoice.add_item("pen", 3, 10)
    return invoice
