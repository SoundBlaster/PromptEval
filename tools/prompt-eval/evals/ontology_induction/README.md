# Ontology Induction Suite

Evaluates the 9 prompt contracts in the SpecGraph ontology induction pipeline
(`SPECS/ontology/authoring-prompts/NN_*.prompt.md` in the Ontology repository).

Each case targets a single stage in isolation: the upstream context is a **frozen** fixture
(`fixtures/<stage>_<intent>/before/input.yaml`) so the eval measures the prompt under test,
not upstream noise.

## Primary agent and model

All runs use **GitHub Copilot CLI with GPT-5.5**:

```bash
peval run \
  --suite ontology_induction \
  --case-set tuning \
  --prompts prompts/ontology_induction/03_concept_extractor.md \
  --agent copilot \
  --model gpt-5.5 \
  --judge copilot \
  --judge-model gpt-5.5
```

The `subagent` judge (Codex CLI) is kept available for cross-engine comparison:

```bash
peval run \
  --suite ontology_induction \
  --case-set tuning \
  --prompts prompts/ontology_induction/09_yaml_assembler.md \
  --agent codex \
  --model gpt-5.5-codex-spark \
  --judge subagent \
  --judge-model gpt-5.5-codex-spark
```

## Case sets

| Set | Purpose |
|---|---|
| `tuning` | Fast iteration on a specific stage (examcalc golden intent). |
| `validation` | Held-out intents for generalization checks before accepting a prompt change. |
| `stage_03` | All Stage 03 Concept Extractor cases. |
| `stage_09` | All Stage 09 YAML Assembler cases. |

Always run `--case-set validation` before accepting a prompt change:
```bash
peval run ... --case-set validation ...
```

## Prompt source of truth

Prompt working copies live under `prompts/ontology_induction/`. After an improved prompt wins
on both `tuning` and `validation`, copy it back to the Ontology repository:

```bash
cp prompts/ontology_induction/03_concept_extractor.md \
   /path/to/0AL/Ontology/SPECS/ontology/authoring-prompts/03_ConceptExtractor.prompt.md
```

## Frozen fixtures

`fixtures/<stage>_<intent>/before/input.yaml` is the **frozen** upstream context — a reviewed
artifact from the previous pipeline stage. It is intentionally not regenerated on each run.
Updating a fixture requires a deliberate review step; document any change in a `NOTES.md` next
to the fixture.

## Deterministic checks

| Stage | Check |
|---|---|
| 01, 03, 06 | `peval-validate-stage <stage> output.yaml` — schema and enum validation |
| 09 | `peval-validate-stage 09 output.yaml` + `peval-ontologyc check output.yaml` (requires `ONTOLOGY_REPO`) |

For the `ontologyc` check, set `ONTOLOGY_REPO` to the absolute path of the Ontology repository:

```bash
export ONTOLOGY_REPO=/Users/egor/Development/GitHub/0AL/Ontology
```

## Recording results

```bash
peval record --run runs/<id> --title "stage09 v2 vs baseline, examcalc tuning"
```

Records under `records/ontology_induction/` are committed to track improvement history.
