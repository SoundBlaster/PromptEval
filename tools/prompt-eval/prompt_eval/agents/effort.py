from __future__ import annotations

# Canonical, engine-agnostic model-mode vocabulary shared by every agent adapter.
# A single token (e.g. "fast") is mapped by each adapter onto its own reasoning-effort knob,
# so callers select effort once and the harness stays decoupled from any specific CLI.
#
# Codex exposes reasoning effort through `--config model_reasoning_effort="<level>"`.
MODEL_MODE_CONFIG = {
    "fast": 'model_reasoning_effort="low"',
    "medium": 'model_reasoning_effort="medium"',
    "xhigh": 'model_reasoning_effort="xhigh"',
}
SUPPORTED_MODEL_MODES = tuple(MODEL_MODE_CONFIG)

# Copilot CLI exposes reasoning effort through `--effort <level>`.
COPILOT_EFFORT = {
    "fast": "low",
    "medium": "medium",
    "xhigh": "xhigh",
}
