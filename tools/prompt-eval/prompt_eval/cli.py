from __future__ import annotations
import argparse
import json
from pathlib import Path
from collections import defaultdict
from .runner import run_suite


def print_report(run: Path) -> None:
    report = run / "report.md"
    print(report.read_text() if report.exists() else f"Missing {report}")


def compare_run(run: Path) -> None:
    results = run / "results.jsonl"
    if not results.exists():
        print(f"Missing {results}")
        return
    grouped = defaultdict(list)
    for line in results.read_text().splitlines():
        if line.strip():
            row = json.loads(line)
            grouped[row["prompt"]].append(row["score"]["total"])
    print("| Prompt | Cases | Avg score |")
    print("|---|---:|---:|")
    for prompt, scores in sorted(grouped.items(), key=lambda item: sum(item[1]) / len(item[1]), reverse=True):
        print(f"| {Path(prompt).name} | {len(scores)} | {sum(scores) / len(scores):.1f} |")


def main() -> None:
    parser = argparse.ArgumentParser(prog="peval")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    runp = sub.add_parser("run")
    runp.add_argument("--suite", required=True)
    runp.add_argument("--prompts", nargs="+", required=True)
    runp.add_argument("--agent", default="noop", choices=["fixture-good", "fixture-bad", "codex", "noop"])
    cmp = sub.add_parser("compare", help="print prompt average scores for a completed run"); cmp.add_argument("--run", required=True)
    rep = sub.add_parser("report", help="print report.md for a completed run"); rep.add_argument("--run", required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    if args.cmd == "list":
        print("Suites:")
        for s in (root / "evals").iterdir():
            if s.is_dir(): print(f"- {s.name}")
        print("Prompts:")
        for p in (root / "prompts").rglob("*.md"): print(f"- {p.relative_to(root)}")
    elif args.cmd == "run":
        run_dir = run_suite(root, args.suite, [root / p for p in args.prompts], args.agent)
        print(run_dir)
    elif args.cmd == "compare":
        compare_run(Path(args.run))
    else:
        print_report(Path(args.run))

if __name__ == "__main__":
    main()
