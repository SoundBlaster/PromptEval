from __future__ import annotations
from .models import DEFAULT_RUBRIC, CheckResult, ScoreBreakdown

def score_from_checks(checks: list[CheckResult], rubric: dict[str, int] | None = None) -> ScoreBreakdown:
    passed = sum(1 for c in checks if c.passed)
    total = len(checks) or 1
    ratio = passed / total
    weights = rubric or DEFAULT_RUBRIC
    cats = {key: int(weight * ratio) for key, weight in weights.items()}
    tags = []
    if any((not c.passed and c.name.startswith("command:")) for c in checks):
        tags.append("commands_failed")
    if any((not c.passed and "forbidden_regex:@staticmethod" in c.name) for c in checks):
        tags.append("static_helper_relapse")
    if any((not c.passed and c.name == "max_changed_files") for c in checks):
        tags.append("excessive_diff")
    total_score = sum(cats.values())
    return ScoreBreakdown(categories=cats, total=total_score, failure_tags=tags, summary=f"{passed}/{total} checks passed")
