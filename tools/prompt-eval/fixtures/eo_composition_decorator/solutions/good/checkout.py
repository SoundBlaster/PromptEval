class Amount:
    def total(self):
        raise NotImplementedError


class BaseAmount(Amount):
    def __init__(self, value):
        self.value = float(value)

    def total(self):
        return self.value


class AmountDecorator(Amount):
    def __init__(self, wrapped):
        self.wrapped = wrapped

    def total(self):
        return self.wrapped.total()


class ExpressFee(AmountDecorator):
    def total(self):
        return self.wrapped.total() + 10


class LoyaltyDiscount(AmountDecorator):
    def total(self):
        return self.wrapped.total() - 5


class RegionalTax(AmountDecorator):
    def __init__(self, wrapped, rate):
        super().__init__(wrapped)
        self.rate = float(rate)

    def total(self):
        return self.wrapped.total() * (1 + self.rate)


class Checkout:
    def __init__(self, amount):
        self.amount = amount

    def total(self):
        return round(self.amount.total(), 2)
