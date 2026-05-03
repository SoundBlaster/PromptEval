class LineItem:
    def __init__(self, sku, quantity, unit_price):
        self.sku = sku
        self.quantity = quantity
        self.unit_price = unit_price

    def subtotal(self):
        return self.quantity * self.unit_price


class DiscountPolicy:
    def __init__(self, percent):
        self.percent = percent

    def apply(self, amount):
        return amount * (1 - self.percent / 100)


class TaxPolicy:
    def __init__(self, rate):
        self.rate = rate

    def apply(self, amount):
        return amount * (1 + self.rate / 100)


class Invoice:
    def __init__(self, discount, tax):
        self.discount = discount
        self.tax = tax
        self.items = []

    def add_item(self, sku, quantity, unit_price):
        self.items.append(LineItem(sku, quantity, unit_price))

    def subtotal(self):
        return sum(item.subtotal() for item in self.items)

    def total(self):
        base = self.subtotal()
        discounted = self.discount.apply(base)
        taxed = self.tax.apply(base)
        return discounted + (taxed - base)


def create_standard_invoice():
    invoice = Invoice(DiscountPolicy(10), TaxPolicy(20))
    invoice.add_item("book", 2, 50)
    invoice.add_item("pen", 3, 10)
    return invoice
