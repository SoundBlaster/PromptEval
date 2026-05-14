import json
from unittest.mock import patch

from prompt_eval.judges import openai_judge
from prompt_eval.judges.common import build_judge_prompt, parse_judge_response
from prompt_eval.models import CaseChecks, CaseJudge, EvalCase, JudgeBinaryEval


def _case() -> EvalCase:
    return EvalCase(
        id="demo",
        title="Demo",
        fixture="fsd_sibling_import",
        task="Refactor X",
        checks=CaseChecks(),
        rubric={"layer_compliance": 30, "public_api_correctness": 20},
        judge=CaseJudge(
            categories=["layer_compliance", "public_api_correctness"],
            criteria=["Reward foo", "Penalize bar"],
            binary_evals=[
                JudgeBinaryEval(
                    id="layer_ok",
                    question="Did the agent respect layer rules?",
                    pass_condition="No upward imports.",
                    fail_condition="Upward imports present.",
                    category="layer_compliance",
                ),
            ],
        ),
    )


def test_build_judge_prompt_includes_task_and_binary_evals():
    case = _case()
    prompt = build_judge_prompt(case, "system prompt text", "+a\n-b", "pass commands:tests")
    assert "Refactor X" in prompt
    assert "layer_ok" in prompt
    assert "system prompt text" in prompt
    assert "+a\n-b" in prompt


def test_parse_judge_response_with_clean_json():
    case = _case()
    response = json.dumps(
        {
            "categories": {"layer_compliance": 25, "public_api_correctness": 20},
            "binary_evals": [
                {
                    "id": "layer_ok",
                    "passed": True,
                    "category": "layer_compliance",
                    "question": "Did the agent respect layer rules?",
                    "evidence": "no upward imports observed",
                }
            ],
            "failure_tags": [],
            "summary": "Looks clean.",
        }
    )
    result = parse_judge_response(response, case, ["layer_compliance", "public_api_correctness"])
    assert result.categories == {"layer_compliance": 25, "public_api_correctness": 20}
    assert result.summary == "Looks clean."
    assert result.binary_evals[0].passed is True


def test_judge_openai_returns_missing_model_when_unset(monkeypatch):
    monkeypatch.delenv("PEVAL_OPENAI_MODEL", raising=False)
    monkeypatch.delenv("PEVAL_OPENAI_JUDGE_MODEL", raising=False)
    result = openai_judge.judge_openai(_case(), "p", "d", "s")
    assert "judge_missing_model" in result.failure_tags


def test_judge_openai_parses_mocked_response(monkeypatch):
    monkeypatch.setenv("PEVAL_OPENAI_JUDGE_MODEL", "fake-model")

    fake_content = json.dumps(
        {
            "categories": {"layer_compliance": 30, "public_api_correctness": 18},
            "binary_evals": [
                {
                    "id": "layer_ok",
                    "passed": False,
                    "category": "layer_compliance",
                    "question": "Did the agent respect layer rules?",
                    "evidence": "imports from pages into shared",
                }
            ],
            "failure_tags": ["upward_import"],
            "summary": "One layer violation.",
        }
    )
    with patch.object(openai_judge, "_chat_completion", return_value=fake_content) as mock_call:
        result = openai_judge.judge_openai(_case(), "prompt", "diff", "checks summary")
    assert mock_call.called
    assert result.categories == {"layer_compliance": 30, "public_api_correctness": 18}
    assert result.failure_tags == ["upward_import"]
    assert result.binary_evals[0].passed is False
    assert "violation" in result.summary.lower()


def test_build_judge_prompt_includes_before_tree_when_provided():
    case = _case()
    base = build_judge_prompt(case, "p", "d", "s")
    enriched = build_judge_prompt(case, "p", "d", "s", before_tree="### FILE: src/main.tsx\n```\n// stub\n```")
    assert "Starting project state" not in base
    assert "Starting project state" in enriched
    assert "stub" in enriched


def test_judge_openai_handles_http_error(monkeypatch):
    import urllib.error

    monkeypatch.setenv("PEVAL_OPENAI_JUDGE_MODEL", "fake-model")
    with patch.object(
        openai_judge,
        "_chat_completion",
        side_effect=urllib.error.URLError("connection refused"),
    ):
        result = openai_judge.judge_openai(_case(), "prompt", "diff", "summary")
    assert "judge_http_error" in result.failure_tags
    assert result.categories == {}
