from __future__ import annotations
from pathlib import Path
from collections import defaultdict
from .models import CaseRunResult


def write_report(run_dir: Path, suite: str, results: list[CaseRunResult]) -> Path:
    md = ["# Prompt Eval Report", "", f"Suite: {suite}", f"Run: {run_dir.name}", ""]
    grouped = defaultdict(list)
    for r in results: grouped[r.prompt].append(r)
    md.append("| Prompt | Cases | Avg score | Functional | Scope | EO | Verification | Communication |")
    md.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    for p, rs in grouped.items():
        n = len(rs)
        avg = sum(x.score.total for x in rs) / n
        cat = lambda k: sum(x.score.categories[k] for x in rs)/n
        md.append(f"| {Path(p).name} | {n} | {avg:.1f} | {cat('functional_correctness'):.1f} | {cat('scope_control'):.1f} | {cat('eo_adherence'):.1f} | {cat('verification'):.1f} | {cat('communication'):.1f} |")
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
