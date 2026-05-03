from prompt_eval.models import CheckResult
from prompt_eval.scoring import score_from_checks

def test_scoring_range():
    s = score_from_checks([CheckResult(True,"a"), CheckResult(False,"command:pytest")])
    assert 0 <= s.total <= 100
    assert "commands_failed" in s.failure_tags

def test_scoring_uses_custom_rubric_categories():
    s = score_from_checks(
        [CheckResult(True, "a"), CheckResult(False, "b")],
        {"security": 60, "portability": 40},
    )
    assert s.categories == {"security": 30, "portability": 20}
    assert s.total == 50
