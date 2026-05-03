from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

import yaml

from .agents.codex_agent import run_codex
from .config import load_case


DEFAULT_GENERATOR_MODEL = "gpt-5.3-codex-spark"
DEFAULT_GENERATOR_MODEL_MODE = "fast"

GENERATOR_PROMPT = """You generate PromptEval coding tasks.

Create a complete eval fixture from the user's task description.
The output must be deterministic, small enough to review, and compatible with
the existing PromptEval fixture format.

Required output layout:
- generated/<case_id>/before/...
- generated/<case_id>/good/...
- generated/<case_id>/bad/...
- generated/<case_id>/case.yaml

Rules:
- Use Python unless the user explicitly asks for another stack.
- Put a minimal working project under before/.
- Put the expected strong solution under good/.
- Put a plausible weak solution under bad/.
- Include tests in before/ that describe current behavior, and update tests in
  good/ and bad/ as needed so deterministic checks can distinguish behavior.
- Keep the task realistic, but compact.
- Do not write files outside generated/<case_id>/.
- Do not create symlinks.
- Do not leave TODO placeholders.
- Keep case.yaml valid YAML. Do not use Markdown backticks in YAML values.
- Avoid backslash-heavy regex in case.yaml. Prefer simple patterns like
  "class TaxRule", "def total", "TaxHelper", or "set_".
- Quote or block-style any YAML text that contains punctuation.

case.yaml must include:
- id
- title
- fixture: <case_id>
- task
- checks.commands with pytest and compileall when Python is used
- checks.required_regex or forbidden_regex for deterministic design signals
- checks.max_changed_files
- rubric
- notes
- judge.categories
- judge.criteria

Use these rubric categories unless the task needs a different suite:
- functional_correctness: 40
- scope_control: 20
- eo_adherence: 25
- verification: 10
- communication: 5
"""


@dataclass
class GeneratedCase:
    case_id: str
    workdir: Path
    output_dir: Path
    case_yaml: Path
    before_dir: Path
    good_dir: Path
    bad_dir: Path


def _slug(value: str) -> str:
    lowered = value.lower()
    slug = re.sub(r"[^a-z0-9]+", "_", lowered).strip("_")
    return slug[:64].strip("_") or "generated_case"


def _task(case_id: str, description: str) -> str:
    return f"""Generate one PromptEval case.

case_id: {case_id}

Task description:
{description}

After writing files, verify the generated fixture locally. Prefer:
- python -m pytest -q generated/{case_id}/before
- python -m pytest -q generated/{case_id}/good
- python -m pytest -q generated/{case_id}/bad
- python -m compileall -q generated/{case_id}
"""


def _init_workspace(path: Path) -> None:
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "peval@example.local"], cwd=path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "peval"], cwd=path, check=True, capture_output=True)
    (path / ".gitkeep").write_text("")
    subprocess.run(["git", "add", ".gitkeep"], cwd=path, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "baseline"], cwd=path, check=True, capture_output=True)


def _normalize_regex_checks(items) -> list[dict]:
    normalized = []
    for item in items or []:
        if isinstance(item, str):
            normalized.append({"pattern": item, "target": "diff", "reason": "Generated deterministic design signal"})
        elif isinstance(item, dict):
            normalized.append(item)
        else:
            raise ValueError(f"regex check must be a mapping or string, got {type(item).__name__}")
    return normalized


def _python_fixture(output_dir: Path) -> bool:
    return any((output_dir / name).rglob("*.py") for name in ("before", "good", "bad"))


def _normalize_commands(commands, output_dir: Path) -> list:
    if _python_fixture(output_dir):
        return [["python", "-m", "pytest", "-q"], ["python", "-m", "compileall", "-q", "."]]
    return commands or []


def _normalize_criteria(criteria) -> list[str]:
    if criteria is None:
        return []
    if isinstance(criteria, str):
        return [criteria]
    if isinstance(criteria, dict):
        return [str(value) for value in criteria.values()]
    return list(criteria)


def _normalize_notes(notes) -> str:
    if notes is None:
        return ""
    if isinstance(notes, list):
        return " ".join(str(item) for item in notes)
    return str(notes)


def _case_yaml_data(case_yaml: Path) -> dict:
    text = case_yaml.read_text()
    try:
        return yaml.safe_load(text) or {}
    except yaml.YAMLError:
        repaired = re.sub(r'(?<!\\)\\(?![0abtnvfre "\\/N_LPxuU])', r"\\\\", text)
        if repaired == text:
            raise
        case_yaml.write_text(repaired)
        return yaml.safe_load(repaired) or {}


def _normalize_case_yaml(case_yaml: Path) -> None:
    raw = _case_yaml_data(case_yaml)
    checks = raw.setdefault("checks", {})
    checks["commands"] = _normalize_commands(checks.get("commands"), case_yaml.parent)
    checks["forbidden_regex"] = _normalize_regex_checks(checks.get("forbidden_regex"))
    checks["required_regex"] = _normalize_regex_checks(checks.get("required_regex"))
    raw["notes"] = _normalize_notes(raw.get("notes"))
    judge = raw.get("judge")
    if isinstance(judge, dict):
        judge["criteria"] = _normalize_criteria(judge.get("criteria"))
    case_yaml.write_text(yaml.safe_dump(raw, sort_keys=False))


def _validate_regex_checks(case: Path) -> None:
    loaded = load_case(case)
    for check in loaded.checks.required_regex + loaded.checks.forbidden_regex:
        try:
            re.compile(check.pattern)
        except re.error as exc:
            raise ValueError(f"invalid regex {check.pattern!r} in {case}: {exc}") from exc


def _validate_case_dir(workdir: Path, output_dir: Path, case_id: str) -> GeneratedCase:
    case_yaml = output_dir / "case.yaml"
    before_dir = output_dir / "before"
    good_dir = output_dir / "good"
    bad_dir = output_dir / "bad"
    missing = [str(path) for path in (case_yaml, before_dir, good_dir, bad_dir) if not path.exists()]
    if missing:
        raise ValueError(f"generated case is missing required paths: {', '.join(missing)}")
    raw = _case_yaml_data(case_yaml)
    if raw.get("fixture") != case_id:
        raise ValueError(f"case.yaml fixture must be {case_id!r}, got {raw.get('fixture')!r}")
    _normalize_case_yaml(case_yaml)
    _validate_regex_checks(case_yaml)
    return GeneratedCase(case_id=case_id, workdir=workdir, output_dir=output_dir, case_yaml=case_yaml, before_dir=before_dir, good_dir=good_dir, bad_dir=bad_dir)


def _validate_case(root: Path, case_id: str) -> GeneratedCase:
    return _validate_case_dir(root, root / "generated" / case_id, case_id)


def generate_case(
    description: str,
    case_id: str | None = None,
    output_root: Path | None = None,
    model: str = DEFAULT_GENERATOR_MODEL,
    model_mode: str = DEFAULT_GENERATOR_MODEL_MODE,
    codex_bin: str | None = None,
) -> GeneratedCase:
    selected_id = _slug(case_id or description.splitlines()[0])
    temp = Path(tempfile.mkdtemp(prefix="peval-generate-"))
    try:
        _init_workspace(temp)
        agent = run_codex(temp, _task(selected_id, description), GENERATOR_PROMPT, model, model_mode, codex_bin)
        if not agent.ok:
            raise RuntimeError(agent.stderr or agent.stdout or "Codex generation failed")
        generated = _validate_case(temp, selected_id)
        if output_root is None:
            return generated
        destination = output_root / selected_id
        if destination.exists():
            raise FileExistsError(f"output already exists: {destination}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(generated.output_dir, destination)
        copied = _validate_case_dir(output_root, destination, selected_id)
        shutil.rmtree(temp, ignore_errors=True)
        return copied
    except Exception:
        if output_root is not None:
            shutil.rmtree(temp, ignore_errors=True)
        raise
