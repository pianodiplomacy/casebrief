#!/usr/bin/env python3
"""Offline structural validator for CaseBrief Benchmark Packet 001."""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


REQUIRED_KEYS = (
    "supported_claims",
    "unsupported_claims",
    "missing_evidence",
    "contradictions",
    "uncertainty",
    "proposed_next_action",
    "evidence_references",
)
ARRAY_KEYS = (
    "supported_claims",
    "unsupported_claims",
    "missing_evidence",
    "contradictions",
    "uncertainty",
    "evidence_references",
)
VALID_SOURCE_IDS = {f"SRC-{number:03d}" for number in range(1, 8)}
SOURCE_ID_PATTERN = re.compile(r"\bSRC-[A-Za-z0-9_-]+\b")


class DuplicateKeyError(ValueError):
    """Raised when a JSON object repeats a key."""


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _collect_source_ids(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, dict):
        for key, nested_value in value.items():
            _collect_source_ids(nested_value, f"{path}.{key}", errors)
    elif isinstance(value, list):
        for index, nested_value in enumerate(value):
            _collect_source_ids(nested_value, f"{path}[{index}]", errors)
    elif isinstance(value, str):
        for source_id in SOURCE_ID_PATTERN.findall(value):
            if source_id not in VALID_SOURCE_IDS:
                errors.append(f"{path}: invalid source ID {source_id}")


def _require_source_ids(
    item: dict[str, Any], field: str, path: str, errors: list[str]
) -> None:
    source_ids = item.get(field)
    if (
        not isinstance(source_ids, list)
        or not source_ids
        or any(not isinstance(source_id, str) for source_id in source_ids)
    ):
        errors.append(f"{path}.{field}: expected a non-empty array of source IDs")


def validate_output_text(text: str) -> list[str]:
    """Return structural validation errors; an empty list means schema-valid."""
    try:
        output = json.loads(text, object_pairs_hook=_unique_object)
    except (json.JSONDecodeError, DuplicateKeyError) as error:
        return [f"invalid JSON: {error}"]

    if not isinstance(output, dict):
        return ["output must be one JSON object"]

    errors = []
    for key in REQUIRED_KEYS:
        if key not in output:
            errors.append(f"missing required top-level key: {key}")

    for key in ARRAY_KEYS:
        if key in output and not isinstance(output[key], list):
            errors.append(f"{key}: expected an array")

    if "proposed_next_action" in output:
        action = output["proposed_next_action"]
        if not isinstance(action, dict) or action is None:
            errors.append("proposed_next_action: expected one non-null object")
        else:
            _require_source_ids(
                action, "source_ids", "proposed_next_action", errors
            )

    item_requirements = {
        "supported_claims": "source_ids",
        "unsupported_claims": "asserted_in",
        "missing_evidence": "source_ids",
        "uncertainty": "source_ids",
    }
    for section, required_field in item_requirements.items():
        items = output.get(section)
        if isinstance(items, list):
            for index, item in enumerate(items):
                path = f"{section}[{index}]"
                if not isinstance(item, dict):
                    errors.append(f"{path}: expected an object")
                    continue
                _require_source_ids(item, required_field, path, errors)

    for section in ("contradictions", "evidence_references"):
        items = output.get(section)
        if isinstance(items, list):
            for index, item in enumerate(items):
                if not isinstance(item, dict):
                    errors.append(f"{section}[{index}]: expected an object")

    _collect_source_ids(output, "$", errors)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "input",
        nargs="?",
        type=Path,
        help="JSON file to validate; reads standard input when omitted",
    )
    args = parser.parse_args()

    try:
        text = args.input.read_text(encoding="utf-8") if args.input else sys.stdin.read()
    except OSError as error:
        print(f"could not read input: {error}", file=sys.stderr)
        return 2

    errors = validate_output_text(text)
    if errors:
        print("Schema invalid:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Schema valid (structure and source IDs only; safety and quality not evaluated).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
