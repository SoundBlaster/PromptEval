import json

from prompt_eval.judges.subagent_judge import _judge_categories, _parse, _prompt
from prompt_eval.models import CaseChecks, CaseJudge, EvalCase, JudgeBinaryEval


def _case(**kwargs):
    defaults = dict(
        id="eo",
        title="EO",
        fixture="fixture",
        task="Fix the issue.",
        checks=CaseChecks(),
        rubric={"eo_adherence": 25},
    )
    defaults.update(kwargs)
    return EvalCase(**defaults)


def test_subagent_judge_parse_extracts_agent_message_json():
    message = {
        "type": "item.completed",
        "item": {
            "type": "agent_message",
            "text": json.dumps(
                {
                    "categories": {"eo_adherence": 18, "unknown": 99},
                    "failure_tags": ["getter_envy"],
                    "summary": "behavior is still too external",
                }
            ),
        },
    }

    result = _parse(json.dumps(message), _case())

    assert result.categories == {"eo_adherence": 18}
    assert result.failure_tags == ["getter_envy"]
    assert result.summary == "behavior is still too external"


def test_subagent_judge_parse_clamps_category_scores():
    result = _parse(
        json.dumps({"categories": {"eo_adherence": 100}, "failure_tags": [], "summary": "ok"}),
        _case(),
    )

    assert result.categories == {"eo_adherence": 25}

def test_subagent_judge_parse_filters_to_allowed_categories():
    result = _parse(
        json.dumps(
            {
                "categories": {"functional_correctness": 0, "verification": 0, "eo_adherence": 18},
                "failure_tags": [],
                "summary": "ok",
            }
        ),
        _case(rubric={"functional_correctness": 40, "verification": 10, "eo_adherence": 25}),
        ["eo_adherence"],
    )

    assert result.categories == {"eo_adherence": 18}

def test_subagent_judge_parse_honors_empty_allowed_categories():
    result = _parse(
        json.dumps(
            {
                "categories": {"functional_correctness": 0, "verification": 0, "eo_adherence": 18},
                "failure_tags": [],
                "summary": "ok",
            }
        ),
        _case(rubric={"functional_correctness": 40, "verification": 10, "eo_adherence": 25}),
        [],
    )

    assert result.categories == {}

def test_subagent_prompt_uses_case_rubric_categories():
    case = EvalCase(
        id="security",
        title="Security",
        fixture="fixture",
        task="Fix the issue.",
        checks=CaseChecks(),
        rubric={"security": 60, "portability": 40},
    )

    prompt = _prompt(case, "agent prompt", "diff", "checks passed")

    assert '"security": 60' in prompt
    assert '"portability": 40' in prompt
    assert "0 means severe semantic failure" in prompt
    assert "Use only these semantic category keys: `security`, `portability`" in prompt
    assert "eo_adherence" not in prompt

def test_subagent_prompt_prefers_explicit_judge_categories():
    case = _case(rubric={"functional_correctness": 40, "scope_control": 20, "eo_adherence": 25, "verification": 10})
    case.judge = CaseJudge(categories=["eo_adherence"])

    assert _judge_categories(case) == ["eo_adherence"]
    prompt = _prompt(case, "agent prompt", "diff", "checks passed")
    assert '"eo_adherence": 25' in prompt
    assert "functional_correctness" not in prompt.split("Return exactly one JSON object with this shape:", 1)[1].split("failure_tags", 1)[0]


def test_subagent_judge_parse_binary_evals():
    case = _case()
    case.judge = CaseJudge(
        categories=["eo_adherence"],
        binary_evals=[
            JudgeBinaryEval(
                id="behavior_ownership",
                question="Does behavior stay in domain objects?",
                pass_condition="Behavior is owned by focused domain objects.",
                fail_condition="Behavior is orchestrated through helpers.",
                category="eo_adherence",
            )
        ],
    )
    result = _parse(
        json.dumps(
            {
                "categories": {"eo_adherence": 20},
                "binary_evals": [
                    {
                        "id": "behavior_ownership",
                        "passed": False,
                        "evidence": "Pricing behavior still sits in helper-style wrappers.",
                    }
                ],
                "failure_tags": ["poor_ownership"],
                "summary": "too procedural",
            }
        ),
        case,
    )

    assert result.binary_evals[0].id == "behavior_ownership"
    assert not result.binary_evals[0].passed
    assert result.binary_evals[0].category == "eo_adherence"
    assert result.binary_evals[0].question == "Does behavior stay in domain objects?"
    assert result.binary_evals[0].evidence == "Pricing behavior still sits in helper-style wrappers."


def test_subagent_prompt_includes_binary_eval_contract():
    case = _case()
    case.judge = CaseJudge(
        categories=["eo_adherence"],
        binary_evals=[
            JudgeBinaryEval(
                id="ownership",
                question="Does the patch keep behavior in domain objects?",
                pass_condition="Behavior lives in domain objects.",
                fail_condition="Helpers or passive data bags own behavior.",
                category="eo_adherence",
            )
        ],
    )

    prompt = _prompt(case, "agent prompt", "diff", "checks passed")

    assert '"binary_evals": [' in prompt
    assert "`ownership` (eo_adherence): Does the patch keep behavior in domain objects?" in prompt
    assert "Pass: Behavior lives in domain objects." in prompt
    assert "Fail: Helpers or passive data bags own behavior." in prompt
