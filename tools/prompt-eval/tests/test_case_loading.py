from pathlib import Path
from prompt_eval.config import load_suite

def test_load_suite():
    root = Path(__file__).resolve().parents[1]
    cases = load_suite(root, "elegant_objects")
    assert len(cases) >= 5
