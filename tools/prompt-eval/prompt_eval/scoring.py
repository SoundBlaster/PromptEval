from .models import CATEGORY_KEYS, CheckResult, ScoreBreakdown

def score_from_checks(checks: list[CheckResult]) -> ScoreBreakdown:
    passed = sum(1 for c in checks if c.passed)
    total = len(checks) or 1
    ratio = passed / total
    cats = {
        "functional_correctness": int(40 * ratio),
        "scope_control": int(20 * ratio),
        "eo_adherence": int(25 * ratio),
        "verification": int(10 * ratio),
        "communication": 5 if ratio > 0.7 else (2 if ratio > 0.3 else 0),
    }
    tags = []
    if any((not c.passed and c.name.startswith("command:")) for c in checks):
        tags.append("tests_failed")
    if any((not c.passed and "forbidden_regex:@staticmethod" in c.name) for c in checks):
        tags.append("static_helper_relapse")
    if any((not c.passed and c.name == "max_changed_files") for c in checks):
        tags.append("excessive_diff")
    total_score = sum(cats[k] for k in CATEGORY_KEYS)
    return ScoreBreakdown(categories=cats, total=total_score, failure_tags=tags, summary=f"{passed}/{total} checks passed")
