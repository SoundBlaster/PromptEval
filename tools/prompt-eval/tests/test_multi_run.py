import json
import shutil
from pathlib import Path

from prompt_eval.records import _case_summary, _prompt_summary, _runs_per_cell
from prompt_eval.reports import _fmt_mean_std, write_report
from prompt_eval.runner import run_suite


def test_runs_parameter_creates_per_run_subdirs_and_results():
    root = Path(__file__).resolve().parents[1]
    run_dir = run_suite(
        root=root,
        suite="elegant_objects",
        prompts=[root / "prompts/elegant_objects/eo_lite.md"],
        agent="fixture-good",
        case_sets=["tuning"],
        runs=2,
    )
    try:
        results = (run_dir / "results.jsonl").read_text().strip().splitlines()
        rows = [json.loads(line) for line in results]
        # Each (prompt, case) cell should now yield 2 rows.
        keyed: dict[tuple[str, str], list[int]] = {}
        for row in rows:
            keyed.setdefault((row["prompt"], row["case_id"]), []).append(row["run_index"])
        assert keyed, "no rows produced"
        for indices in keyed.values():
            assert sorted(indices) == [0, 1], f"expected run indices [0, 1], got {sorted(indices)}"

        # Per-run subdirs exist on disk.
        for (prompt_path, case_id), _ in keyed.items():
            prompt_stem = Path(prompt_path).stem
            cell = run_dir / prompt_stem / case_id
            assert (cell / "run_0" / "result.json").exists()
            assert (cell / "run_1" / "result.json").exists()

        # Report renders mean ± std header.
        report_md = (run_dir / "report.md").read_text()
        assert "Runs per cell: 2" in report_md
        assert "Pass rate" in report_md
    finally:
        shutil.rmtree(run_dir, ignore_errors=True)


def test_fmt_mean_std_handles_single_value_and_population():
    assert _fmt_mean_std([]) == "n/a"
    assert _fmt_mean_std([90]) == "90.0"
    formatted = _fmt_mean_std([80, 90])
    assert formatted.startswith("85.0 ± ")


def test_runs_per_cell_inferred_from_results():
    rows = [
        {"run_index": 0, "case_id": "a", "prompt": "p", "score": {"total": 1}, "case_sets": []},
        {"run_index": 1, "case_id": "a", "prompt": "p", "score": {"total": 1}, "case_sets": []},
        {"run_index": 2, "case_id": "a", "prompt": "p", "score": {"total": 1}, "case_sets": []},
    ]
    assert _runs_per_cell(rows) == 3


def test_record_case_summary_aggregates_runs_to_one_row():
    rows = [
        {
            "run_index": 0,
            "case_id": "case_a",
            "prompt": "p/x.md",
            "score": {"total": 80, "failure_tags": ["t1"]},
            "case_sets": ["s1"],
            "judge": {"summary": "first", "binary_evals": []},
        },
        {
            "run_index": 1,
            "case_id": "case_a",
            "prompt": "p/x.md",
            "score": {"total": 100, "failure_tags": ["t2"]},
            "case_sets": ["s1"],
            "judge": {"summary": "second", "binary_evals": []},
        },
    ]
    summary = _case_summary(rows)
    assert len(summary) == 1
    item = summary[0]
    assert item["runs"] == 2
    assert item["score"] == 90.0
    assert item["score_min"] == 80
    assert item["score_max"] == 100
    assert item["score_std"] > 0
    assert sorted(item["failure_tags"]) == ["t1", "t2"]
    # Latest judge summary wins.
    assert item["judge"] == "second"


def test_record_prompt_summary_counts_distinct_cases():
    rows = [
        {
            "run_index": 0,
            "case_id": "case_a",
            "prompt": "p/x.md",
            "score": {"total": 80, "failure_tags": []},
            "case_sets": [],
        },
        {
            "run_index": 1,
            "case_id": "case_a",
            "prompt": "p/x.md",
            "score": {"total": 90, "failure_tags": []},
            "case_sets": [],
        },
    ]
    summaries = _prompt_summary(rows)
    assert len(summaries) == 1
    item = summaries[0]
    assert item["cases"] == 1, "cases counts distinct case_id, not result rows"
    assert item["results"] == 2
    assert item["average"] == 85.0


def test_write_report_single_run_unchanged_shape():
    """Single-run reports should still use the original per-row table."""
    root = Path(__file__).resolve().parents[1]
    run_dir = run_suite(
        root=root,
        suite="elegant_objects",
        prompts=[root / "prompts/elegant_objects/eo_lite.md"],
        agent="fixture-good",
        case_sets=["tuning"],
        runs=1,
    )
    try:
        report = (run_dir / "report.md").read_text()
        assert "Runs per cell" not in report
        assert "Pass rate" not in report
        # Ensure the function returns the expected file path.
        write_report  # imported, prevents unused warning
    finally:
        shutil.rmtree(run_dir, ignore_errors=True)
