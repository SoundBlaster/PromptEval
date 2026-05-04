from pathlib import Path
import shutil
import subprocess
import tempfile
from prompt_eval.agents.codex_agent import run_codex

def test_codex_missing_graceful(tmp_path, monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda _: None)
    r = run_codex(tmp_path, "task", "prompt")
    assert not r.ok
    assert "not found" in r.stderr

def test_codex_missing_reports_selected_binary(tmp_path, monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda _: None)
    r = run_codex(tmp_path, "task", "prompt", codex_bin="/missing/codex")
    assert not r.ok
    assert "--codex-bin '/missing/codex'" in r.stderr

def test_codex_missing_reports_env_binary(tmp_path, monkeypatch):
    monkeypatch.setenv("PEVAL_CODEX_BIN", "/missing/env-codex")
    monkeypatch.setattr(shutil, "which", lambda _: None)
    r = run_codex(tmp_path, "task", "prompt")
    assert not r.ok
    assert "PEVAL_CODEX_BIN='/missing/env-codex'" in r.stderr

def test_codex_unsupported_model_mode_graceful(tmp_path, monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda _: "/usr/bin/codex")
    r = run_codex(tmp_path, "task", "prompt", model_mode="turbo")
    assert not r.ok
    assert "unsupported model mode 'turbo'" in r.stderr
    assert "fast" in r.stderr
    assert "medium" in r.stderr
    assert "xhigh" in r.stderr

def test_codex_model_flag(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(shutil, "which", lambda _: "/usr/bin/codex")

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    r = run_codex(tmp_path, "task", "prompt", model="gpt-5.3-codex-spark")
    assert r.ok
    assert calls[0] == [
        "codex",
        "exec",
        "--ignore-user-config",
        "--json",
        "--full-auto",
        "--model",
        "gpt-5.3-codex-spark",
        "task",
    ]

def test_codex_fast_model_mode(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(shutil, "which", lambda _: "/usr/bin/codex")

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    r = run_codex(tmp_path, "task", "prompt", model="gpt-5.3-codex-spark", model_mode="fast")
    assert r.ok
    assert calls[0] == [
        "codex",
        "exec",
        "--ignore-user-config",
        "--json",
        "--full-auto",
        "--model",
        "gpt-5.3-codex-spark",
        "--config",
        'model_reasoning_effort="low"',
        "task",
    ]

def test_codex_medium_model_mode(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(shutil, "which", lambda _: "/usr/bin/codex")

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    r = run_codex(tmp_path, "task", "prompt", model="gpt-5.5", model_mode="medium")
    assert r.ok
    assert calls[0] == [
        "codex",
        "exec",
        "--ignore-user-config",
        "--json",
        "--full-auto",
        "--model",
        "gpt-5.5",
        "--config",
        'model_reasoning_effort="medium"',
        "task",
    ]

def test_codex_xhigh_model_mode(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(shutil, "which", lambda _: "/usr/bin/codex")

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    r = run_codex(tmp_path, "task", "prompt", model="gpt-5.3-codex-spark", model_mode="xhigh")
    assert r.ok
    assert calls[0] == [
        "codex",
        "exec",
        "--ignore-user-config",
        "--json",
        "--full-auto",
        "--model",
        "gpt-5.3-codex-spark",
        "--config",
        'model_reasoning_effort="xhigh"',
        "task",
    ]

def test_codex_bin_override(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(shutil, "which", lambda _: "/usr/local/bin/codex")

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    r = run_codex(tmp_path, "task", "prompt", codex_bin="/opt/homebrew/bin/codex")
    assert r.ok
    assert calls[0][0] == "/opt/homebrew/bin/codex"

def test_codex_uses_isolated_codex_home(tmp_path, monkeypatch):
    source_home = tmp_path / "source-home"
    child_home = tmp_path / "child-home"
    source_home.mkdir()
    (source_home / "auth.json").write_text("{}")
    captured = {}
    monkeypatch.setenv("CODEX_HOME", str(source_home))
    monkeypatch.setattr(tempfile, "mkdtemp", lambda prefix: str(child_home))
    monkeypatch.setattr(shutil, "which", lambda _: "/usr/bin/codex")

    def fake_run(cmd, **kwargs):
        captured["cmd"] = cmd
        captured["env"] = kwargs["env"]
        config = (child_home / "config.toml").read_text()
        assert 'approval_policy = "never"' in config
        assert 'sandbox_mode = "workspace-write"' in config
        assert "shell_snapshot = false" in config
        assert (child_home / "auth.json").read_text() == "{}"
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    r = run_codex(tmp_path, "task", "prompt")
    assert r.ok
    assert Path(captured["env"]["CODEX_HOME"]) == child_home
    assert not child_home.exists()
