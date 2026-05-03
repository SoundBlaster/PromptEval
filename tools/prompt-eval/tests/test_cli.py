import json

from prompt_eval.cli import compare_run


def test_compare_run_prints_case_set_breakdown(tmp_path, capsys):
    rows = [
        {"prompt": "prompts/eo.md", "case_sets": ["tuning"], "score": {"total": 90}},
        {"prompt": "prompts/eo.md", "case_sets": ["validation"], "score": {"total": 70}},
    ]
    (tmp_path / "results.jsonl").write_text("\n".join(json.dumps(row) for row in rows))

    compare_run(tmp_path)

    out = capsys.readouterr().out
    assert "| Prompt | Cases | Avg score | Tuning | Validation |" in out
    assert "| eo.md | 2 | 80.0 | 90.0 | 70.0 |" in out
