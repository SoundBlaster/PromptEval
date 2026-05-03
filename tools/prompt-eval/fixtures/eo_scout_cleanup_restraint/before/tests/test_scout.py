import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from scout.scout import Scout


def test_cleanup_current_behavior_is_mutating_and_lightweight():
    raw = ["  Alpha", None, "", "Beta "]
    scout = Scout(raw)

    assert scout.cleanup() == ["Alpha", "Beta"]
    assert scout.values == ["Alpha", "Beta"]
