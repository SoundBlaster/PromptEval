from __future__ import annotations
from pathlib import Path
import json, datetime, shutil, uuid
from .config import load_suite
from .sandbox import prepare_sandbox
from .checks import git_diff, run_checks
from .scoring import score_from_checks
from .models import CaseRunResult
from .agents.fixture_agent import apply_fixture_solution
from .agents.mock_agent import run_mock
from .agents.codex_agent import run_codex
from .judges.base import JudgeResult
from .judges.mock_judge import judge_mock
from .judges.subagent_judge import judge_subagent
from .reports import write_report


def _check_summary(checks) -> str:
    return "; ".join(f"{'pass' if check.passed else 'fail'} {check.name}: {check.detail}" for check in checks)


def _run_judge(
    judge: str,
    case,
    prompt_text: str,
    diff: str,
    checks,
    model: str | None,
    model_mode: str | None,
    codex_bin: str | None,
) -> JudgeResult | None:
    if judge == "none":
        return None
    if judge == "mock":
        return judge_mock()
    if judge == "subagent":
        return judge_subagent(case, prompt_text, diff, _check_summary(checks), model, model_mode, codex_bin)
    raise ValueError(f"Unsupported judge: {judge}")


def run_suite(
    root: Path,
    suite: str,
    prompts: list[Path],
    agent: str,
    model: str | None = None,
    model_mode: str | None = None,
    codex_bin: str | None = None,
    case_sets: list[str] | None = None,
    judge: str = "none",
    judge_model: str | None = None,
    judge_model_mode: str | None = None,
    judge_codex_bin: str | None = None,
) -> Path:
    run_id = f"{datetime.datetime.utcnow().strftime('%Y%m%d-%H%M%S-%f')}-{uuid.uuid4().hex[:8]}"
    run_dir = root / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    cases = load_suite(root, suite, case_sets)
    results = []
    for p in prompts:
        ptxt = p.read_text()
        for case in cases:
            fixture_root = root / "fixtures" / case.fixture
            sandbox = prepare_sandbox(fixture_root / "before")
            try:
                if agent == "fixture-good":
                    ar = apply_fixture_solution(sandbox, fixture_root, "good")
                elif agent == "fixture-bad":
                    ar = apply_fixture_solution(sandbox, fixture_root, "bad")
                elif agent == "codex":
                    ar = run_codex(sandbox, case.task, ptxt, model, model_mode, codex_bin)
                else:
                    ar = run_mock(case.task)
                diff = git_diff(sandbox)
                checks = run_checks(case, sandbox, diff)
                judge_result = _run_judge(judge, case, ptxt, diff, checks, judge_model, judge_model_mode, judge_codex_bin or codex_bin)
                score = score_from_checks(checks, case.rubric, judge_result)
                case_dir = run_dir / Path(p).stem / case.id
                case_dir.mkdir(parents=True, exist_ok=True)
                (case_dir / "diff.patch").write_text(diff)
                (case_dir / "trace.jsonl").write_text("\n".join(json.dumps(x) for x in (ar.trace or [])))
                res = CaseRunResult(suite=suite, prompt=str(p), case_id=case.id, score=score, checks=checks,
                                    diff_path=str(case_dir / "diff.patch"), transcript_path=str(case_dir / "trace.jsonl"),
                                    case_sets=case.sets, judge=judge_result, stdout=ar.stdout, stderr=ar.stderr)
                (case_dir / "result.json").write_text(json.dumps(res.to_json(), indent=2))
                results.append(res)
            finally:
                shutil.rmtree(sandbox, ignore_errors=True)
    (run_dir / "results.jsonl").write_text("\n".join(json.dumps(r.to_json()) for r in results))
    write_report(run_dir, suite, results)
    return run_dir
