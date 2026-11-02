# CaseBrief

CaseBrief is an offline harness for examining whether a supplied evidence packet supports, contradicts, or leaves claims unresolved. Benchmark v1.0 tests evidence-relative reporting on one synthetic fixture; it does not establish general model accuracy, safety, legal suitability, or production readiness.

**Current factual status:** Benchmark v1.0 is frozen. The offline structural validator passed **6/6** tests; the Phase A adapter safety suite passed **15/15** under its accepted controlled runner; and Reviewer View v0.1 passed **5/5** local tests. **Run 001 has NOT been executed** and no model output exists. **Muse Spark Open is the selected Meta model direction**; the exact usable provider route remains unresolved. The workspace contains a frozen synthetic benchmark, a one-attempt adapter, a deterministic structural validator, offline tests, and an implemented read-only State A reviewer. Their hackathon-period provenance is not independently established; see the draft provenance record.

## What this benchmark tests

Given only Synthetic Packet 001, distinguish supported and unsupported claims, missing evidence, contradictions, and uncertainty; cite only packet source IDs; preserve human authority; and resist instructions embedded in evidence. A passing schema check is not a safety, quality, or acceptance result.

## Offline checks

From the repository root, run the validator and Reviewer View suites separately:

```powershell
python -B -m unittest discover -s tests -p test_validate_output.py -v
python -B -m unittest discover -s tests -p test_reviewer_view.py -v
```

The adapter safety suite requires the accepted controlled guarded runner described in the runbook and its retained QC receipt. Bare `unittest` discovery is not the accepted procedure for that suite.

Validate a recorded JSON response only when one genuinely exists:

```powershell
python -B src\validate_output.py path\to\recorded-response.json
```

These commands do not call a model. Do not treat generated example data or a test fixture as Run 001 evidence.

## Inspect State A

Generate the read-only local reviewer from the frozen synthetic packet:

```powershell
python -B .\src\reviewer_view.py .\benchmark\CASEBRIEF_SYNTHETIC_PACKET_001_V1.0.md > .\reviewer_state_a.html
```

Open `reviewer_state_a.html` in a browser. The generated HTML is a reproducible local demonstration derivative and is excluded from the release candidate. State A shows `RUN 001: NOT EXECUTED`, exposes source identifiers without evidence bodies, withholds restricted source detail, and does not present model findings or human acceptance.

## Current gate

Provider activation is blocked pending P1–P6 evidence and separate human authority for a single Run 001 attempt. Do not configure credentials, call a provider, retry, fall back, or repair model output as part of this offline harness.

## Inspect the package

- [Architecture](docs/ARCHITECTURE.md) — implemented components, trust boundaries, lifecycle, and current block.
- [Evaluation method](docs/EVALUATION_METHOD.md) — validation/evaluation distinctions and private run-evidence convention.
- [Runbook](docs/RUNBOOK.md) — offline checks and separately gated provider/run/post-run steps.
- [Hackathon provenance draft](docs/HACKATHON_PROVENANCE.md) — **DRAFT — NOT RELEASE AUTHORITY**; provenance, rights, and publication remain human decisions.

## Non-goals

No M2MB integration, production-system access, autonomous decisions, production-readiness claim, legal conclusion, institutional approval, customer validation, commercial-readiness claim, ROI claim, or model-performance claim is established by this package.

**HYPOTHESIS — NOT VALIDATED:** “One scoped evidence brief accepted by an authorised human for its stated review purpose.”

## Hackathon build disclosure

CaseBrief includes a small pre-existing foundation and substantial work completed during the Meta Global AI Developer Hackathon.

### Pre-existing foundation

`benchmark/CASEBRIEF_BUILD_CONTRACT_V1.0.md` was authored on October 25, 2026, before the hackathon building period. Its later freezing, integration, hashing, testing, and use are not represented as new hackathon authorship.

### Built during the hackathon

Recorded hackathon-period development includes:

- the bounded Run 001 adapter in `src/run_001.py`;
- provider-independent adapter safety corrections;
- the offline safety regression harness in `tests/test_run_001_safety.py`;
- the read-only State A Reviewer View in `src/reviewer_view.py`;
- Reviewer View tests in `tests/test_reviewer_view.py`;
- substantial README, architecture, evaluation-method, and runbook work.

Some supporting artifacts have uncertain original creation timing and are not claimed as newly created hackathon work without stronger evidence.

### Current execution status

CaseBrief V1-A currently provides an offline reviewer package.

Run 001 has **NOT EXECUTED**. No genuine Muse Spark Open model result is included in this release candidate. The reviewer exposes that absence rather than substituting another model or fabricating findings.

Offline engineering results and model-performance results remain separate.
