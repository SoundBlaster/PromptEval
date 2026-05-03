from checkout import Checkout


def test_checkout_total_without_options():
    assert Checkout(100).total() == 100.0


def test_checkout_total_with_express():
    assert Checkout(100, express=True).total() == 110.0


def test_checkout_total_with_loyalty():
    assert Checkout(100, loyal_customer=True).total() == 95.0


def test_checkout_total_with_tax_regions():
    assert Checkout(100, region="us").total() == 108.0
    assert Checkout(100, region="eu").total() == 120.0


def test_checkout_total_with_all_features():
    assert Checkout(100, express=True, loyal_customer=True, region="us").total() == 113.4
