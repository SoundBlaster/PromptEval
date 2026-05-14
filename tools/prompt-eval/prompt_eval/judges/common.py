"""Shared helpers for LLM-as-judge implementations.

Both `subagent_judge` (Codex CLI) and `openai_judge` (HTTP) reuse:
- the prompt builder so judges see identical context across backends;
- the JSON parser so binary_evals / failure_tags / category mappings are uniform;
- the category selector so rubric scoping is consistent.
"""

from __future__ import annotations

import json
from typing import Iterable

from .base import JudgeBinaryEvalResult, JudgeResult
from ..models import EvalCase


def message_texts(stdout: str) -> list[str]:
    """Extract `agent_message` text bodies from Codex CLI's JSON stream."""
    texts = []
    for line in stdout.splitlines():
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        item = row.get("item") or {}
        if item.get("type") == "agent_message" and item.get("text"):
            texts.append(item["text"])
    return texts


def extract_json_payload(text: str) -> dict:
    """Best-effort JSON extraction tolerant of code fences and prose."""
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = [line for line in stripped.splitlines() if not line.strip().startswith("```")]
        stripped = "\n".join(lines).strip()
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError("judge response does not contain a JSON object")
    return json.loads(stripped[start : end + 1])


def binary_eval_payload(case: EvalCase, payload: dict) -> list[JudgeBinaryEvalResult]:
    expected = {item.id: item for item in (case.judge.binary_evals if case.judge else [])}
    returned: dict[str, JudgeBinaryEvalResult] = {}
    for item in payload.get("binary_evals", []) or []:
        if not isinstance(item, dict):
            continue
        eval_id = str(item.get("id", ""))
        if eval_id not in expected:
            continue
        spec = expected[eval_id]
        passed_raw = item.get("passed")
        passed = passed_raw is True
        evidence = str(item.get("evidence") or "")
        if not isinstance(passed_raw, bool):
            evidence = f"Invalid `passed` value for judge binary eval: expected JSON boolean, got {passed_raw!r}."
        returned[eval_id] = JudgeBinaryEvalResult(
            id=eval_id,
            passed=passed,
            category=str(item.get("category") or spec.category or ""),
            question=str(item.get("question") or spec.question),
            evidence=evidence,
        )
    return [
        returned.get(
            eval_id,
            JudgeBinaryEvalResult(
                id=eval_id,
                passed=False,
                category=str(spec.category or ""),
                question=str(spec.question),
                evidence="Judge response omitted this configured binary eval.",
            ),
        )
        for eval_id, spec in expected.items()
    ]


def judge_categories(case: EvalCase) -> list[str]:
    if case.judge and case.judge.categories:
        return [key for key in case.judge.categories if key in case.rubric]
    semantic_defaults = ["scope_control", "eo_adherence", "communication", "design_quality", "maintainability"]
    selected = [key for key in semantic_defaults if key in case.rubric]
    return selected or list(case.rubric)


def parse_judge_response(
    response_text: str,
    case: EvalCase,
    allowed_categories: Iterable[str] | None = None,
    *,
    extract_streamed_messages: bool = False,
) -> JudgeResult:
    """Parse a judge's raw output into a structured `JudgeResult`.

    `extract_streamed_messages=True` first walks Codex CLI agent_message frames in
    reverse order. For plain HTTP responses (one chat completion body), set False.
    """
    rubric = case.rubric
    allowed = set(rubric if allowed_categories is None else allowed_categories)
    errors: list[str] = []

    candidates: list[str] = []
    if extract_streamed_messages:
        candidates.extend(reversed(message_texts(response_text)))
    candidates.append(response_text)

    for text in candidates:
        try:
            payload = extract_json_payload(text)
            raw_categories = payload.get("categories", {})
            categories: dict[str, int] = {}
            for key, value in raw_categories.items():
                if key not in rubric or key not in allowed:
                    continue
                categories[key] = max(0, min(int(value), int(rubric[key])))
            return JudgeResult(
                categories=categories,
                failure_tags=[str(tag) for tag in payload.get("failure_tags", [])],
                summary=str(payload.get("summary", "")),
                binary_evals=binary_eval_payload(case, payload),
                raw=text,
            )
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            errors.append(str(exc))
    return JudgeResult(
        categories={},
        failure_tags=["judge_parse_failed"],
        summary="; ".join(errors[-2:]),
        raw=response_text,
    )


def build_judge_prompt(
    case: EvalCase,
    prompt_text: str,
    diff: str,
    deterministic_summary: str,
    before_tree: str | None = None,
) -> str:
    criteria = "\n".join(f"- {item}" for item in (case.judge.criteria if case.judge else []))
    binary_evals = case.judge.binary_evals if case.judge else []
    binary_eval_instructions = "\n".join(
        f"- `{item.id}` ({item.category or 'uncategorized'}): {item.question}\n"
        f"  Pass: {item.pass_condition or 'Satisfies the intended design signal.'}\n"
        f"  Fail: {item.fail_condition or 'Does not satisfy the intended design signal.'}"
        for item in binary_evals
    )
    rubric = json.dumps(case.rubric, indent=2, sort_keys=True)
    categories = judge_categories(case)
    example_categories = json.dumps({key: case.rubric[key] for key in categories}, sort_keys=True)
    example_binary = json.dumps(
        [
            {
                "id": item.id,
                "passed": True,
                "category": item.category or "",
                "question": item.question,
                "evidence": "short concrete reason",
            }
            for item in binary_evals
        ],
        indent=2,
    )
    allowed_categories = ", ".join(f"`{key}`" for key in categories)
    before_section = ""
    if before_tree:
        before_section = (
            f"\nStarting project state (the fixture seen by the agent before its patch was applied):\n{before_tree}\n"
        )
    return f"""You are a strict LLM-as-judge for a coding-agent prompt evaluation.

Do not edit files. Judge only the submitted patch.

Return exactly one JSON object with this shape:
{{
  "categories": {example_categories},
  "binary_evals": {example_binary if binary_evals else "[]"},
  "failure_tags": ["short_tag_if_any"],
  "summary": "one short sentence"
}}

The category values above are examples at the maximum score. For each category, return an integer from 0 to that category's rubric maximum: 0 means severe semantic failure; the rubric maximum means fully satisfied.
Use only these semantic category keys: {allowed_categories}. You may omit categories that do not need semantic judgment.
Do not score deterministic categories such as functional correctness or verification unless they are explicitly listed above. Do not increase scores for deterministic checks; those are handled separately. Keep category values within this rubric:
{rubric}

Task:
{case.task}
{before_section}

Semantic criteria:
{criteria or "- Judge whether the patch follows the stated prompt without overfitting or broad unrelated refactoring."}

Binary evals:
{binary_eval_instructions or "- None. Omit or return an empty binary_evals list."}

Deterministic check summary:
{deterministic_summary}

Agent prompt under evaluation:
---
{prompt_text}
---

Patch:
```diff
{diff}
```
"""
