"""Mutable implementation that looks similar but mutates public state."""

from dataclasses import dataclass


@dataclass
class Line:
    """A single invoice line."""

    label: str
    amount: int


class Invoice:
    """Bad: same intent as immutable API, but still mutates public state."""

    def __init__(self, lines=None, tax_rate=0.1, discount=0.0):
        self.lines = [] if lines is None else list(lines)
        self.tax_rate = tax_rate
        self.discount = discount

    def set_discount(self, discount):
        self.discount = discount

    def with_line(self, line: Line):
        self.lines.append(line)
        return self

    def with_discount(self, discount: float):
        self.discount = discount
        return self

    def total(self):
        subtotal = sum(line.amount for line in self.lines)
        discounted = subtotal * (1 - self.discount)
        return discounted * (1 + self.tax_rate)
