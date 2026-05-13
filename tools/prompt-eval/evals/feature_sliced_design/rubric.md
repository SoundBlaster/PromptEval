# Feature-Sliced Design Rubric

Deterministic checks plus optional LLM judge score across functional correctness,
layer compliance, public API correctness, segment organization, and scope control.

Deterministic checks are the first line of defense. The `steiger ./src` command is
the authoritative structural validator — it catches cross-slice imports, public API
sidesteps, and unknown segment names. Additional `required_files` checks verify that
expected structural artifacts (index.ts public APIs, shared segments) were created.

Optional subagent judge for semantic questions: correct slice placement (feature vs.
entity vs. widget), appropriate abstraction level, naming quality (verb for features,
noun for entities), and whether the public API surface is minimal and intentional.

Rubric categories:
- `functional_correctness` — the feature behaves as specified by the task
- `layer_compliance` — correct import direction; no upward imports; no sibling feature/entity cross-imports
- `public_api_correctness` — all external imports go through slice index.ts; no internal path bypasses
- `segment_organization` — code lives in the semantically correct segment (ui/, model/, api/, lib/)
- `scope_control` — changes stay within the task scope; unrelated files untouched
