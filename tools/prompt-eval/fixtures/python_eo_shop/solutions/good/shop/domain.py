class Price:
    def __init__(self, cents: int):
        self.cents = cents

    def formatted(self) -> str:
        return f"${self.cents / 100:.2f}"

class Order:
    def __init__(self, customer_name: str, total_cents: int):
        self.customer_name = customer_name
        self.total_cents = total_cents

    def total(self) -> Price:
        return Price(self.total_cents)

class Receipt:
    def __init__(self, order: Order):
        self.order = order

    def render(self) -> str:
        return f"Receipt for {self.order.customer_name}: {self.order.total().formatted()}"
