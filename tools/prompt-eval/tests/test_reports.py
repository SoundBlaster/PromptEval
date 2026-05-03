from pathlib import Path
from prompt_eval.runner import run_suite

def test_report_generation():
    root = Path(__file__).resolve().parents[1]
    run_dir = run_suite(root, "elegant_objects", [root / "prompts/elegant_objects/baseline.md"], "noop")
    assert (run_dir / "report.md").exists()
