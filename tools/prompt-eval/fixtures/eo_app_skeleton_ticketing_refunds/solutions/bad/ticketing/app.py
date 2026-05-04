class TicketingService:
    def price_tickets(self, event, request, buyer):
        subtotal = 0
        demand = {}
        for line in request:
            subtotal += (event["prices"][line["tier"]] + event["fee_per_ticket"]) * line["quantity"]
            demand[line["tier"]] = demand.get(line["tier"], 0) + line["quantity"]
        unavailable = [
            {"tier": tier, "quantity": quantity - event["capacity"].get(tier, 0)}
            for tier, quantity in demand.items()
            if quantity > event["capacity"].get(tier, 0)
        ]
        discount = subtotal // 10 if buyer.get("early_bird", False) else 0
        return {"subtotal": subtotal, "discount": discount, "total": subtotal - discount, "unavailable": unavailable}

    def refund_tickets(self, order, refund_request, policy):
        days = order["event_day"] - refund_request["today"]
        percent = 100 if days >= policy["full_refund_days"] else (policy["partial_percent"] if days > 0 else 0)
        wanted = {row["tier"]: row["quantity"] for row in refund_request["tickets"]}
        amount = 0
        remaining = []
        for row in order["tickets"]:
            take = min(row["quantity"], wanted.get(row["tier"], 0))
            keep = row["quantity"] - take
            amount += take * row["unit_price"] * percent // 100
            if keep:
                remaining.append({"tier": row["tier"], "quantity": keep})
        status = "partial_refund" if 0 < percent < 100 else ("refunded" if percent == 100 else "rejected")
        return {"status": status, "amount": amount, "remaining_tickets": remaining}


def price_tickets(event, request, buyer):
    return TicketingService().price_tickets(event, request, buyer)


def refund_tickets(order, refund_request, policy):
    return TicketingService().refund_tickets(order, refund_request, policy)
