from dataclasses import dataclass


@dataclass(frozen=True)
class Order:
    items_total: int
    shipping_mode: object

    def total(self) -> int:
        if isinstance(self.shipping_mode, StandardShipping):
            return self.items_total + self.shipping_mode.fee(self.items_total)
        if isinstance(self.shipping_mode, ExpressShipping):
            return self.items_total + self.shipping_mode.fee(self.items_total)
        if isinstance(self.shipping_mode, OvernightShipping):
            return self.items_total + self.shipping_mode.fee(self.items_total)
        raise ValueError("Unknown shipping mode")


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
