from .subscriptions import Subscription


class Invoice:
    def __init__(self, subscription: Subscription, period: str):
        self.subscription = subscription
        self.period = period

    def lines(self) -> list[str]:
        subscription = self.subscription
        return [
            f"Account: {subscription.account_id}",
            f"Period: {self.period}",
            f"Plan: {subscription.plan.name}",
            f"Seats: {subscription.seats}",
            f"Subtotal: {subscription.subtotal().formatted()}",
            f"Total: {subscription.subtotal().formatted()}",
        ]

    def render(self) -> str:
        return "\n".join(self.lines())
