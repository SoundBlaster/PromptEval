from pathlib import Path
from prompt_eval.agents.codex_agent import run_codex

def test_codex_missing_graceful(tmp_path):
    r = run_codex(tmp_path, "task", "prompt")
    if not r.ok:
        assert "not found" in r.stderr
