# CaseBrief runbook

This runbook separates permitted offline work from provider-gated inference. It does not authorize a model call, create a run bundle, or provide provider configuration.

## Offline

Run from the repository root. These commands do not call a provider:

```powershell
python -B -m unittest discover -s tests -p test_validate_output.py -v
python -B -m unittest discover -s tests -p test_reviewer_view.py -v
```

The adapter safety suite is verified using its accepted controlled guarded runner. Bare `unittest` discovery is not the accepted safety-suite procedure because the restrictive audit guard must be installed with the approved import, network, protected-read, and temporary-write boundaries. Preserve the retained controlled-QC receipt: validator **6/6**, safety **15/15**, and real guard probes **5/5**. Do not publish an abbreviated runner or treat a bare-import error as a failed safety assertion.

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

### Offline review workflow

1. Confirm the contract and synthetic packet hashes.
2. Inspect the contract, packet, adapter, validator, and tests without opening evaluator material or real credentials.
3. Run the two suites independently.
4. Record test output separately from any future model evidence.
5. For a genuine captured response only, run `python -B src\validate_output.py <recorded-response-path>`. Do not invent a response to exercise the run workflow.

## Provider-gated preflight — currently blocked

All six provider gates remain unresolved:

- **P1:** approved exact endpoint and model identity.
- **P2:** documented authentication method and credential handling.
- **P3:** supported/default reasoning configuration.
- **P4:** generation-token controls and approved spend boundary.
- **P5:** provider usage, finish, and request-field mapping.
- **P6:** returned model/version metadata, where available.

Before any inference, independently confirm the benchmark's prerequisite questions: eligible model/tooling, actual access/credits, deadline/time zone, submission requirements, and applicable IP/confidentiality/data/licensing terms. Unconfirmed items remain unconfirmed. Do not fill missing provider values from examples or assumptions.

Even when these gates are resolved, a separate human decision must authorize one Run 001 attempt. Phase A acceptance is not execution authority.

## Run — only after separate authorization

- Make at most one request. Do not automatically retry, switch providers, fall back, or use another model.
- Preserve the complete bounded response or bounded HTTP-error body without rewriting it, using exclusive creation. Keep raw artifacts private.
- The adapter's 1 MiB local response cap is not a generation-token ceiling, provider timeout guarantee, or spend limit.
- An oversized response is unsuccessful; its prefix is not a complete response and is not preserved as one. Keep only the sanitized failure metadata emitted by the adapter.
- A nonzero result, timeout, malformed captured body, or provider error is not permission to retry.

No `RUN_001/` bundle is currently present or created. See the run-evidence convention in [Evaluation method](EVALUATION_METHOD.md) before any separately authorized run.

## Post-run — only for a genuine recorded attempt

1. Preserve and identify the genuine request, raw response/error, and transport metadata.
2. Run the deterministic structural validator on a captured success response. Transport capture is not structure validity.
3. Conduct any authorized evaluation privately with the frozen evaluator material. Keep it out of model-facing input and public-release candidates.
4. Have an authorized human review limitations and findings and record the disposition under a separately approved convention.
5. Do not claim safety, quality, human acceptance, production readiness, or general model performance from a validator result or one fixture.
