"""LLM-as-judge that posts to an OpenAI-compatible /v1/chat/completions endpoint.

Independent of Codex CLI. Lets us cross-check `judge_subagent` (Spark over Codex)
with a different model/family — same prompt and same JSON schema, so results are
directly comparable.
"""

from __future__ import annotations

import json
import os
import socket
import urllib.error
import urllib.request

from .base import JudgeResult
from .common import build_judge_prompt, judge_categories, parse_judge_response
from ..models import EvalCase


DEFAULT_API_BASE = "http://localhost:1234/v1"
DEFAULT_TEMPERATURE = 0.0
DEFAULT_MAX_TOKENS = 4096
DEFAULT_TIMEOUT = 600


def _chat_completion(
    api_base: str,
    api_key: str,
    model: str,
    prompt: str,
    max_tokens: int,
    temperature: float,
    timeout: int,
) -> str:
    url = api_base.rstrip("/") + "/chat/completions"
    body = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a strict LLM-as-judge. Reply with one JSON object only, no prose, no code fences."
                ),
            },
            {"role": "user", "content": prompt},
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
    return content


def judge_openai(
    case: EvalCase,
    prompt_text: str,
    diff: str,
    deterministic_summary: str,
    model: str | None = None,
    api_base: str | None = None,
    api_key: str | None = None,
    max_tokens: int | None = None,
    temperature: float | None = None,
    timeout: int | None = None,
    before_tree: str | None = None,
) -> JudgeResult:
    resolved_model = model or os.environ.get("PEVAL_OPENAI_JUDGE_MODEL") or os.environ.get("PEVAL_OPENAI_MODEL")
    if not resolved_model:
        return JudgeResult(
            categories={},
            failure_tags=["judge_missing_model"],
            summary="openai judge requires --judge-model (or PEVAL_OPENAI_JUDGE_MODEL env)",
        )
    resolved_base = (
        api_base
        or os.environ.get("PEVAL_OPENAI_JUDGE_API_BASE")
        or os.environ.get("PEVAL_OPENAI_API_BASE")
        or DEFAULT_API_BASE
    )
    resolved_key = (
        api_key or os.environ.get("PEVAL_OPENAI_JUDGE_API_KEY") or os.environ.get("PEVAL_OPENAI_API_KEY") or "lm-studio"
    )
    resolved_max = max_tokens if max_tokens is not None else DEFAULT_MAX_TOKENS
    resolved_temp = temperature if temperature is not None else DEFAULT_TEMPERATURE
    resolved_timeout = timeout if timeout is not None else DEFAULT_TIMEOUT

    judge_prompt = build_judge_prompt(case, prompt_text, diff, deterministic_summary, before_tree=before_tree)
    try:
        content = _chat_completion(
            resolved_base,
            resolved_key,
            resolved_model,
            judge_prompt,
            resolved_max,
            resolved_temp,
            resolved_timeout,
        )
    except (urllib.error.URLError, socket.timeout, TimeoutError) as exc:
        return JudgeResult(
            categories={},
            failure_tags=["judge_http_error"],
            summary=f"openai judge: HTTP error contacting {resolved_base}: {exc}",
        )
    except (json.JSONDecodeError, ValueError) as exc:
        return JudgeResult(
            categories={},
            failure_tags=["judge_bad_response"],
            summary=f"openai judge: invalid response: {exc}",
        )
    if not content.strip():
        return JudgeResult(
            categories={},
            failure_tags=["judge_empty_response"],
            summary="openai judge returned empty content",
        )
    return parse_judge_response(content, case, judge_categories(case))
