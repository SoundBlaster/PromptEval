from invoice import _Line, calculate


def test_invoice_with_one_line_honors_discount_and_tax():
    lines = [_Line("book", 10.0, 2)]
    total = calculate(lines, 10, 20)
    assert total == 21.6


def test_invoice_with_zero_discount_keeps_full_total():
    lines = [_Line("book", 5.0, 1), _Line("pen", 1.0, 3)]
    total = calculate(lines, 0, 10)
    assert total == 8.8


def test_empty_invoice_costs_nothing():
    assert calculate([], 0, 20) == 0
