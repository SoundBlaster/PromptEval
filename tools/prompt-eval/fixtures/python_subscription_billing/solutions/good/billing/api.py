from .catalog import default_catalog
from .invoices import Invoice
from .money import Money
from .refunds import RefundEstimate, RefundRequest
from .subscriptions import LoyaltyDiscount, Subscription


def render_invoice(account_id: str, plan_sku: str, seats: int, period: str, loyalty_percent: int = 0) -> str:
    plan = default_catalog().plan(plan_sku)
    subscription = Subscription(account_id, plan, seats, LoyaltyDiscount(loyalty_percent))
    return Invoice(subscription, period).render()


def render_refund(account_id: str, paid_cents: int, remaining_days: int) -> str:
    request = RefundRequest(account_id, Money(paid_cents), remaining_days)
    return RefundEstimate(request).render()
