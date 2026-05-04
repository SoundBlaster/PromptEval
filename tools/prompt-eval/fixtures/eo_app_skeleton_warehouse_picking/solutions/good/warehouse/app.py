from dataclasses import dataclass


@dataclass(frozen=True)
class Batch:
    sku: str
    name: str
    quantity: int
    expires: int

    def take(self, requested):
        amount = min(self.quantity, requested)
        return amount, Batch(self.sku, self.name, self.quantity - amount, self.expires)


@dataclass(frozen=True)
class Stock:
    batches: dict

    @classmethod
    def from_boundary(cls, inventory):
        return cls(
            {
                sku: tuple(
                    sorted(
                        (Batch(sku, raw["batch"], raw["quantity"], raw["expires"]) for raw in batches),
                        key=lambda batch: batch.expires,
                    )
                )
                for sku, batches in inventory.items()
            }
        )

    def pick(self, sku, quantity):
        remaining = quantity
        picks = []
        updated = dict(self.batches)
        next_batches = []
        for batch in self.batches.get(sku, ()):
            amount, rest = batch.take(remaining)
            if amount:
                picks.append({"sku": sku, "batch": batch.name, "quantity": amount})
            remaining -= amount
            next_batches.append(rest)
        updated[sku] = tuple(next_batches)
        shortage = [] if remaining == 0 else [{"sku": sku, "quantity": remaining}]
        return picks, shortage, Stock(updated)

    def snapshot(self):
        return {
            sku: {batch.name: batch.quantity for batch in batches}
            for sku, batches in self.batches.items()
        }


@dataclass(frozen=True)
class Order:
    lines: tuple

    @classmethod
    def from_boundary(cls, order):
        return cls(tuple((line["sku"], line["quantity"]) for line in order))

    def plan_in(self, stock):
        picks = []
        shortages = []
        current = stock
        for sku, quantity in self.lines:
            selected, missing, current = current.pick(sku, quantity)
            picks.extend(selected)
            shortages.extend(missing)
        return {"picks": picks, "shortages": shortages, "remaining": current.snapshot()}


def plan_pick(inventory, order):
    return Order.from_boundary(order).plan_in(Stock.from_boundary(inventory))


def commit_pick(inventory, order, carrier):
    stock = Stock.from_boundary(inventory)
    if not carrier.get("accepted", False):
        return {"status": "rejected", "reason": "carrier_unavailable", "remaining": stock.snapshot()}
    plan = Order.from_boundary(order).plan_in(stock)
    return {"status": "committed", "picks": plan["picks"], "remaining": plan["remaining"]}
