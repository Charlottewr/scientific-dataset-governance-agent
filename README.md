# Scientific Dataset Discovery and Metadata Governance Agent

An evidence-first portfolio prototype for discovering, normalizing, classifying and reviewing public scientific datasets before integration into a downstream metadata platform.

The project turns heterogeneous source records into reviewable JSON recommendations containing:

- normalized metadata and field-level provenance;
- domain, phenotype, omics layer, format and access classification;
- duplicate and version signals;
- explainable GenEngine compatibility checks;
- confidence, evidence, rationale and information gaps;
- explicit routing to automatic acceptance, human review or rejection.

> Status: capstone prototype in active development. The included records are synthetic examples that resemble public-source metadata; they are not exported research datasets.

## Why this design

The architecture borrows product ideas, not code, from established open-source ecosystems:

- OpenMetadata: quality, provenance, lifecycle and governance context;
- FAIR Data Point: findable and interoperable metadata exposed to humans and software agents;
- Data.gov harvesting: separation between source adapters and the searchable catalog;
- auditable AI evaluation pipelines: low-confidence and disputed cases are routed to people.

The prototype stays deliberately small so every recommendation is reproducible and interview-ready.

## Pipeline

```text
approved source record
        |
        v
normalize fields and retain evidence
        |
        v
classify domain / phenotype / omics / format / access
        |
        v
detect duplicates and versions
        |
        v
run GenEngine compatibility rules
        |
        v
score confidence and route to human review
        |
        v
integration-ready JSON
```

## Quick start

### Core pipeline

```bash
python -m dataset_agent.cli \
  --input data/sample_datasets.json \
  --output data/output/recommendations.json
```

### Tests

```bash
python -m unittest discover -s tests -v
```

### API

```bash
pip install -r requirements.txt
uvicorn dataset_agent.api:app --reload
```

Open `http://127.0.0.1:8000/docs` for the Swagger interface.

### Docker

```bash
docker build -t dataset-governance-agent .
docker run --rm -p 8000:8000 dataset-governance-agent
```

## Example decision

```json
{
  "confidence": 0.833,
  "decision": "human_review",
  "rationale": [
    "Compatibility score=1.000",
    "Evidence records=2",
    "Possible duplicate detected (metadata_similarity, score=1.00)"
  ],
  "compatibility": {
    "compatible": true,
    "passed_rules": [
      "Stable source identifier present",
      "Core descriptive metadata present",
      "Domain classified",
      "At least one supported distribution format",
      "Access status resolved",
      "Field-level provenance evidence retained"
    ]
  }
}
```

## Repository structure

```text
dataset_agent/
  normalize.py       # schema harmonization and evidence capture
  classify.py        # transparent rule-based classification
  deduplicate.py     # stable-ID and metadata similarity checks
  compatibility.py   # explainable GenEngine rules
  recommend.py       # confidence and review routing
  pipeline.py        # orchestration
  api.py             # FastAPI endpoint
data/
  sample_datasets.json
tests/
  test_pipeline.py
```

## Roadmap

- [ ] Live adapters for NCBI GEO, dbGaP and other approved sources
- [ ] Scheduled monitoring and metadata change events
- [ ] Reviewer queue with approve/reject/needs-information actions
- [ ] Version lineage and before/after metadata diffs
- [ ] JSON Schema export and contract validation
- [ ] Evaluation dashboard: coverage, duplicate rate, confidence calibration and review agreement
- [ ] Optional semantic similarity model behind an auditable adapter
- [ ] SQLite persistence and immutable audit log

## Responsible use

This tool recommends whether metadata is ready for integration; it does not decide scientific validity, participant privacy, consent compliance or data-use authorization. Controlled-access datasets always remain subject to their source repository's policies and human review.


