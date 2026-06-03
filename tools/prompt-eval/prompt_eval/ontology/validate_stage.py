from __future__ import annotations
import sys
from pathlib import Path
import yaml
from .stage_schemas import STAGE_SCHEMAS, StageSchema


def _strip_fences(text: str) -> str:
    """Tolerate an artifact wrapped in a single ```yaml ... ``` markdown fence."""
    lines = text.strip().splitlines()
    if lines and lines[0].lstrip().startswith("```"):
        lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
    return "\n".join(lines)


def _get(doc: dict, dotted: str):
    node = doc
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node


def validate_doc(doc, schema: StageSchema) -> list[str]:
    errors: list[str] = []
    if not isinstance(doc, dict):
        return [f"stage {schema.stage}: document is not a YAML mapping"]

    kind = doc.get("kind")
    if kind != schema.kind:
        errors.append(f"stage {schema.stage}: expected kind={schema.kind!r}, got {kind!r}")
    if kind in schema.forbid_kinds:
        errors.append(f"stage {schema.stage}: emitted a later-stage artifact kind={kind!r}")

    for key in schema.required:
        if key not in doc:
            errors.append(f"stage {schema.stage}: missing required key {key!r}")

    for key, allowed in schema.enums.items():
        if key in doc and doc[key] not in allowed:
            errors.append(f"stage {schema.stage}: {key}={doc[key]!r} not in {allowed}")

    for dotted, required in schema.nested_required.items():
        node = _get(doc, dotted)
        if node is None:
            errors.append(f"stage {schema.stage}: missing nested object {dotted!r}")
            continue
        if not isinstance(node, dict):
            errors.append(f"stage {schema.stage}: {dotted!r} is not a mapping")
            continue
        for key in required:
            if key not in node:
                errors.append(f"stage {schema.stage}: {dotted}.{key} is required")

    for dotted, allowed in schema.nested_enums.items():
        value = _get(doc, dotted)
        if value is not None and value not in allowed:
            errors.append(f"stage {schema.stage}: {dotted}={value!r} not in {allowed}")

    for lf in schema.list_fields:
        items = doc.get(lf.name)
        if items is None:
            if lf.min_items > 0:
                errors.append(f"stage {schema.stage}: list {lf.name!r} is required with >= {lf.min_items} item(s)")
            continue
        if not isinstance(items, list):
            errors.append(f"stage {schema.stage}: {lf.name!r} must be a list")
            continue
        if len(items) < lf.min_items:
            errors.append(f"stage {schema.stage}: {lf.name!r} has {len(items)} item(s), need >= {lf.min_items}")
        for i, item in enumerate(items):
            if not isinstance(item, dict):
                errors.append(f"stage {schema.stage}: {lf.name}[{i}] is not a mapping")
                continue
            for key in lf.required:
                if key not in item:
                    errors.append(f"stage {schema.stage}: {lf.name}[{i}].{key} is required")
            for key, allowed in lf.enums.items():
                if key in item and item[key] not in allowed:
                    errors.append(f"stage {schema.stage}: {lf.name}[{i}].{key}={item[key]!r} not in {allowed}")

    return errors


def validate_file(stage: str, path: Path) -> list[str]:
    schema = STAGE_SCHEMAS.get(stage)
    if schema is None:
        return [f"unknown stage {stage!r}; known stages: {', '.join(sorted(STAGE_SCHEMAS))}"]
    if not path.exists():
        return [f"stage {stage}: output file not found: {path}"]
    try:
        doc = yaml.safe_load(_strip_fences(path.read_text()))
    except yaml.YAMLError as exc:
        return [f"stage {stage}: invalid YAML: {exc}"]
    if doc is None:
        return [f"stage {stage}: output file is empty"]
    return validate_doc(doc, schema)


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 2:
        print("usage: peval-validate-stage <stage> <output.yaml>", file=sys.stderr)
        return 2
    stage, file = args
    errors = validate_file(stage, Path(file))
    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        return 1
    print(f"stage {stage}: schema OK ({file})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
