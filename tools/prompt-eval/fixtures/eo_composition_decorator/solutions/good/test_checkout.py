from checkout import BaseAmount, Checkout, ExpressFee, LoyaltyDiscount, RegionalTax


def usd():
    return 0.08


def eur():
    return 0.2


def test_checkout_without_wrappers():
    assert Checkout(BaseAmount(100)).total() == 100.0


def test_checkout_with_express():
    amount = ExpressFee(BaseAmount(100))
    assert Checkout(amount).total() == 110.0


def test_checkout_with_loyal_discount():
    amount = LoyaltyDiscount(BaseAmount(100))
    assert Checkout(amount).total() == 95.0


def test_checkout_with_tax_regions():
    assert Checkout(RegionalTax(BaseAmount(100), usd())).total() == 108.0
    assert Checkout(RegionalTax(BaseAmount(100), eur())).total() == 120.0


def test_checkout_full_pipeline():
    amount = ExpressFee(LoyaltyDiscount(BaseAmount(100)))
    amount = RegionalTax(amount, usd())
    assert Checkout(amount).total() == 113.4
