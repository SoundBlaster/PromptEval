# Feature-Sliced Design Guide

You are a coding agent working on a web frontend codebase organized with Feature-Sliced Design (FSD).

## Layer hierarchy (high → low)

```
app → pages → widgets → features → entities → shared
```

Higher layers may import from lower layers. Lower layers must never import from higher layers.
Sibling slices on the same layer must never import from each other.

## Public API rule

Every slice must expose a single `index.ts` that acts as its public contract.
External code imports only from the slice root: `@/features/login`, not `@/features/login/ui/form`.
Never use `export *` in index.ts — export exactly what consumers need.

## Segment naming

Use FSD segment names inside each slice:
- `ui/` — React components
- `model/` — hooks, state, selectors, schemas, business logic
- `api/` — request functions, DTOs, mappers
- `lib/` — slice-local helper functions
- `config/` — feature flags, constants

Avoid `components/`, `hooks/`, `utils/`, `services/` — these are technical groupings, not FSD segments.

## Naming conventions

- **Features** — business action verbs: `add-to-cart`, `send-comment`, `submit-order`
- **Entities** — business nouns: `user`, `product`, `order`
- **Shared** — purely reusable, domain-agnostic code

## Lazy extraction

Keep code at the point of use. Extract to a lower layer only when code is reused by
multiple slices or represents an independent business concept. Avoid premature decomposition.

## Cross-entity imports

When one entity must reference a type from another entity, use the `@x` cross-import segment:
```
entities/user/@x/order.ts  →  entities/order imports from '@/entities/user/@x/order'
```

## Before finishing

Run `steiger ./src` to verify no FSD violations remain.
