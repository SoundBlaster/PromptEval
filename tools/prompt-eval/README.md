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

## Codex integration (optional)
```bash
peval run --suite elegant_objects --prompts prompts/elegant_objects/eo_lite.md --agent codex
```
If `codex` CLI is not installed, run is marked gracefully with a clear error.

## Add a prompt
Drop a new markdown file under `prompts/<suite>/` and pass it via `--prompts`.
Prompts can target any coding policy, architecture style, security rule, migration strategy, or review rubric.

## Add an eval case
Create a case YAML under `evals/<suite>/cases/` and include it in `suite.yaml`.
Each case points at a fixture, a task, deterministic checks, and a rubric.
Represent shell commands as argv lists, for example `["python", "-m", "pytest", "-q"]`.

## Add a suite
Create a new directory under `evals/<suite>/`, add a `suite.yaml`, and place matching prompts under `prompts/<suite>/`.
Suites are independent: one can evaluate Elegant Objects refactoring, another can evaluate secure coding, API migrations, performance fixes, or project-specific agent behavior.

## Scoring
Deterministic checks (commands, required/forbidden regex, diff scope) map into the categories declared by each case rubric.
Rubric categories are not hardcoded, so suites can define their own dimensions such as `security`, `portability`, `maintainability`, `api_compatibility`, or `eo_adherence`.
Optional LLM judging can be layered on later.

## Reports
Each run includes:
- `results.jsonl`
- per-case `result.json`, `diff.patch`, `trace.jsonl`
- `report.md` prompt comparison and per-case table

## Limitations
- OpenAI judge currently stubbed.
- Codex execution depends on local CLI availability.

## Next steps
- Add stronger rubric-to-check mapping per case.
- Extend failure taxonomy tagging.
- Add richer trace parsing for codex JSON events.
