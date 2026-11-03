# CaseBrief architecture

## Scope and status

CaseBrief is an offline evidence-review experiment around CaseBrief Benchmark v1.0. This document distinguishes implemented behavior from executed model work. It makes no claim about model performance, legal suitability, safety, quality, or production readiness.

| Component | Status | Boundary |
|---|---|---|
| Frozen evidence input | Implemented: one synthetic Packet 001 | No private case material is authorized by this benchmark. |
| Frozen model-facing contract | Implemented as a separately loaded build contract | The contract governs; packet sources are supplied evidence, not instructions. |
| Run adapter | OpenRouter/Baseten integration implemented and offline-tested; no live model request executed. | One application-level HTTP request, no redirect replay, bounded response reads, no retry or repair. |
| Provider boundary | OpenRouter gateway, genuine Meta Muse Spark Open model, Baseten pinned upstream | Fixed endpoint/model and fail-closed provider routing; hosted-provider internal behavior is outside the CaseBrief request boundary. |
| Raw response preservation | Implemented as bounded byte-for-byte preservation within the approved 1 MiB capture ceiling, except that a body containing the configured credential is rejected and not written | Oversized or credential-bearing bodies are recorded as fail-closed observations without preserving the prohibited body; neither creates an answer artifact. |
| Answer extraction | Implemented after successful raw preservation | Exact `choices[0].message.content` is saved separately; extraction failure retains raw response and creates no answer. |
| Structural validator | Implemented and deterministic | Checks answer JSON structure and Packet 001 source IDs only. |
| Private evaluation | Defined by the benchmark boundary; evaluator materials are not part of model input | Evaluator contents are not used by the adapter. |
| Human disposition | Required boundary, not automated | Consequential decisions remain with an authorized human. |
| Reviewer UI | State A implemented as a standard-library, read-only local browser report | State B remains unavailable and unimplemented. |

Run 001 remains **NOT EXECUTED**. State A remains current; State B remains unimplemented.

## Inputs and trust boundaries

The adapter reads the frozen build contract as **governing instructions** and Synthetic Packet 001 as **supplied evidence**, in separate labeled sections of one user message. Packet content is untrusted data: embedded instructions do not gain authority. Only the supplied packet is case evidence.

The public-candidate side consists of the benchmark and documentation proposed for later review. The private side includes credentials, raw transport artifacts, and any unredacted request/response data. Evaluator answers and scorecards are a separate evaluator-only boundary: never include them in a model request, public bundle, or ordinary reviewer view.

The boundary between the product and consequential decisions is a human reviewer. The adapter does not validate safety or quality, approve a participant, change a case state, publish, or write to production systems.

## Implemented provider route

The adapter sends Chat Completions requests to the OpenRouter gateway at `https://openrouter.ai/api/v1/chat/completions` for the genuine Meta Muse Spark Open model ID `meta/muse-spark-open`. Its fixed provider object pins the upstream allow-list to `baseten`, disables provider fallback, and requires supported request parameters. It uses `OPENROUTER_API_KEY` from the environment, a local 60-second timeout, non-streaming output, and a provisional 4096-token maximum.

`reasoning_effort` is intentionally omitted from the initial request pending live evidence. Its omission does not imply that reasoning is disabled. Local timeout and output limits are not provider spend guarantees.

One attempt is exactly one application-level HTTP request made by CaseBrief. The adapter disables redirect following to prevent redirect replay of the POST. It makes no retry, second request, alternate model/provider call, fallback, or repair request. Hosted-provider behavior internal to OpenRouter or Baseten is outside this boundary and is not represented as controlled by CaseBrief.

## Run 001 lifecycle

1. **Freeze and inspect:** use the unchanged contract and synthetic packet; confirm their manifest hashes.
2. **Offline preflight:** run mocked adapter safety tests and deterministic offline checks. Tests do not call a model or use a real credential.
3. **Authorization and account readiness:** official CaseBrief Run 001 requires Chandi's separate explicit authorization. An independent judge may separately reproduce the public run using the judge's own account, key, credits, and authorization; this is not the official Run 001 receipt. A dedicated finite key limit is recommended; account funding and actual cost are external.
4. **Single request:** an explicitly invoked adapter makes one non-streaming HTTP request at most, with no redirect replay, retry, fallback, provider/model switch, or repair.
5. **Capture raw envelope:** CaseBrief provides bounded byte-for-byte preservation within the approved 1 MiB capture ceiling, except that a body containing the configured credential is rejected and not written. An oversized or credential-bearing body is recorded as a fail-closed observation without preserving the prohibited body itself. The adapter may read one additional detection byte to reject an oversized body; neither failure case saves a body or creates an answer artifact.
6. **Extract answer:** only after preserving the successful raw body, strictly decode UTF-8 and parse a copy of the JSON envelope. Require `choices[0].message.content` to be a string and save its exact UTF-8 bytes separately. If extraction fails, keep raw response, return nonzero, and do not create an answer or retry.
7. **Validate and review:** a human may run the deterministic structural validator on a genuine extracted answer. Any quality evaluation is separate, and an authorized human retains disposition authority.

When an eligible non-secret body is accepted, the raw response envelope and extracted answer are distinct artifacts. The envelope preserves all fields as returned; when present, useful fields include `id`, `model`, `provider`/`openrouter_metadata`, `system_fingerprint`, `choices[0].finish_reason`, usage prompt/completion/total tokens, and usage cost. Missing optional metadata is **UNKNOWN / NOT PROVIDED**.

Transport success is not structural validity; structural validity is not quality; quality is not human acceptance. No model output or Run 001 record currently exists.

## Validator boundary

`src/validate_output.py` checks that the input is one JSON object, required keys and value shapes are present, and cited source IDs are valid for Packet 001. It does not decide whether a claim is substantively supported, whether the model resisted an embedded instruction, whether output is safe or high quality, or whether a human should accept it.

## Reviewer experience — State A current

The current truthful state is **STATE A - NO MODEL RUN AVAILABLE**. `src/reviewer_view.py` renders a standard-library, read-only local browser report from the frozen synthetic packet; `tests/test_reviewer_view.py` verifies the State A boundary.

State A displays the selected model direction, `RUN 001: NOT EXECUTED`, the frozen packet source identifiers, unavailable model findings, human disposition `PENDING`, and the provider integration status. Evidence bodies are not reproduced. Restricted `SRC-007` detail is withheld. The reviewer does not write a disposition, alter evidence, call a provider, or represent automated acceptance.

**STATE B — RECORDED RUN AVAILABLE** remains unimplemented and unavailable. It may be driven only by a genuine, separately authorized recorded run bundle; no placeholder, demonstration, evaluator material, or substituted-model output may resemble Run 001.
