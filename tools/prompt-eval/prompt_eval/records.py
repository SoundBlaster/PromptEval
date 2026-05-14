from __future__ import annotations

import math
from collections import defaultdict
from collections import Counter
from pathlib import Path
from typing import Any
import json


def _stdev(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    return math.sqrt(sum((v - mean) ** 2 for v in values) / (len(values) - 1))


def _runs_per_cell(rows: list[dict[str, Any]]) -> int:
    return max((int(row.get("run_index", 0)) for row in rows), default=0) + 1


def _rows(run: Path) -> list[dict[str, Any]]:
    results = run / "results.jsonl"
    if not results.exists():
        raise FileNotFoundError(f"Missing {results}")
    return [json.loads(line) for line in results.read_text().splitlines() if line.strip()]


def _metadata(run: Path) -> dict[str, Any]:
    path = run / "metadata.json"
    return json.loads(path.read_text()) if path.exists() else {}


def _prompt_name(prompt: str) -> str:
    return Path(prompt).name


def _label(key: str) -> str:
    if key.startswith("eo_"):
        return "EO " + key[3:].replace("_", " ").title()
    return key.replace("_", " ").title()


def _set_keys(rows: list[dict[str, Any]]) -> list[str]:
    keys = []
    seen = set()
    for row in rows:
        for case_set in row.get("case_sets", []):
            if case_set not in seen:
                seen.add(case_set)
                keys.append(case_set)
    return keys


def _prompt_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    set_keys = _set_keys(rows)
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[_prompt_name(row["prompt"])].append(row)
    summary = []
    for prompt, prompt_rows in sorted(grouped.items()):
        scores = [row["score"]["total"] for row in prompt_rows]
        distinct_cases = {row["case_id"] for row in prompt_rows}
        item = {
            "prompt": prompt,
            "cases": len(distinct_cases),
            "results": len(prompt_rows),
            "average": round(sum(scores) / len(scores), 1),
            "std": round(_stdev(scores), 2),
            "sets": {},
        }
        for key in set_keys:
            set_scores = [row["score"]["total"] for row in prompt_rows if key in row.get("case_sets", [])]
            if set_scores:
                item["sets"][key] = round(sum(set_scores) / len(set_scores), 1)
        summary.append(item)
    return sorted(summary, key=lambda item: item["average"], reverse=True)


def _case_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(row["case_id"], _prompt_name(row["prompt"]))].append(row)
    out = []
    for (case_id, prompt), prompt_rows in grouped.items():
        prompt_rows = sorted(prompt_rows, key=lambda r: r.get("run_index", 0))
        scores = [r["score"]["total"] for r in prompt_rows]
        tags: list[str] = sorted({tag for r in prompt_rows for tag in r["score"].get("failure_tags", [])})
        latest = prompt_rows[-1]
        out.append(
            {
                "case_id": case_id,
                "prompt": prompt,
                "runs": len(prompt_rows),
                "score": round(sum(scores) / len(scores), 1),
                "score_std": round(_stdev(scores), 2),
                "score_min": min(scores),
                "score_max": max(scores),
                "case_sets": prompt_rows[0].get("case_sets", []),
                "failure_tags": tags,
                "judge": (latest.get("judge") or {}).get("summary", ""),
                "judge_binary_evals": (latest.get("judge") or {}).get("binary_evals", []),
            }
        )
    return out


def _shared_case_wins(prompt: str, rows: list[dict[str, Any]]) -> tuple[int, int]:
    by_case: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_case[row["case_id"]].append(row)
    wins = 0
    total = 0
    for case_rows in by_case.values():
        if len(case_rows) < 2:
            continue
        total += 1
        best = max(row["score"]["total"] for row in case_rows)
        if any(_prompt_name(row["prompt"]) == prompt and row["score"]["total"] == best for row in case_rows):
            wins += 1
    return wins, total


def _failure_tags(rows: list[dict[str, Any]]) -> Counter:
    tags = Counter()
    for row in rows:
        tags.update(row["score"].get("failure_tags", []))
    return tags


def _binary_eval_failures(rows: list[dict[str, Any]]) -> Counter:
    failures = Counter()
    for row in rows:
        for item in (row.get("judge") or {}).get("binary_evals", []):
            if not item.get("passed", True):
                failures[str(item.get("id", "unknown_eval"))] += 1
    return failures


def _prompt_analysis(rows: list[dict[str, Any]], summaries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[_prompt_name(row["prompt"])].append(row)
    best_average = max(summary["average"] for summary in summaries)
    analysis = []
    for summary in summaries:
        prompt = summary["prompt"]
        prompt_rows = grouped[prompt]
        strengths = []
        weaknesses = []
        high_cases = [row["case_id"] for row in prompt_rows if row["score"]["total"] >= 90]
        low_cases = [f"{row['case_id']} ({row['score']['total']})" for row in prompt_rows if row["score"]["total"] < 85]
        tags = _failure_tags(prompt_rows)
        failed_evals = _binary_eval_failures(prompt_rows)
        wins, shared = _shared_case_wins(prompt, rows)

        if summary["average"] == best_average and len(summaries) > 1:
            strengths.append("Top average score in this run.")
        if shared:
            strengths.append(f"Best or tied score on {wins}/{shared} shared cases.")
        if high_cases:
            strengths.append(f"Strong cases (>=90): {', '.join(high_cases[:5])}.")
        if not tags:
            strengths.append("No failure tags recorded.")
        if not failed_evals:
            strengths.append("No judge binary eval failures recorded.")

        if low_cases:
            weaknesses.append(f"Weak cases (<85): {', '.join(low_cases[:5])}.")
        if tags:
            common = ", ".join(f"{tag} x{count}" for tag, count in tags.most_common(5))
            weaknesses.append(f"Failure tags: {common}.")
        if failed_evals:
            common = ", ".join(f"{tag} x{count}" for tag, count in failed_evals.most_common(5))
            weaknesses.append(f"Judge binary eval failures: {common}.")
        if not weaknesses:
            weaknesses.append("No clear weaknesses surfaced by scores or failure tags.")

        analysis.append(
            {
                "prompt": prompt,
                "strengths": strengths,
                "weaknesses": weaknesses,
            }
        )
    return analysis


def _record_payload(run: Path, title: str | None = None) -> dict[str, Any]:
    rows = _rows(run)
    if not rows:
        raise ValueError(f"Run has no results: {run}")
    metadata = _metadata(run)
    prompts = _prompt_summary(rows)
    return {
        "run_id": run.name,
        "title": title or metadata.get("title") or run.name,
        "suite": metadata.get("suite") or rows[0]["suite"],
        "runs": _runs_per_cell(rows),
        "metadata": metadata,
        "prompts": prompts,
        "analysis": _prompt_analysis(rows, prompts),
        "cases": _case_summary(rows),
    }


def _markdown(record: dict[str, Any]) -> str:
    multi_run = record.get("runs", 1) > 1
    lines = [
        f"# {record['title']}",
        "",
        f"Suite: `{record['suite']}`",
        f"Run: `{record['run_id']}`",
    ]
    if multi_run:
        lines.append(f"Runs per cell: `{record['runs']}`")
    lines.append("")
    metadata = record.get("metadata", {})
    if metadata:
        fields = ["agent", "model", "model_mode", "case_sets", "judge", "judge_model", "judge_model_mode"]
        details = [f"- `{field}`: `{metadata[field]}`" for field in fields if metadata.get(field)]
        if details:
            lines += ["## Run Metadata", "", *details, ""]
    set_keys = []
    for prompt in record["prompts"]:
        for key in prompt["sets"]:
            if key not in set_keys:
                set_keys.append(key)
    headers = ["Prompt", "Cases", "Avg score", *[_label(key) for key in set_keys]]
    lines.append("## Prompt Summary")
    lines.append("")
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("|" + "|".join(["---", "---:", "---:", *(["---:"] * len(set_keys))]) + "|")
    for prompt in record["prompts"]:
        avg_cell = f"{prompt['average']:.1f}"
        if multi_run and prompt.get("std", 0):
            avg_cell = f"{prompt['average']:.1f} ± {prompt['std']:.1f}"
        row = [prompt["prompt"], str(prompt["cases"]), avg_cell]
        row.extend(f"{prompt['sets'].get(key, 'n/a')}" for key in set_keys)
        lines.append("| " + " | ".join(row) + " |")
    lines += ["", "## Strengths And Weaknesses", "", "| Prompt | Strengths | Weaknesses |", "|---|---|---|"]
    for item in record.get("analysis", []):
        strengths = "<br>".join(item["strengths"]).replace("|", "\\|")
        weaknesses = "<br>".join(item["weaknesses"]).replace("|", "\\|")
        lines.append(f"| {item['prompt']} | {strengths} | {weaknesses} |")
    if multi_run:
        lines += [
            "",
            "## Case Results",
            "",
            "| Case | Prompt | Score (mean ± std) | Min/Max | Runs | Failure tags | Latest judge | Latest evals |",
            "|---|---|---:|---:|---:|---|---|---|",
        ]
    else:
        lines += [
            "",
            "## Case Results",
            "",
            "| Case | Prompt | Score | Failure tags | Judge | Judge evals |",
            "|---|---|---:|---|---|---|",
        ]
    for case in record["cases"]:
        tags = ", ".join(case["failure_tags"])
        judge = str(case["judge"]).replace("\n", "<br>").replace("|", "\\|")
        binary_evals = case.get("judge_binary_evals") or []
        if binary_evals:
            failed = [item for item in binary_evals if not item.get("passed", True)]
            if not failed:
                evals = "all passed"
            else:
                evals = "; ".join(
                    f"{item.get('id', 'unknown')}: {str(item.get('evidence', 'failed'))}" for item in failed
                ).replace("|", "\\|")
        else:
            evals = ""
        if multi_run:
            score_cell = f"{case['score']:.1f}"
            std = case.get("score_std", 0)
            if std:
                score_cell = f"{case['score']:.1f} ± {std:.1f}"
            min_max = f"{case.get('score_min', case['score'])}/{case.get('score_max', case['score'])}"
            lines.append(
                f"| {case['case_id']} | {case['prompt']} | {score_cell} | {min_max} | "
                f"{case.get('runs', 1)} | {tags} | {judge} | {evals} |"
            )
        else:
            lines.append(f"| {case['case_id']} | {case['prompt']} | {case['score']} | {tags} | {judge} | {evals} |")
    lines.append("")
    return "\n".join(lines)


def _update_index(index: Path, record: dict[str, Any], md_path: Path) -> None:
    prompts = ", ".join(prompt["prompt"] for prompt in record["prompts"])
    scores = ", ".join(f"{prompt['prompt']}={prompt['average']:.1f}" for prompt in record["prompts"])
    line = f"| [{record['run_id']}]({md_path.name}) | {record['title']} | {prompts} | {scores} |"
    if index.exists():
        lines = index.read_text().splitlines()
    else:
        lines = [
            "# Prompt Eval Records",
            "",
            "| Run | Title | Prompts | Scores |",
            "|---|---|---|---|",
        ]
    if not any(f"[{record['run_id']}]" in existing for existing in lines):
        lines.append(line)
    index.write_text("\n".join(lines) + "\n")


def record_run(root: Path, run: Path, title: str | None = None, output_root: Path | None = None) -> Path:
    record = _record_payload(run, title)
    records_root = output_root or (root / "records")
    suite_dir = records_root / record["suite"]
    suite_dir.mkdir(parents=True, exist_ok=True)
    json_path = suite_dir / f"{record['run_id']}.json"
    md_path = suite_dir / f"{record['run_id']}.md"
    json_path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    md_path.write_text(_markdown(record))
    _update_index(suite_dir / "INDEX.md", record, md_path)
    return md_path
