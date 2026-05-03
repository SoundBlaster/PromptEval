from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from .base import JudgeResult
from ..agents.codex_agent import MODEL_MODE_CONFIG, codex_command, create_codex_home
from ..models import EvalCase


def _message_texts(stdout: str) -> list[str]:
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


def _json_payload(text: str) -> dict:
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = [line for line in stripped.splitlines() if not line.strip().startswith("```")]
        stripped = "\n".join(lines).strip()
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError("judge response does not contain a JSON object")
    return json.loads(stripped[start : end + 1])


def _parse(stdout: str, rubric: dict[str, int]) -> JudgeResult:
    errors = []
    for text in list(reversed(_message_texts(stdout))) + [stdout]:
        try:
            payload = _json_payload(text)
            raw_categories = payload.get("categories", {})
            categories = {}
            for key, value in raw_categories.items():
                if key not in rubric:
                    continue
                categories[key] = max(0, min(int(value), int(rubric[key])))
            return JudgeResult(
                categories=categories,
                failure_tags=[str(tag) for tag in payload.get("failure_tags", [])],
                summary=str(payload.get("summary", "")),
                raw=text,
            )
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            errors.append(str(exc))
    return JudgeResult(categories={}, failure_tags=["judge_parse_failed"], summary="; ".join(errors[-2:]), raw=stdout)


def _prompt(case: EvalCase, prompt_text: str, diff: str, deterministic_summary: str) -> str:
    criteria = "\n".join(f"- {item}" for item in (case.judge.criteria if case.judge else []))
    rubric = json.dumps(case.rubric, indent=2, sort_keys=True)
    example_categories = json.dumps({key: 0 for key in case.rubric}, sort_keys=True)
    allowed_categories = ", ".join(f"`{key}`" for key in case.rubric)
    return f"""You are a strict LLM-as-judge for a coding-agent prompt evaluation.

Do not edit files. Judge only the submitted patch.

Return exactly one JSON object with this shape:
{{
  "categories": {example_categories},
  "failure_tags": ["short_tag_if_any"],
  "summary": "one short sentence"
}}

Use only these category keys: {allowed_categories}. You may omit categories that do not need semantic judgment.
Score only categories that require semantic judgment. Do not increase scores for deterministic checks; those are handled separately. Keep category values within this rubric:
{rubric}

Task:
{case.task}

Semantic criteria:
{criteria or "- Judge whether the patch follows the stated prompt without overfitting or broad unrelated refactoring."}

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


def judge_subagent(
    case: EvalCase,
    prompt_text: str,
    diff: str,
    deterministic_summary: str,
    model: str | None = None,
    model_mode: str | None = None,
    codex_bin: str | None = None,
) -> JudgeResult:
    executable = codex_command(codex_bin)
    if executable is None:
        return JudgeResult(categories={}, failure_tags=["judge_missing"], summary="codex CLI not found")

    work_dir = Path(tempfile.mkdtemp(prefix="peval-judge-"))
    codex_home = create_codex_home()
    env = os.environ.copy()
    env["CODEX_HOME"] = str(codex_home)
    cmd = [executable, "exec", "--ignore-user-config", "--skip-git-repo-check", "--json", "--full-auto"]
    if model:
        cmd += ["--model", model]
    if model_mode:
        cmd += ["--config", MODEL_MODE_CONFIG[model_mode]]
    cmd.append(_prompt(case, prompt_text, diff, deterministic_summary))
    try:
        proc = subprocess.run(cmd, cwd=work_dir, env=env, capture_output=True, text=True)
        if proc.returncode != 0:
            detail = (proc.stdout + proc.stderr)[-800:]
            return JudgeResult(categories={}, failure_tags=["judge_failed"], summary=detail, raw=proc.stdout)
        return _parse(proc.stdout, case.rubric)
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)
        shutil.rmtree(codex_home, ignore_errors=True)
