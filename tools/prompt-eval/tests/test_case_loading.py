from pathlib import Path
import re
import pytest
from prompt_eval.config import load_suite, suite_case_sets

def test_load_suite():
    root = Path(__file__).resolve().parents[1]
    cases = load_suite(root, "elegant_objects")
    assert len(cases) >= 7

def test_elegant_objects_suite_includes_medium_fixture_without_task_leakage():
    root = Path(__file__).resolve().parents[1]
    cases = load_suite(root, "elegant_objects")
    fixtures = {case.fixture for case in cases}
    assert "python_subscription_billing" in fixtures
    assert all("EO style" not in case.task for case in cases)

def test_elegant_objects_suite_declares_tuning_and_validation_sets():
    root = Path(__file__).resolve().parents[1]
    assert suite_case_sets(root, "elegant_objects") == ["tuning", "eo_refactoring", "validation", "eo_feature_lens", "generated", "eo_greenfield", "eo_app_skeleton"]
    tuning = load_suite(root, "elegant_objects", ["tuning"])
    validation = load_suite(root, "elegant_objects", ["validation"])
    generated = load_suite(root, "elegant_objects", ["generated"])
    feature_lens = load_suite(root, "elegant_objects", ["eo_feature_lens"])
    refactoring = load_suite(root, "elegant_objects", ["eo_refactoring"])
    greenfield = load_suite(root, "elegant_objects", ["eo_greenfield"])
    app_skeleton = load_suite(root, "elegant_objects", ["eo_app_skeleton"])
    assert len(tuning) == 5
    assert len(validation) == 2
    assert len(generated) == 13
    assert len(feature_lens) == 10
    assert len(refactoring) == 7
    assert len(greenfield) == 3
    assert len(app_skeleton) == 2
    assert {case.fixture for case in validation} == {"python_subscription_billing"}
    assert all("tuning" in case.sets for case in tuning)
    assert all("validation" in case.sets for case in validation)
    assert all("generated" in case.sets for case in generated)
    assert all("eo_feature_lens" in case.sets for case in feature_lens)
    assert all("eo_refactoring" in case.sets for case in refactoring)
    assert all("eo_greenfield" in case.sets for case in greenfield)
    assert all("eo_app_skeleton" in case.sets for case in app_skeleton)
    assert all(case.judge and case.judge.criteria for case in tuning + validation)
    assert all(case.judge and case.judge.categories == ["scope_control", "eo_adherence", "communication"] for case in tuning + validation)

def test_elegant_objects_regex_checks_compile():
    root = Path(__file__).resolve().parents[1]
    for case in load_suite(root, "elegant_objects"):
        regexes = case.checks.required_regex + case.checks.forbidden_regex
        for check in regexes:
            try:
                re.compile(check.pattern)
            except re.error as exc:
                pytest.fail(f"{case.id}: invalid regex {check.pattern!r}: {exc}")

def test_load_suite_accepts_yaml_syntax(tmp_path):
    suite_dir = tmp_path / "evals" / "custom"
    cases_dir = suite_dir / "cases"
    cases_dir.mkdir(parents=True)
    (suite_dir / "suite.yaml").write_text(
        """
        name: custom
        cases:
          - case.yaml # comments are valid YAML
        """
    )
    (cases_dir / "case.yaml").write_text(
        """
        id: sample
        title: Sample
        fixture: fixture
        task: |
          Implement the requested change.
        checks:
          commands:
            - ["python", "-m", "pytest", "-q"]
        rubric:
          security: 100
        """
    )
    cases = load_suite(tmp_path, "custom")
    assert cases[0].task == "Implement the requested change.\n"
    assert cases[0].checks.commands == [["python", "-m", "pytest", "-q"]]

def test_load_suite_accepts_case_entries_with_sets(tmp_path):
    suite_dir = tmp_path / "evals" / "custom"
    cases_dir = suite_dir / "cases"
    cases_dir.mkdir(parents=True)
    (suite_dir / "suite.yaml").write_text(
        """
        name: custom
        cases:
          - path: train.yaml
            sets: [tuning]
          - path: heldout.yaml
            sets: [validation]
        """
    )
    case_text = """
        id: {id}
        title: Sample
        fixture: fixture
        task: |
          Implement the requested change.
        checks: {{}}
        rubric:
          functional_correctness: 100
        """
    (cases_dir / "train.yaml").write_text(case_text.format(id="train"))
    (cases_dir / "heldout.yaml").write_text(case_text.format(id="heldout"))

    assert [case.id for case in load_suite(tmp_path, "custom")] == ["train", "heldout"]
    assert [case.id for case in load_suite(tmp_path, "custom", ["validation"])] == ["heldout"]
    assert suite_case_sets(tmp_path, "custom") == ["tuning", "validation"]
