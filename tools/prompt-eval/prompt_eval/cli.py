from __future__ import annotations
import argparse
import json
from pathlib import Path
from collections import defaultdict
from .config import suite_case_sets
from .runner import run_suite


def print_report(run: Path) -> None:
    report = run / "report.md"
    print(report.read_text() if report.exists() else f"Missing {report}")


def _label(key: str) -> str:
    return key.replace("_", " ").title()


def compare_run(run: Path) -> None:
    results = run / "results.jsonl"
    if not results.exists():
        print(f"Missing {results}")
        return
    grouped = defaultdict(list)
    set_keys = []
    seen_sets = set()
    for line in results.read_text().splitlines():
        if line.strip():
            row = json.loads(line)
            grouped[row["prompt"]].append(row)
            for case_set in row.get("case_sets", []):
                if case_set not in seen_sets:
                    seen_sets.add(case_set)
                    set_keys.append(case_set)
    headers = ["Prompt", "Cases", "Avg score", *[_label(k) for k in set_keys]]
    print("| " + " | ".join(headers) + " |")
    print("|" + "|".join(["---", "---:", "---:", *(["---:"] * len(set_keys))]) + "|")
    ranked = sorted(grouped.items(), key=lambda item: sum(r["score"]["total"] for r in item[1]) / len(item[1]), reverse=True)
    for prompt, rows in ranked:
        scores = [r["score"]["total"] for r in rows]
        out = [Path(prompt).name, str(len(scores)), f"{sum(scores) / len(scores):.1f}"]
        for key in set_keys:
            set_scores = [r["score"]["total"] for r in rows if key in r.get("case_sets", [])]
            out.append(f"{sum(set_scores) / len(set_scores):.1f}" if set_scores else "n/a")
        print("| " + " | ".join(out) + " |")


def main() -> None:
    parser = argparse.ArgumentParser(prog="peval")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    runp = sub.add_parser("run")
    runp.add_argument("--suite", required=True)
    runp.add_argument("--prompts", nargs="+", required=True)
    runp.add_argument("--agent", default="noop", choices=["fixture-good", "fixture-bad", "codex", "noop"])
    runp.add_argument("--model", help="model name for agents that support model selection")
    runp.add_argument("--model-mode", choices=["fast"], help="model execution mode for agents that support it")
    runp.add_argument("--codex-bin", help="path or command name for the Codex CLI binary")
    runp.add_argument("--case-set", action="append", help="run only cases tagged with this set; repeat to include multiple sets")
    runp.add_argument("--judge", default="none", choices=["none", "mock", "subagent"], help="optional LLM-as-judge layer")
    runp.add_argument("--judge-model", help="model name for the LLM judge")
    runp.add_argument("--judge-model-mode", choices=["fast"], help="model execution mode for the LLM judge")
    runp.add_argument("--judge-codex-bin", help="path or command name for the Codex CLI used by the LLM judge")
    cmp = sub.add_parser("compare", help="print prompt average scores for a completed run"); cmp.add_argument("--run", required=True)
    rep = sub.add_parser("report", help="print report.md for a completed run"); rep.add_argument("--run", required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    if args.cmd == "list":
        print("Suites:")
        for s in (root / "evals").iterdir():
            if s.is_dir():
                sets = suite_case_sets(root, s.name)
                suffix = f" ({', '.join(sets)})" if sets else ""
                print(f"- {s.name}{suffix}")
        print("Prompts:")
        for p in (root / "prompts").rglob("*.md"): print(f"- {p.relative_to(root)}")
    elif args.cmd == "run":
        run_dir = run_suite(
            root,
            args.suite,
            [root / p for p in args.prompts],
            args.agent,
            args.model,
            args.model_mode,
            args.codex_bin,
            args.case_set,
            args.judge,
            args.judge_model,
            args.judge_model_mode,
            args.judge_codex_bin,
        )
        print(run_dir)
    elif args.cmd == "compare":
        compare_run(Path(args.run))
    else:
        print_report(Path(args.run))

if __name__ == "__main__":
    main()
