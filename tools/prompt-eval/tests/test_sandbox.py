from pathlib import Path
from prompt_eval.sandbox import prepare_sandbox

def test_prepare_sandbox_has_git_diff_clean():
    root = Path(__file__).resolve().parents[1]
    sb = prepare_sandbox(root / "fixtures/python_eo_shop/before")
    assert (sb / ".git").exists()
