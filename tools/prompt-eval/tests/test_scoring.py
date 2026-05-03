from prompt_eval.models import CheckResult
from prompt_eval.scoring import score_from_checks
from prompt_eval.judges.base import JudgeResult

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

def test_scoring_uses_judge_as_additional_ceiling():
    s = score_from_checks(
        [CheckResult(True, "command:pytest")],
        {"functional_correctness": 40, "eo_adherence": 25},
        JudgeResult(categories={"eo_adherence": 10, "unknown": 99}, failure_tags=["poor_ownership"], summary="too procedural"),
    )
    assert s.categories == {"functional_correctness": 40, "eo_adherence": 10}
    assert s.total == 50
    assert "poor_ownership" in s.failure_tags
    assert "judge: too procedural" in s.summary
