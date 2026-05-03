from pathlib import Path
import shutil
from prompt_eval.config import load_suite
from prompt_eval.sandbox import prepare_sandbox
from prompt_eval.agents.fixture_agent import apply_fixture_solution
from prompt_eval.checks import git_diff, run_checks
from prompt_eval.models import CaseChecks, EvalCase, RegexCheck

def test_regex_and_command_checks():
    root = Path(__file__).resolve().parents[1]
    case = [c for c in load_suite(root, "elegant_objects") if c.id == "static_helper_relapse"][0]
    sb = prepare_sandbox(root / "fixtures/python_eo_shop/before")
    try:
        apply_fixture_solution(sb, root / "fixtures/python_eo_shop", "bad")
        checks = run_checks(case, sb, git_diff(sb))
        assert any((not c.passed and "forbidden_regex" in c.name) for c in checks)
    finally:
        shutil.rmtree(sb, ignore_errors=True)

def test_file_regex_checks_can_scope_paths():
    root = Path(__file__).resolve().parents[1]
    sb = prepare_sandbox(root / "fixtures/python_subscription_billing/before")
    try:
        case = EvalCase(
            id="scoped",
            title="Scoped",
            fixture="python_subscription_billing",
            task="task",
            checks=CaseChecks(
                required_regex=[
                    RegexCheck(pattern="loyalty_percent", target="files", paths=["billing/*.py"]),
                    RegexCheck(pattern="loyalty_percent", target="files", paths=["tests/*.py"]),
                ]
            ),
            rubric={},
        )
        checks = run_checks(case, sb, git_diff(sb))
        assert not checks[0].passed
        assert checks[1].passed
    finally:
        shutil.rmtree(sb, ignore_errors=True)
