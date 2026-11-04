# Run 002 public receipt

## Outcome

**RUN 002 — CONTRACT REJECTED.**

Run 002 used the frozen fixture/model/route constraints from Run 001, with `reasoning.effort = low`. This receipt records one observation only; it is not a general model evaluation.

## Public-safe request and response facts

- Prompt tokens: 1,739
- Completion tokens: 2,126
- Reasoning tokens: 512
- Total tokens: 3,865
- Visible content: 7,554 characters
- `finish_reason`: `stop`
- `native_finish_reason`: `stop`
- Reported cost: US$0.01106845
- Answer extraction: succeeded
- Retry: none
- Repair: none

## Frozen validator result

The frozen validator **failed as delivered** with:

```text
invalid JSON: Expecting value: line 1 column 1 (char 0)
```

Read-only forensic inspection established that the delivered artifact began with a Markdown fence. Removing the outer wrapper **in memory only** yielded valid JSON with the expected seven top-level fields. This inspection was not a validator pass and did not change the result: the original artifact remains rejected as delivered.

## Scope and privacy

No answer body, private reasoning, raw response body, credential, or private evaluator material is reproduced here. No retry or repair occurred. This receipt does not claim quality or human acceptance.
