import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from invoice import Invoice, Line


def test_setters_allow_mutation():
    invoice = Invoice()
    invoice.set_lines([Line("hosting", 100), Line("domain", 40)])
    invoice.set_discount(0.10)

    assert invoice.lines == [Line("hosting", 100), Line("domain", 40)]
    assert invoice.discount == 0.10


def test_setter_total_matches_expected_value():
    invoice = Invoice([Line("hosting", 100), Line("domain", 40)])
    invoice.set_discount(0.10)

    assert invoice.total() == pytest.approx(138.6)
