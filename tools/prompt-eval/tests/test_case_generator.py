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


def _write_nested_generated(root: Path, case_id: str) -> None:
    out = root / "generated" / case_id
    for name in ("before", "good", "bad"):
        package = out / name / "src" / "sample"
        package.mkdir(parents=True)
        (package / "__init__.py").write_text("")
        (package / "domain.py").write_text("class Domain:\n    pass\n")
    (out / "case.yaml").write_text(
        f"""id: {case_id}
title: Nested Case
fixture: {case_id}
task: Add behavior.
checks: {{}}
rubric:
  functional_correctness: 40
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


def test_generate_case_detects_nested_python_fixture(tmp_path, monkeypatch):
    calls = []

    def fake_run_codex(sandbox, task, prompt_text, model, model_mode, codex_bin):
        calls.append((model, model_mode, codex_bin))
        _write_nested_generated(sandbox, "nested_python")
        return AgentRun(ok=True)

    monkeypatch.setattr(case_generator, "run_codex", fake_run_codex)

    generated = case_generator.generate_case("Nested Python case", case_id="nested_python", output_root=tmp_path)
    case_yaml = yaml.safe_load((generated.output_dir / "case.yaml").read_text())

    assert case_yaml["checks"]["commands"] == [["python", "-m", "pytest", "-q"], ["python", "-m", "compileall", "-q", "."]]
    assert calls == [("gpt-5.3-codex-spark", None, None)]


def test_generate_case_removes_temp_workspace_after_copy(tmp_path, monkeypatch):
    seen = []

    def fake_run_codex(sandbox, task, prompt_text, model, model_mode, codex_bin):
        seen.append(sandbox)
        _write_generated(sandbox, "cleanup_case")
        return AgentRun(ok=True)

    monkeypatch.setattr(case_generator, "run_codex", fake_run_codex)

    case_generator.generate_case("Cleanup case", case_id="cleanup_case", output_root=tmp_path)

    assert seen
    assert not seen[0].exists()


def test_generate_case_rejects_missing_required_layout(tmp_path, monkeypatch):
    def fake_run_codex(sandbox, task, prompt_text, model, model_mode, codex_bin):
        (sandbox / "generated" / "broken").mkdir(parents=True)
        return AgentRun(ok=True)

    monkeypatch.setattr(case_generator, "run_codex", fake_run_codex)

    with pytest.raises(ValueError, match="missing required paths"):
        case_generator.generate_case("Broken case", case_id="broken", output_root=tmp_path)


def test_generate_case_rejects_invalid_regex(tmp_path, monkeypatch):
    def fake_run_codex(sandbox, task, prompt_text, model, model_mode, codex_bin):
        _write_generated(sandbox, "invalid_regex")
        case_yaml = sandbox / "generated" / "invalid_regex" / "case.yaml"
        text = case_yaml.read_text().replace('- "Helper"', '- "isinstance("')
        case_yaml.write_text(text)
        return AgentRun(ok=True)

    monkeypatch.setattr(case_generator, "run_codex", fake_run_codex)

    with pytest.raises(ValueError, match="invalid regex"):
        case_generator.generate_case("Invalid regex case", case_id="invalid_regex", output_root=tmp_path)


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
