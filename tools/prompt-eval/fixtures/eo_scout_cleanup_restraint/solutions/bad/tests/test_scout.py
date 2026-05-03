import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from scout.scout import Scout


def test_cleanup_is_local_and_respects_input_immutability():
    raw = ["  Alpha", "alpha", None, "", "Beta ", "beta ", "", "BANANA"]
    scout = Scout(raw)

    cleaned = scout.cleanup()

    assert cleaned == ["alpha", "beta", "banana"]
    assert raw == ["  Alpha", "alpha", None, "", "Beta ", "beta ", "", "BANANA"]
    assert scout.values == raw
