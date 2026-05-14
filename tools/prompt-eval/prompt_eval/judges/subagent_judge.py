from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from .base import JudgeResult
from .common import (
    binary_eval_payload,
    build_judge_prompt,
    extract_json_payload,
    judge_categories,
    message_texts,
    parse_judge_response,
)
from ..agents.codex_agent import MODEL_MODE_CONFIG, codex_command, create_codex_home
from ..models import EvalCase


# Backward-compatible internal helpers (existing tests import these names directly).
_message_texts = message_texts
_json_payload = extract_json_payload
_binary_eval_payload = binary_eval_payload
_judge_categories = judge_categories


def _parse(stdout: str, case: EvalCase, allowed_categories: list[str] | None = None) -> JudgeResult:
    return parse_judge_response(stdout, case, allowed_categories, extract_streamed_messages=True)


def _prompt(
    case: EvalCase,
    prompt_text: str,
    diff: str,
    deterministic_summary: str,
    before_tree: str | None = None,
) -> str:
    return build_judge_prompt(case, prompt_text, diff, deterministic_summary, before_tree=before_tree)


def judge_subagent(
    case: EvalCase,
    prompt_text: str,
    diff: str,
    deterministic_summary: str,
    model: str | None = None,
    model_mode: str | None = None,
    codex_bin: str | None = None,
    before_tree: str | None = None,
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
    cmd.append(_prompt(case, prompt_text, diff, deterministic_summary, before_tree=before_tree))
    try:
        proc = subprocess.run(cmd, cwd=work_dir, env=env, capture_output=True, text=True)
        if proc.returncode != 0:
            detail = (proc.stdout + proc.stderr)[-800:]
            return JudgeResult(categories={}, failure_tags=["judge_failed"], summary=detail, raw=proc.stdout)
        return _parse(proc.stdout, case, _judge_categories(case))
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)
        shutil.rmtree(codex_home, ignore_errors=True)
