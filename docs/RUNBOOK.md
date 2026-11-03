# CaseBrief runbook

This runbook separates offline work, independent judge reproduction, and the official Run 001. It does not itself authorize the official run.

## Offline preflight

Use Python 3.10 or later. Run from the repository root:

```powershell
python -B -m unittest discover -s tests -p test_run_001_safety.py -v
python -B -m unittest discover -s tests -p test_validate_output.py -v
python -B -m unittest discover -s tests -p test_reviewer_view.py -v
```

The adapter safety suite installs its audit guard before importing `src.run_001`. Its read allow-list covers only the test and adapter source, required frozen contract/packet inputs, and narrowly named import-cache entries; `-B` prevents bytecode creation. The guard blocks network access, `.env`, evaluator/private evidence, and unauthorized workspace reads/writes. Tests use mocked transport and a dummy credential only. These commands do not call a model.

Generate the local State A reviewer:

```powershell
python -B .\src\reviewer_view.py .\benchmark\CASEBRIEF_SYNTHETIC_PACKET_001_V1.0.md > .\reviewer_state_a.html
```

`reviewer_state_a.html` is a reproducible local demonstration derivative, not a source artifact or Run 001 evidence.

For a readable frozen-artifact integrity check, compare only the two model-facing files with their manifest entries:

```powershell
$manifest = Get-Content -Raw benchmark\MANIFEST_V1.0.json | ConvertFrom-Json
foreach ($name in @('CASEBRIEF_BUILD_CONTRACT_V1.0.md', 'CASEBRIEF_SYNTHETIC_PACKET_001_V1.0.md')) {
    $entry = $manifest.files | Where-Object { $_.frozen_filename -eq $name }
    $actual = (Get-FileHash -Algorithm SHA256 "benchmark\$name").Hash
    if ($actual -ne $entry.sha256) { throw "Frozen artifact mismatch: $name" }
    "$name $actual MATCH"
}
```

Do not open evaluator files to recompute their hashes. A matching hash establishes byte integrity against the manifest, not provenance, licensing, or publication approval.

## Implemented route and preflight

The OpenRouter/Baseten integration is implemented and offline-tested only; no live model request has been executed. The adapter uses the OpenRouter Chat Completions endpoint `https://openrouter.ai/api/v1/chat/completions`, model `meta/muse-spark-open` (Meta Muse Spark Open), and pins the upstream provider to `baseten`. Its provider object is fixed to an explicit Baseten-only allow-list, `allow_fallbacks: false`, and `require_parameters: true`. It sends one user message containing the complete frozen contract before the complete synthetic packet. The request is non-streaming with `max_tokens: 4096`; `reasoning_effort` is intentionally omitted as the approved initial configuration pending live evidence. Omission does not establish that reasoning is disabled.

Before any authorized inference:

- Confirm current endpoint/model/provider availability and the provider routing behavior from approved current evidence.
- Check the current published model/provider rate at the [OpenRouter model listing](https://openrouter.ai/meta/muse-spark-open). The planning expectation is spend well below US$1 at currently published rates, not a guaranteed cost; this patch makes no live pricing lookup, and actual cost depends on usage and account/provider terms.
- Supply `OPENROUTER_API_KEY` out of band only. Do not put credentials in source, prompts, command history, test fixtures, output, or logs.
- A dedicated API key with a finite OpenRouter credit/spend limit is recommended. Account funding is separate from expected inference cost, and neither is established by this repository.
- Confirm frozen contract and packet hashes, applicable data/IP/confidentiality terms, and the appropriate run authorization.

The 60-second timeout is local. `max_tokens: 4096`, bounded response bytes, and the local timeout do not guarantee a spend ceiling.

## Request boundary

One attempt means exactly one application-level HTTP request made by CaseBrief. The adapter does not automatically retry, make a second request, switch models or providers, issue repair requests, or allow provider fallback. HTTP redirects are not followed, so a redirected POST is not replayed. Hosted-provider behavior internal to OpenRouter or Baseten is outside CaseBrief's request boundary and is not represented as controlled by CaseBrief.

## Judge reproduction and official Run 001

**Independent judge reproduction:** A judge may independently run the public adapter using the judge's own OpenRouter account, key, credits, and authorization. After supplying `OPENROUTER_API_KEY` through an approved out-of-band environment-secret mechanism, invoke:

```powershell
python -B .\src\run_001.py
```

This independent reproduction is not the official CaseBrief Run 001 receipt and does not require Chandi's authorization.

**Official CaseBrief Run 001:** Requires Chandi's separate explicit authorization. An offline test, a judge reproduction, a configured key, or a successful preflight does not grant this authorization. Run 001 remains **NOT EXECUTED** unless and until the authorized official attempt occurs.

## Capture and post-run — only for a genuine attempt

- CaseBrief provides bounded byte-for-byte preservation within the approved 1 MiB capture ceiling, except that a body containing the configured credential is rejected and not written.
- An oversized or credential-bearing body is recorded as a fail-closed observation without preserving the prohibited body itself. Neither case creates an answer artifact or triggers retry, fallback, provider switching, repair, or a second request.
- A non-secret successful body within the ceiling is preserved at `raw\CASEBRIEF_RUN_001_OPENROUTER_RESPONSE.raw`; a non-secret bounded HTTP-error body is separately preserved at `raw\CASEBRIEF_RUN_001_OPENROUTER_HTTP_ERROR.raw`, using exclusive creation. An error, timeout, malformed response, redirect, or nonzero result is not permission to retry.
- After successful raw preservation, the adapter strictly decodes and parses a copy of the envelope and saves exactly `choices[0].message.content` as UTF-8 bytes at `raw\CASEBRIEF_RUN_001_OPENROUTER_ANSWER.json`. It does not trim, wrap, repair, or reserialize the answer. Extraction failure retains the raw response, returns non-zero, and creates no answer.
- Only for a genuine captured answer, run the deterministic structural validator:

  ```powershell
  python -B .\src\validate_output.py .\raw\CASEBRIEF_RUN_001_OPENROUTER_ANSWER.json
  ```

- Preserve the full raw envelope as source evidence. When present it may contain `id`, `model`, `provider` or `openrouter_metadata`, `system_fingerprint`, `choices[0].finish_reason`, `usage.prompt_tokens`, `usage.completion_tokens`, `usage.total_tokens`, and `usage.cost`. Missing optional metadata is **UNKNOWN / NOT PROVIDED**.
- Keep artifacts private. Conduct any separately authorized evaluation privately with frozen evaluator material; never include it in model-facing input or public release.
- **Transport success != structural validity != quality != human acceptance.** A validator result or one fixture does not establish safety, quality, human acceptance, production readiness, or general model performance.

No State B or Run 001 evidence bundle is created by the offline procedures.
