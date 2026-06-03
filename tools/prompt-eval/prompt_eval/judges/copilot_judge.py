from __future__ import annotations
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from .base import JudgeResult
from .common import build_judge_prompt, judge_categories, parse_judge_response
from ..agents.copilot_agent import copilot_command, copilot_error
from ..agents.effort import COPILOT_EFFORT
from ..models import EvalCase


def judge_copilot(
    case: EvalCase,
    prompt_text: str,
    diff: str,
    deterministic_summary: str,
    model: str | None = None,
    model_mode: str | None = None,
    copilot_bin: str | None = None,
    before_tree: str | None = None,
) -> JudgeResult:
    prefix = copilot_command(copilot_bin)
    if prefix is None:
        return JudgeResult(
            categories={},
            failure_tags=["judge_missing"],
            summary=copilot_error(copilot_bin),
        )

    work_dir = Path(tempfile.mkdtemp(prefix="peval-copilot-judge-"))
    judge_prompt = build_judge_prompt(case, prompt_text, diff, deterministic_summary, before_tree=before_tree)
    # Copilot reads the judge rubric from the prompt; env var overrides keep it isolated from
    # the user's global Copilot config the same way the codex judge uses a temp CODEX_HOME.
    env = os.environ.copy()
    cmd = [*prefix, "-p", judge_prompt, "--allow-all-tools", "--allow-all-paths", "--disable-builtin-mcps"]
    if model:
        cmd += ["--model", model]
    if model_mode and model_mode in COPILOT_EFFORT:
        cmd += ["--effort", COPILOT_EFFORT[model_mode]]
    try:
        proc = subprocess.run(cmd, cwd=str(work_dir), env=env, capture_output=True, text=True)
        if proc.returncode != 0:
            detail = (proc.stdout + proc.stderr)[-800:]
            return JudgeResult(categories={}, failure_tags=["judge_failed"], summary=detail, raw=proc.stdout)
        # Copilot outputs plain text (not a Codex JSON event stream), so we parse directly.
        return parse_judge_response(proc.stdout, case, judge_categories(case), extract_streamed_messages=False)
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)
