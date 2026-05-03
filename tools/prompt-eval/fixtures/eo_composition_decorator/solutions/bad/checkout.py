class Checkout:
    def total(self, amount):
        raise NotImplementedError


class BaseCheckout(Checkout):
    def __init__(self, amount):
        self.amount = float(amount)

    def total(self):
        return self.amount


class PremiumCheckout(Checkout):
    def __init__(self, amount):
        self.amount = float(amount)

    def total(self):
        return self.amount - 5


class RegionCheckout(Checkout):
    def __init__(self, checkout, region):
        self.checkout = checkout
        self.region = region

    def total(self):
        if self.region == "us":
            return self.checkout.total() * 1.08
        if self.region == "eu":
            return self.checkout.total() * 1.2
        return self.checkout.total()


class ExpressCheckout(Checkout):
    def __init__(self, amount):
        self.amount = float(amount)

    def total(self):
        return self.amount + 10


class PricingEngine:
    def __init__(self, amount, express=False, loyal_customer=False, region="local"):
        self.amount = float(amount)
        self.express = bool(express)
        self.loyal_customer = bool(loyal_customer)
        self.region = region

    def total(self):
        if self.express and self.loyal_customer:
            base = ExpressCheckout(self.amount).total() - 5
            total = RegionCheckout(BaseCheckout(base), self.region).total()
        elif self.express:
            total = RegionCheckout(ExpressCheckout(self.amount), self.region).total()
        elif self.loyal_customer:
            total = RegionCheckout(PremiumCheckout(self.amount), self.region).total()
        else:
            total = RegionCheckout(BaseCheckout(self.amount), self.region).total()
        return round(total, 2)
