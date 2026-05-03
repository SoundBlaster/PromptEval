from pathlib import Path

import yaml

import pytest

from prompt_eval.agents.base import AgentRun
from prompt_eval import case_generator


def _write_generated(root: Path, case_id: str) -> None:
    out = root / "generated" / case_id
    for name in ("before", "good", "bad"):
        package = out / name
        package.mkdir(parents=True)
        (package / "test_sample.py").write_text("def test_sample():\n    assert True\n")
    (out / "case.yaml").write_text(
        f"""id: {case_id}
title: Generated Case
fixture: {case_id}
task: Add domain behavior without procedural helpers.
checks:
  commands:
    - ["python", "-m", "pytest", "-q"]
  forbidden_regex:
    - "Helper"
  max_changed_files: 4
rubric:
  functional_correctness: 40
  scope_control: 20
  eo_adherence: 25
  verification: 10
  communication: 5
notes:
  - Generated draft.
judge:
  categories: [scope_control, eo_adherence, communication]
  criteria:
    eo_adherence: Keep behavior inside focused domain objects.
"""
    )


def test_generate_case_uses_codex_and_copies_output(tmp_path, monkeypatch):
    calls = []

    def fake_run_codex(sandbox, task, prompt_text, model, model_mode, codex_bin):
        calls.append((sandbox, task, prompt_text, model, model_mode, codex_bin))
        _write_generated(sandbox, "discount_policy")
        return AgentRun(ok=True)

    monkeypatch.setattr(case_generator, "run_codex", fake_run_codex)

    generated = case_generator.generate_case(
        "Generate a discount policy task",
        case_id="discount_policy",
        output_root=tmp_path,
        model="gpt-5.3-codex-spark",
        model_mode="fast",
        codex_bin="codex",
    )

    assert generated.output_dir == tmp_path / "discount_policy"
    assert (generated.output_dir / "before" / "test_sample.py").exists()
    case_yaml = yaml.safe_load((generated.output_dir / "case.yaml").read_text())
    assert case_yaml["checks"]["commands"] == [["python", "-m", "pytest", "-q"], ["python", "-m", "compileall", "-q", "."]]
    assert case_yaml["checks"]["forbidden_regex"][0]["pattern"] == "Helper"
    assert case_yaml["notes"] == "Generated draft."
    assert case_yaml["judge"]["criteria"] == ["Keep behavior inside focused domain objects."]
    assert "case_id: discount_policy" in calls[0][1]
    assert calls[0][3:] == ("gpt-5.3-codex-spark", "fast", "codex")


def test_generate_case_rejects_missing_required_layout(tmp_path, monkeypatch):
    def fake_run_codex(sandbox, task, prompt_text, model, model_mode, codex_bin):
        (sandbox / "generated" / "broken").mkdir(parents=True)
        return AgentRun(ok=True)

    monkeypatch.setattr(case_generator, "run_codex", fake_run_codex)

    with pytest.raises(ValueError, match="missing required paths"):
        case_generator.generate_case("Broken case", case_id="broken", output_root=tmp_path)


def test_generate_case_repairs_regex_yaml_escapes(tmp_path, monkeypatch):
    def fake_run_codex(sandbox, task, prompt_text, model, model_mode, codex_bin):
        out = sandbox / "generated" / "regex_case"
        for name in ("before", "good", "bad"):
            package = out / name
            package.mkdir(parents=True)
            (package / "test_sample.py").write_text("def test_sample():\n    assert True\n")
        (out / "case.yaml").write_text(
            """id: regex_case
title: Regex Case
fixture: regex_case
task: Add behavior.
checks:
  commands:
    - ["python", "-m", "pytest", "-q"]
  required_regex:
    - "class\\s+TaxPolicy"
rubric:
  functional_correctness: 40
"""
        )
        return AgentRun(ok=True)

    monkeypatch.setattr(case_generator, "run_codex", fake_run_codex)

    generated = case_generator.generate_case("Regex case", case_id="regex_case", output_root=tmp_path)
    case_yaml = yaml.safe_load((generated.output_dir / "case.yaml").read_text())

    assert case_yaml["checks"]["required_regex"][0]["pattern"] == r"class\s+TaxPolicy"


def test_generate_case_repairs_parenthesis_regex_yaml_escapes(tmp_path, monkeypatch):
    def fake_run_codex(sandbox, task, prompt_text, model, model_mode, codex_bin):
        out = sandbox / "generated" / "paren_case"
        for name in ("before", "good", "bad"):
            package = out / name
            package.mkdir(parents=True)
            (package / "test_sample.py").write_text("def test_sample():\n    assert True\n")
        (out / "case.yaml").write_text(
            """id: paren_case
title: Paren Case
fixture: paren_case
task: Add behavior.
checks:
  required_regex:
    - "def total\\(self\\)"
rubric:
  functional_correctness: 40
"""
        )
        return AgentRun(ok=True)

    monkeypatch.setattr(case_generator, "run_codex", fake_run_codex)

    generated = case_generator.generate_case("Paren case", case_id="paren_case", output_root=tmp_path)
    case_yaml = yaml.safe_load((generated.output_dir / "case.yaml").read_text())

    assert case_yaml["checks"]["required_regex"][0]["pattern"] == r"def total\(self\)"
