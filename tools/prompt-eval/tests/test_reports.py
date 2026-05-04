from pathlib import Path
from prompt_eval.models import CaseRunResult, ScoreBreakdown
from prompt_eval.reports import write_report
from prompt_eval.runner import run_suite
from prompt_eval.judges.base import JudgeBinaryEvalResult, JudgeResult


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


def test_report_includes_case_set_breakdown(tmp_path):
    results = [
        CaseRunResult(
            suite="generic",
            prompt="prompts/eo.md",
            case_id="train",
            score=ScoreBreakdown(categories={"design": 80}, total=80),
            checks=[],
            diff_path="train.diff",
            transcript_path="train.trace",
            case_sets=["tuning"],
        ),
        CaseRunResult(
            suite="generic",
            prompt="prompts/eo.md",
            case_id="heldout",
            score=ScoreBreakdown(categories={"design": 60}, total=60),
            checks=[],
            diff_path="heldout.diff",
            transcript_path="heldout.trace",
            case_sets=["validation"],
        ),
    ]
    write_report(tmp_path, "generic", results)
    report = (tmp_path / "report.md").read_text()
    assert "| Prompt | Cases | Avg score | Tuning avg | Validation avg | Design |" in report
    assert "| eo.md | 2 | 70.0 | 80.0 | 60.0 | 70.0 |" in report
    assert "Case set: `validation`" in report


def test_report_includes_judge_summary(tmp_path):
    result = CaseRunResult(
        suite="generic",
        prompt="prompts/eo.md",
        case_id="case-a",
        score=ScoreBreakdown(categories={"design": 10}, total=10),
        checks=[],
        diff_path="diff.patch",
        transcript_path="trace.jsonl",
        judge=JudgeResult(
            categories={"design": 10},
            failure_tags=[],
            summary="object ownership | acceptable\nsecond line",
            binary_evals=[JudgeBinaryEvalResult(id="ownership", passed=False, evidence="Behavior stays procedural.")],
        ),
    )
    write_report(tmp_path, "generic", [result])
    report = (tmp_path / "report.md").read_text()
    assert "| Prompt | Score | Result | Failure tags | Judge | Judge evals |" in report
    assert "object ownership \\| acceptable<br>second line" in report
    assert "ownership: Behavior stays procedural." in report
