Implement the task with practical Elegant Objects style:
- Prefer behavior-rich objects over passive data bags.
- Avoid new Utils/Helpers/Managers/Processors/Services when an object can own behavior.
- Keep constructors simple; do work in explicit methods/factories.
- DTOs are allowed at boundaries; convert before domain behavior.
- Compound names are signals, not auto-rename commands.
- Apply local scout cleanup only; report larger refactors separately.
