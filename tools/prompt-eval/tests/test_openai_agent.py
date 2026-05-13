from pathlib import Path
import shutil
import tempfile

from prompt_eval.agents.openai_agent import _apply, _parse_blocks


def test_apply_writes_files_and_handles_file_delete():
    tmp = Path(tempfile.mkdtemp(prefix="peval-openai-test-"))
    try:
        (tmp / "old.ts").write_text("old\n")
        writes, deletes = _parse_blocks("### FILE: src/new.ts\n```\nexport const x = 1;\n```\n\n### DELETE: old.ts\n")
        _apply(tmp, writes, deletes)
        assert (tmp / "src/new.ts").read_text() == "export const x = 1;\n"
        assert not (tmp / "old.ts").exists()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_apply_handles_directory_delete_without_error():
    tmp = Path(tempfile.mkdtemp(prefix="peval-openai-test-"))
    try:
        (tmp / "src" / "legacy").mkdir(parents=True)
        (tmp / "src" / "legacy" / "a.ts").write_text("a\n")
        (tmp / "src" / "legacy" / "b.ts").write_text("b\n")
        writes, deletes = _parse_blocks("### DELETE: src/legacy\n")
        _apply(tmp, writes, deletes)
        assert not (tmp / "src" / "legacy").exists()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_parse_blocks_rejects_path_traversal_and_absolute_paths():
    writes, deletes = _parse_blocks("### FILE: /etc/passwd\n```\npwned\n```\n\n### FILE: ../escape.ts\n```\nx\n```\n")
    assert writes == {}
    assert deletes == []
