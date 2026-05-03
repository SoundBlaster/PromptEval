from __future__ import annotations
import argparse
from pathlib import Path
from .runner import run_suite


def main() -> None:
    parser = argparse.ArgumentParser(prog="peval")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    runp = sub.add_parser("run")
    runp.add_argument("--suite", required=True)
    runp.add_argument("--prompts", nargs="+", required=True)
    runp.add_argument("--agent", default="noop", choices=["fixture-good", "fixture-bad", "codex", "noop"])
    cmp = sub.add_parser("compare"); cmp.add_argument("--run", required=True)
    rep = sub.add_parser("report"); rep.add_argument("--run", required=True)
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
    else:
        run = Path(args.run)
        report = run / "report.md"
        print(report.read_text() if report.exists() else f"Missing {report}")

if __name__ == "__main__":
    main()
