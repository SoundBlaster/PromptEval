from __future__ import annotations
from pathlib import Path
import yaml
from .models import EvalCase, CaseChecks, RegexCheck

def _load(path: Path):
    return yaml.safe_load(path.read_text()) or {}

def load_case(path: Path) -> EvalCase:
    raw = _load(path)
    checks = raw.get("checks", {})
    mk = lambda items: [RegexCheck(**i) for i in items or []]
    case_checks = CaseChecks(commands=checks.get("commands", []), required_files=checks.get("required_files", []), forbidden_regex=mk(checks.get("forbidden_regex")), required_regex=mk(checks.get("required_regex")), max_changed_files=checks.get("max_changed_files"))
    return EvalCase(id=raw["id"], title=raw["title"], fixture=raw["fixture"], task=raw["task"], checks=case_checks, rubric=raw.get("rubric", {}), notes=raw.get("notes", ""))

def load_suite(root: Path, suite_name: str) -> list[EvalCase]:
    suite = _load(root / "evals" / suite_name / "suite.yaml")
    return [load_case(root / "evals" / suite_name / "cases" / p) for p in suite["cases"]]
