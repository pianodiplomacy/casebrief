# CaseBrief judge and developer runbook

This runbook is an offline inspection path. It does not authorize or perform inference.

## Judge path

1. Read the [Five-Gate Architecture](ARCHITECTURE.md).
2. Inspect the frozen [Synthetic Packet 001](../benchmark/CASEBRIEF_SYNTHETIC_PACKET_001_V1.0.md) and [build contract](../benchmark/CASEBRIEF_BUILD_CONTRACT_V1.0.md).
3. Run all five offline test suites below.
4. Read the public-safe [Run 001](RUN_001_RECEIPT.md), [Run 002](RUN_002_RECEIPT.md), and [Run 003](RUN_003_RECEIPT.md) receipts.
5. Optionally inspect `src/run_001.py`, `src/run_002.py`, and `src/run_003.py`; do not execute them for this offline path.
6. Read the [prior-work disclosure](../README.md#prior-work-disclosure) and the [scope limits](../README.md#scope-and-limitations).

Private evidence, raw response bodies, evaluator material, and private reasoning are not needed for this path and must not be sought or published.

## Offline prerequisites and tests

Use Python 3.10 or later from the repository root. No package installation is required. Run:

```powershell
python -B -m unittest discover -s tests -p test_run_001_safety.py -v
python -B -m unittest discover -s tests -p test_run_002_safety.py -v
python -B -m unittest discover -s tests -p test_run_003_safety.py -v
python -B -m unittest discover -s tests -p test_validate_output.py -v
python -B -m unittest discover -s tests -p test_reviewer_view.py -v
```

In the release-candidate repository state, these suites passed **22/22**, **19/19**, **15/15**, **6/6**, and **5/5**, respectively (**67/67 total**). They are offline engineering tests, not model-quality or production-readiness results. Adapter tests use mocked transport and do not call a model. Each adapter safety suite installs its audit guard before importing its adapter; `-B` disables bytecode creation.

## Historical Reviewer View

To render the read-only historical State A view from the synthetic packet:

```powershell
python -B .\src\reviewer_view.py .\benchmark\CASEBRIEF_SYNTHETIC_PACKET_001_V1.0.md > .\reviewer_state_a.html
```

The generated view is explicitly pre-run: `RUN 001: NOT EXECUTED` is historical text, not the current run status. It does not display the later receipt. State B has not been implemented.

## Run observations and safety boundary

The three public-safe receipts document the recorded outcomes without publishing answer bodies, private reasoning, raw response bodies, credentials, or private error content:

- [Run 001 — Artifact Absent](RUN_001_RECEIPT.md)
- [Run 002 — Contract Rejected](RUN_002_RECEIPT.md)
- [Run 003 — Operational Failure](RUN_003_RECEIPT.md)

The recorded observations are not permission to rerun an experiment. Do not execute an adapter as part of judging or offline testing. Never place secrets, private reasoning, customer or confidential case evidence, or evaluator material in source, tests, prompts, public receipts, or logs. Do not silently repair an artifact before scoring or delegate a consequential decision to the system.
