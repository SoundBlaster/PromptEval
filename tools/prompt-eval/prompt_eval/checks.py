from __future__ import annotations
from pathlib import Path
import re, subprocess
from .models import EvalCase, CheckResult


def git_diff(sandbox: Path) -> str:
    return subprocess.run(["git", "diff"], cwd=sandbox, text=True, capture_output=True, check=True).stdout


def changed_files_count(diff: str) -> int:
    return len([l for l in diff.splitlines() if l.startswith("diff --git")])


def run_checks(case: EvalCase, sandbox: Path, diff: str) -> list[CheckResult]:
    out = []
    for cmd in case.checks.commands:
        p = subprocess.run(cmd, shell=True, cwd=sandbox, text=True, capture_output=True)
        out.append(CheckResult(p.returncode == 0, f"command:{cmd}", (p.stdout + p.stderr)[-400:]))
    for req in case.checks.required_files:
        out.append(CheckResult((sandbox / req).exists(), f"required_file:{req}"))
    files_blob = "\n".join([p.read_text(errors="ignore") for p in sandbox.rglob("*.py")])
    for rr in case.checks.required_regex:
        hay = diff if rr.target == "diff" else files_blob
        ok = bool(re.search(rr.pattern, hay, re.MULTILINE))
        out.append(CheckResult(ok, f"required_regex:{rr.pattern}", rr.reason))
    for fr in case.checks.forbidden_regex:
        hay = diff if fr.target == "diff" else files_blob
        ok = not bool(re.search(fr.pattern, hay, re.MULTILINE))
        out.append(CheckResult(ok, f"forbidden_regex:{fr.pattern}", fr.reason))
    if case.checks.max_changed_files is not None:
        c = changed_files_count(diff)
        out.append(CheckResult(c <= case.checks.max_changed_files, "max_changed_files", f"changed={c}"))
    return out
