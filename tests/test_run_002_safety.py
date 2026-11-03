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
        "src/run_002.py",
        "src/run_001.py",
        "tests/test_run_002_safety.py",
        "benchmark/CASEBRIEF_BUILD_CONTRACT_V1.0.md",
        "benchmark/CASEBRIEF_SYNTHETIC_PACKET_001_V1.0.md",
    )
}
SAFE_IMPORT_CACHES = {
    (PROJECT_ROOT / "src" / "__pycache__").resolve(): ("run_001.", "run_002."),
    (PROJECT_ROOT / "tests" / "__pycache__").resolve(): "test_run_002_safety.",
}


def _is_allowed_import_cache_read(path):
    return (
        path.parent in SAFE_IMPORT_CACHES
        and path.name.startswith(SAFE_IMPORT_CACHES[path.parent])
        and path.suffix == ".pyc"
    )


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

run_002 = importlib.import_module("src.run_002")
run_001 = importlib.import_module("src.run_001")

OUTPUT_LIMIT_BYTES = run_002.OUTPUT_LIMIT_BYTES
DUMMY_CREDENTIAL = "dummy-openrouter-key-for-run-002-offline-tests"
DUMMY_ENVIRONMENT = {"OPENROUTER_API_KEY": DUMMY_CREDENTIAL}
RUN_001_OUTPUT_NAMES = (
    "CASEBRIEF_RUN_001_OPENROUTER_RESPONSE.raw",
    "CASEBRIEF_RUN_001_OPENROUTER_HTTP_ERROR.raw",
    "CASEBRIEF_RUN_001_OPENROUTER_ANSWER.json",
)


def _envelope(content="mock answer"):
    return json.dumps(
        {
            "id": "mock-completion-id",
            "model": run_002.MODEL_ID,
            "provider": run_002.PROVIDER_ID,
            "choices": [{"message": {"content": content}, "finish_reason": "stop"}],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 2,
                "total_tokens": 12,
            },
        },
        separators=(",", ":"),
    ).encode("utf-8")


def _padded_envelope(size):
    prefix = b'{"choices":[{"message":{"content":"ok"}}],"pad":"'
    suffix = b'"}'
    padding_size = size - len(prefix) - len(suffix)
    if padding_size < 0:
        raise ValueError("requested test envelope size is too small")
    return prefix + b"x" * padding_size + suffix


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


class Run002SafetyTests(unittest.TestCase):
    def _temporary_paths(self, directory):
        run_002.RAW_RESPONSE_PATH = Path(directory) / RUN_001_OUTPUT_NAMES[0].replace(
            "001", "002"
        )
        run_002.RAW_HTTP_ERROR_PATH = Path(directory) / RUN_001_OUTPUT_NAMES[1].replace(
            "001", "002"
        )
        run_002.RAW_ANSWER_PATH = Path(directory) / RUN_001_OUTPUT_NAMES[2].replace(
            "001", "002"
        )

    def _successful_attempt(self, content=None, environment=None):
        with tempfile.TemporaryDirectory() as directory:
            self._temporary_paths(directory)
            response = _MockResponse(_envelope() if content is None else content)
            opener = Mock()
            opener.open.return_value = response
            opener.factory_mock = Mock(return_value=opener)
            attempt_environment = (
                DUMMY_ENVIRONMENT if environment is None else environment
            )
            with (
                patch.dict(os.environ, attempt_environment, clear=True),
                patch.object(run_002, "build_opener", opener.factory_mock),
                contextlib.redirect_stdout(io.StringIO()) as stdout,
                contextlib.redirect_stderr(io.StringIO()) as stderr,
            ):
                result = run_002.main()
            saved_response = (
                run_002.RAW_RESPONSE_PATH.read_bytes()
                if run_002.RAW_RESPONSE_PATH.exists()
                else None
            )
            saved_answer = (
                run_002.RAW_ANSWER_PATH.read_bytes()
                if run_002.RAW_ANSWER_PATH.exists()
                else None
            )
            return (
                result,
                opener,
                response,
                saved_response,
                saved_answer,
                run_002.RAW_HTTP_ERROR_PATH.exists(),
                stdout.getvalue(),
                stderr.getvalue(),
            )

    def test_request_has_exact_low_reasoning_and_unchanged_route(self):
        (
            result,
            opener,
            _response,
            saved_response,
            saved_answer,
            _http_error_saved,
            stdout,
            stderr,
        ) = self._successful_attempt()
        self.assertEqual(result, 0)
        opener.open.assert_called_once()
        opener.factory_mock.assert_called_once()
        self.assertIsInstance(
            opener.factory_mock.call_args.args[0], run_002.NoRedirectHandler
        )
        request = opener.open.call_args.args[0]
        self.assertEqual(request.full_url, "https://openrouter.ai/api/v1/chat/completions")
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(opener.open.call_args.kwargs, {"timeout": 60})
        self.assertEqual(run_002.MODEL_ID, run_001.MODEL_ID)
        self.assertEqual(run_002.MODEL_ENDPOINT, run_001.MODEL_ENDPOINT)
        self.assertEqual(run_002.PROVIDER_ID, run_001.PROVIDER_ID)
        self.assertEqual(run_002.LOCAL_TIMEOUT_SECONDS, run_001.LOCAL_TIMEOUT_SECONDS)
        self.assertEqual(run_002.MAX_OUTPUT_TOKENS, run_001.MAX_OUTPUT_TOKENS)
        self.assertEqual(request.get_header("Authorization"), f"Bearer {DUMMY_CREDENTIAL}")
        request_body = json.loads(request.data.decode("utf-8"))
        prompt = request_body["messages"][0]["content"]
        self.assertEqual(
            request_body,
            {
                "model": "meta/muse-spark-open",
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
        contract = run_002.CONTRACT_PATH.read_text(encoding="utf-8")
        packet = run_002.PACKET_PATH.read_text(encoding="utf-8")
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

    def test_output_paths_are_run_002_only(self):
        expected_names = (
            "CASEBRIEF_RUN_002_OPENROUTER_RESPONSE.raw",
            "CASEBRIEF_RUN_002_OPENROUTER_HTTP_ERROR.raw",
            "CASEBRIEF_RUN_002_OPENROUTER_ANSWER.json",
        )
        configured = (
            run_002.RAW_RESPONSE_PATH.name,
            run_002.RAW_HTTP_ERROR_PATH.name,
            run_002.RAW_ANSWER_PATH.name,
        )
        self.assertEqual(configured, expected_names)
        self.assertTrue(all("RUN_001" not in name for name in configured))

    def test_invalid_credentials_fail_before_transport_without_disclosure(self):
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
                    patch.object(run_002, "build_opener") as opener_factory,
                    contextlib.redirect_stdout(output),
                    contextlib.redirect_stderr(output),
                ):
                    result = run_002.main()
                self.assertEqual(result, 2)
                opener_factory.assert_not_called()
                if value:
                    self.assertNotIn(value, output.getvalue())

    def test_missing_credential_fails_before_transport(self):
        with tempfile.TemporaryDirectory() as directory:
            self._temporary_paths(directory)
            with (
                patch.dict(os.environ, {}, clear=True),
                patch.object(run_002, "build_opener") as opener_factory,
                contextlib.redirect_stderr(io.StringIO()),
            ):
                result = run_002.main()
        self.assertEqual(result, 2)
        opener_factory.assert_not_called()

    def test_each_preexisting_run_002_output_stops_before_transport(self):
        paths = (
            "RAW_RESPONSE_PATH",
            "RAW_HTTP_ERROR_PATH",
            "RAW_ANSWER_PATH",
        )
        for attribute in paths:
            with self.subTest(path=attribute), tempfile.TemporaryDirectory() as directory:
                self._temporary_paths(directory)
                existing_path = getattr(run_002, attribute)
                existing_path.write_bytes(b"pre-existing Run 002 sentinel")
                with (
                    patch.dict(os.environ, DUMMY_ENVIRONMENT, clear=True),
                    patch.object(run_002, "build_opener") as opener_factory,
                    contextlib.redirect_stderr(io.StringIO()),
                ):
                    result = run_002.main()
                self.assertEqual(result, 2)
                opener_factory.assert_not_called()
                self.assertEqual(
                    existing_path.read_bytes(), b"pre-existing Run 002 sentinel"
                )

    def test_run_001_sentinels_remain_unchanged_and_paths_are_not_written(self):
        with tempfile.TemporaryDirectory() as directory:
            self._temporary_paths(directory)
            sentinels = {
                Path(directory) / name: f"sentinel:{name}".encode("ascii")
                for name in RUN_001_OUTPUT_NAMES
            }
            for path, content in sentinels.items():
                path.write_bytes(content)
            with (
                patch.dict(os.environ, DUMMY_ENVIRONMENT, clear=True),
                patch.object(run_002, "build_opener", return_value=Mock(
                    open=Mock(return_value=_MockResponse(_envelope()))
                )),
                contextlib.redirect_stdout(io.StringIO()),
                contextlib.redirect_stderr(io.StringIO()),
            ):
                self.assertEqual(run_002.main(), 0)
            for path, content in sentinels.items():
                self.assertEqual(path.read_bytes(), content)

            for name in RUN_001_OUTPUT_NAMES:
                protected_path = PROJECT_ROOT / "raw" / name
                with self.subTest(path=name):
                    with self.assertRaisesRegex(RuntimeError, "workspace writes"):
                        _deny_network(
                            "open",
                            (protected_path, "wb", os.O_WRONLY | os.O_CREAT),
                        )

    def test_successful_raw_response_is_preserved_and_answer_is_exact(self):
        body = _envelope("  Exact answer\nwith spacing.  ")
        (
            result,
            opener,
            response,
            saved_response,
            saved_answer,
            http_error_saved,
            stdout,
            stderr,
        ) = self._successful_attempt(body)
        self.assertEqual(result, 0)
        opener.open.assert_called_once()
        self.assertEqual(saved_response, body)
        self.assertEqual(saved_answer, b"  Exact answer\nwith spacing.  ")
        self.assertFalse(http_error_saved)
        self.assertEqual(response.total_bytes_read, len(body))
        self.assertNotIn(DUMMY_CREDENTIAL, stdout + stderr)

    def test_null_content_fails_extraction_after_preserving_raw_only(self):
        body = _envelope(None)
        (
            result,
            opener,
            _response,
            saved_response,
            saved_answer,
            http_error_saved,
            _stdout,
            stderr,
        ) = self._successful_attempt(body)
        self.assertEqual(result, 1)
        opener.open.assert_called_once()
        self.assertEqual(saved_response, body)
        self.assertIsNone(saved_answer)
        self.assertFalse(http_error_saved)
        self.assertIn("answer extraction failed", stderr)

    def test_malformed_response_fails_without_retry_or_answer(self):
        body = b"not-json"
        (
            result,
            opener,
            _response,
            saved_response,
            saved_answer,
            _http_error_saved,
            _stdout,
            stderr,
        ) = self._successful_attempt(body)
        self.assertEqual(result, 1)
        opener.open.assert_called_once()
        self.assertEqual(saved_response, body)
        self.assertIsNone(saved_answer)
        self.assertIn("answer extraction failed", stderr)

    def test_credential_bearing_success_body_is_never_saved_or_logged(self):
        body = _envelope(f"echoed value: {DUMMY_CREDENTIAL}")
        (
            result,
            opener,
            _response,
            saved_response,
            saved_answer,
            _http_error_saved,
            stdout,
            stderr,
        ) = self._successful_attempt(body)
        self.assertEqual(result, 1)
        opener.open.assert_called_once()
        self.assertIsNone(saved_response)
        self.assertIsNone(saved_answer)
        self.assertNotIn(DUMMY_CREDENTIAL, stdout + stderr)

    def test_credential_bearing_http_error_is_never_saved_or_logged(self):
        body = f'{{"error":"{DUMMY_CREDENTIAL}"}}'.encode("utf-8")
        response = _MockResponse(body)
        error = HTTPError(
            run_002.MODEL_ENDPOINT, 400, "mocked error", response.headers, response
        )
        with tempfile.TemporaryDirectory() as directory:
            self._temporary_paths(directory)
            opener = Mock()
            opener.open.side_effect = error
            output = io.StringIO()
            with (
                patch.dict(os.environ, DUMMY_ENVIRONMENT, clear=True),
                patch.object(run_002, "build_opener", return_value=opener),
                contextlib.redirect_stdout(output),
                contextlib.redirect_stderr(output),
            ):
                result = run_002.main()
            self.assertEqual(result, 1)
            opener.open.assert_called_once()
            self.assertFalse(run_002.RAW_HTTP_ERROR_PATH.exists())
            self.assertNotIn(DUMMY_CREDENTIAL, output.getvalue())

    def test_http_error_body_is_preserved_separately_without_retry(self):
        body = b'{"error":"mocked-provider-error"}'
        response = _MockResponse(body)
        error = HTTPError(
            run_002.MODEL_ENDPOINT, 400, "mocked error", response.headers, response
        )
        with tempfile.TemporaryDirectory() as directory:
            self._temporary_paths(directory)
            opener = Mock()
            opener.open.side_effect = error
            with (
                patch.dict(os.environ, DUMMY_ENVIRONMENT, clear=True),
                patch.object(run_002, "build_opener", return_value=opener),
                contextlib.redirect_stderr(io.StringIO()),
            ):
                result = run_002.main()
            self.assertEqual(result, 1)
            opener.open.assert_called_once()
            self.assertEqual(run_002.RAW_HTTP_ERROR_PATH.read_bytes(), body)
            self.assertFalse(run_002.RAW_RESPONSE_PATH.exists())
            self.assertFalse(run_002.RAW_ANSWER_PATH.exists())

    def test_transport_failure_is_not_retried(self):
        with tempfile.TemporaryDirectory() as directory:
            self._temporary_paths(directory)
            opener = Mock()
            opener.open.side_effect = URLError(DUMMY_CREDENTIAL)
            output = io.StringIO()
            with (
                patch.dict(os.environ, DUMMY_ENVIRONMENT, clear=True),
                patch.object(run_002, "build_opener", return_value=opener),
                contextlib.redirect_stderr(output),
            ):
                result = run_002.main()
        self.assertEqual(result, 1)
        opener.open.assert_called_once()
        self.assertNotIn(DUMMY_CREDENTIAL, output.getvalue())

    def test_redirect_is_not_followed_or_replayed(self):
        handler = run_002.NoRedirectHandler()
        request = urllib.request.Request(
            run_002.MODEL_ENDPOINT, data=b"{}", method="POST"
        )
        self.assertIsNone(
            handler.redirect_request(
                request, None, 307, "Temporary Redirect", {}, "https://example.invalid/"
            )
        )
        response = _MockResponse(b"redirect body")
        error = HTTPError(
            run_002.MODEL_ENDPOINT, 307, "Temporary Redirect", {}, response
        )
        with tempfile.TemporaryDirectory() as directory:
            self._temporary_paths(directory)
            opener = Mock()
            opener.open.side_effect = error
            with (
                patch.dict(os.environ, DUMMY_ENVIRONMENT, clear=True),
                patch.object(run_002, "build_opener", return_value=opener),
                contextlib.redirect_stderr(io.StringIO()),
            ):
                self.assertEqual(run_002.main(), 1)
            opener.open.assert_called_once()
            self.assertEqual(
                run_002.RAW_HTTP_ERROR_PATH.read_bytes(), b"redirect body"
            )

    def test_oversized_success_body_is_rejected_without_preserving_prefix(self):
        response = _MockResponse(_envelope() + b"x" * OUTPUT_LIMIT_BYTES)
        with tempfile.TemporaryDirectory() as directory:
            self._temporary_paths(directory)
            opener = Mock()
            opener.open.return_value = response
            output = io.StringIO()
            with (
                patch.dict(os.environ, DUMMY_ENVIRONMENT, clear=True),
                patch.object(run_002, "build_opener", return_value=opener),
                contextlib.redirect_stdout(output),
                contextlib.redirect_stderr(output),
            ):
                result = run_002.main()
            self.assertEqual(result, 1)
            opener.open.assert_called_once()
            self.assertEqual(response.total_bytes_read, OUTPUT_LIMIT_BYTES + 1)
            self.assertFalse(run_002.RAW_RESPONSE_PATH.exists())
            self.assertFalse(run_002.RAW_ANSWER_PATH.exists())
            self.assertIn(f"cap={OUTPUT_LIMIT_BYTES}", output.getvalue())
            self.assertNotIn("x" * 100, output.getvalue())

    def test_oversized_http_error_body_is_rejected_without_preserving_prefix(self):
        response = _MockResponse(b"x" * (OUTPUT_LIMIT_BYTES + 1))
        error = HTTPError(
            run_002.MODEL_ENDPOINT, 413, "mocked oversized error", {}, response
        )
        with tempfile.TemporaryDirectory() as directory:
            self._temporary_paths(directory)
            opener = Mock()
            opener.open.side_effect = error
            with (
                patch.dict(os.environ, DUMMY_ENVIRONMENT, clear=True),
                patch.object(run_002, "build_opener", return_value=opener),
                contextlib.redirect_stderr(io.StringIO()),
            ):
                result = run_002.main()
            self.assertEqual(result, 1)
            opener.open.assert_called_once()
            self.assertEqual(response.total_bytes_read, OUTPUT_LIMIT_BYTES + 1)
            self.assertFalse(run_002.RAW_HTTP_ERROR_PATH.exists())

    def test_response_at_capture_limit_is_read_in_bounded_chunks(self):
        body = _padded_envelope(OUTPUT_LIMIT_BYTES)
        (
            result,
            opener,
            response,
            saved_response,
            saved_answer,
            _http_error_saved,
            _stdout,
            _stderr,
        ) = self._successful_attempt(body)
        self.assertEqual(result, 0)
        opener.open.assert_called_once()
        self.assertEqual(saved_response, body)
        self.assertEqual(saved_answer, b"ok")
        self.assertEqual(response.total_bytes_read, OUTPUT_LIMIT_BYTES)
        self.assertTrue(all(0 < size <= 65_536 for size in response.read_sizes))

    def test_import_does_not_send_a_request(self):
        source_path = Path(run_002.__file__)
        with (
            patch.dict(os.environ, {}, clear=True),
            patch.object(urllib.request, "build_opener") as opener_factory,
            patch.object(urllib.request, "urlopen") as urlopen,
        ):
            reloaded_module = importlib.reload(run_002)
        opener_factory.assert_not_called()
        urlopen.assert_not_called()
        self.assertEqual(Path(reloaded_module.__file__), source_path)

    def test_offline_guard_blocks_real_network_and_workspace_writes(self):
        with self.assertRaisesRegex(RuntimeError, "blocked network"):
            with socket.socket() as test_socket:
                test_socket.connect(("127.0.0.1", 1))
        with self.assertRaisesRegex(RuntimeError, "workspace writes"):
            _deny_network(
                "open",
                (
                    PROJECT_ROOT / "raw" / RUN_001_OUTPUT_NAMES[0],
                    "wb",
                    os.O_WRONLY | os.O_CREAT,
                ),
            )


if __name__ == "__main__":
    unittest.main()
