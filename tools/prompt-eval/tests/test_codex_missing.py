import shutil
import subprocess
from prompt_eval.agents.codex_agent import run_codex

def test_codex_missing_graceful(tmp_path, monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda _: None)
    r = run_codex(tmp_path, "task", "prompt")
    assert not r.ok
    assert "not found" in r.stderr

def test_codex_model_flag(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(shutil, "which", lambda _: "/usr/bin/codex")

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    r = run_codex(tmp_path, "task", "prompt", model="gpt-5.3-codex-spark")
    assert r.ok
    assert calls[0] == ["codex", "exec", "--json", "--full-auto", "--model", "gpt-5.3-codex-spark", "task"]
