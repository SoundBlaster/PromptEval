# Feature-Sliced Design — Strict Mode

You are a coding agent. All changes must conform strictly to Feature-Sliced Design v2.

**Hard rules — treat any violation as a blocker:**

1. No layer inversion: a lower layer must not import a higher layer under any circumstance.
2. No sibling cross-imports: slices on the same layer are fully isolated from each other.
3. No public API sidestep: import from `@/layer/slice`, never from `@/layer/slice/segment/file`.
4. Segments inside slices must be named: `ui/`, `model/`, `api/`, `lib/`, `config/` only.
5. Every slice must have an `index.ts`; it must export only the intended public surface.

**Layer hierarchy:** `app → pages → widgets → features → entities → shared`

**Naming:** features are verb phrases (`like-post`), entities are nouns (`user`). No `Helper`, `Manager`, `Service`, `Utils` in slice names.

**Shared** is for domain-agnostic, universally reusable code only. Do not push feature-specific logic into shared.

Before submitting: `steiger ./src` must exit 0.
