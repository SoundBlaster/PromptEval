from __future__ import annotations
from pathlib import Path
from collections import defaultdict
from .models import CaseRunResult


def _category_keys(results: list[CaseRunResult]) -> list[str]:
    keys = []
    seen = set()
    for result in results:
        for key in result.score.categories:
            if key not in seen:
                seen.add(key)
                keys.append(key)
    return keys


def _label(key: str) -> str:
    if key.startswith("eo_"):
        return "EO " + key[3:].replace("_", " ").title()
    return key.replace("_", " ").title()


def write_report(run_dir: Path, suite: str, results: list[CaseRunResult]) -> Path:
    md = ["# Prompt Eval Report", "", f"Suite: {suite}", f"Run: {run_dir.name}", ""]
    category_keys = _category_keys(results)
    grouped = defaultdict(list)
    for r in results: grouped[r.prompt].append(r)
    headers = ["Prompt", "Cases", "Avg score", *[_label(k) for k in category_keys]]
    md.append("| " + " | ".join(headers) + " |")
    md.append("|" + "|".join(["---", "---:", "---:", *(["---:"] * len(category_keys))]) + "|")
    for p, rs in grouped.items():
        n = len(rs)
        avg = sum(x.score.total for x in rs) / n
        cat = lambda k: sum(x.score.categories.get(k, 0) for x in rs)/n
        row = [Path(p).name, str(n), f"{avg:.1f}", *[f"{cat(k):.1f}" for k in category_keys]]
        md.append("| " + " | ".join(row) + " |")
    by_case = defaultdict(list)
    for r in results: by_case[r.case_id].append(r)
    for case, rs in by_case.items():
        md += ["", f"## {case}", "", "| Prompt | Score | Result | Failure tags |", "|---|---:|---|---|"]
        for r in rs:
            ok = "pass" if all(c.passed for c in r.checks) else "fail"
            md.append(f"| {Path(r.prompt).name} | {r.score.total} | {ok} | {', '.join(r.score.failure_tags)} |")
            md.append(f"- Diff: `{r.diff_path}`; Transcript: `{r.transcript_path}`")
    out = run_dir / "report.md"
    out.write_text("\n".join(md))
    return out
