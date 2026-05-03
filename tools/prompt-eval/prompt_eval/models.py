from __future__ import annotations
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

CATEGORY_KEYS = ["functional_correctness", "scope_control", "eo_adherence", "verification", "communication"]

@dataclass
class RegexCheck:
    pattern: str
    target: str = "diff"
    reason: str = ""

@dataclass
class CaseChecks:
    commands: list[str] = field(default_factory=list)
    required_files: list[str] = field(default_factory=list)
    forbidden_regex: list[RegexCheck] = field(default_factory=list)
    required_regex: list[RegexCheck] = field(default_factory=list)
    max_changed_files: int | None = None

@dataclass
class EvalCase:
    id: str
    title: str
    fixture: str
    task: str
    checks: CaseChecks
    rubric: dict[str, int]
    notes: str = ""

@dataclass
class CheckResult:
    passed: bool
    name: str
    detail: str = ""

@dataclass
class ScoreBreakdown:
    categories: dict[str, int]
    total: int
    failure_tags: list[str] = field(default_factory=list)
    summary: str = ""

@dataclass
class CaseRunResult:
    suite: str
    prompt: str
    case_id: str
    score: ScoreBreakdown
    checks: list[CheckResult]
    diff_path: str
    transcript_path: str
    stdout: str = ""
    stderr: str = ""

    def to_json(self) -> dict[str, Any]:
        data = asdict(self)
        return data
