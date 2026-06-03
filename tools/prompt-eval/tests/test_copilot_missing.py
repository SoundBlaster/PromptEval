from pathlib import Path
import shutil
import subprocess
from prompt_eval.agents.copilot_agent import run_copilot


def test_copilot_missing_graceful(tmp_path, monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda _: None)
    r = run_copilot(tmp_path, "task", "prompt")
    assert not r.ok
    assert "not found" in r.stderr


def test_copilot_missing_reports_selected_binary(tmp_path, monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda _: None)
    r = run_copilot(tmp_path, "task", "prompt", copilot_bin="/missing/copilot")
    assert not r.ok
    assert "--copilot-bin '/missing/copilot'" in r.stderr


def test_copilot_missing_reports_env_binary(tmp_path, monkeypatch):
    monkeypatch.setenv("PEVAL_COPILOT_BIN", "/missing/env-copilot")
    monkeypatch.setattr(shutil, "which", lambda _: None)
    r = run_copilot(tmp_path, "task", "prompt")
    assert not r.ok
    assert "PEVAL_COPILOT_BIN='/missing/env-copilot'" in r.stderr


def test_copilot_unsupported_model_mode_graceful(tmp_path, monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/copilot" if name == "copilot" else None)
    r = run_copilot(tmp_path, "task", "prompt", model_mode="turbo")
    assert not r.ok
    assert "unsupported model mode 'turbo'" in r.stderr
    assert "fast" in r.stderr
    assert "medium" in r.stderr
    assert "xhigh" in r.stderr


def test_copilot_model_and_effort_flags(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/copilot" if name == "copilot" else None)

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    r = run_copilot(tmp_path, "task", "prompt", model="claude-opus-4-8", model_mode="fast")
    assert r.ok
    assert calls[0] == [
        "copilot",
        "-p",
        "task",
        "--allow-all-tools",
        "--allow-all-paths",
        "--disable-builtin-mcps",
        "--model",
        "claude-opus-4-8",
        "--effort",
        "low",
    ]
    assert (Path(tmp_path) / "AGENTS.md").read_text() == "prompt"


def test_copilot_falls_back_to_gh_wrapper(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(shutil, "which", lambda name: "/opt/homebrew/bin/gh" if name == "gh" else None)

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    r = run_copilot(tmp_path, "task", "prompt")
    assert r.ok
    assert calls[0][:4] == ["gh", "copilot", "--", "-p"]
