"""Lightweight FSD structural checker.

Replaces Steiger on greenfield fixtures where Steiger's `insignificant-slice`
rule fires on legitimately-small slice counts. Implements the three FSD rules
that matter most for prompt evaluation:

1. Layer hierarchy — `app > pages > widgets > features > entities > shared`.
   No upward imports. No sibling slice imports inside features/, entities/, widgets/.
2. Public API — cross-slice imports must hit the slice root (`@/<layer>/<slice>`),
   not an internal segment file.
3. Segment names — slice subdirectories use `ui/`, `model/`, `api/`, `lib/`,
   `config/`. Common offenders flagged: `components/`, `hooks/`, `utils/`,
   `services/`, `helpers/`.

The checker is purely structural — it doesn't run TypeScript, doesn't need
node_modules, and doesn't care whether a slice is "insignificant".
"""

from __future__ import annotations

import re
from pathlib import Path

from .models import CheckResult


# Higher index = higher layer. Higher layers may import lower layers, never vice versa.
LAYERS = ["shared", "entities", "features", "widgets", "pages", "app"]
LAYER_RANK = {name: idx for idx, name in enumerate(LAYERS)}
ALLOWED_SEGMENTS = {"ui", "model", "api", "lib", "config", "@x"}
FORBIDDEN_SEGMENTS = {
    "components": "use ui/ instead of components/ inside a slice",
    "hooks": "use model/ instead of hooks/ inside a slice",
    "utils": "use lib/ instead of utils/ inside a slice",
    "services": "use api/ or model/ instead of services/ inside a slice",
    "helpers": "use lib/ instead of helpers/ inside a slice",
}

IMPORT_RE = re.compile(
    r"""(?:^|\s)(?:import\s+(?:type\s+)?[^'"`]*\s+from\s+|import\s+|export\s+\*?\s*(?:\{[^}]*\}\s+)?from\s+)['"]([^'"]+)['"]""",
    re.MULTILINE,
)
ALIAS_PREFIX = "@/"
SOURCE_SUFFIXES = (".ts", ".tsx", ".js", ".jsx")


def _is_source(path: Path) -> bool:
    return path.suffix.lower() in SOURCE_SUFFIXES


def _imports(text: str) -> list[str]:
    return IMPORT_RE.findall(text)


def _classify_path(rel: Path) -> tuple[str | None, str | None, str | None]:
    """Return (layer, slice, segment) for a source file under src/."""
    parts = rel.parts
    if len(parts) < 2 or parts[0] != "src":
        return None, None, None
    layer = parts[1]
    if layer not in LAYER_RANK:
        return None, None, None
    if layer == "app":
        return layer, None, None
    if layer == "shared":
        if len(parts) >= 3:
            return layer, None, parts[2]
        return layer, None, None
    if len(parts) < 3:
        return layer, None, None
    slice_name = parts[2]
    segment = parts[3] if len(parts) >= 4 else None
    return layer, slice_name, segment


def _classify_alias_import(spec: str) -> tuple[str | None, str | None, list[str]]:
    """Return (layer, slice, remainder) for an `@/...` import spec."""
    if not spec.startswith(ALIAS_PREFIX):
        return None, None, []
    parts = spec[len(ALIAS_PREFIX) :].split("/")
    if not parts:
        return None, None, []
    layer = parts[0]
    if layer not in LAYER_RANK:
        return None, None, []
    if layer == "app":
        return layer, None, parts[1:]
    if layer == "shared":
        # shared has no business-level slice; segments come right after layer.
        return layer, None, parts[1:]
    slice_name = parts[1] if len(parts) > 1 else None
    return layer, slice_name, parts[2:]


def check_fsd_structure(sandbox: Path) -> list[CheckResult]:
    """Walk the sandbox and return one CheckResult per FSD rule type.

    Each rule produces a single CheckResult: passed when no violations were found,
    failed with a concise multiline detail listing the offenders otherwise.
    """
    src = sandbox / "src"
    if not src.exists():
        return [
            CheckResult(passed=False, name="fsd_structure:layout", detail="no src/ directory under sandbox"),
        ]

    detected_layers = sorted({p.name for p in src.iterdir() if p.is_dir() and p.name in LAYER_RANK})
    layers_present = bool(detected_layers)

    layer_violations: list[str] = []
    public_api_violations: list[str] = []
    segment_violations: list[str] = []

    for path in sorted(src.rglob("*")):
        if path.is_dir():
            # Segment naming violations are detected on directories, not files.
            rel = path.relative_to(sandbox)
            layer, slice_name, segment = _classify_path(rel)
            if layer not in {"features", "entities", "widgets"}:
                continue
            if slice_name is None or segment is None:
                continue
            depth_from_slice = len(rel.parts) - 4  # src / layer / slice / segment
            if depth_from_slice != 0:
                continue
            if segment in FORBIDDEN_SEGMENTS:
                segment_violations.append(f"{rel.as_posix()}: {FORBIDDEN_SEGMENTS[segment]}")
            elif segment not in ALLOWED_SEGMENTS and not segment.startswith("@"):
                segment_violations.append(
                    f"{rel.as_posix()}: unknown segment `{segment}`; allowed: {', '.join(sorted(ALLOWED_SEGMENTS))}"
                )
            continue
        if not path.is_file() or not _is_source(path):
            continue
        rel = path.relative_to(sandbox)
        importer_layer, importer_slice, _ = _classify_path(rel)
        if importer_layer is None:
            continue
        try:
            text = path.read_text()
        except (UnicodeDecodeError, OSError):
            continue
        for spec in _imports(text):
            layer, slice_name, remainder = _classify_alias_import(spec)
            if layer is None:
                continue

            # Rule 1: layer hierarchy. Importer's layer must be strictly higher
            # than (or equal to, for same-layer imports we check sibling rule)
            # the imported layer.
            if LAYER_RANK[layer] > LAYER_RANK[importer_layer]:
                layer_violations.append(f"{rel.as_posix()} imports from upper layer `{spec}`")
                continue

            # Sibling slice imports inside features/entities/widgets are forbidden.
            if (
                layer == importer_layer
                and layer in {"features", "entities", "widgets"}
                and slice_name
                and importer_slice
                and slice_name != importer_slice
            ):
                # Allow `@x` cross-import segments for entities.
                if not (layer == "entities" and remainder and remainder[0] == "@x"):
                    layer_violations.append(f"{rel.as_posix()} imports sibling slice `{spec}`")
                    continue

            # Rule 2: public API. Same-slice imports may go deep. Cross-slice
            # imports (different slice, or different layer entirely) must hit
            # the slice root — i.e. `remainder` must be empty (or `@x/<file>`).
            same_slice = layer == importer_layer and slice_name == importer_slice
            if same_slice:
                continue
            if layer == "shared":
                # shared has no slice — first segment is allowed (e.g. shared/ui).
                # But going deeper than one level past the layer is a bypass too.
                if len(remainder) > 2:
                    public_api_violations.append(f"{rel.as_posix()} reaches into shared internals via `{spec}`")
                continue
            if layer == "app":
                continue
            if remainder:
                # Allow `@x/<sibling>` cross-imports for entities.
                if remainder[0] == "@x":
                    continue
                public_api_violations.append(f"{rel.as_posix()} bypasses public API via `{spec}`")

    results = [
        CheckResult(
            passed=layers_present,
            name="fsd_structure:layers_present",
            detail=(
                f"detected layers: {', '.join(detected_layers)}"
                if layers_present
                else "no FSD layer directory (app, pages, widgets, features, entities, shared) under src/"
            ),
        ),
        CheckResult(
            passed=not layer_violations,
            name="fsd_structure:layer_hierarchy",
            detail="; ".join(layer_violations[:10]) or "ok",
        ),
        CheckResult(
            passed=not public_api_violations,
            name="fsd_structure:public_api",
            detail="; ".join(public_api_violations[:10]) or "ok",
        ),
        CheckResult(
            passed=not segment_violations,
            name="fsd_structure:segment_names",
            detail="; ".join(segment_violations[:10]) or "ok",
        ),
    ]
    return results
