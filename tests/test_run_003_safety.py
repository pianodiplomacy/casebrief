import contextlib
import importlib
import io
import json
import os
import socket
import sys
import tempfile
import unittest
import urllib.request
from pathlib import Path
from unittest.mock import Mock, patch
from urllib.error import HTTPError, URLError


PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEMP_ROOT = Path(tempfile.gettempdir()).resolve()
ALLOWED_WORKSPACE_READS = {
    (PROJECT_ROOT / relative).resolve()
    for relative in (
        "src/run_001.py",
        "src/run_002.py",
        "src/run_003.py",
        "src/validate_output.py",
        "tests/test_run_003_safety.py",
        "benchmark/CASEBRIEF_BUILD_CONTRACT_V1.0.md",
        "benchmark/CASEBRIEF_SYNTHETIC_PACKET_001_V1.0.md",
    )
}
SAFE_IMPORT_CACHES = {
    (PROJECT_ROOT / "src" / "__pycache__").resolve(): (
        "run_001.",
        "run_002.",
        "run_003.",
        "validate_output.",
    ),
    (PROJECT_ROOT / "tests" / "__pycache__").resolve(): "test_run_003_safety.",
}


def _is_allowed_import_cache_read(path):
    prefixes = SAFE_IMPORT_CACHES.get(path.parent)
    if prefixes is None or path.suffix != ".pyc":
        return False
    if isinstance(prefixes, str):
        prefixes = (prefixes,)
    return path.name.startswith(prefixes)


def _resolved_path(value):
    if not isinstance(value, (str, bytes, os.PathLike)):
        return None
    try:
        return Path(value).resolve()
    except (OSError, TypeError, ValueError):
        return None


def _is_within(path, parent):
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def _deny_network(event, arguments):
    if event.startswith("socket."):
        raise RuntimeError(f"Offline test guard blocked network access: {event}")

    if event == "open" and arguments:
        path = _resolved_path(arguments[0])
        mode = arguments[1] if len(arguments) > 1 else None
        flags = (
            arguments[2]
            if len(arguments) > 2 and isinstance(arguments[2], int)
            else 0
        )
        writing = (
            isinstance(mode, str) and any(character in mode for character in "wax+")
        ) or bool(
            flags
            & (
                os.O_WRONLY
                | os.O_RDWR
                | os.O_CREAT
                | os.O_TRUNC
                | os.O_APPEND
            )
        )
        if path is not None and _is_within(path, PROJECT_ROOT):
            if writing:
                raise RuntimeError("Offline test guard blocked workspace writes")
            if (
                path not in ALLOWED_WORKSPACE_READS
                and not _is_allowed_import_cache_read(path)
            ):
                raise RuntimeError(
                    "Offline test guard blocked unauthorized workspace reads"
                )
        elif path is not None and writing and not _is_within(path, TEMP_ROOT):
            raise RuntimeError(
                "Offline test guard blocked writes outside temporary storage"
            )

    if event in {
        "os.mkdir",
        "os.remove",
        "os.rmdir",
        "os.rename",
        "os.replace",
        "os.chmod",
        "os.chown",
        "os.link",
        "os.symlink",
    }:
        for value in arguments[:2]:
            path = _resolved_path(value)
            if path is not None and (
                _is_within(path, PROJECT_ROOT) or not _is_within(path, TEMP_ROOT)
            ):
                raise RuntimeError(
                    "Offline test guard blocked filesystem mutation outside "
                    "temporary storage"
                )


sys.addaudithook(_deny_network)

run_001 = importlib.import_module("src.run_001")
run_002 = importlib.import_module("src.run_002")
run_003 = importlib.import_module("src.run_003")
validate_output = importlib.import_module("src.validate_output")

DUMMY_CREDENTIAL = "dummy-openrouter-key-for-run-003-offline-tests"
DUMMY_ENVIRONMENT = {"OPENROUTER_API_KEY": DUMMY_CREDENTIAL}
RUN_001_OUTPUT_NAMES = (
    "CASEBRIEF_RUN_001_OPENROUTER_RESPONSE.raw",
    "CASEBRIEF_RUN_001_OPENROUTER_HTTP_ERROR.raw",
    "CASEBRIEF_RUN_001_OPENROUTER_ANSWER.json",
)
RUN_002_OUTPUT_NAMES = (
    "CASEBRIEF_RUN_002_OPENROUTER_RESPONSE.raw",
    "CASEBRIEF_RUN_002_OPENROUTER_HTTP_ERROR.raw",
    "CASEBRIEF_RUN_002_OPENROUTER_ANSWER.json",
)
RUN_003_OUTPUT_NAMES = (
    "CASEBRIEF_RUN_003_OPENROUTER_RESPONSE.raw",
    "CASEBRIEF_RUN_003_OPENROUTER_HTTP_ERROR.raw",
    "CASEBRIEF_RUN_003_OPENROUTER_ANSWER.json",
)


def _valid_output():
    return {
        "supported_claims": [],
        "unsupported_claims": [],
        "missing_evidence": [],
        "contradictions": [],
        "uncertainty": [],
        "proposed_next_action": {
            "action": "Request evidence.",
            "source_ids": ["SRC-001"],
            "limitations": "Advisory only.",
        },
        "evidence_references": [],
    }


def _envelope(content="mock answer"):
    return json.dumps(
        {
            "id": "mock-completion-id",
            "model": run_003.MODEL_ID,
            "provider": run_003.PROVIDER_ID,
            "choices": [{"message": {"content": content}, "finish_reason": "stop"}],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 2,
                "total_tokens": 12,
            },
        },
        separators=(",", ":"),
    ).encode("utf-8")


class _MockResponse:
    def __init__(self, content=b"", headers=None):
        self.content = content
        self.headers = headers or {}
        self.read_sizes = []
        self.total_bytes_read = 0

    def __enter__(self):
        return self

    def __exit__(self, *_arguments):
        return False

    def read(self, size=-1):
        self.read_sizes.append(size)
        if size < 0:
            result = self.content[self.total_bytes_read :]
        else:
            result = self.content[self.total_bytes_read : self.total_bytes_read + size]
        self.total_bytes_read += len(result)
        return result

    def close(self):
        pass


class Run003SafetyTests(unittest.TestCase):
    def _temporary_paths(self, directory):
        run_003.RAW_RESPONSE_PATH = Path(directory) / RUN_003_OUTPUT_NAMES[0]
        run_003.RAW_HTTP_ERROR_PATH = Path(directory) / RUN_003_OUTPUT_NAMES[1]
        run_003.RAW_ANSWER_PATH = Path(directory) / RUN_003_OUTPUT_NAMES[2]

    def _successful_attempt(self, content=None, environment=None):
        with tempfile.TemporaryDirectory() as directory:
            self._temporary_paths(directory)
            response_body = _envelope() if content is None else content
            response = _MockResponse(response_body)
            opener = Mock()
            opener.open.return_value = response
            opener.factory_mock = Mock(return_value=opener)
            attempt_environment = (
                DUMMY_ENVIRONMENT if environment is None else environment
            )
            with (
                patch.dict(os.environ, attempt_environment, clear=True),
                patch.object(run_003, "build_opener", opener.factory_mock),
                contextlib.redirect_stdout(io.StringIO()) as stdout,
                contextlib.redirect_stderr(io.StringIO()) as stderr,
            ):
                result = run_003.main()
            saved_response = (
                run_003.RAW_RESPONSE_PATH.read_bytes()
                if run_003.RAW_RESPONSE_PATH.exists()
                else None
            )
            saved_answer = (
                run_003.RAW_ANSWER_PATH.read_bytes()
                if run_003.RAW_ANSWER_PATH.exists()
                else None
            )
            return (
                result,
                opener,
                response,
                saved_response,
                saved_answer,
                run_003.RAW_HTTP_ERROR_PATH.exists(),
                stdout.getvalue(),
                stderr.getvalue(),
            )

    def test_request_changes_only_response_format_from_run_002(self):
        answer = json.dumps(_valid_output(), separators=(",", ":"))
        (
            result,
            opener,
            _response,
            saved_response,
            saved_answer,
            _http_error_saved,
            stdout,
            stderr,
        ) = self._successful_attempt(_envelope(answer))
        self.assertEqual(result, 0)
        opener.open.assert_called_once()
        opener.factory_mock.assert_called_once()
        self.assertIsInstance(
            opener.factory_mock.call_args.args[0], run_003.NoRedirectHandler
        )
        request = opener.open.call_args.args[0]
        self.assertEqual(request.full_url, run_002.MODEL_ENDPOINT)
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(opener.open.call_args.kwargs, {"timeout": 60})
        self.assertEqual(run_003.MODEL_ID, run_002.MODEL_ID)
        self.assertEqual(run_003.MODEL_ENDPOINT, run_002.MODEL_ENDPOINT)
        self.assertEqual(run_003.PROVIDER_ID, "baseten")
        self.assertEqual(run_003.LOCAL_TIMEOUT_SECONDS, 60)
        self.assertEqual(run_003.MAX_OUTPUT_TOKENS, 4096)
        self.assertEqual(request.get_header("Authorization"), f"******")

        request_body = json.loads(request.data.decode("utf-8"))
        prompt = request_body["messages"][0]["content"]
        response_format = request_body.pop("response_format")
        self.assertEqual(response_format, run_003.RESPONSE_FORMAT)
        self.assertEqual(response_format["type"], "json_schema")
        self.assertEqual(
            response_format["json_schema"]["name"], "casebrief_evidence_brief"
        )
        self.assertIs(response_format["json_schema"]["strict"], True)
        self.assertEqual(
            request_body,
            {
                "model": run_002.MODEL_ID,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                "max_tokens": 4096,
                "provider": {
                    "only": ["baseten"],
                    "allow_fallbacks": False,
                    "require_parameters": True,
                },
                "reasoning": {"effort": "low"},
            },
        )
        self.assertNotIn("reasoning_effort", request_body)
        contract = run_003.CONTRACT_PATH.read_text(encoding="utf-8")
        packet = run_003.PACKET_PATH.read_text(encoding="utf-8")
        self.assertIn(contract, prompt)
        self.assertIn(packet, prompt)
        self.assertLess(
            prompt.index("=== GOVERNING INSTRUCTIONS: FROZEN BUILD CONTRACT ==="),
            prompt.index("=== SUPPLIED CASE EVIDENCE: SYNTHETIC PACKET 001 ==="),
        )
        self.assertNotIn(DUMMY_CREDENTIAL, request.data.decode("utf-8"))
        self.assertNotIn(DUMMY_CREDENTIAL, stdout + stderr)
        self.assertNotIn(DUMMY_CREDENTIAL.encode("utf-8"), saved_response)
        self.assertNotIn(DUMMY_CREDENTIAL.encode("utf-8"), saved_answer)

    def test_schema_matches_all_frozen_contract_fields_and_shapes(self):
        schema = run_003.CASEBRIEF_OUTPUT_SCHEMA
        properties = schema["properties"]
        self.assertEqual(tuple(properties), validate_output.REQUIRED_KEYS)
        self.assertEqual(schema["required"], list(validate_output.REQUIRED_KEYS))
        self.assertIs(schema["additionalProperties"], False)
        self.assertEqual(
            set(properties),
            {
                "supported_claims",
                "unsupported_claims",
                "missing_evidence",
                "contradictions",
                "uncertainty",
                "proposed_next_action",
                "evidence_references",
            },
        )
        expected_nested_fields = {
            "supported_claims": {"claim", "source_ids", "limitations"},
            "unsupported_claims": {
                "claim",
                "asserted_in",
                "assessment_sources",
                "limitations",
            },
            "missing_evidence": {"needed", "related_claim", "source_ids"},
            "contradictions": {"description", "source_ids", "resolution"},
            "uncertainty": {"description", "source_ids", "reason"},
            "proposed_next_action": {"action", "source_ids", "limitations"},
            "evidence_references": {"source_id", "relevance"},
        }
        for field, expected_fields in expected_nested_fields.items():
            field_schema = properties[field]
            if field == "proposed_next_action":
                item_schema = field_schema
            else:
                self.assertEqual(field_schema["type"], "array")
                item_schema = field_schema["items"]
            self.assertEqual(item_schema["type"], "object")
            self.assertEqual(set(item_schema["properties"]), expected_fields)
            self.assertEqual(
                item_schema["required"], list(item_schema["properties"])
            )
            self.assertIs(item_schema["additionalProperties"], False)

        for field in (
            "supported_claims",
            "unsupported_claims",
            "missing_evidence",
            "contradictions",
            "uncertainty",
            "evidence_references",
        ):
            self.assertEqual(properties[field]["type"], "array")
        self.assertEqual(properties["proposed_next_action"]["type"], "object")

        required_source_id_schemas = [
            properties["supported_claims"]["items"]["properties"]["source_ids"],
            properties["unsupported_claims"]["items"]["properties"]["asserted_in"],
            properties["missing_evidence"]["items"]["properties"]["source_ids"],
            properties["contradictions"]["items"]["properties"]["source_ids"],
            properties["uncertainty"]["items"]["properties"]["source_ids"],
            properties["proposed_next_action"]["properties"]["source_ids"],
        ]
        expected_source_ids = [f"SRC-{number:03d}" for number in range(1, 8)]
        for source_schema in required_source_id_schemas:
            self.assertEqual(source_schema["type"], "array")
            self.assertEqual(source_schema["minItems"], 1)
            self.assertEqual(source_schema["items"]["enum"], expected_source_ids)
        assessment_sources = properties["unsupported_claims"]["items"][
            "properties"
        ]["assessment_sources"]
        self.assertEqual(assessment_sources["type"], "array")
        self.assertNotIn("minItems", assessment_sources)
        self.assertEqual(assessment_sources["items"]["enum"], expected_source_ids)
        self.assertEqual(
            properties["evidence_references"]["items"]["properties"]["source_id"][
                "enum"
            ],
            expected_source_ids,
        )

    def test_run_003_artifact_paths_are_exclusive_and_distinct(self):
        configured = (
            run_003.RAW_RESPONSE_PATH.name,
            run_003.RAW_HTTP_ERROR_PATH.name,
            run_003.RAW_ANSWER_PATH.name,
        )
        run_001_paths = {
            run_001.RAW_RESPONSE_PATH.resolve(),
            run_001.RAW_HTTP_ERROR_PATH.resolve(),
            run_001.RAW_ANSWER_PATH.resolve(),
        }
        run_002_paths = {
            run_002.RAW_RESPONSE_PATH.resolve(),
            run_002.RAW_HTTP_ERROR_PATH.resolve(),
            run_002.RAW_ANSWER_PATH.resolve(),
        }
        run_003_paths = {
            run_003.RAW_RESPONSE_PATH.resolve(),
            run_003.RAW_HTTP_ERROR_PATH.resolve(),
            run_003.RAW_ANSWER_PATH.resolve(),
        }
        self.assertEqual(configured, RUN_003_OUTPUT_NAMES)
        self.assertEqual(len(run_003_paths), 3)
        self.assertTrue(all("RUN_003" in name for name in configured))
        self.assertTrue(run_001_paths.isdisjoint(run_003_paths))
        self.assertTrue(run_002_paths.isdisjoint(run_003_paths))

    def test_existing_run_003_artifact_prevents_transport(self):
        for output_name in RUN_003_OUTPUT_NAMES:
            with self.subTest(path=output_name), tempfile.TemporaryDirectory() as directory:
                self._temporary_paths(directory)
                existing_path = Path(directory) / output_name
                existing_path.write_bytes(b"pre-existing Run 003 sentinel")
                with (
                    patch.dict(os.environ, DUMMY_ENVIRONMENT, clear=True),
                    patch.object(run_003, "build_opener") as opener_factory,
                    contextlib.redirect_stderr(io.StringIO()),
                ):
                    result = run_003.main()
                self.assertEqual(result, 2)
                opener_factory.assert_not_called()
                self.assertEqual(
                    existing_path.read_bytes(), b"pre-existing Run 003 sentinel"
                )

    def test_successful_response_capture_and_answer_extraction_are_exact(self):
        answer = json.dumps(_valid_output(), separators=(",", ":"))
        raw_body = _envelope("  " + answer + "\n")
        (
            result,
            opener,
            _response,
            saved_response,
            saved_answer,
            http_error_saved,
            _stdout,
            _stderr,
        ) = self._successful_attempt(raw_body)
        self.assertEqual(result, 0)
        opener.open.assert_called_once()
        self.assertEqual(saved_response, raw_body)
        self.assertEqual(saved_answer, ("  " + answer + "\n").encode("utf-8"))
        self.assertFalse(http_error_saved)
        self.assertEqual(
            run_003._extract_answer(raw_body), run_002._extract_answer(raw_body)
        )
        self.assertEqual(
            validate_output.validate_output_text(saved_answer.decode("utf-8")), []
        )

    def test_invalid_answer_is_extracted_without_repair_or_validation(self):
        answer = "```json\n{}\n```"
        raw_body = _envelope(answer)
        (
            result,
            opener,
            _response,
            saved_response,
            saved_answer,
            http_error_saved,
            _stdout,
            stderr,
        ) = self._successful_attempt(raw_body)
        self.assertEqual(result, 0)
        opener.open.assert_called_once()
        self.assertEqual(saved_response, raw_body)
        self.assertEqual(saved_answer, answer.encode("utf-8"))
        self.assertFalse(http_error_saved)
        self.assertEqual(validate_output.validate_output_text(answer), [
            "invalid JSON: Expecting value: line 1 column 1 (char 0)"
        ])
        self.assertNotIn(DUMMY_CREDENTIAL, stderr)

    def test_invalid_credentials_fail_before_transport(self):
        invalid_values = (
            "",
            " " + DUMMY_CREDENTIAL,
            DUMMY_CREDENTIAL + " ",
            DUMMY_CREDENTIAL + "\r",
            DUMMY_CREDENTIAL + "\n",
            DUMMY_CREDENTIAL + "\x01",
            "******",
        )
        for value in invalid_values:
            with self.subTest(value=value), tempfile.TemporaryDirectory() as directory:
                self._temporary_paths(directory)
                output = io.StringIO()
                with (
                    patch.dict(os.environ, {"OPENROUTER_API_KEY": value}, clear=True),
                    patch.object(run_003, "build_opener") as opener_factory,
                    contextlib.redirect_stdout(output),
                    contextlib.redirect_stderr(output),
                ):
                    result = run_003.main()
                self.assertEqual(result, 2)
                opener_factory.assert_not_called()
                if value:
                    self.assertNotIn(value, output.getvalue())

    def test_missing_credential_fails_before_transport(self):
        with tempfile.TemporaryDirectory() as directory:
            self._temporary_paths(directory)
            with (
                patch.dict(os.environ, {}, clear=True),
                patch.object(run_003, "build_opener") as opener_factory,
                contextlib.redirect_stderr(io.StringIO()),
            ):
                result = run_003.main()
        self.assertEqual(result, 2)
        opener_factory.assert_not_called()

    def test_credential_bearing_response_is_never_saved_or_logged(self):
        raw_body = _envelope(f"answer contains {DUMMY_CREDENTIAL}")
        (
            result,
            opener,
            _response,
            saved_response,
            saved_answer,
            http_error_saved,
            stdout,
            stderr,
        ) = self._successful_attempt(raw_body)
        self.assertEqual(result, 1)
        opener.open.assert_called_once()
        self.assertIsNone(saved_response)
        self.assertIsNone(saved_answer)
        self.assertFalse(http_error_saved)
        self.assertNotIn(DUMMY_CREDENTIAL, stdout + stderr)

    def test_http_error_is_preserved_separately_without_retry(self):
        with tempfile.TemporaryDirectory() as directory:
            self._temporary_paths(directory)
            body = b'{"error":"offline test"}'
            error = HTTPError(
                "https://openrouter.ai/api/v1/chat/completions",
                400,
                "bad request",
                {},
                _MockResponse(body),
            )
            opener = Mock()
            opener.open.side_effect = error
            with (
                patch.dict(os.environ, DUMMY_ENVIRONMENT, clear=True),
                patch.object(run_003, "build_opener", return_value=opener),
                contextlib.redirect_stderr(io.StringIO()),
            ):
                result = run_003.main()
            opener.open.assert_called_once()
            self.assertEqual(result, 1)
            self.assertEqual(run_003.RAW_HTTP_ERROR_PATH.read_bytes(), body)
            self.assertFalse(run_003.RAW_RESPONSE_PATH.exists())
            self.assertFalse(run_003.RAW_ANSWER_PATH.exists())

    def test_transport_failure_is_not_retried(self):
        with tempfile.TemporaryDirectory() as directory:
            self._temporary_paths(directory)
            opener = Mock()
            opener.open.side_effect = URLError("offline test")
            with (
                patch.dict(os.environ, DUMMY_ENVIRONMENT, clear=True),
                patch.object(run_003, "build_opener", return_value=opener),
                contextlib.redirect_stderr(io.StringIO()),
            ):
                result = run_003.main()
            opener.open.assert_called_once()
            self.assertEqual(result, 1)
            self.assertFalse(run_003.RAW_RESPONSE_PATH.exists())
            self.assertFalse(run_003.RAW_HTTP_ERROR_PATH.exists())
            self.assertFalse(run_003.RAW_ANSWER_PATH.exists())

    def test_redirect_handler_refuses_replay(self):
        handler = run_003.NoRedirectHandler()
        request = urllib.request.Request(
            "https://openrouter.ai/api/v1/chat/completions",
            data=b"request",
            method="POST",
        )
        response = handler.redirect_request(
            request, None, 307, "Temporary Redirect", {}, "https://example.invalid/"
        )
        self.assertIsNone(response)

    def test_oversized_response_is_not_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            self._temporary_paths(directory)
            response = _MockResponse(
                b"x" * (run_003.OUTPUT_LIMIT_BYTES + 1)
            )
            opener = Mock()
            opener.open.return_value = response
            with (
                patch.dict(os.environ, DUMMY_ENVIRONMENT, clear=True),
                patch.object(run_003, "build_opener", return_value=opener),
                contextlib.redirect_stderr(io.StringIO()),
            ):
                result = run_003.main()
            opener.open.assert_called_once()
            self.assertEqual(result, 1)
            self.assertFalse(run_003.RAW_RESPONSE_PATH.exists())
            self.assertFalse(run_003.RAW_ANSWER_PATH.exists())
            self.assertLessEqual(
                response.total_bytes_read, run_003.OUTPUT_LIMIT_BYTES + 1
            )

    def test_run_001_and_run_002_sentinels_remain_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            self._temporary_paths(directory)
            protected_names = RUN_001_OUTPUT_NAMES + RUN_002_OUTPUT_NAMES
            sentinels = {
                Path(directory) / name: f"sentinel:{name}".encode("ascii")
                for name in protected_names
            }
            for path, content in sentinels.items():
                path.write_bytes(content)
            body = _envelope(json.dumps(_valid_output(), separators=(",", ":")))
            opener = Mock(open=Mock(return_value=_MockResponse(body)))
            with (
                patch.dict(os.environ, DUMMY_ENVIRONMENT, clear=True),
                patch.object(run_003, "build_opener", return_value=opener),
                contextlib.redirect_stdout(io.StringIO()),
                contextlib.redirect_stderr(io.StringIO()),
            ):
                self.assertEqual(run_003.main(), 0)
            opener.open.assert_called_once()
            for path, content in sentinels.items():
                self.assertEqual(path.read_bytes(), content)

    def test_offline_guard_blocks_real_network_and_workspace_writes(self):
        with self.assertRaisesRegex(RuntimeError, "blocked network access"):
            socket.socket()
        protected_path = PROJECT_ROOT / "raw" / RUN_001_OUTPUT_NAMES[0]
        with self.assertRaisesRegex(RuntimeError, "workspace writes"):
            _deny_network(
                "open",
                (protected_path, "wb", os.O_WRONLY | os.O_CREAT),
            )


if __name__ == "__main__":
    unittest.main()
