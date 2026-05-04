from dataclasses import dataclass


@dataclass(frozen=True)
class RoomType:
    name: str
    base: int
    weekend_surcharge: int
    cleaning_fee: int

    @classmethod
    def named(cls, name, rooms):
        raw = rooms[name]
        return cls(name, raw["base"], raw["weekend_surcharge"], raw["cleaning_fee"])

    def price_for(self, nights):
        return sum(self.base + (self.weekend_surcharge if nights.weekend(day) else 0) for day in nights.days) + self.cleaning_fee


@dataclass(frozen=True)
class Nights:
    days: tuple
    weekend_days: tuple

    @classmethod
    def from_boundary(cls, request):
        return cls(tuple(request["nights"]), tuple(request.get("weekend_nights", ())))

    def weekend(self, day):
        return day in self.weekend_days


@dataclass(frozen=True)
class Guest:
    member: bool

    @classmethod
    def from_boundary(cls, guest):
        return cls(bool(guest.get("member", False)))

    def discount_on(self, subtotal):
        return subtotal // 10 if self.member else 0


@dataclass(frozen=True)
class Availability:
    counts: dict

    @classmethod
    def for_room(cls, rooms, name):
        return cls(dict(rooms[name]["availability"]))

    def unavailable(self, nights):
        return [day for day in nights.days if self.counts.get(day, 0) <= 0]

    def reserve(self, nights):
        remaining = dict(self.counts)
        for day in nights.days:
            remaining[day] -= 1
        return Availability(remaining)

    def snapshot(self):
        return dict(self.counts)


@dataclass(frozen=True)
class Stay:
    room: RoomType
    nights: Nights
    guest: Guest

    def quote(self, availability):
        subtotal = self.room.price_for(self.nights)
        discount = self.guest.discount_on(subtotal)
        return {
            "subtotal": subtotal,
            "discount": discount,
            "total": subtotal - discount,
            "unavailable_nights": availability.unavailable(self.nights),
        }


def _stay(rooms, request, guest):
    room = RoomType.named(request["room_type"], rooms)
    return Stay(room, Nights.from_boundary(request), Guest.from_boundary(guest))


def quote_stay(rooms, request, guest):
    stay = _stay(rooms, request, guest)
    availability = Availability.for_room(rooms, request["room_type"])
    return stay.quote(availability)


def reserve_stay(rooms, request, guest, payment):
    availability = Availability.for_room(rooms, request["room_type"])
    stay = _stay(rooms, request, guest)
    quote = stay.quote(availability)
    if quote["unavailable_nights"]:
        return {"status": "rejected", "reason": "unavailable", "remaining": availability.snapshot()}
    if not payment.get("authorized", False):
        return {"status": "rejected", "reason": "payment_required", "remaining": availability.snapshot()}
    return {
        "status": "reserved",
        "total": quote["total"],
        "remaining": availability.reserve(stay.nights).snapshot(),
    }
