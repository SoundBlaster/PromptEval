# Elegant Objects Rubric

Deterministic checks plus optional LLM judge score across functional correctness, scope control, EO adherence, verification, and communication.

Use deterministic checks for hard facts: tests, syntax/compile checks, required behavior markers, forbidden procedural helpers, static method relapse, setter-driven mutation, and diff scope.

Use the optional subagent judge for semantic design questions that are not robust as regexes: whether behavior is owned by the right object, whether DTOs stay at boundaries without dogmatism, whether names improved because scope improved, and whether a cleanup stayed local rather than becoming an opportunistic rewrite.
