from dataclasses import dataclass
from typing import Protocol


class ShippingMode(Protocol):
    def fee(self, items_total: int) -> int:
        ...


@dataclass(frozen=True)
class Order:
    items_total: int
    shipping_mode: ShippingMode

    def total(self) -> int:
        return self.items_total + self.shipping_mode.fee(self.items_total)


@dataclass(frozen=True)
class StandardShipping:
    fee_amount: int = 5

    def fee(self, items_total: int) -> int:
        return self.fee_amount


@dataclass(frozen=True)
class ExpressShipping:
    fee_amount: int = 12

    def fee(self, items_total: int) -> int:
        return self.fee_amount


@dataclass(frozen=True)
class OvernightShipping:
    fee_amount: int = 20

    def fee(self, items_total: int) -> int:
        return self.fee_amount
