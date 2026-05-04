from pathlib import Path
from prompt_eval.runner import run_suite
from prompt_eval.agents.base import AgentRun
import json


def avg(run_dir):
    rows = [json.loads(line) for line in (run_dir / "results.jsonl").read_text().splitlines() if line.strip()]
    return sum(r["score"]["total"] for r in rows) / len(rows)


def test_good_beats_bad():
    root = Path(__file__).resolve().parents[1]
    p = [root / "prompts/elegant_objects/eo_lite.md"]
    good = run_suite(root, "elegant_objects", p, "fixture-good")
    bad = run_suite(root, "elegant_objects", p, "fixture-bad")
    assert avg(good) > avg(bad)


def test_codex_agent_sees_only_before_fixture(monkeypatch):
    root = Path(__file__).resolve().parents[1]
    p = [root / "prompts/elegant_objects/eo_greenfield.md"]
    seen = []

    def fake_run_codex(sandbox, task, prompt_text, model, model_mode, codex_bin):
        files = sorted(path.relative_to(sandbox).as_posix() for path in sandbox.rglob("*") if path.is_file())
        seen.append({"task": task, "has_solutions": (sandbox / "solutions").exists(), "files": files})
        assert not (sandbox / "solutions").exists()
        assert all(not file.startswith("solutions/") for file in files)
        assert all("solutions" not in file for file in files)
        if (sandbox / "bookstore/app.py").exists():
            assert "BookstoreService" not in (sandbox / "bookstore/app.py").read_text()
        if (sandbox / "library_app/app.py").exists():
            assert "LibraryManager" not in (sandbox / "library_app/app.py").read_text()
        return AgentRun(ok=True)

    monkeypatch.setattr("prompt_eval.runner.run_codex", fake_run_codex)

    run_suite(root, "elegant_objects", p, "codex", case_sets=["eo_app_skeleton"])

    assert len(seen) == 8
    assert all(item["has_solutions"] is False for item in seen)
    assert any("bookstore/app.py" in item["files"] for item in seen)
    assert any("library_app/app.py" in item["files"] for item in seen)
    assert any("hotel_booking/app.py" in item["files"] for item in seen)
    assert any("ticketing/app.py" in item["files"] for item in seen)
    assert all("Good solution" not in item["task"] for item in seen)
    assert all("BookstoreService" not in item["task"] for item in seen)
    assert all("LibraryManager" not in item["task"] for item in seen)
