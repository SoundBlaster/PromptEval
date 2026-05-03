import json

from prompt_eval.judges.subagent_judge import _parse


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

    result = _parse(json.dumps(message), {"eo_adherence": 25})

    assert result.categories == {"eo_adherence": 18}
    assert result.failure_tags == ["getter_envy"]
    assert result.summary == "behavior is still too external"


def test_subagent_judge_parse_clamps_category_scores():
    result = _parse(
        json.dumps({"categories": {"eo_adherence": 100}, "failure_tags": [], "summary": "ok"}),
        {"eo_adherence": 25},
    )

    assert result.categories == {"eo_adherence": 25}
