from __future__ import annotations
from .models import DEFAULT_RUBRIC, CheckResult, ScoreBreakdown
from .judges.base import JudgeResult

def score_from_checks(checks: list[CheckResult], rubric: dict[str, int] | None = None, judge: JudgeResult | None = None) -> ScoreBreakdown:
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
    summary = f"{passed}/{total} checks passed"
    if judge:
        for key, value in judge.categories.items():
            if key in cats:
                cats[key] = min(cats[key], value)
        tags.extend(tag for tag in judge.failure_tags if tag not in tags)
        if judge.summary:
            summary += f"; judge: {judge.summary}"
    total_score = sum(cats.values())
    return ScoreBreakdown(categories=cats, total=total_score, failure_tags=tags, summary=summary)
