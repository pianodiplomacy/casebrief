# CaseBrief Five-Gate Architecture v1.0

## Purpose and status

CaseBrief is being developed as evidence-control infrastructure between AI output and consequential human decisions. Its doctrine is **Evidence before confidence. Human authority stays human.** This implementation demonstrates selected controls on one frozen synthetic fixture; it is not a general evidence-review service.

**Inference success ≠ artifact readiness ≠ contract validity ≠ evidence sufficiency ≠ human authorisation.**

| Gate | Meaning | Current implementation |
|---|---|---|
| 1. Execution | A request is made within explicit execution boundaries. | Controls are implemented at demonstrated scope for the bounded provider route and tested adapters. |
| 2. Artifact | A usable final answer artifact is actually available. | Bounded response capture and extraction are implemented at demonstrated scope; transport success alone is not artifact readiness. |
| 3. Contract | The artifact satisfies deterministic structural requirements. | The frozen validator is implemented and deterministic at demonstrated scope. |
| 4. Evidence | The artifact's claims are adequately supported by the relevant workflow evidence. | Workflow-specific evidence review is human-led / proposed; this is not a proven automated evidence-review service. |
| 5. Human Authority | An authorised person decides whether to accept or act. | Final authority remains human; CaseBrief does not make the consequential decision. |

A human may stop or review at any gate. Passing one gate does not imply passing a later gate.

## Demonstrated components and boundaries

- **Input:** one frozen model-facing build contract and Synthetic Packet 001. The packet is supplied evidence, not instructions; embedded instructions do not gain authority.
- **Provider integration:** a bounded adapter route for Meta Muse Spark Open through OpenRouter with Baseten pinned upstream. These adapters do not establish support for every model, provider, or workflow.
- **Execution controls:** one application-level request per attempt; no automatic retry, redirect replay, provider/model switching, fallback, or repair request. These controls describe the application boundary, not hosted-provider internal behavior.
- **Artifacts:** bounded capture and answer extraction are implemented at demonstrated scope. Private raw response artifacts and reasoning are not public evidence.
- **Contract validation:** `src/validate_output.py` checks JSON structure and Packet 001 source IDs. It does not determine truth, evidence sufficiency, safety, quality, or acceptability.
- **Evidence review and authority:** evidence sufficiency is not automatically determined; consequential decisions remain with a human.
- **Reviewer View:** `src/reviewer_view.py` renders the historical pre-run State A view. State B is not implemented and is not implied by the run receipts.

## Recorded observations

- [Run 001](RUN_001_RECEIPT.md): genuine response; final content was null, so no answer artifact existed and structural validation was not run.
- [Run 002](RUN_002_RECEIPT.md): the delivered artifact was rejected by the frozen validator. In-memory forensic inspection was not a validator pass.
- [Run 003](RUN_003_RECEIPT.md): authentication-related HTTP 401; no model result or answer artifact. The structured-output hypothesis was not tested.

These are individual observations, not general model-performance findings. The [evaluation method](EVALUATION_METHOD.md) distinguishes structural validation from evidence review and human disposition.

## Historical Reviewer View

The existing State A output is explicitly a **pre-run historical view**. It displays `RUN 001: NOT EXECUTED` and historical route status; it does not reflect or display the later Run 001 receipt. That historical text and the State A test are intentionally preserved.

**State B — recorded run available — is not implemented.** No placeholder, demonstration, evaluator material, or substituted-model output should be presented as State B or as a Run 001 result.
