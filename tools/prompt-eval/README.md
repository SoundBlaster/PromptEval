# Prompt Eval

Small local harness to compare coding-agent prompts on EO-style tasks.

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

## Add an eval case
Create a case YAML under `evals/<suite>/cases/` and include it in `suite.yaml`.

## Scoring
Deterministic checks (commands, required/forbidden regex, diff scope) map into 5 categories totaling 100. Optional OpenAI judge can be layered on later.

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
