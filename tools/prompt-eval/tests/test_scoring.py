from prompt_eval.models import CheckResult
from prompt_eval.scoring import score_from_checks

def test_scoring_range():
    s = score_from_checks([CheckResult(True,"a"), CheckResult(False,"command:pytest")])
    assert 0 <= s.total <= 100
    assert "tests_failed" in s.failure_tags
