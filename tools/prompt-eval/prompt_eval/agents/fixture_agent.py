from pathlib import Path
import shutil
from .base import AgentRun


def apply_fixture_solution(sandbox: Path, fixture_root: Path, kind: str) -> AgentRun:
    sol = fixture_root / "solutions" / kind
    shutil.copytree(sol, sandbox, dirs_exist_ok=True)
    return AgentRun(stdout=f"applied fixture {kind}", trace=[{"event": "fixture_apply", "kind": kind}])
