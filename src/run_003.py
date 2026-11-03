#!/usr/bin/env python3
"""Make one explicitly invoked Run 003 request and preserve its raw response."""

import json
import os
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener


MODEL_ID = "meta/muse-spark-open"
MODEL_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
PROVIDER_ID = "baseten"
LOCAL_TIMEOUT_SECONDS = 60
MAX_OUTPUT_TOKENS = 4096
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PACKET_PATH = PROJECT_ROOT / "benchmark" / "CASEBRIEF_SYNTHETIC_PACKET_001_V1.0.md"
RAW_RESPONSE_PATH = PROJECT_ROOT / "raw" / "CASEBRIEF_RUN_003_OPENROUTER_RESPONSE.raw"
RAW_HTTP_ERROR_PATH = (
    PROJECT_ROOT / "raw" / "CASEBRIEF_RUN_003_OPENROUTER_HTTP_ERROR.raw"
)
RAW_ANSWER_PATH = PROJECT_ROOT / "raw" / "CASEBRIEF_RUN_003_OPENROUTER_ANSWER.json"
CONTRACT_PATH = PROJECT_ROOT / "benchmark" / "CASEBRIEF_BUILD_CONTRACT_V1.0.md"
OUTPUT_LIMIT_BYTES = 1_048_576
RESPONSE_READ_CHUNK_BYTES = 65_536

SOURCE_ID_SCHEMA = {
    "type": "string",
    "enum": [f"SRC-{number:03d}" for number in range(1, 8)],
}
SOURCE_IDS_SCHEMA = {
    "type": "array",
    "items": SOURCE_ID_SCHEMA,
    "minItems": 1,
}
ASSESSMENT_SOURCES_SCHEMA = {
    "type": "array",
    "items": SOURCE_ID_SCHEMA,
}


def _object_schema(properties):
    return {
        "type": "object",
        "properties": properties,
        "required": list(properties),
        "additionalProperties": False,
    }


def _string_schema():
    return {"type": "string"}


def _array_schema(properties):
    return {
        "type": "array",
        "items": _object_schema(properties),
    }


CASEBRIEF_OUTPUT_SCHEMA = _object_schema(
    {
        "supported_claims": _array_schema(
            {
                "claim": _string_schema(),
                "source_ids": SOURCE_IDS_SCHEMA,
                "limitations": _string_schema(),
            }
        ),
        "unsupported_claims": _array_schema(
            {
                "claim": _string_schema(),
                "asserted_in": SOURCE_IDS_SCHEMA,
                "assessment_sources": ASSESSMENT_SOURCES_SCHEMA,
                "limitations": _string_schema(),
            }
        ),
        "missing_evidence": _array_schema(
            {
                "needed": _string_schema(),
                "related_claim": _string_schema(),
                "source_ids": SOURCE_IDS_SCHEMA,
            }
        ),
        "contradictions": _array_schema(
            {
                "description": _string_schema(),
                "source_ids": SOURCE_IDS_SCHEMA,
                "resolution": _string_schema(),
            }
        ),
        "uncertainty": _array_schema(
            {
                "description": _string_schema(),
                "source_ids": SOURCE_IDS_SCHEMA,
                "reason": _string_schema(),
            }
        ),
        "proposed_next_action": _object_schema(
            {
                "action": _string_schema(),
                "source_ids": SOURCE_IDS_SCHEMA,
                "limitations": _string_schema(),
            }
        ),
        "evidence_references": _array_schema(
            {
                "source_id": SOURCE_ID_SCHEMA,
                "relevance": _string_schema(),
            }
        ),
    }
)
RESPONSE_FORMAT = {
    "type": "json_schema",
    "json_schema": {
        "name": "casebrief_evidence_brief",
        "strict": True,
        "schema": CASEBRIEF_OUTPUT_SCHEMA,
    },
}


class OversizedResponseError(ValueError):
    def __init__(self) -> None:
        self.observed_minimum_bytes = OUTPUT_LIMIT_BYTES + 1
        super().__init__("response exceeded the local byte ceiling")


class NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, new_url):
        return None


def _validate_configuration() -> str:
    value = os.environ.get("OPENROUTER_API_KEY")
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or value == "******"
        or any(ord(character) < 32 or ord(character) == 127 for character in value)
    ):
        raise ValueError("OPENROUTER_API_KEY is invalid.")
    return value


def _write_new(path: Path, content: bytes) -> None:
    with path.open("xb") as evidence_file:
        evidence_file.write(content)


def _read_bounded(response) -> bytes:
    chunks = []
    total_bytes = 0
    while total_bytes <= OUTPUT_LIMIT_BYTES:
        read_size = min(
            RESPONSE_READ_CHUNK_BYTES,
            OUTPUT_LIMIT_BYTES + 1 - total_bytes,
        )
        chunk = response.read(read_size)
        if not chunk:
            return b"".join(chunks)
        chunks.append(chunk)
        total_bytes += len(chunk)
        if total_bytes > OUTPUT_LIMIT_BYTES:
            raise OversizedResponseError()
    raise OversizedResponseError()


def _report_oversized_response(category: str, error: OversizedResponseError) -> None:
    print(
        f"{category} response rejected: configured cap={OUTPUT_LIMIT_BYTES} "
        f"bytes; observed at least {error.observed_minimum_bytes} bytes. "
        "No response body was preserved, parsed, or validated.",
        file=sys.stderr,
    )


def _contains_credential(content: bytes, api_key: str) -> bool:
    return api_key.encode("utf-8") in content


def _extract_answer(response_bytes: bytes) -> bytes:
    response_text = response_bytes.decode("utf-8", errors="strict")
    response_object = json.loads(response_text)
    if not isinstance(response_object, dict):
        raise ValueError("response envelope must be a JSON object")
    choices = response_object.get("choices")
    if not isinstance(choices, list) or not choices:
        raise ValueError("response envelope must contain a non-empty choices list")
    first_choice = choices[0]
    if not isinstance(first_choice, dict):
        raise ValueError("choices[0] must be an object")
    message = first_choice.get("message")
    if not isinstance(message, dict):
        raise ValueError("choices[0].message must be an object")
    content = message.get("content")
    if not isinstance(content, str):
        raise ValueError("choices[0].message.content must be a string")
    return content.encode("utf-8", errors="strict")


def main() -> int:
    try:
        api_key = _validate_configuration()
    except ValueError:
        print("Run 003 was not sent: OPENROUTER_API_KEY is invalid.", file=sys.stderr)
        return 2

    try:
        RAW_RESPONSE_PATH.parent.mkdir(parents=True, exist_ok=True)
        if any(
            path.exists()
            for path in (RAW_RESPONSE_PATH, RAW_HTTP_ERROR_PATH, RAW_ANSWER_PATH)
        ):
            raise FileExistsError("Run 003 raw evidence already exists")
        contract_text = CONTRACT_PATH.read_text(encoding="utf-8")
        packet = PACKET_PATH.read_bytes()
        packet_text = packet.decode("utf-8")
    except (OSError, UnicodeDecodeError):
        print("Run 003 preflight failed; no request was sent.", file=sys.stderr)
        return 2

    try:
        request_body = json.dumps(
            {
                "model": MODEL_ID,
                "messages": [
                    {
                        "role": "user",
                        "content": (
                            "=== GOVERNING INSTRUCTIONS: FROZEN BUILD CONTRACT ===\n"
                            + contract_text
                            + "\n=== SUPPLIED CASE EVIDENCE: SYNTHETIC PACKET 001 ===\n"
                            + packet_text
                        ),
                    }
                ],
                "stream": False,
                "max_tokens": MAX_OUTPUT_TOKENS,
                "provider": {
                    "only": [PROVIDER_ID],
                    "allow_fallbacks": False,
                    "require_parameters": True,
                },
                "reasoning": {"effort": "low"},
                "response_format": RESPONSE_FORMAT,
            },
            ensure_ascii=True,
        ).encode("utf-8")
        request = Request(
            MODEL_ENDPOINT,
            data=request_body,
            headers={
                "Authorization": f"******",
                "Content-Type": "application/json",
            },
            method="POST",
        )
    except (TypeError, ValueError, UnicodeError):
        print("Run 003 request construction failed; no request was sent.", file=sys.stderr)
        return 2

    try:
        opener = build_opener(NoRedirectHandler())
        with opener.open(request, timeout=LOCAL_TIMEOUT_SECONDS) as response:
            response_bytes = _read_bounded(response)
    except OversizedResponseError as error:
        _report_oversized_response("Successful", error)
        return 1
    except HTTPError as error:
        try:
            error_bytes = _read_bounded(error)
        except OversizedResponseError as oversized_error:
            _report_oversized_response(
                f"HTTP error (status {error.code})", oversized_error
            )
            return 1
        except (URLError, TimeoutError, OSError, ValueError, TypeError):
            print(
                f"HTTP error response body could not be read "
                f"(status {error.code}); no response body was preserved.",
                file=sys.stderr,
            )
            return 1
        if _contains_credential(error_bytes, api_key):
            print(
                "HTTP error response contained the configured credential; "
                "the body was not preserved.",
                file=sys.stderr,
            )
            return 1
        try:
            _write_new(RAW_HTTP_ERROR_PATH, error_bytes)
        except OSError:
            print(
                "HTTP error response could not be preserved.",
                file=sys.stderr,
            )
            return 2
        print(
            f"HTTP error response preserved at {RAW_HTTP_ERROR_PATH.name} "
            f"(status {error.code}); no validation or evaluation was run.",
            file=sys.stderr,
        )
        return 1
    except (URLError, TimeoutError, OSError, ValueError, TypeError):
        print("Request failed without a preserved HTTP response.", file=sys.stderr)
        return 1

    if _contains_credential(response_bytes, api_key):
        print(
            "Successful response contained the configured credential; "
            "the body and answer were not preserved.",
            file=sys.stderr,
        )
        return 1

    try:
        _write_new(RAW_RESPONSE_PATH, response_bytes)
    except OSError:
        print("Raw response could not be preserved.", file=sys.stderr)
        return 2

    try:
        answer_bytes = _extract_answer(response_bytes)
    except (UnicodeError, ValueError):
        print(
            f"Raw response preserved at {RAW_RESPONSE_PATH.name}; "
            "answer extraction failed. No retry or repair was attempted.",
            file=sys.stderr,
        )
        return 1

    if _contains_credential(answer_bytes, api_key):
        print(
            "Extracted answer contained the configured credential; "
            "the answer was not preserved.",
            file=sys.stderr,
        )
        return 1

    try:
        _write_new(RAW_ANSWER_PATH, answer_bytes)
    except OSError:
        print(
            "Raw response preserved, but extracted answer could not be preserved.",
            file=sys.stderr,
        )
        return 2

    print(
        f"Raw response preserved at {RAW_RESPONSE_PATH.name}; "
        f"extracted answer preserved at {RAW_ANSWER_PATH.name}. "
        "No validation or evaluation was run."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
