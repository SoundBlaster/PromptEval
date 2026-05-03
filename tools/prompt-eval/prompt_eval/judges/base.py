from dataclasses import dataclass

@dataclass
class JudgeResult:
    categories: dict[str, int]
    failure_tags: list[str]
    summary: str
    raw: str = ""
