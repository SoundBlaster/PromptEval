import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from price_catalog import PriceCatalog


def test_price_of_does_not_need_eager_loader_call():
    calls = []

    def loader():
        calls.append("called")
        return {"A": 12.0, "B": 3.0}

    catalog = PriceCatalog(loader)

    assert calls == []

    assert catalog.price_of("A") == 12.0
    assert calls == ["called"]
    assert catalog.price_of("B") == 3.0


def test_price_of_from_path(tmp_path):
    path = tmp_path / "prices.json"
    path.write_text('{"prices":[{"sku":"A","price":19.0},{"sku":"B","price":5.5}]}', encoding="utf-8")

    catalog = PriceCatalog.from_path(str(path))

    assert catalog.price_of("B") == 5.5
