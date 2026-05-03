from __future__ import annotations
from pathlib import Path
import shutil, subprocess
from .base import AgentRun

def run_codex(sandbox: Path, task: str, prompt_text: str, model: str | None = None) -> AgentRun:
    if shutil.which("codex") is None:
        return AgentRun(ok=False, stderr="codex CLI not found", trace=[{"event":"codex_missing"}])
    (sandbox / "AGENTS.md").write_text(prompt_text)
    cmd = ["codex", "exec", "--json", "--full-auto"]
    if model:
        cmd += ["--model", model]
    cmd.append(task)
    proc = subprocess.run(cmd, cwd=sandbox, capture_output=True, text=True)
    trace = []
    if proc.stdout:
        trace = [{"raw": l} for l in proc.stdout.splitlines()]
    return AgentRun(ok=proc.returncode == 0, stdout=proc.stdout, stderr=proc.stderr, trace=trace)
