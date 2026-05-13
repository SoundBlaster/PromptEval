from __future__ import annotations
import json
import os
import re
import shutil
import socket
import urllib.error
import urllib.request
from pathlib import Path
from .base import AgentRun

DEFAULT_API_BASE = "http://localhost:1234/v1"
DEFAULT_MAX_TOKENS = 8192
DEFAULT_TEMPERATURE = 0.2
DEFAULT_TIMEOUT = 600
MAX_FILE_BYTES = 64_000

SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", ".pytest_cache", ".ruff_cache", "dist", "build"}
TEXT_SUFFIXES = {
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".json",
    ".md",
    ".txt",
    ".py",
    ".yaml",
    ".yml",
    ".html",
    ".css",
    ".sh",
    ".toml",
}

FILE_FORMAT_INSTRUCTIONS = """Output your full solution as a sequence of file blocks. Use this exact format:

### FILE: relative/path/to/file.ts
```
<file contents go here>
```

### FILE: another/file.tsx
```
<file contents>
```

To delete a file, emit:

### DELETE: path/to/old.ts

Rules:
- Use forward slashes in paths, relative to the project root.
- Emit one block per file, including unchanged files only when you must overwrite them.
- Place the entire file content inside the fenced block; do not split a file across blocks.
- Do not include commentary outside the blocks. Reasoning, if any, must come before the first ### FILE: header.
"""

FILE_BLOCK_RE = re.compile(r"^###\s+FILE:\s*(?P<path>\S+)\s*$", re.MULTILINE)
DELETE_BLOCK_RE = re.compile(r"^###\s+DELETE:\s*(?P<path>\S+)\s*$", re.MULTILINE)
FENCE_RE = re.compile(r"^```[\w-]*\s*\n(?P<body>.*?)\n```\s*$", re.DOTALL | re.MULTILINE)


def _gather_files(sandbox: Path) -> str:
    chunks = []
    for path in sorted(sandbox.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(sandbox)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if path.suffix and path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            data = path.read_text()
        except (UnicodeDecodeError, OSError):
            continue
        if len(data.encode("utf-8")) > MAX_FILE_BYTES:
            continue
        chunks.append(f"### FILE: {rel.as_posix()}\n```\n{data}\n```\n")
    return "\n".join(chunks)


def _build_user_message(task: str, files_blob: str) -> str:
    return (
        "Current project state — every file shown is the authoritative source on disk:\n\n"
        f"{files_blob}\n\n"
        "---\n\n"
        f"Task:\n{task}\n\n"
        f"{FILE_FORMAT_INSTRUCTIONS}"
    )


def _chat_completion(
    api_base: str,
    api_key: str,
    model: str,
    system_prompt: str,
    user_message: str,
    max_tokens: int,
    temperature: float,
    timeout: int,
) -> tuple[str, dict]:
    url = api_base.rstrip("/") + "/chat/completions"
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": False,
    }
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8")
    parsed = json.loads(raw)
    choice = (parsed.get("choices") or [{}])[0]
    message = choice.get("message") or {}
    content = message.get("content") or ""
    if not content:
        content = message.get("reasoning_content") or message.get("reasoning") or ""
    return content, parsed


def _safe_relpath(raw: str) -> Path | None:
    candidate = Path(raw)
    if candidate.is_absolute():
        return None
    parts = candidate.parts
    if any(part == ".." for part in parts):
        return None
    if not parts:
        return None
    return candidate


def _strip_fence(block: str) -> str:
    match = FENCE_RE.search(block.strip())
    if match:
        return match.group("body")
    return block.strip("\n")


def _parse_blocks(text: str) -> tuple[dict[Path, str], list[Path]]:
    writes: dict[Path, str] = {}
    deletes: list[Path] = []
    file_matches = list(FILE_BLOCK_RE.finditer(text))
    for idx, match in enumerate(file_matches):
        rel = _safe_relpath(match.group("path"))
        if rel is None:
            continue
        start = match.end()
        end = file_matches[idx + 1].start() if idx + 1 < len(file_matches) else len(text)
        body = _strip_fence(text[start:end])
        writes[rel] = body if body.endswith("\n") else body + "\n"
    for match in DELETE_BLOCK_RE.finditer(text):
        rel = _safe_relpath(match.group("path"))
        if rel is not None:
            deletes.append(rel)
    return writes, deletes


def _apply(sandbox: Path, writes: dict[Path, str], deletes: list[Path]) -> list[dict]:
    trace = []
    for rel, content in writes.items():
        target = sandbox / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
        trace.append({"event": "write", "path": rel.as_posix(), "bytes": len(content)})
    for rel in deletes:
        target = sandbox / rel
        if not target.exists():
            continue
        if target.is_dir():
            shutil.rmtree(target)
            trace.append({"event": "delete_dir", "path": rel.as_posix()})
        else:
            target.unlink()
            trace.append({"event": "delete", "path": rel.as_posix()})
    return trace


def run_openai(
    sandbox: Path,
    task: str,
    prompt_text: str,
    model: str | None = None,
    api_base: str | None = None,
    api_key: str | None = None,
    max_tokens: int | None = None,
    temperature: float | None = None,
    timeout: int | None = None,
) -> AgentRun:
    resolved_model = model or os.environ.get("PEVAL_OPENAI_MODEL")
    if not resolved_model:
        return AgentRun(
            ok=False,
            stderr="openai agent requires --model (or PEVAL_OPENAI_MODEL env)",
            trace=[{"event": "openai_missing_model"}],
        )
    resolved_base = api_base or os.environ.get("PEVAL_OPENAI_API_BASE", DEFAULT_API_BASE)
    resolved_key = api_key or os.environ.get("PEVAL_OPENAI_API_KEY", "lm-studio")
    resolved_max = max_tokens if max_tokens is not None else DEFAULT_MAX_TOKENS
    resolved_temp = temperature if temperature is not None else DEFAULT_TEMPERATURE
    resolved_timeout = timeout if timeout is not None else DEFAULT_TIMEOUT

    files_blob = _gather_files(sandbox)
    user_message = _build_user_message(task, files_blob)
    try:
        content, raw = _chat_completion(
            resolved_base,
            resolved_key,
            resolved_model,
            prompt_text,
            user_message,
            resolved_max,
            resolved_temp,
            resolved_timeout,
        )
    except (urllib.error.URLError, socket.timeout, TimeoutError) as exc:
        return AgentRun(
            ok=False,
            stderr=f"openai agent: HTTP error contacting {resolved_base}: {exc}",
            trace=[{"event": "openai_http_error", "error": str(exc)}],
        )
    except (json.JSONDecodeError, ValueError) as exc:
        return AgentRun(
            ok=False,
            stderr=f"openai agent: invalid response: {exc}",
            trace=[{"event": "openai_bad_response", "error": str(exc)}],
        )

    writes, deletes = _parse_blocks(content)
    trace = [{"event": "openai_request", "model": resolved_model, "api_base": resolved_base, "files": len(writes)}]
    trace.extend(_apply(sandbox, writes, deletes))
    if not writes and not deletes:
        trace.append({"event": "openai_no_files_parsed", "content_head": content[:300]})
    usage = raw.get("usage") if isinstance(raw, dict) else None
    if usage:
        trace.append({"event": "openai_usage", **usage})
    return AgentRun(ok=True, stdout=content, stderr="", trace=trace)
