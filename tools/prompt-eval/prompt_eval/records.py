from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any
import json


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
        item = {
            "prompt": prompt,
            "cases": len(scores),
            "average": round(sum(scores) / len(scores), 1),
            "sets": {},
        }
        for key in set_keys:
            set_scores = [row["score"]["total"] for row in prompt_rows if key in row.get("case_sets", [])]
            if set_scores:
                item["sets"][key] = round(sum(set_scores) / len(set_scores), 1)
        summary.append(item)
    return sorted(summary, key=lambda item: item["average"], reverse=True)


def _case_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "case_id": row["case_id"],
            "prompt": _prompt_name(row["prompt"]),
            "score": row["score"]["total"],
            "case_sets": row.get("case_sets", []),
            "failure_tags": row["score"].get("failure_tags", []),
            "judge": (row.get("judge") or {}).get("summary", ""),
        }
        for row in rows
    ]


def _record_payload(run: Path, title: str | None = None) -> dict[str, Any]:
    rows = _rows(run)
    if not rows:
        raise ValueError(f"Run has no results: {run}")
    metadata = _metadata(run)
    return {
        "run_id": run.name,
        "title": title or metadata.get("title") or run.name,
        "suite": metadata.get("suite") or rows[0]["suite"],
        "metadata": metadata,
        "prompts": _prompt_summary(rows),
        "cases": _case_summary(rows),
    }


def _markdown(record: dict[str, Any]) -> str:
    lines = [
        f"# {record['title']}",
        "",
        f"Suite: `{record['suite']}`",
        f"Run: `{record['run_id']}`",
        "",
    ]
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
        row = [prompt["prompt"], str(prompt["cases"]), f"{prompt['average']:.1f}"]
        row.extend(f"{prompt['sets'].get(key, 'n/a')}" for key in set_keys)
        lines.append("| " + " | ".join(row) + " |")
    lines += ["", "## Case Results", "", "| Case | Prompt | Score | Failure tags | Judge |", "|---|---|---:|---|---|"]
    for case in record["cases"]:
        tags = ", ".join(case["failure_tags"])
        judge = str(case["judge"]).replace("\n", "<br>").replace("|", "\\|")
        lines.append(f"| {case['case_id']} | {case['prompt']} | {case['score']} | {tags} | {judge} |")
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
