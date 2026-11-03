# CaseBrief

CaseBrief is an offline harness for examining whether a supplied evidence packet supports, contradicts, or leaves claims unresolved. Benchmark v1.0 tests evidence-relative reporting on one synthetic fixture; it does not establish general model accuracy, safety, legal suitability, or production readiness.

**Current factual status:** Benchmark v1.0 is frozen. The offline structural validator passed **6/6** tests, the Run 001 adapter safety suite passed **22/22** under its controlled runner, and Reviewer View v0.1 passed **5/5** local tests. The OpenRouter/Baseten integration is implemented and offline-tested. Run 001 produced one genuine response from Meta Muse Spark Open through OpenRouter, with BaseTen returned as provider. The response ended at the length boundary with null final content; no answer artifact existed, and structural validation, quality assessment, and human acceptance were not performed. See the [public Run 001 receipt](docs/RUN_001_RECEIPT.md). Run 002 is implemented locally as a separately authorized, one-variable low-reasoning experiment derived from Run 001; it has not been executed and is not evidence that low reasoning will yield visible content. State A is the pre-run historical view; State B remains unimplemented.

## What this benchmark tests

Given only Synthetic Packet 001, distinguish supported and unsupported claims, missing evidence, contradictions, and uncertainty; cite only packet source IDs; preserve human authority; and resist instructions embedded in evidence. A passing schema check is not a safety, quality, or acceptance result.

## Offline prerequisites and checks

Use Python **3.10 or later**. The adapter and tests use the Python standard library; no package installation is required. From the repository root, run the controlled adapter suite with bytecode creation disabled, followed by the other offline suites:

```powershell
python -B -m unittest discover -s tests -p test_run_001_safety.py -v
python -B -m unittest discover -s tests -p test_run_002_safety.py -v
python -B -m unittest discover -s tests -p test_validate_output.py -v
python -B -m unittest discover -s tests -p test_reviewer_view.py -v
```

Each adapter safety suite installs its audit guard before importing its adapter. Its read allow-list covers only the test and adapter source, required frozen contract/packet inputs, and narrowly named import-cache entries; `-B` prevents bytecode creation. The guards block network access, `.env`, evaluator/private evidence, and unauthorized workspace reads/writes. Tests use mocked transport and dummy credentials only. Neither suite executes a model request. Do not treat generated example data as run evidence.

## Inspect the pre-run State A view

Generate the read-only local reviewer from the frozen synthetic packet:

```powershell
python -B .\src\reviewer_view.py .\benchmark\CASEBRIEF_SYNTHETIC_PACKET_001_V1.0.md > .\reviewer_state_a.html
```

Open `reviewer_state_a.html` in a browser. This is the **pre-run State A view**: it shows `RUN 001: NOT EXECUTED`, exposes source identifiers without evidence bodies, withholds restricted source detail, and does not display the later Run 001 receipt. It is not a current post-run view. State B remains unimplemented.

## Model route and request boundary

CaseBrief uses the genuine **Meta Muse Spark Open** model through the **OpenRouter** gateway, with upstream provider **Baseten** pinned fail-closed:

- Model ID: `meta/muse-spark-open`
- API: `https://openrouter.ai/api/v1/chat/completions`
- Provider allow-list: `baseten`; provider fallback is disabled and required-parameter enforcement is enabled.
- The request is non-streaming, has a provisional 4096-token output ceiling, and uses a 60-second local timeout.
- Run 001 omitted reasoning configuration as its initial setting; omission does not imply reasoning is disabled. Run 002 separately adds exactly `"reasoning": {"effort": "low"}` as a one-variable experiment based on Run 001. This is not a change to Run 001.

The adapter makes one application-level HTTP request: no automatic retry, redirect replay, provider/model switching, fallback, or repair request. This describes CaseBrief's request boundary only, not hosted-provider internal behavior.

## Run 002 low-reasoning experiment

Run 002 is implemented locally only after this patch and has **not** been executed. It preserves the frozen contract and synthetic packet, model, endpoint, Baseten-only route, fallback and parameter settings, token limit, stream setting, timeout, and bounded capture behavior from Run 001. The sole request-variable change is `"reasoning": {"effort": "low"}`. This one-variable experiment asks whether that supported configuration leaves enough completion budget for the frozen CaseBrief JSON answer; it is not proof that low reasoning will produce visible content. Run 002 is separately authorized from Run 001; permission to implement or test it offline does not authorize a model request.

Run 002 uses only `raw\CASEBRIEF_RUN_002_OPENROUTER_RESPONSE.raw`, `raw\CASEBRIEF_RUN_002_OPENROUTER_HTTP_ERROR.raw`, and `raw\CASEBRIEF_RUN_002_OPENROUTER_ANSWER.json`. Its adapter refuses pre-existing outputs, creates artifacts exclusively, and never writes to Run 001 paths. A Run 002 request must be separately authorized; do not execute it as part of the offline checks above.

CaseBrief provides bounded byte-for-byte preservation within the approved 1 MiB capture ceiling, except that a body containing the configured credential is rejected and not written. An oversized or credential-bearing body is recorded as a fail-closed observation without preserving the prohibited body itself. No answer artifact is created for either case, and the adapter does not retry, fall back, switch providers, repair, or issue a second request. A successful non-secret response within the ceiling is preserved at `raw\CASEBRIEF_RUN_001_OPENROUTER_RESPONSE.raw`; after raw preservation, `choices[0].message.content` is strictly extracted without rewriting to `raw\CASEBRIEF_RUN_001_OPENROUTER_ANSWER.json`. A structural validation command for a genuine extracted answer is:

```powershell
python -B .\src\validate_output.py .\raw\CASEBRIEF_RUN_001_OPENROUTER_ANSWER.json
```

Transport success is not structural validity; structural validity is not quality; quality is not human acceptance. Optional response metadata may include `id`, `model`, `provider`/`openrouter_metadata`, `system_fingerprint`, `choices[0].finish_reason`, and usage token/cost fields. Missing metadata is **UNKNOWN / NOT PROVIDED**.

## Independent judge attempt and official Run 001

For a clean checkout, confirm the public frozen build contract and synthetic packet are present, run the documented offline tests, and understand the documented provider/model route. An independent judge may then make a distinct attempt using the judge's own OpenRouter account, key, credits, and authorization. This is not a reproduction of the same stochastic output and does not replace or alter the official receipt. Do not use a private manifest, private raw evidence, evaluator files, or reasoning. Supply `OPENROUTER_API_KEY` through an approved out-of-band environment-secret mechanism; `.env.example` contains only a blank template. Before running, confirm current model/provider rates and account/key limits on the [OpenRouter model listing](https://openrouter.ai/meta/muse-spark-open); any prior planning estimate was not a guaranteed cost.

After confirming the key is available in the environment, a judge's independent reproduction command is:

```powershell
python -B .\src\run_001.py
```

This command makes one request if configuration and output paths pass preflight. A failure is not permission to retry.

The official CaseBrief Run 001 is recorded in the [public receipt](docs/RUN_001_RECEIPT.md). A judge's independent attempt is separate and must not be represented as the official attempt.

## Current status and non-goals

State B remains unavailable. The receipt is a single-run observation, not a quality evaluation, acceptance decision, or generalized model-performance result. No M2MB integration, production-system access, autonomous decisions, production-readiness claim, legal conclusion, institutional approval, customer validation, commercial-readiness claim, ROI claim, or model-performance claim is established.

**HYPOTHESIS — NOT VALIDATED:** “One scoped evidence brief accepted by an authorised human for its stated review purpose.”

## Remaining release decisions

The repository does not establish a license, public contact address, or approved roadmap commitment. These remain release decisions; none is inferred or promised here.

## Inspect the package

- [Architecture](docs/ARCHITECTURE.md) — implemented components, trust boundaries, lifecycle, and current status.
- [Evaluation method](docs/EVALUATION_METHOD.md) — validation/evaluation distinctions and private run-evidence convention.
- [Runbook](docs/RUNBOOK.md) — offline checks and separately authorized run/post-run steps.
- Run 002 low-reasoning experiment — local implementation only; not executed and separately authorized from Run 001.
- [Run 001 receipt](docs/RUN_001_RECEIPT.md) — public-safe metadata for the completed attempt; private raw response and reasoning are excluded.
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
