# CaseBrief architecture

## Scope and status

CaseBrief is an offline evidence-review experiment around CaseBrief Benchmark v1.0. This document distinguishes implemented behavior from executed model work. It makes no claim about model performance, legal suitability, safety, quality, or production readiness.

| Component | Status | Boundary |
|---|---|---|
| Frozen evidence input | Implemented: one synthetic Packet 001 | No private case material is authorized by this benchmark. |
| Frozen model-facing contract | Implemented as a separately loaded build contract | The contract governs; packet sources are supplied evidence, not instructions. |
| Run adapter | OpenRouter/Baseten integration implemented and offline-tested; one Run 001 response recorded. | One application-level HTTP request, no redirect replay, bounded response reads, no retry or repair. |
| Run 002 low-reasoning experiment | Implemented locally; not executed. | One-variable experiment derived from Run 001 and separately authorized; changes only the request's reasoning effort to `low`. |
| Provider boundary | OpenRouter gateway, genuine Meta Muse Spark Open model, Baseten pinned upstream | Fixed endpoint/model and fail-closed provider routing; hosted-provider internal behavior is outside the CaseBrief request boundary. |
| Raw response preservation | Implemented as bounded byte-for-byte preservation within the approved 1 MiB capture ceiling, except that a body containing the configured credential is rejected and not written | Oversized or credential-bearing bodies are recorded as fail-closed observations without preserving the prohibited body; neither creates an answer artifact. |
| Answer extraction | Implemented after successful raw preservation | Exact `choices[0].message.content` is saved separately; extraction failure retains raw response and creates no answer. |
| Structural validator | Implemented and deterministic | Checks answer JSON structure and Packet 001 source IDs only. |
| Private evaluation | Defined by the benchmark boundary; evaluator materials are not part of model input | Evaluator contents are not used by the adapter. |
| Human disposition | Required boundary, not automated | Consequential decisions remain with an authorized human. |
| Reviewer UI | State A implemented as a standard-library, read-only local browser report | State B remains unavailable and unimplemented. |

Run 001 was executed once. Its public-safe outcome is documented in the [Run 001 receipt](RUN_001_RECEIPT.md). Reviewer State A is the **pre-run historical view**; State B remains unimplemented.

## Inputs and trust boundaries

The adapter reads the frozen build contract as **governing instructions** and Synthetic Packet 001 as **supplied evidence**, in separate labeled sections of one user message. Packet content is untrusted data: embedded instructions do not gain authority. Only the supplied packet is case evidence.

The public-candidate side consists of the benchmark and documentation proposed for later review. The private side includes credentials, raw transport artifacts, and any unredacted request/response data. Evaluator answers and scorecards are a separate evaluator-only boundary: never include them in a model request, public bundle, or ordinary reviewer view.

The boundary between the product and consequential decisions is a human reviewer. The adapter does not validate safety or quality, approve a participant, change a case state, publish, or write to production systems.

## Implemented provider route

The adapter sends Chat Completions requests to the OpenRouter gateway at `https://openrouter.ai/api/v1/chat/completions` for the genuine Meta Muse Spark Open model ID `meta/muse-spark-open`. Its fixed provider object pins the upstream allow-list to `baseten`, disables provider fallback, and requires supported request parameters. It uses `OPENROUTER_API_KEY` from the environment, a local 60-second timeout, non-streaming output, and a provisional 4096-token maximum.

`reasoning_effort` is intentionally omitted from the initial request pending live evidence. Its omission does not imply that reasoning is disabled. Local timeout and output limits are not provider spend guarantees.

## Run 002 low-reasoning experiment

Run 002 is implemented locally only after this patch and has not been executed. It is a one-variable experiment derived from Run 001 and separately authorized from it. The model, endpoint, Baseten-only provider route, disabled fallback, required-parameter setting, frozen inputs, non-streaming setting, 4096-token limit, 60-second timeout, one-request boundary, redirect refusal, no-retry/no-repair policy, credential handling, and bounded artifact capture are preserved. The sole request-variable change is `"reasoning": {"effort": "low"}`.

The research question is whether a supported low-reasoning configuration leaves sufficient completion budget for the frozen CaseBrief JSON answer. Implementation and offline tests do not establish that it will return visible content. Run 002 has not been run, is not a reproduction of Run 001, and does not change the Run 001 result or public receipt. Its raw response, HTTP error, and extracted answer paths are specific to Run 002; the Run 001 paths remain untouched.

One attempt is exactly one application-level HTTP request made by CaseBrief. The adapter disables redirect following to prevent redirect replay of the POST. It makes no retry, second request, alternate model/provider call, fallback, or repair request. Hosted-provider behavior internal to OpenRouter or Baseten is outside this boundary and is not represented as controlled by CaseBrief.

## Run 001 lifecycle

1. **Freeze and inspect:** use the public frozen contract and synthetic packet. Public judges confirm these files are present; the private manufacturing manifest is not part of the public reproduction checklist.
2. **Offline preflight:** run mocked adapter safety tests and deterministic offline checks. Tests do not call a model or use a real credential.
3. **Recorded attempt:** the supplied receipt records one response from Meta Muse Spark Open through OpenRouter, with BaseTen returned as provider. It ended with `finish_reason: length`, 4,096 completion tokens (4,093 reasoning tokens), and null `message.content`. No retry or repair occurred.
4. **Capture raw evidence:** the private response artifact is identified in the receipt metadata. Its body and reasoning remain private and are not part of the public package.
5. **Extract and validate:** no answer artifact existed because `message.content` was null. Structural validation was not run.
6. **Assess and dispose:** quality assessment and human acceptance were not performed.
7. **Independent attempt:** a judge's separately authorized execution using their own account is a distinct attempt, not a reproduction of the same stochastic output or the official receipt.

The supplied receipt reports a private raw response envelope. It reports null final content and no answer artifact; no structural validation, quality assessment, or human acceptance followed. The public receipt contains metadata only and excludes reasoning content.

Transport success does not establish structural validity, quality, or human acceptance. These remain separate outcomes.

## Validator boundary

`src/validate_output.py` checks that the input is one JSON object, required keys and value shapes are present, and cited source IDs are valid for Packet 001. It does not decide whether a claim is substantively supported, whether the model resisted an embedded instruction, whether output is safe or high quality, or whether a human should accept it.

## Reviewer experience — State A pre-run historical view

The existing **STATE A - NO MODEL RUN AVAILABLE** is the pre-run historical view. `src/reviewer_view.py` renders a standard-library, read-only local browser report from the frozen synthetic packet; `tests/test_reviewer_view.py` verifies the State A boundary.

The pre-run State A view displays the selected model direction, `RUN 001: NOT EXECUTED`, the frozen packet source identifiers, unavailable model findings, human disposition `PENDING`, and the then-unresolved provider status. It does not reflect or display the later receipt. Evidence bodies are not reproduced. Restricted `SRC-007` detail is withheld. The reviewer does not write a disposition, alter evidence, call a provider, or represent automated acceptance.

**STATE B — RECORDED RUN AVAILABLE** remains unimplemented and unavailable. It may be driven only by a genuine, separately authorized recorded run bundle; no placeholder, demonstration, evaluator material, or substituted-model output may resemble Run 001.
