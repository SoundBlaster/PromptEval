# Agent instructions

This task is an explicit refactoring task toward Elegant Objects.

Preserve observable behavior first. Refactor in small, reviewable steps. Existing tests are characterization tests unless the task explicitly asks to change behavior. If tests are missing, add the smallest tests needed to pin current behavior before changing structure.

Use EO as the refactoring target:
- Move behavior from procedural helpers, renderers, controllers, dictionaries, and raw primitives into focused objects.
- Prefer immutable values and explicit dependencies.
- Avoid getters/setters in domain code when behavior can be asked from the object.
- Avoid Utils, Helpers, Managers, Processors, and broad Services.
- Avoid constructor work: initialization assigns dependencies and values; I/O, parsing, caching, and heavy validation belong in behavior or collaborators.
- Prefer composition and decorators over inheritance trees, flags, casts, and type-branching ladders.
- Keep boundary DTOs at boundaries and convert them into behavior-rich objects before domain behavior.

Keep the refactor narrow:
- Do not change public API unless the task explicitly permits it.
- Do not refactor unrelated modules.
- Do not chase EO purity beyond the requested transformation.
- Do not rename external protocol fields, generated code, test fixture names, or serialization keys.

Before finishing:
- Run relevant tests/checks.
- Review the diff for behavior changes, over-refactoring, DTO leakage, static-helper relapse, mutable setters, and naming dogmatism.
- Report any larger EO opportunities separately instead of applying them.
