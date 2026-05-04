from dataclasses import dataclass


@dataclass(frozen=True)
class Patient:
    name: str
    blocked: bool
    referrals: tuple

    @classmethod
    def named(cls, name, patients):
        raw = patients[name]
        return cls(name, bool(raw.get("blocked", False)), tuple(raw.get("referrals", ())))

    def denial_for(self, specialty):
        if self.blocked:
            return "blocked"
        if specialty != "general" and specialty not in self.referrals:
            return "referral_required"
        return None


@dataclass(frozen=True)
class Doctor:
    name: str
    specialties: tuple
    capacity: dict

    def can_see(self, specialty, day):
        return specialty in self.specialties and self.capacity.get(day, 0) > 0

    def reserve(self, day):
        remaining = dict(self.capacity)
        remaining[day] -= 1
        return Doctor(self.name, self.specialties, remaining)


@dataclass(frozen=True)
class Clinic:
    doctors: tuple

    @classmethod
    def from_boundary(cls, slots):
        return cls(
            tuple(
                Doctor(name, tuple(raw["specialties"]), dict(raw["capacity"]))
                for name, raw in slots.items()
            )
        )

    def assign(self, request):
        doctors = list(self.doctors)
        for index, doctor in enumerate(doctors):
            if doctor.can_see(request.specialty, request.day):
                doctors[index] = doctor.reserve(request.day)
                return doctor.name, Clinic(tuple(doctors))
        return None, self

    def remaining(self):
        return {doctor.name: dict(doctor.capacity) for doctor in self.doctors}


@dataclass(frozen=True)
class VisitRequest:
    patient: Patient
    specialty: str
    day: int

    @classmethod
    def from_boundary(cls, raw, patients):
        return cls(Patient.named(raw["patient"], patients), raw["specialty"], raw["day"])

    def denied(self):
        reason = self.patient.denial_for(self.specialty)
        if reason:
            return {"patient": self.patient.name, "specialty": self.specialty, "reason": reason}
        return None

    def unavailable(self):
        return {"patient": self.patient.name, "specialty": self.specialty, "reason": "unavailable"}

    def scheduled(self, doctor):
        return {"patient": self.patient.name, "doctor": doctor, "day": self.day}


@dataclass(frozen=True)
class Appointment:
    patient: str
    day: int
    start: int
    end: int

    @classmethod
    def from_boundary(cls, raw):
        return cls(raw["patient"], raw["day"], raw["window_start"], raw["window_end"])

    def matches(self, arrival):
        return self.patient == arrival["patient"] and self.day == arrival["day"]

    def check(self, arrival):
        if arrival["time"] <= self.end:
            return {"status": "checked_in", "late_fee": 0}
        return {"status": "late", "late_fee": arrival["time"] - self.end}


def schedule_visits(slots, patients, requests):
    clinic = Clinic.from_boundary(slots)
    scheduled = []
    denied = []
    for raw in requests:
        request = VisitRequest.from_boundary(raw, patients)
        denial = request.denied()
        if denial:
            denied.append(denial)
            continue
        doctor, clinic = clinic.assign(request)
        if doctor is None:
            denied.append(request.unavailable())
        else:
            scheduled.append(request.scheduled(doctor))
    return {"scheduled": scheduled, "denied": denied, "remaining": clinic.remaining()}


def check_in(appointments, arrival):
    for appointment in (Appointment.from_boundary(raw) for raw in appointments):
        if appointment.matches(arrival):
            return appointment.check(arrival)
    return {"status": "not_scheduled"}
