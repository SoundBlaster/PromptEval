from __future__ import annotations
from pathlib import Path
import fnmatch
import re
import shlex
import subprocess
from .models import EvalCase, CheckResult


SKIP_FILE_PARTS = {".git", ".venv", "venv", "env", "site-packages", "__pycache__"}


def git_diff(sandbox: Path) -> str:
    return subprocess.run(["git", "diff"], cwd=sandbox, text=True, capture_output=True, check=True).stdout


def changed_files_count(diff: str) -> int:
    return len([line for line in diff.splitlines() if line.startswith("diff --git")])


def command_argv(cmd: str | list[str]) -> list[str]:
    return cmd if isinstance(cmd, list) else shlex.split(cmd)


def command_name(cmd: str | list[str]) -> str:
    return shlex.join(command_argv(cmd))


def python_files_blob(sandbox: Path, patterns: list[str] | None = None) -> str:
    proc = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "--", "*.py"],
        cwd=sandbox,
        text=True,
        capture_output=True,
        check=True,
    )
    chunks = []
    for rel in proc.stdout.splitlines():
        if patterns and not any(fnmatch.fnmatch(rel, pattern) for pattern in patterns):
            continue
        path = sandbox / rel
        if any(part in SKIP_FILE_PARTS for part in path.relative_to(sandbox).parts):
            continue
        chunks.append(path.read_text(errors="ignore"))
    return "\n".join(chunks)


def run_checks(case: EvalCase, sandbox: Path, diff: str) -> list[CheckResult]:
    out = []
    for cmd in case.checks.commands:
        p = subprocess.run(command_argv(cmd), cwd=sandbox, text=True, capture_output=True)
        out.append(CheckResult(p.returncode == 0, f"command:{command_name(cmd)}", (p.stdout + p.stderr)[-400:]))
    for req in case.checks.required_files:
        out.append(CheckResult((sandbox / req).exists(), f"required_file:{req}"))
    for rr in case.checks.required_regex:
        hay = diff if rr.target == "diff" else python_files_blob(sandbox, rr.paths)
        ok = bool(re.search(rr.pattern, hay, re.MULTILINE))
        out.append(CheckResult(ok, f"required_regex:{rr.pattern}", rr.reason))
    for fr in case.checks.forbidden_regex:
        hay = diff if fr.target == "diff" else python_files_blob(sandbox, fr.paths)
        ok = not bool(re.search(fr.pattern, hay, re.MULTILINE))
        out.append(CheckResult(ok, f"forbidden_regex:{fr.pattern}", fr.reason))
    if case.checks.max_changed_files is not None:
        c = changed_files_count(diff)
        out.append(CheckResult(c <= case.checks.max_changed_files, "max_changed_files", f"changed={c}"))
    return out
