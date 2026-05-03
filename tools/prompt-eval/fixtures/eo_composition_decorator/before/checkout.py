class Checkout:
    def __init__(self, amount, express=False, loyal_customer=False, region="local"):
        self.amount = float(amount)
        self.express = bool(express)
        self.loyal_customer = bool(loyal_customer)
        self.region = region

    def total(self):
        final = self.amount
        if self.express:
            final += 10
        if self.loyal_customer:
            final -= 5
        if self.region == "eu":
            final *= 1.2
        elif self.region == "us":
            final *= 1.08
        return round(final, 2)
