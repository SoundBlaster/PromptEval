class HotelBookingService:
    def quote_stay(self, rooms, request, guest):
        room = rooms[request["room_type"]]
        subtotal = room["cleaning_fee"]
        unavailable = []
        for day in request["nights"]:
            if room["availability"].get(day, 0) <= 0:
                unavailable.append(day)
            subtotal += room["base"]
            if day in request.get("weekend_nights", []):
                subtotal += room["weekend_surcharge"]
        discount = subtotal // 10 if guest.get("member", False) else 0
        return {"subtotal": subtotal, "discount": discount, "total": subtotal - discount, "unavailable_nights": unavailable}

    def reserve_stay(self, rooms, request, guest, payment):
        quote = self.quote_stay(rooms, request, guest)
        remaining = dict(rooms[request["room_type"]]["availability"])
        if quote["unavailable_nights"]:
            return {"status": "rejected", "reason": "unavailable", "remaining": remaining}
        if not payment.get("authorized", False):
            return {"status": "rejected", "reason": "payment_required", "remaining": remaining}
        for day in request["nights"]:
            remaining[day] -= 1
        return {"status": "reserved", "total": quote["total"], "remaining": remaining}


def quote_stay(rooms, request, guest):
    return HotelBookingService().quote_stay(rooms, request, guest)


def reserve_stay(rooms, request, guest, payment):
    return HotelBookingService().reserve_stay(rooms, request, guest, payment)
