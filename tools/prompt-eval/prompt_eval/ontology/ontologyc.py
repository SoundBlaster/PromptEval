from __future__ import annotations
import os
import subprocess
import sys
from pathlib import Path

# Thin wrapper that lets a harness case invoke the real `ontologyc` compiler from the Ontology
# repository as a deterministic check. The repo location is provided out-of-band via ONTOLOGY_REPO
# so the suite stays portable. A prebuilt binary under .build/debug is preferred; otherwise we fall
# back to `swift run`, which builds on first use.


def _resolve_command(repo: Path, subcommand: str, file_abs: Path) -> list[str]:
    binary = repo / ".build" / "debug" / "ontologyc"
    if binary.exists():
        return [str(binary), subcommand, str(file_abs)]
    return ["swift", "run", "--package-path", str(repo), "ontologyc", subcommand, str(file_abs)]


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 2:
        print("usage: peval-ontologyc <check|compile> <package.yaml>", file=sys.stderr)
        return 2
    subcommand, file = args
    repo_env = os.environ.get("ONTOLOGY_REPO")
    if not repo_env:
        print("ONTOLOGY_REPO is not set; cannot locate the ontologyc compiler", file=sys.stderr)
        return 2
    repo = Path(repo_env).expanduser()
    if not repo.exists():
        print(f"ONTOLOGY_REPO does not exist: {repo}", file=sys.stderr)
        return 2
    file_abs = Path(file).resolve()
    if not file_abs.exists():
        print(f"package file not found: {file_abs}", file=sys.stderr)
        return 1
    cmd = _resolve_command(repo, subcommand, file_abs)
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.stdout:
        sys.stdout.write(proc.stdout)
    if proc.stderr:
        sys.stderr.write(proc.stderr)
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
