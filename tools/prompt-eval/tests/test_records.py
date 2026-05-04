import json


from prompt_eval.records import record_run


def test_record_run_writes_compact_markdown_json_and_index(tmp_path):
    run = tmp_path / "runs" / "20260504-sample"
    run.mkdir(parents=True)
    (run / "metadata.json").write_text(
        json.dumps(
            {
                "suite": "elegant_objects",
                "agent": "codex",
                "model": "gpt-test",
                "model_mode": "fast",
                "case_sets": ["holdout"],
                "judge": "subagent",
            }
        )
    )
    rows = [
        {
            "suite": "elegant_objects",
            "prompt": "/repo/prompts/baseline.md",
            "case_id": "case_a",
            "case_sets": ["holdout"],
            "score": {"total": 70, "failure_tags": ["procedural"]},
            "judge": {
                "summary": "too procedural",
                "binary_evals": [
                    {"id": "ownership", "passed": False, "evidence": "Behavior still lives in helper functions."}
                ],
            },
        },
        {
            "suite": "elegant_objects",
            "prompt": "/repo/prompts/eo_refactor.md",
            "case_id": "case_a",
            "case_sets": ["holdout"],
            "score": {"total": 90, "failure_tags": []},
            "judge": {
                "summary": "object behavior",
                "binary_evals": [
                    {"id": "ownership", "passed": True, "evidence": "Behavior stays inside domain objects."}
                ],
            },
        },
    ]
    (run / "results.jsonl").write_text("\n".join(json.dumps(row) for row in rows))

    path = record_run(tmp_path, run, "Holdout sample")

    assert path == tmp_path / "records/elegant_objects/20260504-sample.md"
    md = path.read_text()
    assert "# Holdout sample" in md
    assert "| eo_refactor.md | 1 | 90.0 | 90.0 |" in md
    assert "| baseline.md | 1 | 70.0 | 70.0 |" in md
    assert "## Strengths And Weaknesses" in md
    assert "Top average score in this run." in md
    assert "Best or tied score on 1/1 shared cases." in md
    assert "Strong cases (>=90): case_a." in md
    assert "Weak cases (<85): case_a (70)." in md
    assert "Failure tags: procedural x1." in md
    assert "Judge binary eval failures: ownership x1." in md
    assert "too procedural" in md
    assert "ownership: Behavior still lives in helper functions." in md
    payload = json.loads((path.with_suffix(".json")).read_text())
    assert payload["prompts"][0]["prompt"] == "eo_refactor.md"
    assert payload["analysis"][0]["prompt"] == "eo_refactor.md"
    assert payload["analysis"][1]["prompt"] == "baseline.md"
    assert payload["cases"][0]["judge_binary_evals"]
    index = path.parent / "INDEX.md"
    assert "[20260504-sample](20260504-sample.md)" in index.read_text()
