from dataclasses import dataclass


@dataclass(frozen=True)
class Dish:
    name: str
    price: int
    available: int

    def line_total(self, quantity):
        return self.price * quantity

    def reserve(self, quantity):
        return Dish(self.name, self.price, self.available - quantity)


@dataclass(frozen=True)
class Menu:
    dishes: dict

    @classmethod
    def from_boundary(cls, menu):
        return cls({name: Dish(name, raw["price"], raw["available"]) for name, raw in menu.items()})

    def subtotal(self, cart):
        return sum(self.dishes[name].line_total(quantity) for name, quantity in cart.lines)

    def unavailable(self, demand):
        return [
            {"item": name, "quantity": quantity - self.dishes.get(name, Dish(name, 0, 0)).available}
            for name, quantity in demand.items()
            if quantity > self.dishes.get(name, Dish(name, 0, 0)).available
        ]

    def reserve(self, demand):
        dishes = dict(self.dishes)
        for name, quantity in demand.items():
            dishes[name] = dishes[name].reserve(quantity)
        return Menu(dishes)

    def remaining(self):
        return {name: dish.available for name, dish in self.dishes.items()}


@dataclass(frozen=True)
class Cart:
    lines: tuple

    @classmethod
    def from_boundary(cls, cart):
        return cls(tuple((line["item"], line["quantity"]) for line in cart))

    def demand(self):
        total = {}
        for name, quantity in self.lines:
            total[name] = total.get(name, 0) + quantity
        return total


@dataclass(frozen=True)
class Destination:
    zone: str
    fees: dict
    minimum: int

    @classmethod
    def from_boundary(cls, address):
        return cls(address["zone"], dict(address["fees"]), address["minimum"])

    def fee(self):
        return self.fees[self.zone]

    def missing_for(self, subtotal):
        return max(0, self.minimum - subtotal)


@dataclass(frozen=True)
class Customer:
    loyal: bool

    @classmethod
    def from_boundary(cls, customer):
        return cls(bool(customer.get("loyal", False)))

    def discount_on(self, subtotal):
        return subtotal // 10 if self.loyal else 0


def quote_delivery(menu, cart, address, customer):
    menu = Menu.from_boundary(menu)
    cart = Cart.from_boundary(cart)
    destination = Destination.from_boundary(address)
    subtotal = menu.subtotal(cart)
    discount = Customer.from_boundary(customer).discount_on(subtotal)
    return {
        "subtotal": subtotal,
        "delivery_fee": destination.fee(),
        "discount": discount,
        "total": subtotal + destination.fee() - discount,
        "unavailable": menu.unavailable(cart.demand()),
        "minimum_missing": destination.missing_for(subtotal),
    }


def place_delivery_order(menu, cart, kitchen, address, customer, payment):
    menu_obj = Menu.from_boundary(menu)
    if not kitchen.get("open", False):
        return {"status": "rejected", "reason": "kitchen_closed", "remaining": menu_obj.remaining()}
    quote = quote_delivery(menu, cart, address, customer)
    if quote["unavailable"]:
        return {"status": "rejected", "reason": "unavailable", "remaining": menu_obj.remaining()}
    if quote["minimum_missing"]:
        return {"status": "rejected", "reason": "minimum_not_met", "remaining": menu_obj.remaining()}
    if not payment.get("authorized", False):
        return {"status": "rejected", "reason": "payment_required", "remaining": menu_obj.remaining()}
    reserved = menu_obj.reserve(Cart.from_boundary(cart).demand())
    return {"status": "placed", "total": quote["total"], "remaining": reserved.remaining()}
