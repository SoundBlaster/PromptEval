import json


class PriceCatalog:
    """Catalog loaded from disk during construction."""

    def __init__(self, path: str):
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
        self._prices = {item["sku"]: item["price"] for item in payload["prices"]}

    def price_of(self, sku: str) -> float:
        return self._prices[sku]
