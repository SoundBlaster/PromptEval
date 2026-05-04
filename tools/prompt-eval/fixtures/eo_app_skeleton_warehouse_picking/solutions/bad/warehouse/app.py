class PickingHelper:
    @staticmethod
    def batches(inventory):
        return {
            sku: sorted([dict(batch) for batch in batches], key=lambda batch: batch["expires"])
            for sku, batches in inventory.items()
        }

    @staticmethod
    def remaining(batches):
        return {sku: {batch["batch"]: batch["quantity"] for batch in values} for sku, values in batches.items()}


class WarehouseManager:
    def plan_pick(self, inventory, order):
        batches = PickingHelper.batches(inventory)
        picks = []
        shortages = []
        for line in order:
            missing = line["quantity"]
            for batch in batches.get(line["sku"], []):
                if missing <= 0:
                    break
                taken = min(batch["quantity"], missing)
                if taken:
                    picks.append({"sku": line["sku"], "batch": batch["batch"], "quantity": taken})
                batch["quantity"] -= taken
                missing -= taken
            if missing:
                shortages.append({"sku": line["sku"], "quantity": missing})
        return {"picks": picks, "shortages": shortages, "remaining": PickingHelper.remaining(batches)}

    def commit_pick(self, inventory, order, carrier):
        if not carrier.get("accepted", False):
            return {
                "status": "rejected",
                "reason": "carrier_unavailable",
                "remaining": PickingHelper.remaining(PickingHelper.batches(inventory)),
            }
        plan = self.plan_pick(inventory, order)
        return {"status": "committed", "picks": plan["picks"], "remaining": plan["remaining"]}


def plan_pick(inventory, order):
    return WarehouseManager().plan_pick(inventory, order)


def commit_pick(inventory, order, carrier):
    return WarehouseManager().commit_pick(inventory, order, carrier)
