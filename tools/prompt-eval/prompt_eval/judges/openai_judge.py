import os
from .base import JudgeResult

def judge_openai(*args, **kwargs) -> JudgeResult:
    if not os.getenv("OPENAI_API_KEY"):
        return JudgeResult(categories={}, failure_tags=[], summary="OPENAI_API_KEY not set")
    return JudgeResult(categories={}, failure_tags=[], summary="OpenAI judge stub")
