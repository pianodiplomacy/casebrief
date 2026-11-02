#!/usr/bin/env python3
"""Make one explicitly invoked Run 001 request and preserve its raw response."""

import json
import os
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


MODEL_PROVIDER = "meta"
MODEL_ID = "muse-spark-1.3"
MODEL_ENDPOINT = "https://api.meta.ai/v1/responses"
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PACKET_PATH = PROJECT_ROOT / "benchmark" / "CASEBRIEF_SYNTHETIC_PACKET_001_V1.0.md"
RAW_RESPONSE_PATH = PROJECT_ROOT / "raw" / "CASEBRIEF_RUN_001_META_RESPONSE.raw"
RAW_HTTP_ERROR_PATH = PROJECT_ROOT / "raw" / "CASEBRIEF_RUN_001_META_HTTP_ERROR.raw"
CONTRACT_PATH = PROJECT_ROOT / "benchmark" / "CASEBRIEF_BUILD_CONTRACT_V1.0.md"
OUTPUT_LIMIT_BYTES = 1_048_576
RESPONSE_READ_CHUNK_BYTES = 65_536


class OversizedResponseError(ValueError):
    def __init__(self) -> None:
        self.observed_minimum_bytes = OUTPUT_LIMIT_BYTES + 1
        super().__init__("response exceeded the local byte ceiling")


def _required_environment(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise ValueError(f"{name} must be set to a non-empty value")
    return value


def _validate_configuration() -> str:
    provider = _required_environment("MODEL_PROVIDER")
    model_id = _required_environment("MODEL_ID")
    endpoint = _required_environment("MODEL_ENDPOINT")
    api_key = _required_environment("MODEL_API_KEY")

    if provider != MODEL_PROVIDER:
        raise ValueError("MODEL_PROVIDER does not match the approved provider")
    if model_id != MODEL_ID:
        raise ValueError("MODEL_ID does not match the approved model")
    if endpoint != MODEL_ENDPOINT:
        raise ValueError("MODEL_ENDPOINT does not match the approved endpoint")
    return api_key


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


def main() -> int:
    try:
        api_key = _validate_configuration()
        if RAW_RESPONSE_PATH.exists() or RAW_HTTP_ERROR_PATH.exists():
            raise FileExistsError("Run 001 raw evidence already exists")
        contract_text = CONTRACT_PATH.read_text(encoding="utf-8")
        packet = PACKET_PATH.read_bytes()
        packet_text = packet.decode("utf-8")
    except (OSError, UnicodeDecodeError, ValueError) as error:
        print(f"Run 001 was not sent: {error}", file=sys.stderr)
        return 2

    request_body = json.dumps(
        {
            "model": MODEL_ID,
            "input": (
                "=== GOVERNING INSTRUCTIONS: FROZEN BUILD CONTRACT ===\n"
                + contract_text
                + "\n=== SUPPLIED CASE EVIDENCE: SYNTHETIC PACKET 001 ===\n"
                + packet_text
            ),
        }
    ).encode("utf-8")
    request = Request(
        MODEL_ENDPOINT,
        data=request_body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=60) as response:
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
        except (URLError, TimeoutError, OSError):
            print(
                f"HTTP error response body could not be read "
                f"(status {error.code}); no response body was preserved.",
                file=sys.stderr,
            )
            return 1
        try:
            _write_new(RAW_HTTP_ERROR_PATH, error_bytes)
        except OSError as write_error:
            print(
                f"HTTP error response could not be preserved: {write_error}",
                file=sys.stderr,
            )
            return 2
        print(
            f"HTTP error response preserved at {RAW_HTTP_ERROR_PATH.name} "
            f"(status {error.code}); no validation or evaluation was run.",
            file=sys.stderr,
        )
        return 1
    except (URLError, TimeoutError, OSError):
        print("Request failed without a preserved HTTP response.", file=sys.stderr)
        return 1

    try:
        _write_new(RAW_RESPONSE_PATH, response_bytes)
    except OSError as error:
        print(f"Raw response could not be preserved: {error}", file=sys.stderr)
        return 2

    print(
        f"Raw response preserved at {RAW_RESPONSE_PATH.name}; "
        "no validation or evaluation was run."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
