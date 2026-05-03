from .money import Money


class Plan:
    def __init__(self, sku: str, name: str, monthly_price: Money):
        self.sku = sku
        self.name = name
        self.monthly_price = monthly_price


class PlanCatalog:
    def __init__(self, plans: list[Plan]):
        self.plans = {plan.sku: plan for plan in plans}

    def plan(self, sku: str) -> Plan:
        return self.plans[sku]


def default_catalog() -> PlanCatalog:
    return PlanCatalog([
        Plan("starter", "Starter", Money(1900)),
        Plan("pro", "Pro", Money(4900)),
        Plan("enterprise", "Enterprise", Money(12900)),
    ])
