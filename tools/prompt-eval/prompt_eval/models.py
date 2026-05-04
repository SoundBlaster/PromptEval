from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any
from .judges.base import JudgeResult

DEFAULT_RUBRIC = {
    "functional_correctness": 40,
    "scope_control": 20,
    "design_quality": 25,
    "verification": 10,
    "communication": 5,
}


@dataclass
class RegexCheck:
    pattern: str
    target: str = "diff"
    reason: str = ""
    paths: list[str] = field(default_factory=list)


@dataclass
class CaseChecks:
    commands: list[str | list[str]] = field(default_factory=list)
    required_files: list[str] = field(default_factory=list)
    forbidden_regex: list[RegexCheck] = field(default_factory=list)
    required_regex: list[RegexCheck] = field(default_factory=list)
    max_changed_files: int | None = None


@dataclass
class JudgeBinaryEval:
    id: str
    question: str
    pass_condition: str = ""
    fail_condition: str = ""
    category: str = ""


@dataclass
class CaseJudge:
    criteria: list[str] = field(default_factory=list)
    categories: list[str] = field(default_factory=list)
    binary_evals: list[JudgeBinaryEval] = field(default_factory=list)


@dataclass
class EvalCase:
    id: str
    title: str
    fixture: str
    task: str
    checks: CaseChecks
    rubric: dict[str, int]
    notes: str = ""
    sets: list[str] = field(default_factory=list)
    judge: CaseJudge | None = None


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
    case_sets: list[str] = field(default_factory=list)
    judge: JudgeResult | None = None
    stdout: str = ""
    stderr: str = ""

    def to_json(self) -> dict[str, Any]:
        data = asdict(self)
        return data
