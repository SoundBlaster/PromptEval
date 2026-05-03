from .catalog import Plan
from .money import Money


class Subscription:
    def __init__(self, account_id: str, plan: Plan, seats: int):
        self.account_id = account_id
        self.plan = plan
        self.seats = seats

    def subtotal(self) -> Money:
        return self.plan.monthly_price.times(self.seats)
