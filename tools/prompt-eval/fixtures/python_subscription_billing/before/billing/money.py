class Money:
    def __init__(self, cents: int, currency: str = "USD"):
        self.cents = cents
        self.currency = currency

    def plus(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("currency mismatch")
        return Money(self.cents + other.cents, self.currency)

    def times(self, count: int) -> "Money":
        return Money(self.cents * count, self.currency)

    def formatted(self) -> str:
        return f"${self.cents / 100:.2f}"
