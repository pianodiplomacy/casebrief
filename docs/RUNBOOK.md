# CaseBrief runbook

This runbook covers offline work, independent judge attempts, and the completed official Run 001 receipt. Run 002 is an immutable observation. Run 003 is implemented experimentally but has not been executed; separate authorization is required.

## Offline preflight

Use Python 3.10 or later. Run from the repository root:

```powershell
python -B -m unittest discover -s tests -p test_run_001_safety.py -v
python -B -m unittest discover -s tests -p test_run_002_safety.py -v
python -B -m unittest discover -s tests -p test_run_003_safety.py -v
python -B -m unittest discover -s tests -p test_validate_output.py -v
python -B -m unittest discover -s tests -p test_reviewer_view.py -v
```

Each adapter safety suite installs its audit guard before importing its adapter. Its read allow-list covers only the test and adapter source, required frozen contract/packet inputs, and narrowly named import-cache entries; `-B` prevents bytecode creation. The guards block network access, `.env`, evaluator/private evidence, and unauthorized workspace reads/writes. Tests use mocked transport and dummy credentials only. These commands do not call a model.

Generate the local pre-run State A historical reviewer:

```powershell
python -B .\src\reviewer_view.py .\benchmark\CASEBRIEF_SYNTHETIC_PACKET_001_V1.0.md > .\reviewer_state_a.html
```

`reviewer_state_a.html` is a reproducible **pre-run historical view**, not the current Run 001 status or a source artifact. It does not display the later receipt.

## Public clean-checkout and judge checklist

For a clean checkout or independent judge attempt:

1. Confirm the public frozen build contract and synthetic packet are present.
2. Run the documented offline adapter safety, validator, and Reviewer View tests.
3. Understand the documented OpenRouter/Muse Spark Open route and BaseTen pin.
4. If independently running the model, use the judge's own OpenRouter account, key, credits, and authorization. Supply the key out of band.
5. Treat any execution as a distinct independent attempt, not a reproduction of the same stochastic output or the official Run 001 receipt.

The public manufacturing manifest, private raw evidence, evaluator files, and private reasoning are not required or available for this checklist. Do not seek or inspect them.

## Implemented route and preflight

The OpenRouter/Baseten integration is implemented and offline-tested. One live Run 001 response is recorded in the [public receipt](RUN_001_RECEIPT.md); this record does not authorize another request. The adapter uses the OpenRouter Chat Completions endpoint `https://openrouter.ai/api/v1/chat/completions`, model `meta/muse-spark-open` (Meta Muse Spark Open), and pins the upstream provider to `baseten`. Its provider object is fixed to an explicit Baseten-only allow-list, `allow_fallbacks: false`, and `require_parameters: true`. It sends one user message containing the complete frozen contract before the complete synthetic packet. The request is non-streaming with `max_tokens: 4096`; `reasoning_effort` was intentionally omitted from the initial configuration. Its omission does not establish that reasoning is disabled.

Before any authorized inference:

- Confirm current endpoint/model/provider availability and the provider routing behavior from approved current evidence.
- Check the current published model/provider rate at the [OpenRouter model listing](https://openrouter.ai/meta/muse-spark-open). The planning expectation is spend well below US$1 at currently published rates, not a guaranteed cost; this patch makes no live pricing lookup, and actual cost depends on usage and account/provider terms.
- Supply `OPENROUTER_API_KEY` out of band only. Do not put credentials in source, prompts, command history, test fixtures, output, or logs.
- A dedicated API key with a finite OpenRouter credit/spend limit is recommended. Account funding is separate from expected inference cost, and neither is established by this repository.
- Confirm frozen contract and packet hashes, applicable data/IP/confidentiality terms, and the appropriate run authorization.

The 60-second timeout is local. `max_tokens: 4096`, bounded response bytes, and the local timeout do not guarantee a spend ceiling.

## Run 002 low-reasoning observation — immutable

Run 002 preserved the frozen build contract and synthetic packet and all Run 001 route/transport settings. Its sole request-variable change was `"reasoning": {"effort": "low"}`. The observed answer began with a Markdown fence; the unchanged validator failed with `invalid JSON: Expecting value: line 1 column 1 (char 0)`. Do not repair its content or represent a repaired answer as Run 002 success.

Run 002's preserved artifacts are confined to its own three named paths. Do not rerun Run 002 or modify its observation.

## Run 003 structured-output experiment — implemented, NOT EXECUTED

Run 003 holds Run 002's model, endpoint, Baseten-only route, fallback/parameter settings, low reasoning, token limit, stream setting, timeout, prompt, and capture behavior constant. Its sole request-body addition is Chat Completions `response_format` with `type: "json_schema"` and a strict schema representing the frozen CaseBrief contract. OpenRouter supports this format. Baseten documentation says Muse Spark Open accepts but does not enforce the schema, so the experiment does not assume or guarantee enforcement.

The research question is whether this request-only change causes raw visible content to pass the unchanged deterministic validator without client-side repair. The adapter is `src/run_003.py`, and its exclusive artifacts are `raw\CASEBRIEF_RUN_003_OPENROUTER_RESPONSE.raw`, `raw\CASEBRIEF_RUN_003_OPENROUTER_HTTP_ERROR.raw`, and `raw\CASEBRIEF_RUN_003_OPENROUTER_ANSWER.json`. Run 003 has **NOT BEEN EXECUTED**; offline tests do not authorize a model request. Separate authorization is required before invoking:

```powershell
python -B .\src\run_003.py
```

The Run 003 adapter has the same one-application-request boundary, redirect refusal, no-retry/no-fallback/no-repair policy, credential safeguards, and 1 MiB bounded-capture policy. It never writes to Run 001 or Run 002 paths.

## Request boundary

One attempt means exactly one application-level HTTP request made by CaseBrief. The adapter does not automatically retry, make a second request, switch models or providers, issue repair requests, or allow provider fallback. HTTP redirects are not followed, so a redirected POST is not replayed. Hosted-provider behavior internal to OpenRouter or Baseten is outside CaseBrief's request boundary and is not represented as controlled by CaseBrief.

## Independent judge attempt and official Run 001

**Independent judge attempt:** A judge may make a distinct attempt using the judge's own OpenRouter account, key, credits, and authorization. It is not a reproduction of the same stochastic output or the official receipt. After supplying `OPENROUTER_API_KEY` through an approved out-of-band environment-secret mechanism, invoke:

```powershell
python -B .\src\run_001.py
```

This independent attempt does not require Chandi's authorization and must not be presented as the official Run 001.

**Official CaseBrief Run 001:** Completed once; see the [public receipt](RUN_001_RECEIPT.md). The receipt does not authorize a retry or another official attempt.

## Capture and post-run — only for a genuine attempt

- The supplied Run 001 receipt reports one response, no retry or repair, 4,096 completion tokens including 4,093 reasoning tokens, `finish_reason: length`, and null `message.content`. Reasoning remains private. No answer artifact existed, so structural validation was not run; quality assessment and human acceptance were not performed.
- CaseBrief provides bounded byte-for-byte preservation within the approved 1 MiB capture ceiling, except that a body containing the configured credential is rejected and not written.
- An oversized or credential-bearing body is recorded as a fail-closed observation without preserving the prohibited body itself. Neither case creates an answer artifact or triggers retry, fallback, provider switching, repair, or a second request.
- A non-secret successful body within the ceiling is preserved at `raw\CASEBRIEF_RUN_001_OPENROUTER_RESPONSE.raw`; a non-secret bounded HTTP-error body is separately preserved at `raw\CASEBRIEF_RUN_001_OPENROUTER_HTTP_ERROR.raw`, using exclusive creation. An error, timeout, malformed response, redirect, or nonzero result is not permission to retry.
- After successful raw preservation, the adapter strictly decodes and parses a copy of the envelope and saves exactly `choices[0].message.content` as UTF-8 bytes at `raw\CASEBRIEF_RUN_001_OPENROUTER_ANSWER.json`. It does not trim, wrap, repair, or reserialize the answer. Extraction failure retains the raw response, returns non-zero, and creates no answer.
- Run the deterministic structural validator only when a genuine extracted answer artifact exists. For Run 001, `message.content` was null, so no answer artifact existed and structural validation was not run. For a future eligible answer:

  ```powershell
  python -B .\src\validate_output.py .\raw\CASEBRIEF_RUN_001_OPENROUTER_ANSWER.json
  ```

- Preserve the full raw envelope as source evidence. When present it may contain `id`, `model`, `provider` or `openrouter_metadata`, `system_fingerprint`, `choices[0].finish_reason`, `usage.prompt_tokens`, `usage.completion_tokens`, `usage.total_tokens`, and `usage.cost`. Missing optional metadata is **UNKNOWN / NOT PROVIDED**.
- Keep artifacts private. Conduct any separately authorized evaluation privately with frozen evaluator material; never include it in model-facing input or public release.
- **Transport success != structural validity != quality != human acceptance.** A validator result or one fixture does not establish safety, quality, human acceptance, production readiness, or general model performance.

State B remains unimplemented. Offline procedures neither create nor alter the private Run 001 evidence. Do not open or publish the private raw response or reasoning.
