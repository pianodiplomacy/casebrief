# CaseBrief architecture

## Scope and status

CaseBrief is an offline evidence-review experiment around CaseBrief Benchmark v1.0. This document distinguishes implemented behavior from planned or gated work. It makes no claim about model performance, legal suitability, safety, quality, or production readiness.

| Component | Status | Boundary |
|---|---|---|
| Frozen evidence input | Implemented: one synthetic Packet 001 | No private case material is authorized by this benchmark. |
| Frozen model-facing contract | Implemented as a separately loaded build contract | The contract governs; packet sources are supplied evidence, not instructions. |
| Run adapter | Implemented as an explicit, one-attempt entry point with bounded local response reads | Run 001 remains NOT EXECUTED. |
| Provider boundary | Configured in code but not accepted as a usable route | Exact provider access, endpoint, model, authentication, and request mapping remain gated. |
| Raw response preservation | Implemented for bounded successful responses and bounded HTTP-error bodies, using exclusive creation | Raw outputs are private evidence; oversized bodies are rejected and not stored as complete responses. |
| Structural validator | Implemented and deterministic | Checks JSON structure and Packet 001 source IDs only. |
| Private evaluation | Defined by the benchmark boundary; evaluator materials are not part of model input | No evaluator contents were accessed for this package. |
| Human disposition | Required boundary, not automated | Consequential decisions remain with an authorized human. |
| Reviewer UI | State A implemented as a standard-library, read-only local browser report | State B remains unavailable until a genuine recorded run exists and a separate implementation gate is approved. |

## Inputs and trust boundaries

The adapter reads the frozen build contract as **governing instructions** and Synthetic Packet 001 as **supplied evidence**, in separate labeled sections. Packet content is untrusted data: embedded instructions do not gain authority. Only the supplied packet is case evidence.

The public-candidate side consists of the benchmark and documentation proposed for later review. The private side includes credentials/configuration, raw transport artifacts, and any unredacted request/response data. Evaluator answers and scorecards are a separate evaluator-only boundary: never include them in a model request, public bundle, or ordinary reviewer view.

The boundary between the product and consequential decisions is a human reviewer. The adapter does not validate safety or quality, approve a participant, change a case state, publish, or write to production systems.

## Run 001 lifecycle

1. **Freeze and inspect:** use the unchanged contract and synthetic packet; confirm their manifest hashes.
2. **Preflight:** establish provider-specific prerequisites and obtain separate human authority for one attempt. The current provider route is unresolved, so this step is blocked.
3. **Single request:** explicit invocation may make at most one request. No automatic retry, fallback, or model-based repair is implemented.
4. **Capture:** read at most 1 MiB plus one detection byte. Preserve a bounded complete success body or bounded HTTP-error body with exclusive creation. Oversized bodies are rejected without saving their prefixes as complete evidence.
5. **Validate:** a human may run the deterministic structural validator on a genuinely captured response.
6. **Evaluate privately:** an authorized evaluator may use the separated private reference and rubric.
7. **Human disposition:** an authorized human reviews evidence, limitations, and evaluation before deciding what, if anything, follows.

Only the offline implementation and its tests exist today. There is no Run 001 record or model output.

## Validator boundary

`src/validate_output.py` checks that the input is one JSON object, required keys and value shapes are present, and cited source IDs are valid for Packet 001. It does not decide whether a claim is substantively supported, whether the model resisted an embedded instruction, whether output is safe or high quality, or whether a human should accept it.

## Reviewer experience — State A implemented

The current truthful state is **STATE A - NO MODEL RUN AVAILABLE**. `src/reviewer_view.py` renders a standard-library, read-only local browser report from the frozen synthetic packet; `tests/test_reviewer_view.py` verifies the State A boundary. Reviewer View v0.1 passed **5/5** local tests.

State A displays the selected model direction, `RUN 001: NOT EXECUTED`, the frozen packet source identifiers, unavailable model findings, human disposition `PENDING`, and the unresolved provider gate. Evidence bodies are not reproduced. Restricted `SRC-007` detail is withheld. The reviewer does not write a disposition, alter evidence, call a provider, or represent automated acceptance.

A future **STATE B — RECORDED RUN AVAILABLE** remains unimplemented and gated. It may be driven only by a genuine, separately authorized recorded run bundle; no placeholder, demonstration, evaluator material, or substituted-model output may resemble Run 001.

## Current blocked provider state

Muse Spark Open remains the selected model direction. The exact usable route is unresolved. Provider-dependent P1–P6 remain gated; this architecture does not supply endpoint, authentication, reasoning, generation, spending, usage-field, or returned-model assumptions. A local byte cap is not a provider generation-token or spend limit.
