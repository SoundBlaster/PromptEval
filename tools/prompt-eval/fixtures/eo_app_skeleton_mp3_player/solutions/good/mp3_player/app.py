from dataclasses import dataclass


@dataclass(frozen=True)
class Track:
    key: str
    title: str
    seconds: int
    explicit: bool

    def visible_to(self, listener):
        return not self.explicit or listener.adult()

    def as_dict(self):
        return {"id": self.key, "title": self.title, "seconds": self.seconds}


@dataclass(frozen=True)
class Catalog:
    tracks: dict

    @classmethod
    def from_boundary(cls, library):
        return cls(
            {
                key: Track(key, raw["title"], raw["seconds"], raw.get("explicit", False))
                for key, raw in library.items()
            }
        )

    def track(self, key):
        return self.tracks.get(key)


@dataclass(frozen=True)
class Listener:
    age: int
    max_seconds: int

    @classmethod
    def from_boundary(cls, profile):
        return cls(profile["age"], profile["max_seconds"])

    def adult(self):
        return self.age >= 13


@dataclass(frozen=True)
class Playlist:
    tracks: tuple
    skipped: tuple

    def total_seconds(self):
        return sum(track.seconds for track in self.tracks)

    def include(self, track):
        return Playlist(self.tracks + (track,), self.skipped)

    def skip(self, key, reason):
        return Playlist(self.tracks, self.skipped + ({"id": key, "reason": reason},))

    def as_dict(self):
        return {
            "tracks": [track.as_dict() for track in self.tracks],
            "skipped": list(self.skipped),
            "total_seconds": self.total_seconds(),
        }


@dataclass(frozen=True)
class Device:
    offline: bool
    cached: tuple

    @classmethod
    def from_boundary(cls, device):
        return cls(bool(device.get("offline", False)), tuple(device.get("cached", ())))

    def missing(self, playlist):
        if not self.offline:
            return []
        return [track["id"] for track in playlist.get("tracks", []) if track["id"] not in self.cached]


@dataclass(frozen=True)
class Account:
    active: bool

    @classmethod
    def from_boundary(cls, account):
        return cls(bool(account.get("active", False)))


def build_playlist(library, requested, profile):
    catalog = Catalog.from_boundary(library)
    listener = Listener.from_boundary(profile)
    playlist = Playlist((), ())
    for key in requested:
        track = catalog.track(key)
        if track is None:
            playlist = playlist.skip(key, "unavailable")
        elif not track.visible_to(listener):
            playlist = playlist.skip(key, "restricted")
        elif playlist.total_seconds() + track.seconds > listener.max_seconds:
            playlist = playlist.skip(key, "too_long")
        else:
            playlist = playlist.include(track)
    return playlist.as_dict()


def start_session(playlist, device, account):
    account = Account.from_boundary(account)
    if not account.active:
        return {"status": "rejected", "reason": "inactive_account"}
    missing = Device.from_boundary(device).missing(playlist)
    if missing:
        return {"status": "rejected", "reason": "not_cached", "missing": missing}
    return {
        "status": "playing",
        "track_count": len(playlist.get("tracks", [])),
        "duration": playlist.get("total_seconds", 0),
    }
