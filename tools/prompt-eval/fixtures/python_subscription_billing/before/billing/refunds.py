from .money import Money


class RefundRequest:
    def __init__(self, account_id: str, paid: Money, remaining_days: int, period_days: int = 30):
        self.account_id = account_id
        self.paid = paid
        self.remaining_days = remaining_days
        self.period_days = period_days


class RefundEstimate:
    def __init__(self, request: RefundRequest):
        self.request = request

    def amount(self) -> Money:
        cents = int(self.request.paid.cents * self.request.remaining_days / self.request.period_days)
        return Money(cents, self.request.paid.currency)

    def render(self) -> str:
        return f"Refund for {self.request.account_id}: {self.amount().formatted()}"
