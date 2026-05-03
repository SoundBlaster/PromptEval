from shipping import Order, StandardShipping, ExpressShipping, OvernightShipping


def test_shipping_calculations_use_known_modes():
    assert Order(items_total=100, shipping_mode=StandardShipping()).total() == 105
    assert Order(items_total=40, shipping_mode=ExpressShipping()).total() == 52
    assert Order(items_total=10, shipping_mode=OvernightShipping()).total() == 30
