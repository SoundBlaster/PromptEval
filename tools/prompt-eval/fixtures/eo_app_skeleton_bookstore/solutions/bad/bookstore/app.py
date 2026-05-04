class DiscountHelper:
    @staticmethod
    def discount(subtotal, cart, customer):
        percent = 0
        if customer.get("loyal", False):
            percent += 10
        if len({item["isbn"] for item in cart}) >= 2:
            percent += 5
        return subtotal * percent // 100


class BookstoreService:
    def quote_order(self, catalog, cart, inventory, customer):
        subtotal = sum(catalog[item["isbn"]]["price"] * item["quantity"] for item in cart)
        unavailable = [item["isbn"] for item in cart if inventory.get(item["isbn"], 0) < item["quantity"]]
        discount = DiscountHelper.discount(subtotal, cart, customer)
        return {"subtotal": subtotal, "discount": discount, "total": subtotal - discount, "unavailable": unavailable}

    def place_order(self, catalog, cart, inventory, customer, payment):
        quote = self.quote_order(catalog, cart, inventory, customer)
        if quote["unavailable"] or not payment.get("authorized", False):
            return {"status": "rejected", "unavailable": quote["unavailable"], "remaining_inventory": dict(inventory)}
        remaining = dict(inventory)
        for item in cart:
            remaining[item["isbn"]] -= item["quantity"]
        return {"status": "placed", "total": quote["total"], "remaining_inventory": remaining}


def quote_order(catalog, cart, inventory, customer):
    return BookstoreService().quote_order(catalog, cart, inventory, customer)


def place_order(catalog, cart, inventory, customer, payment):
    return BookstoreService().place_order(catalog, cart, inventory, customer, payment)
