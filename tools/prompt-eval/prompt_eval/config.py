from __future__ import annotations
from pathlib import Path
import yaml
from .models import EvalCase, CaseChecks, CaseJudge, RegexCheck

def _load(path: Path):
    return yaml.safe_load(path.read_text()) or {}

def _list(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    return list(value)

def _unique(items: list[str]) -> list[str]:
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result

def _case_entry(entry) -> tuple[str, list[str]]:
    if isinstance(entry, str):
        return entry, []
    if isinstance(entry, dict):
        path = entry.get("path") or entry.get("case")
        if not path:
            raise ValueError(f"Suite case entry is missing path/case: {entry!r}")
        return path, _list(entry.get("sets"))
    raise ValueError(f"Unsupported suite case entry: {entry!r}")

def load_case(path: Path, sets: list[str] | None = None) -> EvalCase:
    raw = _load(path)
    checks = raw.get("checks", {})
    mk = lambda items: [RegexCheck(**i) for i in items or []]
    case_checks = CaseChecks(commands=checks.get("commands", []), required_files=checks.get("required_files", []), forbidden_regex=mk(checks.get("forbidden_regex")), required_regex=mk(checks.get("required_regex")), max_changed_files=checks.get("max_changed_files"))
    case_sets = _unique(_list(raw.get("sets")) + _list(sets))
    judge_raw = raw.get("judge")
    judge = CaseJudge(criteria=_list(judge_raw.get("criteria"))) if isinstance(judge_raw, dict) else None
    return EvalCase(id=raw["id"], title=raw["title"], fixture=raw["fixture"], task=raw["task"], checks=case_checks, rubric=raw.get("rubric", {}), notes=raw.get("notes", ""), sets=case_sets, judge=judge)

def load_suite(root: Path, suite_name: str, case_sets: list[str] | None = None) -> list[EvalCase]:
    suite = _load(root / "evals" / suite_name / "suite.yaml")
    selected = set(_list(case_sets))
    cases = []
    for entry in suite["cases"]:
        path, sets = _case_entry(entry)
        case = load_case(root / "evals" / suite_name / "cases" / path, sets)
        if not selected or selected.intersection(case.sets):
            cases.append(case)
    return cases

def suite_case_sets(root: Path, suite_name: str) -> list[str]:
    sets = []
    seen = set()
    for case in load_suite(root, suite_name):
        for case_set in case.sets:
            if case_set not in seen:
                seen.add(case_set)
                sets.append(case_set)
    return sets
