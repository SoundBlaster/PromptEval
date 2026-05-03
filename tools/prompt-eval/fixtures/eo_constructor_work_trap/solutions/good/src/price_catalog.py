import json
from collections.abc import Callable


def parse_prices(path: str) -> dict[str, float]:
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return {item["sku"]: item["price"] for item in payload["prices"]}


class PriceCatalog:
    """Price catalog that delays parsing until prices are requested."""

    def __init__(self, loader: Callable[[], dict[str, float]]):
        self._loader = loader
        self._prices: dict[str, float] | None = None

    @classmethod
    def from_path(cls, path: str) -> "PriceCatalog":
        return cls(lambda: parse_prices(path))

    def _ensure_loaded(self) -> None:
        if self._prices is None:
            self._prices = self._loader()

    def price_of(self, sku: str) -> float:
        self._ensure_loaded()
        return self._prices[sku]
