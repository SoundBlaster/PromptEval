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

def _case_set_keys(results: list[CaseRunResult]) -> list[str]:
    keys = []
    seen = set()
    for result in results:
        for key in result.case_sets:
            if key not in seen:
                seen.add(key)
                keys.append(key)
    return keys


def _label(key: str) -> str:
    if key.startswith("eo_"):
        return "EO " + key[3:].replace("_", " ").title()
    return key.replace("_", " ").title()


def _cell(value) -> str:
    return str(value).replace("\n", "<br>").replace("|", "\\|")


def write_report(run_dir: Path, suite: str, results: list[CaseRunResult]) -> Path:
    md = ["# Prompt Eval Report", "", f"Suite: {suite}", f"Run: {run_dir.name}", ""]
    category_keys = _category_keys(results)
    case_set_keys = _case_set_keys(results)
    grouped = defaultdict(list)
    for r in results: grouped[r.prompt].append(r)
    headers = ["Prompt", "Cases", "Avg score", *[f"{_label(k)} avg" for k in case_set_keys], *[_label(k) for k in category_keys]]
    md.append("| " + " | ".join(headers) + " |")
    md.append("|" + "|".join(["---", "---:", "---:", *(["---:"] * (len(case_set_keys) + len(category_keys)))]) + "|")
    for p, rs in grouped.items():
        n = len(rs)
        avg = sum(x.score.total for x in rs) / n
        set_avg = lambda k: [x.score.total for x in rs if k in x.case_sets]
        cat = lambda k: sum(x.score.categories.get(k, 0) for x in rs)/n
        row = [Path(p).name, str(n), f"{avg:.1f}"]
        for key in case_set_keys:
            scores = set_avg(key)
            row.append(f"{sum(scores) / len(scores):.1f}" if scores else "n/a")
        row += [f"{cat(k):.1f}" for k in category_keys]
        md.append("| " + " | ".join(row) + " |")
    by_case = defaultdict(list)
    for r in results: by_case[r.case_id].append(r)
    for case, rs in by_case.items():
        case_sets = ", ".join(rs[0].case_sets) if rs and rs[0].case_sets else "uncategorized"
        md += ["", f"## {case}", "", f"Case set: `{case_sets}`", "", "| Prompt | Score | Result | Failure tags | Judge |", "|---|---:|---|---|---|"]
        for r in rs:
            ok = "pass" if all(c.passed for c in r.checks) else "fail"
            judge = r.judge.summary if r.judge else ""
            md.append(f"| {_cell(Path(r.prompt).name)} | {r.score.total} | {_cell(ok)} | {_cell(', '.join(r.score.failure_tags))} | {_cell(judge)} |")
            md.append(f"- Diff: `{r.diff_path}`; Transcript: `{r.transcript_path}`")
    out = run_dir / "report.md"
    out.write_text("\n".join(md))
    return out
