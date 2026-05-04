from dataclasses import dataclass


@dataclass(frozen=True)
class Patron:
    name: str
    tier: str
    active_loans: int
    blocked: bool

    @classmethod
    def named(cls, name, patrons):
        raw = patrons[name]
        return cls(name, raw["tier"], raw["active_loans"], raw["blocked"])

    def denial_for(self, copy):
        if self.blocked:
            return {"patron": self.name, "copy": copy.name, "reason": "blocked"}
        if self.tier == "child" and self.active_loans >= 2:
            return {"patron": self.name, "copy": copy.name, "reason": "loan_limit"}
        return None


@dataclass(frozen=True)
class Copy:
    name: str
    available: int

    def present(self):
        return self.available > 0

    def lend(self):
        return Copy(self.name, self.available - 1)


@dataclass(frozen=True)
class Shelf:
    copies: dict[str, Copy]

    @classmethod
    def from_catalog(cls, catalog):
        return cls({name: Copy(name, raw["available"]) for name, raw in catalog.items()})

    def copy(self, name):
        return self.copies.get(name, Copy(name, 0))

    def lend(self, copy):
        updated = dict(self.copies)
        updated[copy.name] = copy.lend()
        return Shelf(updated)

    def snapshot(self):
        return {name: copy.available for name, copy in self.copies.items()}


@dataclass(frozen=True)
class Request:
    patron: Patron
    copy: Copy

    def denial(self):
        if not self.copy.present():
            return {"patron": self.patron.name, "copy": self.copy.name, "reason": "unavailable"}
        return self.patron.denial_for(self.copy)

    def loan(self, today):
        return {"patron": self.patron.name, "copy": self.copy.name, "due": today + 14}


@dataclass(frozen=True)
class Lending:
    shelf: Shelf
    patrons: dict
    today: int

    def process(self, requests):
        approved = []
        denied = []
        shelf = self.shelf
        for raw in requests:
            copy = shelf.copy(raw["copy"])
            request = Request(Patron.named(raw["patron"], self.patrons), copy)
            denial = request.denial()
            if denial:
                denied.append(denial)
            else:
                approved.append(request.loan(self.today))
                shelf = shelf.lend(copy)
        return {"approved": approved, "denied": denied, "remaining": shelf.snapshot()}


@dataclass(frozen=True)
class Loan:
    patron: str
    copy: str
    due: int

    @classmethod
    def from_boundary(cls, raw):
        return cls(raw["patron"], raw["copy"], raw["due"])

    def matches(self, returned):
        return self.patron == returned["patron"] and self.copy == returned["copy"]

    def close(self):
        return {"patron": self.patron, "copy": self.copy}

    def fine(self, today):
        if today <= self.due:
            return None
        return {"patron": self.patron, "copy": self.copy, "amount": today - self.due}


def lend_books(catalog, patrons, requests, today):
    return Lending(Shelf.from_catalog(catalog), patrons, today).process(requests)


def return_books(loans, returns, today):
    closed = []
    fines = []
    for loan in (Loan.from_boundary(raw) for raw in loans):
        if any(loan.matches(returned) for returned in returns):
            closed.append(loan.close())
            fine = loan.fine(today)
            if fine:
                fines.append(fine)
    return {"closed": closed, "fines": fines}
