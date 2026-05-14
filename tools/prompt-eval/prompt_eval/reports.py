from __future__ import annotations
import math
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


def _stdev(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    return math.sqrt(sum((v - mean) ** 2 for v in values) / (len(values) - 1))


def _fmt_mean_std(values: list[float], precision: int = 1) -> str:
    if not values:
        return "n/a"
    mean = sum(values) / len(values)
    if len(values) < 2:
        return f"{mean:.{precision}f}"
    return f"{mean:.{precision}f} ± {_stdev(values):.{precision}f}"


def _binary_eval_summary(result: CaseRunResult) -> str:
    if not result.judge or not result.judge.binary_evals:
        return ""
    failed = [item for item in result.judge.binary_evals if not item.passed]
    if not failed:
        return "all passed"
    return "; ".join(f"{item.id}: {item.evidence or 'failed'}" for item in failed)


def _max_run_index(results: list[CaseRunResult]) -> int:
    return max((r.run_index for r in results), default=0)


def write_report(run_dir: Path, suite: str, results: list[CaseRunResult]) -> Path:
    md = ["# Prompt Eval Report", "", f"Suite: {suite}", f"Run: {run_dir.name}", ""]
    multi_run = _max_run_index(results) > 0
    if multi_run:
        runs_total = _max_run_index(results) + 1
        md.append(f"Runs per cell: {runs_total}")
        md.append("")
    category_keys = _category_keys(results)
    case_set_keys = _case_set_keys(results)
    grouped = defaultdict(list)
    for r in results:
        grouped[r.prompt].append(r)
    headers = [
        "Prompt",
        "Cases",
        "Avg score",
        *[f"{_label(k)} avg" for k in case_set_keys],
        *[_label(k) for k in category_keys],
    ]
    md.append("| " + " | ".join(headers) + " |")
    md.append("|" + "|".join(["---", "---:", "---:", *(["---:"] * (len(case_set_keys) + len(category_keys)))]) + "|")

    def fmt(values: list[float]) -> str:
        if not values:
            return "n/a"
        if multi_run:
            return _fmt_mean_std(values)
        mean = sum(values) / len(values)
        return f"{mean:.1f}"

    for p, rs in grouped.items():
        # Group by case_id to compute per-cell means before averaging across prompts.
        per_case: dict[str, list[CaseRunResult]] = defaultdict(list)
        for r in rs:
            per_case[r.case_id].append(r)
        cells = len(per_case)
        all_scores = [x.score.total for x in rs]

        def set_scores_all(key: str) -> list[float]:
            # Per-run scores for cases tagged with `key`.
            return [x.score.total for x in rs if key in x.case_sets]

        def category_values(key: str) -> list[float]:
            return [x.score.categories.get(key, 0) for x in rs]

        row = [Path(p).name, str(cells), fmt(all_scores)]
        for key in case_set_keys:
            row.append(fmt(set_scores_all(key)))
        row += [fmt(category_values(k)) for k in category_keys]
        md.append("| " + " | ".join(row) + " |")
    by_case = defaultdict(list)
    for r in results:
        by_case[r.case_id].append(r)
    for case, rs in by_case.items():
        case_sets = ", ".join(rs[0].case_sets) if rs and rs[0].case_sets else "uncategorized"
        md += [
            "",
            f"## {case}",
            "",
            f"Case set: `{case_sets}`",
            "",
        ]
        if multi_run:
            md += [
                "| Prompt | Score (mean ± std) | Pass rate | Failure tags | Latest judge | Latest evals |",
                "|---|---:|---:|---|---|---|",
            ]
            per_prompt: dict[str, list[CaseRunResult]] = defaultdict(list)
            for r in rs:
                per_prompt[r.prompt].append(r)
            for prompt_path, prompt_rs in per_prompt.items():
                prompt_rs_sorted = sorted(prompt_rs, key=lambda r: r.run_index)
                scores = [r.score.total for r in prompt_rs_sorted]
                passed = sum(1 for r in prompt_rs_sorted if all(c.passed for c in r.checks))
                pass_rate = f"{passed}/{len(prompt_rs_sorted)}"
                failure_tags = sorted({tag for r in prompt_rs_sorted for tag in r.score.failure_tags})
                latest = prompt_rs_sorted[-1]
                judge_summary = latest.judge.summary if latest.judge else ""
                md.append(
                    f"| {_cell(Path(prompt_path).name)} | {_fmt_mean_std(scores)} | {pass_rate} | "
                    f"{_cell(', '.join(failure_tags))} | {_cell(judge_summary)} | "
                    f"{_cell(_binary_eval_summary(latest))} |"
                )
                for r in prompt_rs_sorted:
                    md.append(
                        f"  - run {r.run_index}: score {r.score.total}; "
                        f"diff `{r.diff_path}`; trace `{r.transcript_path}`"
                    )
        else:
            md += [
                "| Prompt | Score | Result | Failure tags | Judge | Judge evals |",
                "|---|---:|---|---|---|---|",
            ]
            for r in rs:
                ok = "pass" if all(c.passed for c in r.checks) else "fail"
                judge = r.judge.summary if r.judge else ""
                md.append(
                    f"| {_cell(Path(r.prompt).name)} | {r.score.total} | {_cell(ok)} | "
                    f"{_cell(', '.join(r.score.failure_tags))} | {_cell(judge)} | "
                    f"{_cell(_binary_eval_summary(r))} |"
                )
                md.append(f"- Diff: `{r.diff_path}`; Transcript: `{r.transcript_path}`")
    out = run_dir / "report.md"
    out.write_text("\n".join(md))
    return out
