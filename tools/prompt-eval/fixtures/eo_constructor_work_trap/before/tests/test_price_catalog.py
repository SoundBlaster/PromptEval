import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from price_catalog import PriceCatalog


def test_price_of_returns_value(tmp_path):
    path = tmp_path / "prices.json"
    path.write_text('{"prices":[{"sku":"A","price":19.0},{"sku":"B","price":5.5}]}', encoding="utf-8")

    catalog = PriceCatalog(str(path))

    assert catalog.price_of("A") == 19.0
    assert catalog.price_of("B") == 5.5
