from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from mp3_player import build_playlist, start_session


LIBRARY = {
    "intro": {"title": "Intro", "seconds": 120, "explicit": False},
    "anthem": {"title": "Anthem", "seconds": 200, "explicit": True},
    "suite": {"title": "Suite", "seconds": 250, "explicit": False},
}


def test_playlist_filters_restricted_missing_and_too_long_tracks():
    requested = ["intro", "anthem", "suite", "missing"]
    profile = {"age": 12, "max_seconds": 300}

    playlist = build_playlist(LIBRARY, requested, profile)

    assert playlist == {
        "tracks": [{"id": "intro", "title": "Intro", "seconds": 120}],
        "skipped": [
            {"id": "anthem", "reason": "restricted"},
            {"id": "suite", "reason": "too_long"},
            {"id": "missing", "reason": "unavailable"},
        ],
        "total_seconds": 120,
    }


def test_playlist_allows_explicit_tracks_for_adults_with_enough_time():
    requested = ["intro", "anthem"]
    profile = {"age": 18, "max_seconds": 400}

    playlist = build_playlist(LIBRARY, requested, profile)

    assert playlist["tracks"] == [
        {"id": "intro", "title": "Intro", "seconds": 120},
        {"id": "anthem", "title": "Anthem", "seconds": 200},
    ]
    assert playlist["skipped"] == []
    assert playlist["total_seconds"] == 320


def test_start_session_requires_active_account_and_offline_cache():
    playlist = {
        "tracks": [
            {"id": "intro", "title": "Intro", "seconds": 120},
            {"id": "anthem", "title": "Anthem", "seconds": 200},
        ],
        "total_seconds": 320,
    }

    assert start_session(playlist, {"offline": False, "cached": []}, {"active": False}) == {
        "status": "rejected",
        "reason": "inactive_account",
    }

    assert start_session(playlist, {"offline": True, "cached": ["intro"]}, {"active": True}) == {
        "status": "rejected",
        "reason": "not_cached",
        "missing": ["anthem"],
    }

    assert start_session(playlist, {"offline": False, "cached": []}, {"active": True}) == {
        "status": "playing",
        "track_count": 2,
        "duration": 320,
    }
