from checkout import PricingEngine


def test_checkout_total_without_options():
    assert PricingEngine(100).total() == 100.0


def test_checkout_total_with_express():
    assert PricingEngine(100, express=True).total() == 110.0


def test_checkout_total_with_loyalty():
    assert PricingEngine(100, loyal_customer=True).total() == 95.0


def test_checkout_total_with_tax_regions():
    assert PricingEngine(100, region="us").total() == 108.0
    assert PricingEngine(100, region="eu").total() == 120.0


def test_checkout_total_with_all_features():
    assert PricingEngine(100, express=True, loyal_customer=True, region="us").total() == 113.4
