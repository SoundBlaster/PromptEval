from __future__ import annotations
from dataclasses import dataclass


@dataclass
class AgentRun:
    stdout: str = ""
    stderr: str = ""
    trace: list[dict] | None = None
    ok: bool = True
