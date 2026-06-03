from __future__ import annotations
import os
from pathlib import Path
import shutil
import subprocess
from .base import AgentRun
from .effort import COPILOT_EFFORT

__all__ = ["run_copilot", "copilot_command", "copilot_error"]


def copilot_command(copilot_bin: str | None = None) -> list[str] | None:
    """Resolve the GitHub Copilot CLI invocation prefix.

    Order: explicit --copilot-bin / PEVAL_COPILOT_BIN, then a `copilot` binary on PATH,
    then the `gh copilot --` wrapper (which runs the gh-managed Copilot CLI). Returns the
    argv prefix to which agent flags are appended, or None when nothing resolves.
    """
    selected = copilot_bin or os.environ.get("PEVAL_COPILOT_BIN")
    if selected:
        return [selected] if Path(selected).exists() or shutil.which(selected) else None
    if shutil.which("copilot"):
        return ["copilot"]
    if shutil.which("gh"):
        return ["gh", "copilot", "--"]
    return None


def copilot_error(copilot_bin: str | None = None) -> str:
    if copilot_bin:
        return f"copilot CLI not found: --copilot-bin {copilot_bin!r} did not resolve as a path or PATH command"
    env_bin = os.environ.get("PEVAL_COPILOT_BIN")
    if env_bin:
        return f"copilot CLI not found: PEVAL_COPILOT_BIN={env_bin!r} did not resolve as a path or PATH command"
    return "copilot CLI not found (install the Copilot CLI or `gh copilot`)"


def run_copilot(
    sandbox: Path,
    task: str,
    prompt_text: str,
    model: str | None = None,
    model_mode: str | None = None,
    copilot_bin: str | None = None,
) -> AgentRun:
    prefix = copilot_command(copilot_bin)
    if prefix is None:
        return AgentRun(ok=False, stderr=copilot_error(copilot_bin), trace=[{"event": "copilot_missing"}])
    if model_mode and model_mode not in COPILOT_EFFORT:
        supported = ", ".join(sorted(COPILOT_EFFORT))
        return AgentRun(
            ok=False,
            stderr=f"unsupported model mode {model_mode!r}; supported modes: {supported}",
            trace=[{"event": "copilot_unsupported_model_mode", "model_mode": model_mode}],
        )
    # Copilot reads repository guidance from AGENTS.md; seed it with the policy prompt so the
    # engine receives the same instruction surface that the codex adapter writes.
    (sandbox / "AGENTS.md").write_text(prompt_text)
    # --disable-builtin-mcps keeps evals from inheriting the global github-mcp-server, mirroring
    # the codex adapter's --ignore-user-config isolation. Auth (gh/keychain) is left intact.
    cmd = [*prefix, "-p", task, "--allow-all-tools", "--allow-all-paths", "--disable-builtin-mcps"]
    if model:
        cmd += ["--model", model]
    if model_mode:
        cmd += ["--effort", COPILOT_EFFORT[model_mode]]
    proc = subprocess.run(cmd, cwd=sandbox, capture_output=True, text=True)
    trace = []
    if proc.stdout:
        trace = [{"raw": line} for line in proc.stdout.splitlines()]
    return AgentRun(ok=proc.returncode == 0, stdout=proc.stdout, stderr=proc.stderr, trace=trace)
