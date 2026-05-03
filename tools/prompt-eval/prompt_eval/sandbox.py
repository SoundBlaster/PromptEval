from __future__ import annotations
from pathlib import Path
import shutil, subprocess, tempfile


def prepare_sandbox(fixture_before: Path) -> Path:
    tmp = Path(tempfile.mkdtemp(prefix="peval-"))
    shutil.copytree(fixture_before, tmp, dirs_exist_ok=True)
    subprocess.run(["git", "init"], cwd=tmp, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "peval@example.local"], cwd=tmp, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "peval"], cwd=tmp, check=True, capture_output=True)
    subprocess.run(["git", "add", "."], cwd=tmp, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "baseline"], cwd=tmp, check=True, capture_output=True)
    return tmp
