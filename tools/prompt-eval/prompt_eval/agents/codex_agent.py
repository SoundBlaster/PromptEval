from __future__ import annotations
import os
from pathlib import Path
import shutil, subprocess, tempfile
from .base import AgentRun

MODEL_MODE_CONFIG = {
    "fast": 'model_reasoning_effort="low"',
}

CODEX_CONFIG = """approval_policy = "never"
sandbox_mode = "workspace-write"

[features]
shell_snapshot = false
multi_agent = false
"""


def create_codex_home() -> Path:
    source_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    codex_home = Path(tempfile.mkdtemp(prefix="peval-codex-home-"))
    codex_home.mkdir(parents=True, exist_ok=True)
    (codex_home / "config.toml").write_text(CODEX_CONFIG)
    auth = source_home / "auth.json"
    if auth.exists():
        shutil.copy2(auth, codex_home / "auth.json")
    return codex_home


def codex_command(codex_bin: str | None = None) -> str | None:
    selected = codex_bin or os.environ.get("PEVAL_CODEX_BIN")
    if selected:
        return selected if Path(selected).exists() or shutil.which(selected) else None
    return "codex" if shutil.which("codex") else None


def codex_error(codex_bin: str | None = None) -> str:
    if codex_bin:
        return f"codex CLI not found: --codex-bin {codex_bin!r} did not resolve as a path or PATH command"
    env_bin = os.environ.get("PEVAL_CODEX_BIN")
    if env_bin:
        return f"codex CLI not found: PEVAL_CODEX_BIN={env_bin!r} did not resolve as a path or PATH command"
    return "codex CLI not found"


def run_codex(
    sandbox: Path,
    task: str,
    prompt_text: str,
    model: str | None = None,
    model_mode: str | None = None,
    codex_bin: str | None = None,
) -> AgentRun:
    executable = codex_command(codex_bin)
    if executable is None:
        return AgentRun(ok=False, stderr=codex_error(codex_bin), trace=[{"event":"codex_missing"}])
    if model_mode and model_mode not in MODEL_MODE_CONFIG:
        supported = ", ".join(sorted(MODEL_MODE_CONFIG))
        return AgentRun(ok=False, stderr=f"unsupported model mode {model_mode!r}; supported modes: {supported}", trace=[{"event":"codex_unsupported_model_mode", "model_mode":model_mode}])
    (sandbox / "AGENTS.md").write_text(prompt_text)
    cmd = [executable, "exec", "--ignore-user-config", "--json", "--full-auto"]
    if model:
        cmd += ["--model", model]
    if model_mode:
        cmd += ["--config", MODEL_MODE_CONFIG[model_mode]]
    cmd.append(task)
    codex_home = create_codex_home()
    env = os.environ.copy()
    env["CODEX_HOME"] = str(codex_home)
    try:
        proc = subprocess.run(cmd, cwd=sandbox, env=env, capture_output=True, text=True)
    finally:
        shutil.rmtree(codex_home, ignore_errors=True)
    trace = []
    if proc.stdout:
        trace = [{"raw": l} for l in proc.stdout.splitlines()]
    return AgentRun(ok=proc.returncode == 0, stdout=proc.stdout, stderr=proc.stderr, trace=trace)
