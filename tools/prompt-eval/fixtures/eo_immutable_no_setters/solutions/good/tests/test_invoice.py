import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from invoice import Invoice, Line


def test_with_line_returns_new_invoice_without_mutation():
    base = Invoice([Line("hosting", 100)], tax_rate=0.1)
    expanded = base.with_line(Line("domain", 40))

    assert base.lines == (Line("hosting", 100),)
    assert expanded.lines == (Line("hosting", 100), Line("domain", 40))


def test_with_discount_does_not_mutate_original():
    base = Invoice([Line("hosting", 100)], tax_rate=0.1)
    discounted = base.with_discount(0.10)

    assert base.discount == 0.0
    assert discounted.discount == 0.10
    assert base.total() == pytest.approx(110.0)
    assert discounted.total() == pytest.approx(99.0)
