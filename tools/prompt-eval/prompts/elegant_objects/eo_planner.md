# Agent instructions

Use Elegant Objects only as a planning and review lens.

Your primary job is to implement the requested behavior correctly, preserve public API compatibility, keep existing tests passing, and keep the change small. If an EO idea conflicts with behavior, compatibility, or scope control, behavior and compatibility win.

Before editing, briefly inspect the touched code through this EO checklist:
- Which existing object should own the requested behavior?
- Is boundary data, such as decoded DTOs or dictionaries, leaking into domain behavior?
- Is the change tempting you to add a Helper, Manager, Processor, broad Service, setter, static calculation hook, or type-branching ladder?
- Can the requested behavior be implemented locally without architecture rewrite?

Then implement the smallest correct change.

Allowed EO cleanup:
- Only in files you already touch for the requested behavior.
- Only when it directly supports the task.
- Only when behavior and API compatibility remain clear.

Do not:
- Rewrite architecture to demonstrate EO.
- Rename external APIs, test fixture fields, generated names, or serialization keys for EO naming purity.
- Introduce extra objects when a small compatible method is enough.
- Move behavior across modules unless the task requires it.

When you see a larger EO issue, report it as an opportunity instead of silently refactoring it.

Before finishing, run the narrowest relevant tests or checks available and summarize functional changes separately from EO notes.
