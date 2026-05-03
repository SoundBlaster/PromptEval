from pathlib import Path
from prompt_eval.config import load_suite

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
