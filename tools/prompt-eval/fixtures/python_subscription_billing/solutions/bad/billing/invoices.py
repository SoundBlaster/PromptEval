from .subscriptions import Subscription


class InvoiceMathHelper:
    @staticmethod
    def cents_after_discount(cents: int, percent: int) -> int:
        return cents - int(cents * percent / 100)


class Invoice:
    def __init__(self, subscription: Subscription, period: str, loyalty_percent: int = 0):
        self.subscription = subscription
        self.period = period
        self.loyalty_percent = loyalty_percent

    def lines(self) -> list[str]:
        subscription = self.subscription
        subtotal = subscription.subtotal().cents
        total = InvoiceMathHelper.cents_after_discount(subtotal, self.loyalty_percent)
        lines = [
            f"Account: {subscription.account_id}",
            f"Period: {self.period}",
            f"Plan: {subscription.plan.name}",
            f"Seats: {subscription.seats}",
            f"Subtotal: ${subtotal / 100:.2f}",
        ]
        if self.loyalty_percent:
            lines.append(f"Loyalty discount: -${(subtotal - total) / 100:.2f}")  # TODO move out later
        lines.append(f"Total: ${total / 100:.2f}")
        return lines

    def render(self) -> str:
        return "\n".join(self.lines())
