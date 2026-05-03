import shutil
from prompt_eval.agents.codex_agent import run_codex

def test_codex_missing_graceful(tmp_path, monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda _: None)
    r = run_codex(tmp_path, "task", "prompt")
    assert not r.ok
    assert "not found" in r.stderr
