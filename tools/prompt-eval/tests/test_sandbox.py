from pathlib import Path
import shutil
import subprocess
from prompt_eval.sandbox import prepare_sandbox
from prompt_eval.checks import git_diff


def test_prepare_sandbox_has_git_diff_clean():
    root = Path(__file__).resolve().parents[1]
    sb = prepare_sandbox(root / "fixtures/python_eo_shop/before")
    try:
        assert (sb / ".git").exists()
        diff = subprocess.run(["git", "diff"], cwd=sb, text=True, capture_output=True, check=True).stdout
        assert diff == ""
    finally:
        shutil.rmtree(sb, ignore_errors=True)


def test_git_diff_includes_newly_created_files():
    root = Path(__file__).resolve().parents[1]
    sb = prepare_sandbox(root / "fixtures/python_eo_shop/before")
    try:
        (sb / "new_module.py").write_text("def hello():\n    return 'hi'\n")
        diff = git_diff(sb)
        assert "new_module.py" in diff
        assert "def hello" in diff
    finally:
        shutil.rmtree(sb, ignore_errors=True)


def test_prepare_sandbox_contains_only_before_fixture_files():
    root = Path(__file__).resolve().parents[1]
    fixture = root / "fixtures/eo_app_skeleton_bookstore"
    sb = prepare_sandbox(fixture / "before")
    try:
        assert (sb / "bookstore/app.py").exists()
        assert (fixture / "solutions/good/bookstore/app.py").exists()
        assert not (sb / "solutions").exists()
        assert "BookstoreService" not in (sb / "bookstore/app.py").read_text()
        assert "DiscountHelper" not in (sb / "bookstore/app.py").read_text()
    finally:
        shutil.rmtree(sb, ignore_errors=True)
