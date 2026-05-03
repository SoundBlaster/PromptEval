"""Immutable invoice using explicit immutable dependencies."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Line:
    """A single invoice line."""

    label: str
    amount: int


class Invoice:
    """Immutable value object with pure value updates."""

    def __init__(self, lines=None, tax_rate=0.1, discount=0.0):
        self._lines = tuple(Line(line.label, line.amount) for line in (lines or ()))
        self._tax_rate = tax_rate
        self._discount = discount

    @property
    def lines(self):
        return self._lines

    @property
    def discount(self):
        return self._discount

    def with_line(self, line: Line):
        return Invoice(self._lines + (line,), self._tax_rate, self._discount)

    def with_discount(self, discount: float):
        return Invoice(self._lines, self._tax_rate, discount)

    def total(self):
        subtotal = sum(line.amount for line in self._lines)
        discounted = subtotal * (1 - self._discount)
        return discounted * (1 + self._tax_rate)
