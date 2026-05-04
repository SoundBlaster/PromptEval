# Prompt Eval

Small local harness to compare coding-agent prompts on deterministic code-edit tasks.
The core runner is domain-agnostic; `elegant_objects` is the first included suite.

## Quick start
```bash
cd tools/prompt-eval
python -m venv .venv && source .venv/bin/activate
pip install -e . pytest
peval list
```

## Offline demo
```bash
peval run --suite elegant_objects --prompts prompts/elegant_objects/eo_lite.md --agent fixture-good
peval run --suite elegant_objects --prompts prompts/elegant_objects/eo_lite.md --agent fixture-bad
```
Good fixture should score higher than bad fixture. Reports are written to `runs/<id>/report.md`.
The included `elegant_objects` suite mixes a compact shop fixture with a larger subscription billing fixture that has nearby refund code as a scope-control distractor.
It also includes `procedural_helper.md` as an explicit negative-control prompt for Codex runs.

## Record evaluation results
Raw run artifacts under `runs/` are intentionally local and gitignored because they include full diffs and traces. Preserve important evaluation outcomes as compact records:
```bash
peval record --run runs/<id> --title "EO app skeleton holdout, Spark fast"
```

Or record automatically after a run:
```bash
peval run --suite elegant_objects --case-set eo_app_skeleton_holdout --prompts prompts/elegant_objects/baseline.md prompts/elegant_objects/eo_refactor.md --agent codex --record --record-title "EO app skeleton holdout"
```

Records are written to `records/<suite>/` as Markdown plus JSON. Each record includes prompt scores, per-case results, and a deterministic strengths/weaknesses analysis based on scores, failure tags, and judge summaries. Commit these summaries when the run result is part of prompt research; keep raw `runs/` artifacts local unless a diff or trace is needed for debugging a specific failure.

## Avoid prompt overfitting
Suites can tag cases into sets. The included `elegant_objects` suite uses:
- `tuning`: small known cases for fast prompt editing.
- `validation`: held-out realistic cases for checking whether the prompt generalizes.
- `generated`: generated EO cases promoted from draft fixtures.
- `eo_feature_lens`: ordinary feature work where EO should only guide planning and local review.
- `eo_refactoring`: explicit refactoring tasks where EO is the target transformation.
- `eo_app_skeleton`: larger greenfield application skeleton tasks where product behavior is specified but the internal object model is not.
- `eo_app_skeleton_tuning`: app-skeleton cases intended for prompt iteration.
- `eo_app_skeleton_holdout`: app-skeleton cases intended for final generalization checks, not manual prompt tuning.

Run only the prompt-authoring set while editing:
```bash
peval run --suite elegant_objects --case-set tuning --prompts prompts/elegant_objects/eo_lite.md --agent fixture-good
```

Then run without `--case-set`, or explicitly run `--case-set validation`, before accepting a prompt change. `peval compare` and `report.md` show set-level averages so a prompt that only improves known cases is visible.

The EO prompts are intentionally split by task mode:
- `eo_planner.md`: use EO only as a planning lens for feature work in existing code.
- `eo_refactor.md`: use EO as the target for explicit behavior-preserving refactoring.
- `eo_greenfield.md`: use EO as the design foundation for from-scratch tasks.

Avoid comparing these prompts only on the full mixed suite. Prefer mode-specific runs, for example:
```bash
peval run --suite elegant_objects --case-set eo_feature_lens --prompts prompts/elegant_objects/baseline.md prompts/elegant_objects/eo_planner.md --agent codex
peval run --suite elegant_objects --case-set eo_refactoring --prompts prompts/elegant_objects/baseline.md prompts/elegant_objects/eo_refactor.md --agent codex
peval run --suite elegant_objects --case-set eo_app_skeleton --prompts prompts/elegant_objects/baseline.md prompts/elegant_objects/eo_greenfield.md --agent codex
peval run --suite elegant_objects --case-set eo_app_skeleton_holdout --prompts prompts/elegant_objects/eo_refactor.md --agent codex
```

## Codex integration (optional)
```bash
peval run --suite elegant_objects --prompts prompts/elegant_objects/eo_lite.md --agent codex
```
If `codex` CLI is not installed, run is marked gracefully with a clear error.
Pass `--model <name>` to select a Codex model, for example `--model gpt-5.3-codex-spark`.
Model mode is not forced by default; Codex uses the selected model's own default reasoning effort.
Pass `--model-mode fast` to explicitly run Codex with `model_reasoning_effort="low"`, or `--model-mode medium` for `model_reasoning_effort="medium"`.
Pass `--codex-bin <path>` when multiple Codex binaries are installed and PATH would otherwise pick the wrong one.
Codex runs use `--ignore-user-config` plus an isolated temporary `CODEX_HOME` with copied auth, so evals do not inherit global MCP servers or optional runtime features.

## LLM-as-judge (optional)
Keep deterministic checks as the first line of defense: tests, syntax checks, required files, regex checks, and diff scope limits. Use the LLM judge only for semantic design judgments that are hard to encode deterministically, such as behavior ownership, naming dogmatism, DTO leakage, and over-broad refactoring.

```bash
peval run --suite elegant_objects --prompts prompts/elegant_objects/eo_lite.md --agent codex --judge subagent --judge-model gpt-5.3-codex-spark --judge-model-mode fast
```

The `subagent` judge runs a separate Codex CLI process against the task, diff, deterministic check summary, rubric, and case-specific judge criteria. Judge scores can only lower matching rubric categories; they do not increase deterministic scores.

## Add a prompt
Drop a new markdown file under `prompts/<suite>/` and pass it via `--prompts`.
Prompts can target any coding policy, architecture style, security rule, migration strategy, or review rubric.

## Add an eval case
Create a case YAML under `evals/<suite>/cases/` and include it in `suite.yaml`.
Each case points at a fixture, a task, deterministic checks, and a rubric.
Represent shell commands as argv lists, for example `["python", "-m", "pytest", "-q"]`.
Prefer adding new prompt-tuning cases under a `tuning` set and new held-out checks under `validation`.

## Generate a draft eval case
Use Codex to turn a text task description into a reviewable draft fixture:
```bash
peval generate-case "Add an invoice tax rule task where the good solution keeps tax behavior in domain objects and the bad solution uses a TaxHelper"
```

The generator writes `generated-cases/<case-id>/` with `before/`, `good/`, `bad/`, and `case.yaml`.
Review the draft before promoting it into `fixtures/<case-id>/` and `evals/<suite>/cases/<case-id>.yaml`.
Pass `--case-id`, `--description-file`, `--model`, `--model-mode fast`, `--model-mode medium`, or `--codex-bin` when needed.

## Add a suite
Create a new directory under `evals/<suite>/`, add a `suite.yaml`, and place matching prompts under `prompts/<suite>/`.
Suites are independent: one can evaluate Elegant Objects refactoring, another can evaluate secure coding, API migrations, performance fixes, or project-specific agent behavior.

## Scoring
Deterministic checks (commands, required/forbidden regex, diff scope) map into the categories declared by each case rubric.
Rubric categories are not hardcoded, so suites can define their own dimensions such as `security`, `portability`, `maintainability`, `api_compatibility`, or `eo_adherence`.
Optional LLM judging can be layered on for semantic checks and is recorded in `result.json` and `report.md`.

## Reports
Each run includes:
- `results.jsonl`
- `metadata.json`
- per-case `result.json`, `diff.patch`, `trace.jsonl`
- `report.md` prompt comparison and per-case table

## Limitations
- OpenAI judge currently stubbed; use `--judge subagent` for local Codex-based judging.
- Codex execution depends on local CLI availability.

## Next steps
- Add stronger rubric-to-check mapping per case.
- Extend failure taxonomy tagging.
- Add richer trace parsing for codex JSON events.
- Add generated train/validation suites for closed-loop prompt improvement.
