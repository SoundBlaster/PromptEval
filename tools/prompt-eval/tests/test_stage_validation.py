import textwrap
from prompt_eval.ontology.validate_stage import validate_file, main


def _write(tmp_path, name, text):
    p = tmp_path / name
    p.write_text(textwrap.dedent(text))
    return p


def test_stage_01_valid(tmp_path):
    p = _write(
        tmp_path,
        "out.yaml",
        """
        kind: IntentClassification
        intentType: ProductCreationIntent
        domain: education
        subdomain: assessment
        productType: app
        criticality: high
        primaryConcern: exam integrity
        requiresExistingOntology: false
        uncertainties: []
        confidence: 0.7
        """,
    )
    assert validate_file("01", p) == []


def test_stage_01_bad_enum_and_missing_key(tmp_path):
    p = _write(
        tmp_path,
        "out.yaml",
        """
        kind: IntentClassification
        intentType: NotAType
        domain: education
        subdomain: assessment
        productType: app
        criticality: severe
        primaryConcern: x
        requiresExistingOntology: false
        confidence: 0.7
        """,
    )
    errors = validate_file("01", p)
    assert any("intentType" in e for e in errors)
    assert any("criticality" in e for e in errors)
    assert any("uncertainties" in e for e in errors)


def test_stage_03_metaclass_enum_and_min_items(tmp_path):
    p = _write(
        tmp_path,
        "out.yaml",
        """
        kind: CandidateConceptSet
        concepts:
          - id: c1
            label: Exam Policy Profile
            metaClass: NotAMetaClass
            rationale: governs allowed calculator behavior
            confidence: 0.8
        """,
    )
    errors = validate_file("03", p)
    assert any("metaClass" in e for e in errors)


def test_stage_03_emitting_package_is_rejected(tmp_path):
    p = _write(
        tmp_path,
        "out.yaml",
        """
        kind: DomainOntologyPackage
        concepts: []
        """,
    )
    errors = validate_file("03", p)
    assert any("later-stage artifact" in e for e in errors)


def test_stage_09_requires_package_kind(tmp_path):
    p = _write(
        tmp_path,
        "out.yaml",
        """
        kind: ProductOntologyDraft
        apiVersion: ontology.specgraph.io/v1alpha1
        metadata: {id: x, namespace: x, version: 0.1.0}
        spec: {}
        """,
    )
    errors = validate_file("09", p)
    assert any("expected kind='DomainOntologyPackage'" in e for e in errors)


def test_strips_markdown_fence(tmp_path):
    p = _write(
        tmp_path,
        "out.yaml",
        """
        ```yaml
        kind: CandidateConceptSet
        concepts:
          - id: c1
            label: A
            metaClass: DomainEntity
            rationale: r
            confidence: 0.5
        ```
        """,
    )
    assert validate_file("03", p) == []


def test_main_exit_codes(tmp_path, capsys):
    good = _write(
        tmp_path,
        "good.yaml",
        """
        kind: CandidateConceptSet
        concepts:
          - id: c1
            label: A
            metaClass: Actor
            rationale: r
            confidence: 0.5
        """,
    )
    assert main(["03", str(good)]) == 0
    assert main(["03", str(tmp_path / "missing.yaml")]) == 1
    assert main(["99", str(good)]) == 1
    assert main(["03"]) == 2
