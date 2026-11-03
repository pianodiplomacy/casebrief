# Evaluation method

## Benchmark v1.0 scope

Benchmark v1.0 is a frozen, single-fixture experiment: Synthetic Packet 001 and its frozen output contract test evidence-relative claims, source references, uncertainty, untrusted evidence instructions, and human authority. A successful result on this fixture is an observation about this fixture only. It does not establish general model accuracy or performance on another packet, provider, or task.

## Separate stages; do not collapse verdicts

1. **Transport capture completed:** a bounded response body was received and exclusively preserved. This does not imply valid JSON or a successful review. For Run 001, the supplied receipt reports a private raw response and no extracted answer artifact.
2. **Structure valid:** the deterministic validator accepts one JSON object with required schema structure and packet source IDs. This does not establish safety, substantive correctness, or quality.
3. **Safety assessed:** a separate review checks critical failure conditions, including invented evidence/source IDs, obedience to embedded instructions, unsupported production-readiness claims, and unauthorized consequential decisions. Structural validity is not a safety result.
4. **Quality assessed:** a reviewer assesses evidence-relative accuracy, limitations, uncertainty, and usefulness. Safety does not establish quality.
5. **Human disposition:** an authorized human decides whether the brief is acceptable for the stated review purpose. Neither schema validity nor safety/quality observations transfer that authority to the system.

Thus: transport capture ≠ structure validity ≠ safety ≠ quality ≠ human acceptance. A bounded malformed body such as `not-json` can be captured with adapter exit status 0; that means capture completed, not that any later stage passed.

## Run 001 and future attempts

Run 001 was executed once, as recorded in the [public receipt](RUN_001_RECEIPT.md). The supplied metadata reports no retry or repair. The receipt does not authorize another request. Any future inference is a separate attempt requiring its own authorization; there is no automatic retry, fallback provider, or model-based repair. A failed or ambiguous transport is not permission to send another request.

For Run 001, `message.content` was null and no answer artifact existed. Structural validation was not run; quality assessment and human acceptance were not performed. Transport success does not establish structural validity, quality, or human acceptance.

The adapter's local response-byte ceiling bounds reading and storage only. It does not constrain provider generation tokens, provider-side timeout behavior, or spend.

## Deterministic validation

`src/validate_output.py` parses a single JSON object, checks required top-level keys and structural types, and checks Packet 001 source-ID integrity. The validator is offline and deterministic for a given input. It does not score safety, quality, truth, or acceptability.

## Private evaluator separation

The reference answer and scorecard are evaluator-only. They must remain private, must not be sent to a model, and must not be placed in a public candidate bundle. Evaluation is performed only after genuine response capture and structural validation, by an authorized evaluator using the frozen materials. This document does not reproduce or summarize evaluator contents.

## UNKNOWN and evidence-relative handling

Use an unresolved/unknown disposition when supplied evidence is missing, ambiguous, conflicting, or insufficient. Absence of evidence is not evidence of absence; missing evidence alone does not establish falsity. Do not invent a source, turn uncertainty into certainty, or interpret an unverified claim as established fact.

## Reproducibility limits

The public frozen packet, contract, and deterministic validator support repeatable local structural checks. The supplied Run 001 receipt identifies one private raw response artifact; it has no answer artifact or structural validation result because `message.content` was null. Do not infer the existence of other request, transport, or evaluation artifacts. Any future independent provider attempt may vary with provider implementation/version, request interpretation, generation behavior, and runtime conditions; it is not reproduction of the same stochastic output.

One fixture and one attempt cannot support a generalized `pass@1` claim. Such language would imply a defined population of tasks/trials and an estimate over that population; this benchmark provides neither. Report only fixture-specific observations and keep any performance statement within the observed evidence.

## Proposed private run-evidence convention

Do not create or publish an additional `RUN_001/` bundle as part of this public receipt. The following remains a convention for a separately authorized future run; the supplied Run 001 receipt identifies a private raw response, and its body must remain private:

| Artifact | Role | Release classification |
|---|---|---|
| `run.json` | Run identity, timestamps, benchmark/adapter identifiers, and hashes of associated artifacts; exclude secrets | PRIVATE |
| `request.json` | Exact submitted request for audit/reproduction; protect credentials and sensitive request data | PRIVATE |
| `response.raw` | Unmodified bounded successful response, if eligible for preservation | PRIVATE |
| `error.raw` | Unmodified bounded HTTP-error body when present instead of `response.raw`, if eligible for preservation | PRIVATE |
| `transport.json` | Sanitized status, timing, outcome, byte count, cap, and transport-failure metadata | PRIVATE pending review |
| `validation.json` | Validator version, input hash, result, and structural errors | PUBLIC-CANDIDATE only after sanitization and explicit human release review; otherwise PRIVATE |
| `evaluation.json` | Evaluator-only scoring/notes tied to the private reference and rubric | EVALUATOR-ONLY; never include in public bundle or model request |

Exactly one of `response.raw` or `error.raw` may be present for an eligible captured HTTP outcome. A transport failure, oversized response, or credential-bearing body may have neither. Do not move or reinterpret existing files to match this proposed convention.
