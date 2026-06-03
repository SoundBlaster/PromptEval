from __future__ import annotations
from dataclasses import dataclass, field

# Lightweight, deterministic schema definitions for the per-stage prompt-contract outputs of
# the SpecGraph ontology induction pipeline (SPECS/ontology/authoring-prompts/NN_*.prompt.md).
#
# These intentionally mirror the "Output Schema" section of each contract. They are NOT a full
# JSON-schema: they assert the structural invariants that are cheap to check and that catch the
# most common prompt failures (wrong `kind`, missing required keys, invalid enum values, and
# emitting a later-stage artifact too early). Semantic quality is left to the LLM judge.

META_CLASSES = [
    "Actor",
    "DomainEntity",
    "ValueObject",
    "Capability",
    "Command",
    "Event",
    "Policy",
    "Invariant",
    "Risk",
    "EvidenceRequirement",
]
INTENT_TYPES = [
    "ProductCreationIntent",
    "FeatureIntent",
    "ChangeIntent",
    "ClarificationIntent",
    "EvidenceIntent",
    "ArchitectureIntent",
    "PolicyIntent",
]
CRITICALITY = ["low", "medium", "high"]
EXCLUDED_REASONS = ["implementation_leakage", "duplicate", "too_vague", "unsupported_by_intent"]


@dataclass
class ListField:
    """A list-valued field whose items must each carry `required` keys and obey `enums`."""

    name: str
    required: list[str] = field(default_factory=list)
    enums: dict[str, list[str]] = field(default_factory=dict)
    min_items: int = 0


@dataclass
class StageSchema:
    stage: str
    kind: str  # expected value of the top-level discriminator (`kind` or, for stage 09, `kind`)
    required: list[str] = field(default_factory=list)
    enums: dict[str, list[str]] = field(default_factory=dict)  # top-level scalar -> allowed values
    nested_required: dict[str, list[str]] = field(default_factory=dict)  # dotted path -> required keys
    nested_enums: dict[str, list[str]] = field(default_factory=dict)  # dotted path -> allowed values
    list_fields: list[ListField] = field(default_factory=list)
    forbid_kinds: list[str] = field(default_factory=list)  # artifact kinds that must NOT appear here


STAGE_SCHEMAS: dict[str, StageSchema] = {
    "01": StageSchema(
        stage="01",
        kind="IntentClassification",
        required=[
            "intentType",
            "domain",
            "subdomain",
            "productType",
            "criticality",
            "primaryConcern",
            "requiresExistingOntology",
            "uncertainties",
            "confidence",
        ],
        enums={"intentType": INTENT_TYPES, "criticality": CRITICALITY},
        forbid_kinds=["DomainOntologyPackage", "ProductOntologyDraft", "CandidateConceptSet"],
    ),
    "03": StageSchema(
        stage="03",
        kind="CandidateConceptSet",
        required=["concepts"],
        list_fields=[
            ListField(
                name="concepts",
                required=["id", "label", "metaClass", "rationale", "confidence"],
                enums={"metaClass": META_CLASSES},
                min_items=1,
            ),
            ListField(name="excludedCandidates", required=["id", "reason"], enums={"reason": EXCLUDED_REASONS}),
        ],
        forbid_kinds=["DomainOntologyPackage", "ProductOntologyDraft"],
    ),
    "06": StageSchema(
        stage="06",
        kind="ProductOntologyDraft",
        required=["schemaVersion", "metadata", "spec"],
        nested_required={
            "metadata": ["status", "sourceIntentId", "producedBy", "confidence"],
            # namespaceCandidate, protocols, and validationNotes are required by the stage 06
            # contract's Output Schema (06_OntologySynthesizer.prompt.md). Including them here
            # ensures the validator catches drafts that silently omit these sections.
            "spec": [
                "namespaceCandidate",
                "governingConcept",
                "classes",
                "relations",
                "protocols",
                "policies",
                "stateMachines",
                "assumptions",
                "validationNotes",
            ],
        },
        nested_enums={"metadata.status": ["candidate"]},
        forbid_kinds=["DomainOntologyPackage"],
    ),
    "09": StageSchema(
        stage="09",
        kind="DomainOntologyPackage",
        required=["apiVersion", "kind", "metadata", "spec"],
        nested_required={"metadata": ["id", "namespace", "version"]},
        forbid_kinds=["ProductOntologyDraft", "CandidateConceptSet"],
    ),
}
