from .base import JudgeResult


def judge_mock(*args, **kwargs) -> JudgeResult:
    return JudgeResult(categories={}, failure_tags=[], summary="mock judge disabled")
