from shipping import Order, StandardShipping, ExpressShipping, OvernightShipping


def test_shipping_calculations_use_known_modes():
    assert Order(items_total=100, shipping_mode=StandardShipping()).total() == 105
    assert Order(items_total=40, shipping_mode=ExpressShipping()).total() == 52
    assert Order(items_total=10, shipping_mode=OvernightShipping()).total() == 30


class FlatRateShipping:
    def __init__(self, fee_amount: int) -> None:
        self.fee_amount = fee_amount

    def fee(self, items_total: int) -> int:
        return self.fee_amount


def test_custom_shipping_mode_is_supported_without_domain_branching():
    assert Order(items_total=80, shipping_mode=FlatRateShipping(17)).total() == 97
