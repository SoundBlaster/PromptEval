"""Mutable invoice implementation with setter-driven state updates."""

from dataclasses import dataclass


@dataclass
class Line:
    """A single invoice line."""

    label: str
    amount: int


class Invoice:
    """Mutable aggregate updated through explicit setter methods."""

    def __init__(self, lines=None, tax_rate=0.1):
        self.lines = [] if lines is None else list(lines)
        self.tax_rate = tax_rate
        self.discount = 0.0

    def set_lines(self, lines):
        self.lines = list(lines)

    def set_discount(self, discount):
        self.discount = discount

    def add_line(self, line: Line):
        self.lines.append(line)

    def total(self):
        subtotal = sum(line.amount for line in self.lines)
        discounted = subtotal * (1 - self.discount)
        return discounted * (1 + self.tax_rate)
