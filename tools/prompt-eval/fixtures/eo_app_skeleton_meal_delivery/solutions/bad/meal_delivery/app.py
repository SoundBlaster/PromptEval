class DeliveryHelper:
    @staticmethod
    def demand(cart):
        total = {}
        for line in cart:
            total[line["item"]] = total.get(line["item"], 0) + line["quantity"]
        return total


class MealDeliveryService:
    def quote_delivery(self, menu, cart, address, customer):
        subtotal = sum(menu[line["item"]]["price"] * line["quantity"] for line in cart)
        demand = DeliveryHelper.demand(cart)
        unavailable = [
            {"item": name, "quantity": quantity - menu.get(name, {"available": 0})["available"]}
            for name, quantity in demand.items()
            if quantity > menu.get(name, {"available": 0})["available"]
        ]
        fee = address["fees"][address["zone"]]
        discount = subtotal // 10 if customer.get("loyal", False) else 0
        return {
            "subtotal": subtotal,
            "delivery_fee": fee,
            "discount": discount,
            "total": subtotal + fee - discount,
            "unavailable": unavailable,
            "minimum_missing": max(0, address["minimum"] - subtotal),
        }

    def place_delivery_order(self, menu, cart, kitchen, address, customer, payment):
        remaining = {name: raw["available"] for name, raw in menu.items()}
        if not kitchen.get("open", False):
            return {"status": "rejected", "reason": "kitchen_closed", "remaining": remaining}
        quote = self.quote_delivery(menu, cart, address, customer)
        if quote["unavailable"]:
            return {"status": "rejected", "reason": "unavailable", "remaining": remaining}
        if quote["minimum_missing"]:
            return {"status": "rejected", "reason": "minimum_not_met", "remaining": remaining}
        if not payment.get("authorized", False):
            return {"status": "rejected", "reason": "payment_required", "remaining": remaining}
        for name, quantity in DeliveryHelper.demand(cart).items():
            remaining[name] -= quantity
        return {"status": "placed", "total": quote["total"], "remaining": remaining}


def quote_delivery(menu, cart, address, customer):
    return MealDeliveryService().quote_delivery(menu, cart, address, customer)


def place_delivery_order(menu, cart, kitchen, address, customer, payment):
    return MealDeliveryService().place_delivery_order(menu, cart, kitchen, address, customer, payment)
