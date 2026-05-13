You are a coding agent following Feature-Sliced Design (FSD).

Key rules:
- Layer order: `app → pages → widgets → features → entities → shared`. Higher layers may import lower layers. Lower layers must never import higher layers. Sibling slices on the same layer must not import each other.
- Every slice exposes a single `index.ts` public API. External code imports from `@/layer/slice`, never from internal paths like `@/layer/slice/segment/file`.
- Inside a slice, use only these segment names: `ui/`, `model/`, `api/`, `lib/`, `config/`. Avoid `components/`, `hooks/`, `utils/`, `services/`.
- Feature slices are verb phrases (add-to-cart, send-comment). Entity slices are nouns (user, product). Shared is for domain-agnostic reusable code only.
- Each distinct user action (add item, toggle, send, delete, login) lives in its own `features/<verb-phrase>` slice. Do not bury action logic inside entity slices — entities own data and presentation, features own actions on that data.
- A reusable composite UI block that combines multiple features and/or entities (a navbar, a sidebar, a product card with actions) belongs in `widgets/<noun>`, not inside a page.
