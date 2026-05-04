from .base import AgentRun


def run_mock(task: str) -> AgentRun:
    return AgentRun(stdout="noop", trace=[{"event": "noop", "task": task}])
