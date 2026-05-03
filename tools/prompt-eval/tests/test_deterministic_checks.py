from pathlib import Path
from prompt_eval.config import load_suite
from prompt_eval.sandbox import prepare_sandbox
from prompt_eval.agents.fixture_agent import apply_fixture_solution
from prompt_eval.checks import git_diff, run_checks

def test_regex_and_command_checks():
    root = Path(__file__).resolve().parents[1]
    case = [c for c in load_suite(root, "elegant_objects") if c.id == "static_helper_relapse"][0]
    sb = prepare_sandbox(root / "fixtures/python_eo_shop/before")
    apply_fixture_solution(sb, root / "fixtures/python_eo_shop", "bad")
    checks = run_checks(case, sb, git_diff(sb))
    assert any((not c.passed and "forbidden_regex" in c.name) for c in checks)
