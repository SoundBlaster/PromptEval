from __future__ import annotations
from pathlib import Path
import json
import datetime
import shutil
import uuid
from .config import load_suite
from .sandbox import prepare_sandbox
from .checks import command_name, git_diff, run_checks
from .scoring import score_from_checks
from .models import CaseRunResult
from .agents.fixture_agent import apply_fixture_solution
from .agents.mock_agent import run_mock
from .agents.codex_agent import run_codex
from .agents.openai_agent import run_openai
from .judges.base import JudgeResult
from .judges.mock_judge import judge_mock
from .judges.subagent_judge import judge_subagent
from .reports import write_report


def _check_summary(checks) -> str:
    return "; ".join(f"{'pass' if check.passed else 'fail'} {check.name}: {check.detail}" for check in checks)


def _acceptance_contract(case) -> str:
    lines = ["Acceptance criteria visible to the coding agent:", "", "Deterministic checks:"]
    if case.checks.commands:
        lines.extend(f"- Run `{command_name(cmd)}`" for cmd in case.checks.commands)
    if case.checks.required_files:
        lines.extend(f"- Required file: `{path}`" for path in case.checks.required_files)
    for check in case.checks.required_regex:
        paths = f" paths={','.join(check.paths)}" if check.paths else ""
        reason = f" reason={check.reason}" if check.reason else ""
        lines.append(f"- Required pattern `{check.pattern}` target={check.target}{paths}{reason}")
    for check in case.checks.forbidden_regex:
        paths = f" paths={','.join(check.paths)}" if check.paths else ""
        reason = f" reason={check.reason}" if check.reason else ""
        lines.append(f"- Forbidden pattern `{check.pattern}` target={check.target}{paths}{reason}")
    if case.checks.max_changed_files is not None:
        lines.append(f"- Change at most {case.checks.max_changed_files} files")
    if len(lines) == 3:
        lines.append("- No deterministic checks declared")

    if case.rubric:
        lines += ["", "Rubric categories:"]
        lines.extend(f"- {key}: {value}" for key, value in case.rubric.items())

    if case.judge and case.judge.criteria:
        lines += ["", "Semantic review criteria:"]
        lines.extend(f"- {item}" for item in case.judge.criteria)

    if case.judge and case.judge.binary_evals:
        lines += ["", "Binary semantic acceptance checks:"]
        for item in case.judge.binary_evals:
            category = f" category={item.category}" if item.category else ""
            lines.append(f"- {item.id}{category}: {item.question}")
            if item.pass_condition:
                lines.append(f"  Pass: {item.pass_condition}")
            if item.fail_condition:
                lines.append(f"  Fail: {item.fail_condition}")

    lines += ["", "Before finishing, run the narrowest relevant checks available in this workspace."]
    return "\n".join(lines)


def _agent_task(case) -> str:
    return f"{case.task.rstrip()}\n\n{_acceptance_contract(case)}\n"


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
    api_base: str | None = None,
    api_key: str | None = None,
    max_tokens: int | None = None,
    request_timeout: int | None = None,
) -> Path:
    run_id = f"{datetime.datetime.utcnow().strftime('%Y%m%d-%H%M%S-%f')}-{uuid.uuid4().hex[:8]}"
    run_dir = root / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    cases = load_suite(root, suite, case_sets)
    metadata = {
        "run_id": run_id,
        "suite": suite,
        "prompts": [str(path) for path in prompts],
        "agent": agent,
        "model": model,
        "model_mode": model_mode,
        "codex_bin": codex_bin,
        "case_sets": case_sets or [],
        "judge": judge,
        "judge_model": judge_model,
        "judge_model_mode": judge_model_mode,
        "judge_codex_bin": judge_codex_bin,
    }
    (run_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))
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
                    ar = run_codex(sandbox, _agent_task(case), ptxt, model, model_mode, codex_bin)
                elif agent == "openai":
                    ar = run_openai(
                        sandbox,
                        _agent_task(case),
                        ptxt,
                        model,
                        api_base,
                        api_key,
                        max_tokens,
                        timeout=request_timeout,
                    )
                else:
                    ar = run_mock(case.task)
                diff = git_diff(sandbox)
                checks = run_checks(case, sandbox, diff)
                judge_result = _run_judge(
                    judge, case, ptxt, diff, checks, judge_model, judge_model_mode, judge_codex_bin or codex_bin
                )
                score = score_from_checks(checks, case.rubric, judge_result)
                case_dir = run_dir / Path(p).stem / case.id
                case_dir.mkdir(parents=True, exist_ok=True)
                (case_dir / "diff.patch").write_text(diff)
                (case_dir / "trace.jsonl").write_text("\n".join(json.dumps(x) for x in (ar.trace or [])))
                res = CaseRunResult(
                    suite=suite,
                    prompt=str(p),
                    case_id=case.id,
                    score=score,
                    checks=checks,
                    diff_path=str(case_dir / "diff.patch"),
                    transcript_path=str(case_dir / "trace.jsonl"),
                    case_sets=case.sets,
                    judge=judge_result,
                    stdout=ar.stdout,
                    stderr=ar.stderr,
                )
                (case_dir / "result.json").write_text(json.dumps(res.to_json(), indent=2))
                results.append(res)
            finally:
                shutil.rmtree(sandbox, ignore_errors=True)
    (run_dir / "results.jsonl").write_text("\n".join(json.dumps(r.to_json()) for r in results))
    write_report(run_dir, suite, results)
    return run_dir
