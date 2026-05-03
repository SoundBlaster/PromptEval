from shop.domain import Order, Receipt

def test_receipt_render():
    text = Receipt(Order("Ada", 1234)).render()
    assert "Ada" in text
    assert "$12.34" in text
