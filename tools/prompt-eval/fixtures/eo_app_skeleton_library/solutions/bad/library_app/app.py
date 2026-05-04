class LibraryManager:
    def lend_books(self, catalog, patrons, requests, today):
        remaining = {name: raw["available"] for name, raw in catalog.items()}
        approved = []
        denied = []
        for request in requests:
            patron = patrons[request["patron"]]
            copy = request["copy"]
            if remaining.get(copy, 0) <= 0:
                denied.append({"patron": request["patron"], "copy": copy, "reason": "unavailable"})
            elif patron.get("blocked", False):
                denied.append({"patron": request["patron"], "copy": copy, "reason": "blocked"})
            elif patron.get("tier") == "child" and patron.get("active_loans", 0) >= 2:
                denied.append({"patron": request["patron"], "copy": copy, "reason": "loan_limit"})
            else:
                remaining[copy] -= 1
                approved.append({"patron": request["patron"], "copy": copy, "due": today + 14})
        return {"approved": approved, "denied": denied, "remaining": remaining}

    def return_books(self, loans, returns, today):
        closed = []
        fines = []
        for loan in loans:
            for returned in returns:
                if loan["patron"] == returned["patron"] and loan["copy"] == returned["copy"]:
                    closed.append({"patron": loan["patron"], "copy": loan["copy"]})
                    if today > loan["due"]:
                        fines.append({"patron": loan["patron"], "copy": loan["copy"], "amount": today - loan["due"]})
        return {"closed": closed, "fines": fines}


def lend_books(catalog, patrons, requests, today):
    return LibraryManager().lend_books(catalog, patrons, requests, today)


def return_books(loans, returns, today):
    return LibraryManager().return_books(loans, returns, today)
