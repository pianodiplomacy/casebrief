# CaseBrief

**Evidence before confidence. Human authority stays human.**

CaseBrief is being developed as evidence-control infrastructure between AI output and consequential human decisions. This release candidate demonstrates bounded execution controls, artifact handling, and deterministic contract validation on one frozen synthetic fixture. It does not establish general model quality, automated evidence sufficiency, or production readiness.

## Five-Gate Architecture v1.0

**Inference success ≠ artifact readiness ≠ contract validity ≠ evidence sufficiency ≠ human authorisation.**

1. **Execution** — bounded request controls are implemented at demonstrated scope.
2. **Artifact** — bounded artifact capture and extraction are implemented at demonstrated scope.
3. **Contract** — deterministic structural validation is implemented at demonstrated scope.
4. **Evidence** — workflow-specific evidence review is human-led / proposed, not a proven automated service.
5. **Human Authority** — final authority remains human.

A human may stop or review at any gate. See the [architecture](docs/ARCHITECTURE.md).

## What happened

- **RUN 001 — ARTIFACT ABSENT.** A genuine Meta Muse Spark Open response came through OpenRouter; BaseTen was the returned provider. Final content was null; `finish_reason` was `length`; usage reported 4,093 reasoning tokens of 4,096 completion tokens and US$0.01944095. One request; no retry or repair. Structural validation was not run because no final-answer artifact existed. See the [Run 001 receipt](docs/RUN_001_RECEIPT.md).
- **RUN 002 — CONTRACT REJECTED.** With `reasoning.effort = low`, visible content was returned: 512 reasoning tokens, 2,126 completion tokens, 7,554 visible characters, `finish_reason: stop`, and reported cost US$0.01106845. The frozen validator rejected the delivered artifact: `invalid JSON: Expecting value: line 1 column 1 (char 0)`. Read-only inspection found an outer Markdown fence; removing it in memory yielded valid JSON with the expected seven top-level fields. That was not a validator pass: the original remains rejected as delivered. No retry or repair. See the [Run 002 receipt](docs/RUN_002_RECEIPT.md).
- **RUN 003 — OPERATIONAL FAILURE.** HTTP 401, classified as authentication-related. No model result, answer artifact, or validation. No retry or repair. The structured-output hypothesis was not tested. See the [Run 003 receipt](docs/RUN_003_RECEIPT.md).

**Inspect:** start with the [architecture](docs/ARCHITECTURE.md), [synthetic fixture](benchmark/CASEBRIEF_SYNTHETIC_PACKET_001_V1.0.md), [offline tests](#offline-tests), and three receipts above; adapters are optional reading, not to be executed.

## Judge quickstart

1. Understand the [Five-Gate Architecture](docs/ARCHITECTURE.md).
2. Inspect the frozen [synthetic fixture](benchmark/CASEBRIEF_SYNTHETIC_PACKET_001_V1.0.md).
3. Run the five [offline test suites](#offline-tests).
4. Read the [Run 001](docs/RUN_001_RECEIPT.md), [Run 002](docs/RUN_002_RECEIPT.md), and [Run 003](docs/RUN_003_RECEIPT.md) public-safe receipts.
5. Optionally inspect [`src/run_001.py`](src/run_001.py), [`src/run_002.py`](src/run_002.py), and [`src/run_003.py`](src/run_003.py) without executing them. Offline tests do not make inference requests.
6. Read the [prior-work disclosure](#prior-work-disclosure).
7. Review [what CaseBrief does not claim](#scope-and-limitations).

Judges do not need private evidence, raw responses, or reasoning to understand this project.

## Offline tests

Use Python 3.10 or later from the repository root. These commands run offline only; do not run the inference adapters as part of this quickstart.

```powershell
python -B -m unittest discover -s tests -p test_run_001_safety.py -v
python -B -m unittest discover -s tests -p test_run_002_safety.py -v
python -B -m unittest discover -s tests -p test_run_003_safety.py -v
python -B -m unittest discover -s tests -p test_validate_output.py -v
python -B -m unittest discover -s tests -p test_reviewer_view.py -v
```

Verified in this repository state: Run 001 safety **22/22**; Run 002 safety **19/19**; Run 003 safety **15/15**; validator **6/6**; Reviewer View **5/5**. **Total: 67/67.** These are offline engineering tests, not model-quality or production-readiness results. Adapter tests use mocked transport and do not call a model.

## Prior-work disclosure

`benchmark/CASEBRIEF_BUILD_CONTRACT_V1.0.md` was authored on **October 25, 2026**, before the hackathon building period. It is pre-existing foundation and is not represented as newly authored during the hackathon.

Repository history records event-period implementation in dated November 2–3, 2026 commits, including the V1-A offline Reviewer View, bounded Run 001 route and safety work, Run 001 receipt publication, and Run 002/003 experiment adapters and tests. This disclosure follows repository history and does not claim uncertain supporting artifacts as newly created during the event.

## Scope and limitations

This is one synthetic fixture and a small set of run observations. CaseBrief does not claim general model quality, safety, legal suitability, production readiness, institutional approval, customer validation, support for every model or workflow, or autonomous consequential decision-making. A valid schema is not evidence sufficiency, quality, or human acceptance. State A is a historical pre-run view; State B has not been implemented.

## Project documents

- [Architecture](docs/ARCHITECTURE.md)
- [Runbook and offline judge path](docs/RUNBOOK.md)
- [Evaluation method](docs/EVALUATION_METHOD.md)
- [Frozen build contract](benchmark/CASEBRIEF_BUILD_CONTRACT_V1.0.md)
- [Apache License 2.0](LICENSE)
- [Contributing safely](CONTRIBUTING.md)
