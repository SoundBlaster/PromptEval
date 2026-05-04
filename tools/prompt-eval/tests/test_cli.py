import json

from pathlib import Path

from prompt_eval.cli import compare_run
from prompt_eval import cli


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


def test_generate_case_cli_accepts_positional_description(tmp_path, monkeypatch, capsys):
    calls = []

    def fake_generate_case(description, case_id, output_root, model, model_mode, codex_bin):
        calls.append((description, case_id, output_root, model, model_mode, codex_bin))

        class Generated:
            output_dir = tmp_path / "generated"

        return Generated()

    monkeypatch.chdir(Path(__file__).resolve().parents[1])
    monkeypatch.setattr(cli, "generate_case", fake_generate_case)
    monkeypatch.setattr(
        "sys.argv",
        [
            "peval",
            "generate-case",
            "Build a case",
            "--case-id",
            "sample",
            "--output-root",
            str(tmp_path),
            "--model",
            "gpt-test",
            "--model-mode",
            "fast",
            "--codex-bin",
            "codex-test",
        ],
    )

    cli.main()

    assert calls == [("Build a case", "sample", tmp_path, "gpt-test", "fast", "codex-test")]
    assert str(tmp_path / "generated") in capsys.readouterr().out


def test_generate_case_cli_accepts_description_file(tmp_path, monkeypatch, capsys):
    description = tmp_path / "description.txt"
    description.write_text("Build from file")
    calls = []

    def fake_generate_case(description_text, case_id, output_root, model, model_mode, codex_bin):
        calls.append((description_text, case_id, output_root, model, model_mode, codex_bin))

        class Generated:
            output_dir = tmp_path / "generated"

        return Generated()

    monkeypatch.chdir(Path(__file__).resolve().parents[1])
    monkeypatch.setattr(cli, "generate_case", fake_generate_case)
    monkeypatch.setattr(
        "sys.argv",
        [
            "peval",
            "generate-case",
            "--description-file",
            str(description),
            "--case-id",
            "sample",
        ],
    )

    cli.main()

    root = Path(__file__).resolve().parents[1]
    assert calls == [("Build from file", "sample", root / "generated-cases", "gpt-5.3-codex-spark", "fast", None)]
    assert str(tmp_path / "generated") in capsys.readouterr().out


def test_record_cli_records_completed_run(tmp_path, monkeypatch, capsys):
    calls = []
    run = tmp_path / "runs" / "sample"

    def fake_record_run(root, run_dir, title):
        calls.append((root, run_dir, title))
        return tmp_path / "records/elegant_objects/sample.md"

    monkeypatch.chdir(Path(__file__).resolve().parents[1])
    monkeypatch.setattr(cli, "record_run", fake_record_run)
    monkeypatch.setattr(
        "sys.argv",
        [
            "peval",
            "record",
            "--run",
            str(run),
            "--title",
            "Sample run",
        ],
    )

    cli.main()

    root = Path(__file__).resolve().parents[1]
    assert calls == [(root, run, "Sample run")]
    assert str(tmp_path / "records/elegant_objects/sample.md") in capsys.readouterr().out
