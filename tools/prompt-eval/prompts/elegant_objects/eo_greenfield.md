# Agent instructions

This is a greenfield Elegant Objects implementation.

Design the solution around small behavior-rich objects from the start. Because there is no legacy design to preserve, EO may guide the initial object model. Still keep the implementation minimal and testable.

Greenfield EO constraints:
- Objects do work; they are not passive data bags.
- Keep state immutable where practical.
- Inject dependencies explicitly.
- Keep constructors simple: assign values and dependencies only.
- Avoid getters/setters in domain code when behavior can express the need.
- Avoid Utils, Helpers, Managers, Processors, and broad Services.
- Keep DTOs and dictionaries at input/output boundaries.
- Prefer composition and decorators over inheritance, flags, casts, and type-branching ladders.
- Use short names only when scope makes them obvious; do not make names cryptic.

Implementation discipline:
- Start with the smallest object model that satisfies the requested behavior.
- Add tests for the public behavior.
- Keep I/O, parsing, and formatting at boundaries unless the task asks otherwise.
- Do not overbuild frameworks or abstract factories for small tasks.

Before finishing, run relevant tests/checks and summarize the object model briefly.
