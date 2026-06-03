# Ontology Induction Rubric

Derived from `SPECS/ontology/ontology-quality-rubric.md` in the Ontology repository.

Scale: 0 = reject-level | 1 = weak, major revision | 2 = acceptable | 3 = strong, ready.

## Criteria

| Criterion | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| `domain_framing` | Surface product noun only | Domain roughly identified | Deep domain frame identified | Deep frame plus governing concept identified |
| `concept_coverage` | Only entities | Entities and actors | Entities, actors, capabilities, commands, events | Full model includes states, policies, invariants, risks, evidence |
| `behavioral_modeling` | No behavior | Some actions listed | Commands/events present | State machines and lifecycle transitions included |
| `policy_modeling` | No policies | Implicit rules only | Explicit rules | Rules are enforceable, testable, and linked to concepts/events |
| `trust_evidence` | No evidence | Audit mentioned vaguely | Evidence concepts included | Evidence requirements and verification paths modeled |
| `uncertainty_handling` | Overconfident | Some assumptions marked | Unclear points marked | Clarification questions link to affected concepts |
| `implementation_leakage` | UI/config/code dominates | Some leakage | Mostly domain-focused | Clean domain/implementation boundary |
| `relation_quality` | Generic links only | Some domain verbs | Typed meaningful relations | Relations support competency questions and retrieval |
| `competency_questions` | None | Generic questions | Questions cover some concepts | Questions test policy, lifecycle, evidence, and relation paths |
| `yaml_readiness` | Cannot map to schema | Requires major schema interpretation | Mostly maps to schema | Maps cleanly to `DomainOntologyPackage` |

## Hard Reject Criteria

Reject if any condition is true:
- Ontology contains only nouns and no behavior.
- No governing concept in a domain that clearly has one.
- Policies missing in a policy/security/trust/compliance-heavy domain.
- States/lifecycles missing for lifecycle-heavy entities.
- Implementation details modeled as domain core without justification.
- No competency questions generated.
- No uncertainty or assumptions marked.
- Generated ontology contradicts explicit user intent.
- Regulatory/legal/institutional/medical claims invented as facts.
- YAML assembly requires unsupported `DomainOntologyPackage` fields.

## Expected Baseline for ExamCalc

```yaml
examcalc_expected_score:
  domain_framing: 3       # ExamPolicyProfile as governing concept, deep domain identified
  concept_coverage: 3     # entities, capabilities, commands, events, policies, evidence
  behavioral_modeling: 2  # commands+events present; state machine lifecycle modeled
  policy_modeling: 3      # 4 explicit enforceable policies
  trust_evidence: 3       # AuditLogEntry + EvidenceRequirement, verification paths
  uncertainty_handling: 2 # assumptions listed; clarification questions from intent
  implementation_leakage: 3 # clean: no screens/buttons/endpoints as core concepts
  relation_quality: 3     # typed relations, all resolve, support competency questions
  competency_questions: 3 # CQ-001..CQ-004 test policy, lifecycle, evidence, relations
  yaml_readiness: 3       # authentic package passes ontologyc check
```
