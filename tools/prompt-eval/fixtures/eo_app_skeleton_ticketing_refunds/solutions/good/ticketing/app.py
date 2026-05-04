from dataclasses import dataclass


@dataclass(frozen=True)
class Event:
    prices: dict
    capacity: dict
    fee: int

    @classmethod
    def from_boundary(cls, event):
        return cls(dict(event["prices"]), dict(event["capacity"]), event["fee_per_ticket"])

    def line_total(self, tier, quantity):
        return (self.prices[tier] + self.fee) * quantity

    def shortage(self, demand):
        return [
            {"tier": tier, "quantity": quantity - self.capacity.get(tier, 0)}
            for tier, quantity in demand.items()
            if quantity > self.capacity.get(tier, 0)
        ]


@dataclass(frozen=True)
class TicketRequest:
    lines: tuple

    @classmethod
    def from_boundary(cls, request):
        return cls(tuple((line["tier"], line["quantity"]) for line in request))

    def demand(self):
        total = {}
        for tier, quantity in self.lines:
            total[tier] = total.get(tier, 0) + quantity
        return total

    def subtotal_in(self, event):
        return sum(event.line_total(tier, quantity) for tier, quantity in self.lines)


@dataclass(frozen=True)
class Buyer:
    early_bird: bool

    @classmethod
    def from_boundary(cls, buyer):
        return cls(bool(buyer.get("early_bird", False)))

    def discount_on(self, subtotal):
        return subtotal // 10 if self.early_bird else 0


@dataclass(frozen=True)
class RefundPolicy:
    full_days: int
    partial_percent: int

    @classmethod
    def from_boundary(cls, policy):
        return cls(policy["full_refund_days"], policy["partial_percent"])

    def percent_for(self, days_before):
        if days_before >= self.full_days:
            return 100
        if days_before > 0:
            return self.partial_percent
        return 0


@dataclass(frozen=True)
class TicketLedger:
    rows: tuple

    @classmethod
    def from_boundary(cls, rows):
        return cls(tuple((row["tier"], row["quantity"], row["unit_price"]) for row in rows))

    def refund(self, requested, percent):
        remaining = []
        amount = 0
        wanted = {row["tier"]: row["quantity"] for row in requested}
        for tier, quantity, unit_price in self.rows:
            take = min(quantity, wanted.get(tier, 0))
            keep = quantity - take
            if take:
                amount += take * unit_price * percent // 100
            if keep:
                remaining.append({"tier": tier, "quantity": keep})
        status = "partial_refund" if 0 < percent < 100 else ("refunded" if percent == 100 else "rejected")
        return {"status": status, "amount": amount, "remaining_tickets": remaining}


def price_tickets(event, request, buyer):
    event = Event.from_boundary(event)
    tickets = TicketRequest.from_boundary(request)
    subtotal = tickets.subtotal_in(event)
    discount = Buyer.from_boundary(buyer).discount_on(subtotal)
    return {
        "subtotal": subtotal,
        "discount": discount,
        "total": subtotal - discount,
        "unavailable": event.shortage(tickets.demand()),
    }


def refund_tickets(order, refund_request, policy):
    percent = RefundPolicy.from_boundary(policy).percent_for(order["event_day"] - refund_request["today"])
    return TicketLedger.from_boundary(order["tickets"]).refund(refund_request["tickets"], percent)
