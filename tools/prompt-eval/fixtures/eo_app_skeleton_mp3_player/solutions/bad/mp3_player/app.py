class PlaylistHelper:
    @staticmethod
    def total(tracks):
        return sum(track["seconds"] for track in tracks)


class Mp3PlayerManager:
    def build_playlist(self, library, requested, profile):
        tracks = []
        skipped = []
        for key in requested:
            raw = library.get(key)
            if raw is None:
                skipped.append({"id": key, "reason": "unavailable"})
            elif raw.get("explicit", False) and profile["age"] < 13:
                skipped.append({"id": key, "reason": "restricted"})
            elif PlaylistHelper.total(tracks) + raw["seconds"] > profile["max_seconds"]:
                skipped.append({"id": key, "reason": "too_long"})
            else:
                tracks.append({"id": key, "title": raw["title"], "seconds": raw["seconds"]})
        return {"tracks": tracks, "skipped": skipped, "total_seconds": PlaylistHelper.total(tracks)}

    def start_session(self, playlist, device, account):
        if not account.get("active", False):
            return {"status": "rejected", "reason": "inactive_account"}
        if device.get("offline", False):
            missing = [track["id"] for track in playlist.get("tracks", []) if track["id"] not in device.get("cached", [])]
            if missing:
                return {"status": "rejected", "reason": "not_cached", "missing": missing}
        return {
            "status": "playing",
            "track_count": len(playlist.get("tracks", [])),
            "duration": playlist.get("total_seconds", 0),
        }


def build_playlist(library, requested, profile):
    return Mp3PlayerManager().build_playlist(library, requested, profile)


def start_session(playlist, device, account):
    return Mp3PlayerManager().start_session(playlist, device, account)
