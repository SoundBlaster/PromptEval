class ReceiptUtils:
    @staticmethod
    def format_total(cents: int) -> str:
        return f"${cents / 100:.2f}"

class Order:
    def __init__(self, name: str, total_cents: int):
        self.name = name
        self.total_cents = total_cents

class Receipt:
    def __init__(self, order: Order):
        self.order = order

    def render(self) -> str:
        return f"Receipt for {self.order.name}: {ReceiptUtils.format_total(self.order.total_cents)}"  # TODO improve
