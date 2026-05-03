from pathlib import Path
from prompt_eval.runner import run_suite
import json

def avg(run_dir):
    rows=[json.loads(l) for l in (run_dir/"results.jsonl").read_text().splitlines() if l.strip()]
    return sum(r["score"]["total"] for r in rows)/len(rows)

def test_good_beats_bad():
    root = Path(__file__).resolve().parents[1]
    p = [root / "prompts/elegant_objects/eo_lite.md"]
    good = run_suite(root, "elegant_objects", p, "fixture-good")
    bad = run_suite(root, "elegant_objects", p, "fixture-bad")
    assert avg(good) > avg(bad)
