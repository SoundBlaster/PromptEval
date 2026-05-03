from pathlib import Path
from prompt_eval.models import CaseRunResult, ScoreBreakdown
from prompt_eval.reports import write_report
from prompt_eval.runner import run_suite

def test_report_generation():
    root = Path(__file__).resolve().parents[1]
    run_dir = run_suite(root, "elegant_objects", [root / "prompts/elegant_objects/baseline.md"], "noop")
    assert (run_dir / "report.md").exists()

def test_report_uses_dynamic_category_columns(tmp_path):
    result = CaseRunResult(
        suite="generic",
        prompt="prompts/security.md",
        case_id="case-a",
        score=ScoreBreakdown(categories={"security": 10, "portability": 20}, total=30),
        checks=[],
        diff_path="diff.patch",
        transcript_path="trace.jsonl",
    )
    write_report(tmp_path, "generic", [result])
    report = (tmp_path / "report.md").read_text()
    assert "| Prompt | Cases | Avg score | Security | Portability |" in report
