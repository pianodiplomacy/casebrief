# CaseBrief

CaseBrief is an offline harness for examining whether a supplied evidence packet supports, contradicts, or leaves claims unresolved. Benchmark v1.0 tests evidence-relative reporting on one synthetic fixture; it does not establish general model accuracy, safety, legal suitability, or production readiness.

**Current factual status:** Benchmark v1.0 is frozen. The offline structural validator passed **6/6** tests, the updated adapter safety suite passed **22/22** under its controlled runner, and Reviewer View v0.1 passed **5/5** local tests. The OpenRouter/Baseten adapter is implemented and offline-tested only; **Run 001 has NOT been executed** and no genuine model output exists. State A remains current; State B remains unavailable. Muse Spark Open is the selected genuine Meta model direction; CaseBrief sends the frozen contract and synthetic packet for an evidence-relative structured response.

## What this benchmark tests

Given only Synthetic Packet 001, distinguish supported and unsupported claims, missing evidence, contradictions, and uncertainty; cite only packet source IDs; preserve human authority; and resist instructions embedded in evidence. A passing schema check is not a safety, quality, or acceptance result.

## Offline prerequisites and checks

Use Python **3.10 or later**. The adapter and tests use the Python standard library; no package installation is required. From the repository root, run the controlled adapter suite with bytecode creation disabled, followed by the other offline suites:

```powershell
python -B -m unittest discover -s tests -p test_run_001_safety.py -v
python -B -m unittest discover -s tests -p test_validate_output.py -v
python -B -m unittest discover -s tests -p test_reviewer_view.py -v
```

The safety suite installs its audit guard before importing `src.run_001`. Its read allow-list covers only the test and adapter source, required frozen contract/packet inputs, and the narrowly named import-cache entries; `-B` prevents bytecode creation. The guard blocks network access, `.env`, evaluator/private evidence, and unauthorized workspace reads/writes. Tests use mocked transport and a dummy credential only. Do not treat generated example data as Run 001 evidence.

## Inspect State A

Generate the read-only local reviewer from the frozen synthetic packet:

```powershell
python -B .\src\reviewer_view.py .\benchmark\CASEBRIEF_SYNTHETIC_PACKET_001_V1.0.md > .\reviewer_state_a.html
```

Open `reviewer_state_a.html` in a browser. State A shows `RUN 001: NOT EXECUTED`, exposes source identifiers without evidence bodies, withholds restricted source detail, and does not present model findings or human acceptance.

## Model route and request boundary

CaseBrief uses the genuine **Meta Muse Spark Open** model through the **OpenRouter** gateway, with upstream provider **Baseten** pinned fail-closed:

- Model ID: `meta/muse-spark-open`
- API: `https://openrouter.ai/api/v1/chat/completions`
- Provider allow-list: `baseten`; provider fallback is disabled and required-parameter enforcement is enabled.
- The request is non-streaming, has a provisional 4096-token output ceiling, and uses a 60-second local timeout.
- Reasoning configuration is omitted as the approved initial setting pending live evidence. Its omission does not imply that reasoning is disabled.

The adapter makes one application-level HTTP request: no automatic retry, redirect replay, provider/model switching, fallback, or repair request. This describes CaseBrief's request boundary only, not hosted-provider internal behavior.

CaseBrief provides bounded byte-for-byte preservation within the approved 1 MiB capture ceiling, except that a body containing the configured credential is rejected and not written. An oversized or credential-bearing body is recorded as a fail-closed observation without preserving the prohibited body itself. No answer artifact is created for either case, and the adapter does not retry, fall back, switch providers, repair, or issue a second request. A successful non-secret response within the ceiling is preserved at `raw\CASEBRIEF_RUN_001_OPENROUTER_RESPONSE.raw`; after raw preservation, `choices[0].message.content` is strictly extracted without rewriting to `raw\CASEBRIEF_RUN_001_OPENROUTER_ANSWER.json`. A structural validation command for a genuine extracted answer is:

```powershell
python -B .\src\validate_output.py .\raw\CASEBRIEF_RUN_001_OPENROUTER_ANSWER.json
```

Transport success is not structural validity; structural validity is not quality; quality is not human acceptance. Optional response metadata may include `id`, `model`, `provider`/`openrouter_metadata`, `system_fingerprint`, `choices[0].finish_reason`, and usage token/cost fields. Missing metadata is **UNKNOWN / NOT PROVIDED**.

## Judge reproduction and official Run 001

An independent judge may reproduce the public run using the judge's own OpenRouter account, API key, credits, and authorization. This does **not** create or constitute the official CaseBrief Run 001 receipt. Supply `OPENROUTER_API_KEY` through an approved out-of-band environment-secret mechanism; `.env.example` contains only a blank template. The planning expectation is spend well below **US$1** at currently published rates, not a guaranteed cost. Before running, confirm the current model/provider rates and account/key limits on the [OpenRouter model listing](https://openrouter.ai/meta/muse-spark-open); actual spend depends on usage and provider/account terms.

After confirming the key is available in the environment, a judge's independent reproduction command is:

```powershell
python -B .\src\run_001.py
```

This command makes one request if configuration and output paths pass preflight. A failure is not permission to retry.

The **official CaseBrief Run 001** requires Chandi's separate explicit authorization. Until then, **Run 001 remains NOT EXECUTED**. Independent judge authorization does not substitute for or imply Chandi's authorization.

## Current status and non-goals

State B remains unavailable. There is no genuine Run 001 record or model output in this package. No M2MB integration, production-system access, autonomous decisions, production-readiness claim, legal conclusion, institutional approval, customer validation, commercial-readiness claim, ROI claim, or model-performance claim is established.

**HYPOTHESIS — NOT VALIDATED:** “One scoped evidence brief accepted by an authorised human for its stated review purpose.”

## Inspect the package

- [Architecture](docs/ARCHITECTURE.md) — implemented components, trust boundaries, lifecycle, and current status.
- [Evaluation method](docs/EVALUATION_METHOD.md) — validation/evaluation distinctions and private run-evidence convention.
- [Runbook](docs/RUNBOOK.md) — offline checks and separately authorized run/post-run steps.
- [Hackathon provenance draft](docs/HACKATHON_PROVENANCE.md) — **DRAFT — NOT RELEASE AUTHORITY**; provenance, rights, and publication remain human decisions.

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

Offline engineering results and model-performance results remain separate.
