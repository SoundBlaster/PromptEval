from .catalog import Plan
from .money import Money


class LoyaltyDiscount:
    def __init__(self, percent: int):
        if percent < 0 or percent > 100:
            raise ValueError("discount percent out of range")
        self.percent = percent

    def apply_to(self, subtotal: Money) -> Money:
        return subtotal.percent(self.percent)


class Subscription:
    def __init__(self, account_id: str, plan: Plan, seats: int, discount=None):
        self.account_id = account_id
        self.plan = plan
        self.seats = seats
        self.discount = discount or LoyaltyDiscount(0)

    def subtotal(self) -> Money:
        return self.plan.monthly_price.times(self.seats)

    def discount_amount(self) -> Money:
        return self.discount.apply_to(self.subtotal())

    def total(self) -> Money:
        return self.subtotal().minus(self.discount_amount())
