from dataclasses import dataclass


@dataclass(frozen=True)
class Book:
    isbn: str
    price: int

    @classmethod
    def from_catalog(cls, isbn, catalog):
        return cls(isbn, catalog[isbn]["price"])


@dataclass(frozen=True)
class Line:
    book: Book
    quantity: int

    def subtotal(self):
        return self.book.price * self.quantity

    def reserve_in(self, shelf):
        return shelf.reserve(self.book.isbn, self.quantity)


@dataclass(frozen=True)
class Cart:
    lines: tuple[Line, ...]

    @classmethod
    def from_boundary(cls, catalog, cart):
        return cls(tuple(Line(Book.from_catalog(item["isbn"], catalog), item["quantity"]) for item in cart))

    def subtotal(self):
        return sum(line.subtotal() for line in self.lines)

    def unavailable_in(self, shelf):
        return [line.book.isbn for line in self.lines if not shelf.has(line.book.isbn, line.quantity)]

    def reserve_in(self, shelf):
        reserved = shelf
        for line in self.lines:
            reserved = line.reserve_in(reserved)
        return reserved

    def has_bundle(self):
        return len({line.book.isbn for line in self.lines}) >= 2


@dataclass(frozen=True)
class Shelf:
    copies: dict[str, int]

    def has(self, isbn, quantity):
        return self.copies.get(isbn, 0) >= quantity

    def reserve(self, isbn, quantity):
        updated = dict(self.copies)
        updated[isbn] = updated[isbn] - quantity
        return Shelf(updated)

    def snapshot(self):
        return dict(self.copies)


@dataclass(frozen=True)
class Reader:
    loyal: bool

    @classmethod
    def from_boundary(cls, customer):
        return cls(bool(customer.get("loyal", False)))


@dataclass(frozen=True)
class Discounts:
    cart: Cart
    reader: Reader

    def amount(self):
        basis = 0
        if self.reader.loyal:
            basis += 10
        if self.cart.has_bundle():
            basis += 5
        return self.cart.subtotal() * basis // 100


@dataclass(frozen=True)
class Quote:
    cart: Cart
    discounts: Discounts
    unavailable: tuple[str, ...]

    def as_dict(self):
        subtotal = self.cart.subtotal()
        discount = self.discounts.amount()
        return {
            "subtotal": subtotal,
            "discount": discount,
            "total": subtotal - discount,
            "unavailable": list(self.unavailable),
        }


@dataclass(frozen=True)
class Payment:
    authorized: bool

    @classmethod
    def from_boundary(cls, payment):
        return cls(bool(payment.get("authorized", False)))


def quote_order(catalog, cart, inventory, customer):
    books = Cart.from_boundary(catalog, cart)
    reader = Reader.from_boundary(customer)
    shelf = Shelf(dict(inventory))
    return Quote(books, Discounts(books, reader), tuple(books.unavailable_in(shelf))).as_dict()


def place_order(catalog, cart, inventory, customer, payment):
    books = Cart.from_boundary(catalog, cart)
    shelf = Shelf(dict(inventory))
    unavailable = tuple(books.unavailable_in(shelf))
    quote = Quote(books, Discounts(books, Reader.from_boundary(customer)), unavailable).as_dict()
    if unavailable or not Payment.from_boundary(payment).authorized:
        return {"status": "rejected", "unavailable": list(unavailable), "remaining_inventory": dict(inventory)}
    reserved = books.reserve_in(shelf)
    return {"status": "placed", "total": quote["total"], "remaining_inventory": reserved.snapshot()}
