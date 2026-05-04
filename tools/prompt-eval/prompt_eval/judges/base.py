from dataclasses import dataclass, field


@dataclass
class JudgeBinaryEvalResult:
    id: str
    passed: bool
    category: str = ""
    question: str = ""
    evidence: str = ""

@dataclass
class JudgeResult:
    categories: dict[str, int]
    failure_tags: list[str]
    summary: str
    binary_evals: list[JudgeBinaryEvalResult] = field(default_factory=list)
    raw: str = ""
