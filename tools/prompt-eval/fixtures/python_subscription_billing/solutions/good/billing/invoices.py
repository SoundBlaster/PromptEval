from .subscriptions import Subscription


class Invoice:
    def __init__(self, subscription: Subscription, period: str):
        self.subscription = subscription
        self.period = period

    def lines(self) -> list[str]:
        subscription = self.subscription
        lines = [
            f"Account: {subscription.account_id}",
            f"Period: {self.period}",
            f"Plan: {subscription.plan.name}",
            f"Seats: {subscription.seats}",
            f"Subtotal: {subscription.subtotal().formatted()}",
        ]
        if subscription.discount.percent:
            lines.append(f"Loyalty discount: -{subscription.discount_amount().formatted()}")
        lines.append(f"Total: {subscription.total().formatted()}")
        return lines

    def render(self) -> str:
        return "\n".join(self.lines())
