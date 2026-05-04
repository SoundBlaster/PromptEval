class ClinicManager:
    def schedule_visits(self, slots, patients, requests):
        remaining = {doctor: dict(raw["capacity"]) for doctor, raw in slots.items()}
        scheduled = []
        denied = []
        for request in requests:
            patient = patients[request["patient"]]
            if patient.get("blocked", False):
                denied.append({"patient": request["patient"], "specialty": request["specialty"], "reason": "blocked"})
                continue
            if request["specialty"] != "general" and request["specialty"] not in patient.get("referrals", []):
                denied.append({"patient": request["patient"], "specialty": request["specialty"], "reason": "referral_required"})
                continue
            assigned = None
            for doctor, raw in slots.items():
                if request["specialty"] in raw["specialties"] and remaining[doctor].get(request["day"], 0) > 0:
                    assigned = doctor
                    remaining[doctor][request["day"]] -= 1
                    break
            if assigned is None:
                denied.append({"patient": request["patient"], "specialty": request["specialty"], "reason": "unavailable"})
            else:
                scheduled.append({"patient": request["patient"], "doctor": assigned, "day": request["day"]})
        return {"scheduled": scheduled, "denied": denied, "remaining": remaining}

    def check_in(self, appointments, arrival):
        for appointment in appointments:
            if appointment["patient"] == arrival["patient"] and appointment["day"] == arrival["day"]:
                if arrival["time"] <= appointment["window_end"]:
                    return {"status": "checked_in", "late_fee": 0}
                return {"status": "late", "late_fee": arrival["time"] - appointment["window_end"]}
        return {"status": "not_scheduled"}


def schedule_visits(slots, patients, requests):
    return ClinicManager().schedule_visits(slots, patients, requests)


def check_in(appointments, arrival):
    return ClinicManager().check_in(appointments, arrival)
