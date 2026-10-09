"""Economic H3 contract/state tests. Every network request is mocked."""

import argparse
from concurrent.futures import ThreadPoolExecutor
import copy
import io
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import Mock, patch
from urllib import error, request
import zlib

from tools.video import h3


KEY = "mock-secret-never-print"
SUBSCRIPTION_KEY = "mock-subscription-secret-never-print"
SIGNED_URL = "https://cdn.example.com/video.mp4?signature=mock-private-signature"
PROMPT = "A character breathes, then returns to the opening pose. Silence."
IMAGE_PROBE = {"streams": [{"codec_type": "video", "codec_name": "png", "width": 1536, "height": 864}], "format": {}}
VIDEO_PROBE = {"streams": [{"codec_type": "video", "codec_name": "h264", "width": 1366, "height": 768, "avg_frame_rate": "24/1", "r_frame_rate": "24/1", "duration": "8.000000", "nb_read_frames": "192"}], "format": {"duration": "8.000000", "format_name": "mov,mp4,m4a,3gp,3g2,mj2"}}


class Response:
    def __init__(self, raw, headers=None):
        self.raw = io.BytesIO(raw)
        self.headers = headers or {}

    def read(self, size=-1):
        return self.raw.read(size)

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


class Opener:
    def __init__(self, *responses):
        self.responses = list(responses)
        self.calls = []

    def open(self, req, timeout):
        self.calls.append(req)
        if not self.responses:
            raise AssertionError("unexpected mocked HTTP call")
        value = self.responses.pop(0)
        if isinstance(value, BaseException):
            raise value
        return value


def json_response(value):
    return Response(json.dumps(value).encode())


def task(status="succeeded", **extras):
    value = {"id": "task_123", "model": "MiniMax-H3", "status": status, "resolution": "768P", "duration": 8, "ratio": "16:9", "task_type": "generation", "modality": "video", "created_at": 1791540000, "updated_at": 1791540001}
    if status == "succeeded":
        value.update(content={"url": SIGNED_URL}, usage={"total_seconds": 8, "output_seconds": 8, "input_seconds": 0, "input_image_count": 2})
    value.update(extras)
    return {"task": value}


class H3Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.first = self.root / "first.png"
        self.first.write_bytes(b"\x89PNG\r\n\x1a\n" + b"fixture image, not for actual upload")
        self.prompt = self.root / "motion.txt"
        self.prompt.write_text(PROMPT)
        self.env = patch.dict(os.environ, {"MINIMAX_API_KEY": KEY}, clear=True)
        self.env.start()
        self.addCleanup(self.env.stop)
        self.probe = patch.object(h3, "probe", return_value=copy.deepcopy(IMAGE_PROBE))
        self.probe_mock = self.probe.start()
        self.addCleanup(self.probe.stop)
        # A regression must fail locally instead of ever reaching a paid service.
        self.network = patch.object(request.OpenerDirector, "open", side_effect=AssertionError("real HTTP forbidden in tests"))
        self.network.start()
        self.addCleanup(self.network.stop)

    def submit_args(self, **extras):
        value = dict(first_frame=self.first, last_frame=None, prompt_file=self.prompt, state_dir=self.root / "jobs", duration=8, take_id="take-01", billing="payg", dry_run=False, env_file=None, timeout=60)
        value.update(extras)
        return argparse.Namespace(**value)

    def client(self, *responses, media=(), api_key=KEY):
        client = h3.Client(api_key)
        client.api_opener = Opener(*responses)
        client.media_opener = Opener(*media)
        return client

    def accepted(self, billing="payg", api_key=KEY):
        client = self.client(json_response({"task_id": "task_123"}), api_key=api_key)
        result = h3.submit(self.submit_args(billing=billing), lambda *_: client)
        return Path(result["job"]), client

    def status_args(self, path, **extras):
        value = dict(job=path, billing=None, env_file=None, timeout=60, wait=False, interval=10, max_wait=600)
        value.update(extras)
        return argparse.Namespace(**value)

    def download_args(self, path, **extras):
        value = dict(job=path, output=self.root / "output.mp4", billing=None, env_file=None, timeout=60, max_bytes=1024)
        value.update(extras)
        return argparse.Namespace(**value)

    def assert_private(self, value):
        text = json.dumps(value)
        for forbidden in [KEY, SUBSCRIPTION_KEY, SIGNED_URL, "mock-private-signature", "base64", PROMPT, "raw-private-message"]:
            self.assertNotIn(forbidden, text)

    def test_exact_payload_auth_and_same_image_roles(self):
        path, client = self.accepted()
        req = client.api_opener.calls[0]
        self.assertEqual(req.method, "POST")
        self.assertEqual(req.full_url, h3.CREATE_URL)
        self.assertNotIn(KEY, req.full_url)
        self.assertEqual(req.get_header("Authorization"), "Bearer " + KEY)
        self.assertEqual(req.get_header("Content-type"), "application/json")
        body = json.loads(req.data)
        self.assertEqual((body["model"], body["resolution"], body["duration"], body["ratio"]), ("MiniMax-H3", "768P", 8, "adaptive"))
        self.assertEqual([x.get("role") for x in body["content"][1:]], ["first_frame", "last_frame"])
        self.assertEqual(body["content"][1]["image_url"], body["content"][2]["image_url"])
        self.assertTrue(body["content"][1]["image_url"]["url"].startswith("data:image/png;base64,"))
        self.assertEqual(set(body), {"model", "resolution", "duration", "ratio", "content"})
        record = h3.load_job(path)
        self.assertEqual(record["request_fingerprint"], h3.digest(req.data))
        self.assertEqual(record["inputs"][0]["sha256"], h3.digest(self.first.read_bytes()))
        self.assertEqual(record["prompt"]["sha256"], h3.digest(self.prompt.read_bytes()))
        self.assertEqual(record["estimated_cost"]["total"], 0.64)
        self.assertEqual(path.stat().st_mode & 0o777, 0o600)
        self.assert_private(record)

    def test_dry_run_does_not_load_env_write_state_or_network(self):
        for mode in ["payg", "credits"]:
            with self.subTest(billing=mode), patch.object(h3, "read_key", side_effect=AssertionError("no key reads")):
                result = h3.submit(self.submit_args(billing=mode, dry_run=True, env_file=self.root / "does-not-exist"))
            self.assertTrue(result["dry_run"])
            self.assertEqual(result["billing"]["mode"], mode)
            self.assertEqual(result["estimated_cost"]["total_credits"], 640)
            self.assertFalse(self.submit_args().state_dir.exists())
            self.assert_private(result)

    def test_credits_submit_uses_subscription_key_and_unchanged_payload(self):
        payg_body, payg_record = h3.prepare(self.first, None, self.prompt)
        client = self.client(json_response({"task_id": "task_123"}), api_key=SUBSCRIPTION_KEY)
        factory = Mock(return_value=client)
        with patch.dict(os.environ, {"MINIMAX_SUBSCRIPTION_KEY": SUBSCRIPTION_KEY}):
            result = h3.submit(self.submit_args(billing="credits"), factory)
        factory.assert_called_once_with(SUBSCRIPTION_KEY, 60)
        req = client.api_opener.calls[0]
        self.assertEqual(req.full_url, h3.CREATE_URL)
        self.assertEqual(req.get_header("Authorization"), "Bearer " + SUBSCRIPTION_KEY)
        self.assertEqual(req.data, payg_body)
        self.assertEqual(result["request_fingerprint"], payg_record["request_fingerprint"])
        record = h3.load_job(Path(result["job"]))
        self.assertEqual(record["billing"], {"mode": "credits", "key_env": "MINIMAX_SUBSCRIPTION_KEY"})
        self.assertEqual(record["estimated_cost"]["output_credits_per_second"], 80)
        self.assertEqual(record["estimated_cost"]["total_credits"], 640)
        self.assertEqual(record["estimated_cost"]["credits_per_usd"], 1000)
        self.assert_private(result)
        self.assert_private(record)

    def test_selected_dotenv_key_is_literal_and_env_precedence_is_per_mode(self):
        marker = self.root / "never-created"
        env_file = self.root / "mock.env"
        env_file.write_text('OTHER=$(touch ' + str(marker) + ')\nMINIMAX_API_KEY=file-payg-key\nexport MINIMAX_SUBSCRIPTION_KEY="literal-${OTHER}-`id`" # comment\n')
        # The fixture process has only the mock payg key; credits must read its own assignment.
        self.assertEqual(h3.read_key(env_file, "credits"), "literal-${OTHER}-`id`")
        self.assertEqual(h3.read_key(env_file), KEY)
        with patch.dict(os.environ, {"MINIMAX_SUBSCRIPTION_KEY": SUBSCRIPTION_KEY}, clear=True):
            self.assertEqual(h3.read_key(env_file, "credits"), SUBSCRIPTION_KEY)
            self.assertEqual(h3.read_key(env_file, "payg"), "file-payg-key")
        self.assertFalse(marker.exists())

    def test_credits_missing_or_invalid_key_never_falls_back_or_reserves(self):
        env_file = self.root / "mock.env"
        env_file.write_text("MINIMAX_API_KEY=" + KEY + "\n")
        cases = [({}, None, "api_key_missing"), ({}, env_file, "env_file_invalid"),
                 ({"MINIMAX_SUBSCRIPTION_KEY": SUBSCRIPTION_KEY + " invalid"}, env_file, "api_key_invalid")]
        for extra_env, selected_file, code in cases:
            factory = Mock()
            with self.subTest(code=code), patch.dict(os.environ, extra_env), self.assertRaises(h3.SafeError) as cm:
                h3.submit(self.submit_args(billing="credits", env_file=selected_file), factory)
            self.assertEqual(cm.exception.details, {"code": code})
            factory.assert_not_called()
            self.assertFalse(list(self.submit_args().state_dir.glob("*.json")))
            self.assert_private(cm.exception.details)

    def test_credits_status_download_and_attach_default_to_recorded_key(self):
        with patch.dict(os.environ, {"MINIMAX_SUBSCRIPTION_KEY": SUBSCRIPTION_KEY}):
            path, _ = self.accepted("credits", SUBSCRIPTION_KEY)
            client = self.client(json_response(task("running")), json_response(task()), api_key=SUBSCRIPTION_KEY)
            factory = Mock(return_value=client)
            result = h3.status(self.status_args(path, wait=True), factory, sleep=lambda _: None, monotonic=lambda: 0)
            factory.assert_called_once_with(SUBSCRIPTION_KEY, 60)
            self.assertEqual(result["billing"]["mode"], "credits")
            self.assertTrue(all(r.get_header("Authorization") == "Bearer " + SUBSCRIPTION_KEY for r in client.api_opener.calls))
            raw = b"mock credits mp4"
            client = self.client(json_response(task()), media=[Response(raw)], api_key=SUBSCRIPTION_KEY)
            factory = Mock(return_value=client)
            self.probe_mock.return_value = copy.deepcopy(VIDEO_PROBE)
            result = h3.download(self.download_args(path), factory)
            factory.assert_called_once_with(SUBSCRIPTION_KEY, 60)
            self.assertIsNone(client.media_opener.calls[0].get_header("Authorization"))
            self.assert_private(result)
            with patch.object(h3, "read_key", side_effect=AssertionError("offline resume must not read keys")):
                self.assertTrue(h3.download(self.download_args(path, billing="credits"))["reused_existing"])
            record = h3.load_job(path)
            unknown = self.root / "credits-unknown.json"
            record["task_id"] = None
            record["submission"]["state"] = "unknown"
            h3.save_job(unknown, record)
            client = self.client(json_response(task("running")), api_key=SUBSCRIPTION_KEY)
            factory = Mock(return_value=client)
            result = h3.attach(argparse.Namespace(job=unknown, billing=None, task_id="task_123", env_file=None, timeout=60), factory)
            factory.assert_called_once_with(SUBSCRIPTION_KEY, 60)
            self.assertEqual(result["billing"]["mode"], "credits")
            self.assertEqual([r.method for r in client.api_opener.calls], ["GET"])
            self.assert_private(h3.load_job(unknown))

    def test_legacy_jobs_without_billing_resume_as_payg(self):
        path, _ = self.accepted()
        legacy = h3.load_job(path)
        legacy.pop("billing")
        for field in ["credits_per_usd", "output_credits_per_second", "total_credits"]:
            legacy["estimated_cost"].pop(field)
        h3.save_job(path, legacy)
        with patch.dict(os.environ, {"MINIMAX_SUBSCRIPTION_KEY": SUBSCRIPTION_KEY}):
            with patch.object(h3, "read_key", side_effect=AssertionError("duplicate legacy take must not read keys")):
                self.assertTrue(h3.submit(self.submit_args())["reused_existing"])
            client = self.client(json_response(task()))
            factory = Mock(return_value=client)
            result = h3.status(self.status_args(path), factory)
            factory.assert_called_once_with(KEY, 60)
            self.assertEqual(result["billing"], {"mode": "payg", "key_env": "MINIMAX_API_KEY"})
            # Exercise download and attach against original jobs, without the normalized field.
            h3.save_job(path, legacy)
            self.probe_mock.return_value = copy.deepcopy(VIDEO_PROBE)
            factory = Mock(return_value=self.client(json_response(task()), media=[Response(b"mp4")]))
            h3.download(self.download_args(path), factory)
            factory.assert_called_once_with(KEY, 60)
            unknown = self.root / "legacy-unknown.json"
            legacy["task_id"] = None
            legacy["submission"]["state"] = "unknown"
            h3.save_job(unknown, legacy)
            factory = Mock(return_value=self.client(json_response(task("running"))))
            h3.attach(argparse.Namespace(job=unknown, task_id="task_123", env_file=None, timeout=60), factory)
            factory.assert_called_once_with(KEY, 60)

    def test_explicit_billing_conflicts_stop_all_commands_even_offline_resume(self):
        for recorded, selected in [("credits", "payg"), ("payg", "credits"), (None, "credits")]:
            with self.subTest(recorded=recorded):
                _, record = h3.prepare(self.first, None, self.prompt, billing=recorded or "payg")
                if recorded is None:
                    record.pop("billing")
                record["task_id"] = "task_123"
                record["submission"]["state"] = "accepted"
                directory = self.root / str(recorded)
                directory.mkdir()
                path = directory / (record["request_fingerprint"] + "-take-01.json")
                output = directory / "already-downloaded.mp4"
                output.write_bytes(b"mp4")
                record["output"] = {"sha256": h3.file_digest(output), "size_bytes": 3}
                h3.save_job(path, record)
                original = path.read_bytes()
                operations = [(h3.submit, self.submit_args(state_dir=directory, billing=selected)),
                              (h3.status, self.status_args(path, billing=selected)),
                              (h3.download, self.download_args(path, billing=selected, output=output)),
                              (h3.attach, argparse.Namespace(job=path, billing=selected, task_id="task_123", env_file=None, timeout=60))]
                for operation, args in operations:
                    factory = Mock()
                    with patch.object(h3, "read_key", side_effect=AssertionError("conflict must precede key reads")), self.assertRaises(h3.SafeError) as cm:
                        operation(args, factory)
                    self.assertEqual(cm.exception.details, {"code": "billing_mismatch"})
                    factory.assert_not_called()
                    self.assertEqual(path.read_bytes(), original)

    def test_invalid_job_billing_cannot_select_another_environment_variable(self):
        path, _ = self.accepted()
        original = h3.load_job(path)
        for metadata in [None, {}, {"mode": []}, {"mode": "other", "key_env": KEY},
                         {"mode": "credits", "key_env": "MINIMAX_API_KEY"}, {"mode": "payg", "key_env": "MINIMAX_SUBSCRIPTION_KEY"}]:
            record = copy.deepcopy(original)
            record["billing"] = metadata
            h3.save_job(path, record)
            operations = [(h3.submit, self.submit_args()), (h3.status, self.status_args(path)),
                          (h3.download, self.download_args(path)),
                          (h3.attach, argparse.Namespace(job=path, task_id="task_123", env_file=None, timeout=60))]
            for operation, args in operations:
                with self.subTest(operation=operation.__name__), patch.object(h3, "read_key", side_effect=AssertionError("invalid metadata must precede key reads")), self.assertRaises(h3.SafeError) as cm:
                    operation(args, Mock())
                self.assertEqual(cm.exception.details, {"code": "job_billing_invalid"})
                self.assert_private(cm.exception.details)

    def test_rejected_payg_take_requires_new_take_id_for_credits(self):
        raw = json.dumps({"type": "error", "error": {"message": KEY + " (1008)"}}).encode()
        client = self.client(error.HTTPError(h3.CREATE_URL, 402, KEY, {}, io.BytesIO(raw)))
        with self.assertRaises(h3.SafeError):
            h3.submit(self.submit_args(), lambda *_: client)
        path = next(self.submit_args().state_dir.glob("*.json"))
        original = path.read_bytes()
        self.assertEqual(h3.load_job(path)["submission"]["state"], "rejected")
        with patch.dict(os.environ, {"MINIMAX_API_KEY": "another-mock-payg-key", "MINIMAX_SUBSCRIPTION_KEY": SUBSCRIPTION_KEY}):
            with patch.object(h3, "read_key", side_effect=AssertionError("key changes must not repeat rejected POST")):
                self.assertTrue(h3.submit(self.submit_args())["reused_existing"])
                with self.assertRaises(h3.SafeError) as cm:
                    h3.submit(self.submit_args(billing="credits"))
                self.assertEqual(cm.exception.details, {"code": "billing_mismatch"})
            credits_client = self.client(json_response({"task_id": "task_456"}), api_key=SUBSCRIPTION_KEY)
            factory = Mock(return_value=credits_client)
            result = h3.submit(self.submit_args(billing="credits", take_id="credits-take-01"), factory)
            factory.assert_called_once_with(SUBSCRIPTION_KEY, 60)
        self.assertEqual(result["request_fingerprint"], h3.load_job(path)["request_fingerprint"])
        self.assertEqual(path.read_bytes(), original)
        self.assertEqual(len(client.api_opener.calls), 1)
        self.assertEqual(len(credits_client.api_opener.calls), 1)

    def test_polling_stops_if_recorded_billing_changes(self):
        with patch.dict(os.environ, {"MINIMAX_SUBSCRIPTION_KEY": SUBSCRIPTION_KEY}):
            path, _ = self.accepted("credits", SUBSCRIPTION_KEY)
            client = self.client(json_response(task("running")), api_key=SUBSCRIPTION_KEY)
            factory = Mock(return_value=client)

            def change_billing(_):
                record = h3.load_job(path)
                record["billing"] = {"mode": "payg", "key_env": "MINIMAX_API_KEY"}
                h3.save_job(path, record)

            with self.assertRaises(h3.SafeError) as cm:
                h3.status(self.status_args(path, wait=True), factory, sleep=change_billing, monotonic=lambda: 0)
        self.assertEqual(cm.exception.details, {"code": "billing_mismatch"})
        factory.assert_called_once_with(SUBSCRIPTION_KEY, 60)
        self.assertEqual(len(client.api_opener.calls), 1)

    def test_subscription_key_errors_and_cli_output_are_redacted(self):
        raw = json.dumps({"type": "error", "error": {"message": SUBSCRIPTION_KEY + KEY + SIGNED_URL + " (1008)"}}).encode()
        client = self.client(error.HTTPError(h3.CREATE_URL, 402, SUBSCRIPTION_KEY, {}, io.BytesIO(raw)), api_key=SUBSCRIPTION_KEY)
        submit = h3.submit
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch.dict(os.environ, {"MINIMAX_SUBSCRIPTION_KEY": SUBSCRIPTION_KEY}), patch.object(h3, "submit", side_effect=lambda args: submit(args, lambda *_: client)), patch("sys.stdout", stdout), patch("sys.stderr", stderr):
            code = h3.main(["submit", "--billing", "credits", "--first-frame", str(self.first), "--prompt-file", str(self.prompt), "--state-dir", str(self.submit_args().state_dir)])
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(stderr.getvalue()), {"error": {"code": "api_http_error", "http_status": 402, "provider_code": "1008"}})
        self.assert_private(stdout.getvalue())
        self.assert_private(stderr.getvalue())
        self.assert_private(h3.load_job(next(self.submit_args().state_dir.glob("*.json"))))

    def test_duplicate_submit_reuses_job_without_even_loading_key(self):
        path, client = self.accepted()
        with patch.object(h3, "read_key", side_effect=AssertionError("no key reads")):
            result = h3.submit(self.submit_args(), lambda *_: client)
        self.assertTrue(result["reused_existing"])
        self.assertEqual(result["task_id"], "task_123")
        self.assertEqual(len(client.api_opener.calls), 1)
        self.assertEqual(Path(result["job"]), path)

    def test_fingerprint_is_path_independent_but_changes_with_prompt_and_image(self):
        body, initial = h3.prepare(self.first, None, self.prompt)
        renamed = self.root / "renamed.png"
        renamed.write_bytes(self.first.read_bytes())
        _, alias = h3.prepare(renamed, None, self.prompt)
        self.assertEqual(initial["request_fingerprint"], alias["request_fingerprint"])
        self.prompt.write_text(PROMPT + " blink")
        _, changed_prompt = h3.prepare(self.first, None, self.prompt)
        self.assertNotEqual(initial["request_fingerprint"], changed_prompt["request_fingerprint"])
        renamed.write_bytes(renamed.read_bytes() + b"another pixel")
        _, changed_image = h3.prepare(self.first, renamed, self.prompt)
        self.assertNotEqual(changed_prompt["request_fingerprint"], changed_image["request_fingerprint"])

    def test_explicit_new_take_is_the_only_retry_with_identical_inputs(self):
        client = self.client(json_response({"task_id": "task_123"}), json_response({"task_id": "task_456"}))
        first = h3.submit(self.submit_args(), lambda *_: client)
        second = h3.submit(self.submit_args(take_id="take-02"), lambda *_: client)
        self.assertEqual(first["request_fingerprint"], second["request_fingerprint"])
        self.assertNotEqual(first["job"], second["job"])
        self.assertEqual(len(client.api_opener.calls), 2)

    def test_reservation_precedes_post_and_timeout_never_reposts(self):
        outer = self

        class TimeoutClient:
            def create(self, body):
                records = list(outer.submit_args().state_dir.glob("*.json"))
                outer.assertEqual(len(records), 1)
                outer.assertEqual(h3.load_job(records[0])["submission"]["state"], "submitting")
                raise h3.SafeError("api_transport_error")

        with self.assertRaises(h3.SafeError) as cm:
            h3.submit(self.submit_args(), lambda *_: TimeoutClient())
        self.assertEqual(cm.exception.details["code"], "api_transport_error")
        path = next(self.submit_args().state_dir.glob("*.json"))
        record = h3.load_job(path)
        self.assertEqual(record["submission"]["state"], "unknown")
        with patch.object(h3, "read_key", side_effect=AssertionError("must not resubmit")):
            result = h3.submit(self.submit_args())
        self.assertTrue(result["reused_existing"])
        self.assertIsNone(result["task_id"])
        self.assert_private(record)

    def test_crash_marker_blocks_a_new_post_even_without_a_task_id(self):
        _, record = h3.prepare(self.first, None, self.prompt)
        record["submission"]["state"] = "submitting"
        directory = self.submit_args().state_dir
        directory.mkdir()
        path = directory / (record["request_fingerprint"] + "-take-01.json")
        h3.save_job(path, record)
        with patch.object(h3, "read_key", side_effect=AssertionError("crash must not lead to a new POST")):
            result = h3.submit(self.submit_args())
        self.assertEqual(result["submission"], "submitting")
        self.assertTrue(result["reused_existing"])

    def test_interrupted_post_leaves_unknown_marker(self):
        class Interrupted:
            def create(self, _):
                raise KeyboardInterrupt

        with self.assertRaises(h3.SafeError) as cm:
            h3.submit(self.submit_args(), lambda *_: Interrupted())
        self.assertEqual(cm.exception.details["code"], "submission_interrupted")
        path = next(self.submit_args().state_dir.glob("*.json"))
        self.assertEqual(h3.load_job(path)["submission"]["state"], "unknown")

    def test_invalid_or_missing_create_response_leaves_unknown_reservation(self):
        for raw in [b"not JSON " + KEY.encode(), b'{"unrecognized":"raw-private-message"}', b'{"task_id":"https://private.example/key"}']:
            with self.subTest(raw_type=raw[:10]):
                args = self.submit_args(state_dir=self.root / str(h3.digest(raw)))
                client = self.client(Response(raw))
                with self.assertRaises(h3.SafeError):
                    h3.submit(args, lambda *_: client)
                path = next(args.state_dir.glob("*.json"))
                self.assertEqual(h3.load_job(path)["submission"]["state"], "unknown")
                h3.submit(args, lambda *_: client)
                self.assertEqual(len(client.api_opener.calls), 1)
                self.assert_private(h3.load_job(path))

    def test_http_failures_have_only_safe_codes_and_are_not_retried(self):
        for status in [400, 401, 402, 422, 429, 500, 529, 302, 408]:
            with self.subTest(http_status=status):
                raw = json.dumps({"type": "error", "error": {"message": KEY + " " + SIGNED_URL + " raw-private-message (1026)"}}).encode()
                exception = error.HTTPError(h3.CREATE_URL, status, "private error " + KEY, {}, io.BytesIO(raw))
                client = self.client(exception)
                args = self.submit_args(state_dir=self.root / ("http-" + str(status)))
                with self.assertRaises(h3.SafeError) as cm:
                    h3.submit(args, lambda *_: client)
                self.assertEqual(cm.exception.details, {"code": "api_http_error", "http_status": status, "provider_code": "1026"})
                path = next(args.state_dir.glob("*.json"))
                expected = "rejected" if status in {400, 401, 402, 422, 429} else "unknown"
                self.assertEqual(h3.load_job(path)["submission"]["state"], expected)
                h3.submit(args, lambda *_: client)
                self.assertEqual(len(client.api_opener.calls), 1)
                self.assert_private(h3.load_job(path))

    def test_concurrent_duplicate_submits_send_one_post(self):
        barrier = threading.Barrier(2)
        original = h3.prepare
        client = self.client(json_response({"task_id": "task_123"}))

        def prepared(*args, **kwargs):
            value = original(*args, **kwargs)
            barrier.wait(timeout=5)
            return value

        with patch.object(h3, "prepare", side_effect=prepared), ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(h3.submit, self.submit_args(), lambda *_: client) for _ in range(2)]
            values = [f.result(timeout=10) for f in futures]
        self.assertEqual(len(client.api_opener.calls), 1)
        self.assertEqual(sum(v.get("reused_existing", False) for v in values), 1)

    def test_status_wait_resumes_existing_task_and_records_whitelisted_fields(self):
        path, _ = self.accepted()
        final = task()
        final["task"]["usage"]["private_url"] = SIGNED_URL
        final["task"]["private_metadata"] = KEY
        client = self.client(json_response(task("queued")), json_response(task("running")), json_response(final))
        slept = []
        result = h3.status(self.status_args(path, wait=True), lambda *_: client, sleep=slept.append, monotonic=lambda: 0)
        self.assertEqual(result["status"], "succeeded")
        self.assertEqual(slept, [10, 10])
        self.assertEqual([r.method for r in client.api_opener.calls], ["GET"] * 3)
        self.assertEqual(client.api_opener.calls[0].full_url, h3.QUERY_URL + "task_123")
        record = h3.load_job(path)
        self.assertTrue(record["observed"]["download_available"])
        self.assertNotIn("private_url", record["observed"]["usage"])
        self.assert_private(result)
        self.assert_private(record)

    def test_poll_deadline_keeps_task_resumable(self):
        path, _ = self.accepted()
        client = self.client(json_response(task("running")))
        times = iter([0, 601])
        with self.assertRaises(h3.SafeError) as cm:
            h3.status(self.status_args(path, wait=True), lambda *_: client, monotonic=lambda: next(times))
        self.assertEqual(cm.exception.details["code"], "poll_deadline_reached")
        self.assertEqual(h3.load_job(path)["task_id"], "task_123")
        result = h3.status(self.status_args(path), lambda *_: self.client(json_response(task())))
        self.assertEqual(result["status"], "succeeded")

    def test_failed_and_cancelled_tasks_are_recorded_without_private_messages(self):
        path, _ = self.accepted()
        for state in ["failed", "cancelled"]:
            client = self.client(json_response(task(state, error={"code": "1026", "message": KEY + SIGNED_URL + "raw-private-message"})))
            result = h3.status(self.status_args(path, wait=True), lambda *_: client)
            self.assertEqual(result["status"], state)
            self.assertEqual(result["observed"]["provider_code"], "1026")
            self.assert_private(result)
            self.assert_private(h3.load_job(path))

    def test_wrong_model_settings_id_status_or_kind_cannot_succeed(self):
        path, _ = self.accepted()
        for changes in [{"model": "MiniMax-Hailuo-2.3"}, {"resolution": "2K"}, {"duration": 6}, {"duration": 8.0}, {"id": "another_task"}, {"status": "Success"}, {"ratio": "9:16"}, {"task_type": "regeneration"}, {"modality": "text"}]:
            with self.subTest(fields=list(changes)):
                client = self.client(json_response(task(**changes)))
                with self.assertRaises(h3.SafeError):
                    h3.status(self.status_args(path), lambda *_: client)
        client = self.client(json_response({"task": {"id": "task_123", "status": "succeeded", "model": h3.MODEL}}))
        with self.assertRaises(h3.SafeError):
            h3.status(self.status_args(path), lambda *_: client)
        self.assert_private(h3.load_job(path))

    def test_attach_operator_recovered_id_queries_without_post(self):
        body, record = h3.prepare(self.first, None, self.prompt)
        path = self.root / "unknown.json"
        record["submission"]["state"] = "unknown"
        h3.save_job(path, record)
        args = argparse.Namespace(job=path, task_id="task_123", env_file=None, timeout=60)
        client = self.client(json_response(task("running")))
        result = h3.attach(args, lambda *_: client)
        self.assertEqual(result["task_id"], "task_123")
        self.assertEqual(h3.load_job(path)["submission"]["state"], "accepted")
        self.assertEqual([r.method for r in client.api_opener.calls], ["GET"])
        with self.assertRaises(h3.SafeError):
            h3.attach(args, lambda *_: client)

    def test_download_has_no_bearer_fresh_query_hash_probe_and_offline_resume(self):
        path, _ = self.accepted()
        raw = b"mock mp4 contents"
        client = self.client(json_response(task()), media=[Response(raw, {"Content-Type": "video/mp4", "Content-Length": str(len(raw))})])
        self.probe_mock.return_value = copy.deepcopy(VIDEO_PROBE)
        result = h3.download(self.download_args(path), lambda *_: client)
        self.assertEqual([r.method for r in client.api_opener.calls], ["GET"])
        req = client.media_opener.calls[0]
        self.assertEqual(req.full_url, SIGNED_URL)
        self.assertIsNone(req.get_header("Authorization"))
        self.assertEqual(result["output"]["sha256"], h3.digest(raw))
        self.assertEqual(result["output"]["ffprobe"]["streams"][0]["height"], 768)
        self.assertFalse(result["output"]["audio_removal_required"])
        self.assert_private(result)
        self.assert_private(h3.load_job(path))
        with patch.object(h3, "read_key", side_effect=AssertionError("no network/key for existing output")):
            resumed = h3.download(self.download_args(path))
        self.assertTrue(resumed["reused_existing"])
        self.assertEqual(self.download_args(path).output.read_bytes(), raw)

    def test_download_audio_is_recorded_for_explicit_removal(self):
        path, _ = self.accepted()
        video = copy.deepcopy(VIDEO_PROBE)
        video["streams"].append({"codec_type": "audio", "codec_name": "aac", "channels": 2, "sample_rate": "48000"})
        self.probe_mock.return_value = video
        client = self.client(json_response(task()), media=[Response(b"mp4", {"Content-Type": "video/mp4"})])
        result = h3.download(self.download_args(path), lambda *_: client)
        self.assertTrue(result["output"]["audio_removal_required"])

    def test_expired_signed_download_can_resume_by_get_without_post(self):
        path, _ = self.accepted()
        exception = error.HTTPError(SIGNED_URL, 403, KEY, {}, io.BytesIO(KEY.encode()))
        client = self.client(json_response(task()), media=[exception])
        with self.assertRaises(h3.SafeError) as cm:
            h3.download(self.download_args(path), lambda *_: client)
        self.assertEqual(cm.exception.details, {"code": "download_http_error", "http_status": 403})
        self.assertFalse(self.download_args(path).output.exists())
        self.assertFalse(list(self.root.glob("*.part")))
        refreshed = task(content={"url": "https://cdn.example.com/video.mp4?signature=new-private"})
        resumed = self.client(json_response(refreshed), media=[Response(b"mp4")])
        self.probe_mock.return_value = copy.deepcopy(VIDEO_PROBE)
        h3.download(self.download_args(path), lambda *_: resumed)
        self.assertEqual([r.method for r in resumed.api_opener.calls], ["GET"])
        self.assertIn("new-private", resumed.media_opener.calls[0].full_url)
        self.assert_private(h3.load_job(path))

    def test_download_bad_length_type_and_limits_leave_no_output(self):
        path, _ = self.accepted()
        cases = [({"Content-Length": "9"}, "download_truncated"), ({"Content-Length": "1025"}, "download_length_invalid"), ({"Content-Length": "bad"}, "download_length_invalid"), ({"Content-Type": "text/html"}, "download_content_type_invalid")]
        for headers, code in cases:
            with self.subTest(code=code):
                client = self.client(json_response(task()), media=[Response(b"mp4", headers)])
                with self.assertRaises(h3.SafeError) as cm:
                    h3.download(self.download_args(path), lambda *_: client)
                self.assertEqual(cm.exception.details["code"], code)
                self.assertFalse(self.download_args(path).output.exists())
                self.assertFalse(list(self.root.glob("*.part")))
        client = self.client(json_response(task()), media=[Response(b"x" * 1025)])
        with self.assertRaises(h3.SafeError) as cm:
            h3.download(self.download_args(path), lambda *_: client)
        self.assertEqual(cm.exception.details["code"], "download_too_large")

    def test_download_bad_probe_duration_ratio_or_container_leaves_no_output(self):
        path, _ = self.accepted()
        cases = ["broken", "duration", "ratio", "container", "frames", "rate"]
        for case in cases:
            with self.subTest(case=case):
                data = copy.deepcopy(VIDEO_PROBE)
                if case == "broken": data["streams"] = []
                if case == "duration": data["format"]["duration"] = "6.000"
                if case == "ratio": data["streams"][0]["width"] = 768
                if case == "container": data["format"]["format_name"] = "image2"
                if case == "frames": data["streams"][0]["nb_read_frames"] = "0"
                if case == "rate": data["streams"][0]["avg_frame_rate"] = "0/0"
                self.probe_mock.return_value = data
                client = self.client(json_response(task()), media=[Response(b"mp4")])
                with self.assertRaises(h3.SafeError):
                    h3.download(self.download_args(path), lambda *_: client)
                self.assertFalse(self.download_args(path).output.exists())
                self.assertFalse(list(self.root.glob("*.part")))
        self.assert_private(h3.load_job(path))

    def test_observed_h3_768p_native_canvas_is_preserved(self):
        path, _ = self.accepted()
        data = copy.deepcopy(VIDEO_PROBE)
        data["streams"][0]["width"] = 1344
        self.probe_mock.return_value = data
        client = self.client(json_response(task()), media=[Response(b"native H3 fixture")])
        result = h3.download(self.download_args(path), lambda *_: client)
        self.assertEqual(result["output"]["ffprobe"]["streams"][0]["width"], 1344)
        self.assertEqual(result["output"]["ffprobe"]["streams"][0]["height"], 768)
        self.assertEqual(self.download_args(path).output.read_bytes(), b"native H3 fixture")

    def test_native_canvas_exception_does_not_accept_other_wrong_ratios(self):
        for width, height, resolution in [(1280, 768, "768P"), (768, 1344, "768P"),
                                          (768, 768, "768P"), (1344, 768, "2K")]:
            with self.subTest(width=width, height=height, resolution=resolution):
                data = copy.deepcopy(VIDEO_PROBE)
                data["streams"][0].update(width=width, height=height)
                self.probe_mock.return_value = data
                with self.assertRaises(h3.SafeError) as caught:
                    h3.verify_output(self.root / "fixture.mp4", {"resolution": resolution, "duration": 8})
                self.assertEqual(caught.exception.details["code"], "output_ratio_invalid")

    def test_existing_output_is_never_overwritten(self):
        path, _ = self.accepted()
        output = self.download_args(path).output
        output.write_bytes(b"the operator's old output")
        with patch.object(h3, "read_key", side_effect=AssertionError("no key reads")), self.assertRaises(h3.SafeError) as cm:
            h3.download(self.download_args(path))
        self.assertEqual(cm.exception.details["code"], "output_exists")
        self.assertEqual(output.read_bytes(), b"the operator's old output")

    def test_download_before_success_and_missing_url_are_safe(self):
        path, _ = self.accepted()
        for reply in [task("running"), task("failed"), task(content={})]:
            client = self.client(json_response(reply))
            with self.assertRaises(h3.SafeError):
                h3.download(self.download_args(path), lambda *_: client)
            self.assertEqual(client.media_opener.calls, [])

    def test_no_redirect_replays_api_post_and_media_redirect_drops_auth(self):
        req = request.Request(h3.CREATE_URL, data=b"{}", headers={"Authorization": "Bearer " + KEY}, method="POST")
        self.assertIsNone(h3.NoRedirect().redirect_request(req, None, 307, "", {}, "https://other.example/post"))
        forwarded = h3.MediaRedirect().redirect_request(req, None, 302, "", {}, SIGNED_URL)
        self.assertEqual(forwarded.method, "GET")
        self.assertIsNone(forwarded.get_header("Authorization"))
        with self.assertRaises(h3.SafeError):
            h3.MediaRedirect().redirect_request(req, None, 302, "", {}, "http://other.example/video.mp4")
        with self.assertRaises(h3.SafeError):
            h3.MediaRedirect(KEY).redirect_request(req, None, 302, "", {}, "https://cdn.example.com/video?key=" + KEY)

    def test_invalid_download_urls_never_receive_a_request(self):
        for url in ["http://cdn.example/video", "https://user:password@cdn.example/video", "https://cdn.example/video#private", "https://[malformed/video", "https://cdn.example/video?api_key=" + KEY]:
            with self.subTest(kind=url.split(":")[0]):
                client = self.client()
                with self.assertRaises(h3.SafeError):
                    client.download(url, self.root / "unused.mp4")
                self.assertEqual(client.media_opener.calls, [])

    def test_literal_dotenv_uses_only_named_key_no_execution_or_interpolation(self):
        marker = self.root / "should-not-exist"
        env_file = self.root / "test.env"
        env_file.write_text('OTHER=$(touch ' + str(marker) + ')\nexport MINIMAX_API_KEY="literal-${OTHER}-`id`" # comment\n')
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(h3.read_key(env_file), "literal-${OTHER}-`id`")
        self.assertFalse(marker.exists())
        self.assertEqual(h3.read_key(env_file), KEY)  # Existing process env wins.

    def test_invalid_env_is_safe_and_raw_contents_are_not_printed(self):
        env_file = self.root / "test.env"
        for text in ['', 'MINIMAX_API_KEY="unterminated ' + KEY, 'MINIMAX_API_KEY=x\nMINIMAX_API_KEY=y', 'MINIMAX_API_KEY="embedded space ' + KEY + '"']:
            env_file.write_text(text)
            with patch.dict(os.environ, {}, clear=True), self.assertRaises(h3.SafeError) as cm:
                h3.read_key(env_file)
            self.assert_private(cm.exception.details)

    def test_input_validation_precedes_auth_or_submission(self):
        for duration in [3, 16, 8.5, True]:
            with self.subTest(duration=duration), self.assertRaises(h3.SafeError):
                h3.prepare(self.first, None, self.prompt, duration)
        with self.assertRaises(h3.SafeError):
            h3.prepare(self.first, None, self.prompt, take_id="../../escape")
        for text in [" ", "x" * 7001]:
            self.prompt.write_text(text)
            with self.assertRaises(h3.SafeError):
                h3.prepare(self.first, None, self.prompt)
        self.prompt.write_text(PROMPT)
        for dimensions in [(255, 256), (6000, 3375), (1536, 1024)]:
            self.probe_mock.return_value = {"streams": [{"codec_type": "video", "width": dimensions[0], "height": dimensions[1]}], "format": {}}
            with self.assertRaises(h3.SafeError):
                h3.prepare(self.first, None, self.prompt)
        self.probe_mock.side_effect = [IMAGE_PROBE, {"streams": [{"codec_type": "video", "width": 1920, "height": 1080}]}]
        with self.assertRaises(h3.SafeError) as cm:
            h3.prepare(self.first, None, self.prompt)
        self.assertEqual(cm.exception.details["code"], "frame_dimensions_mismatch")

    def test_request_body_and_image_limits_checked_locally(self):
        with patch.object(h3, "MAX_IMAGE_BYTES", 5), self.assertRaises(h3.SafeError) as cm:
            h3.prepare(self.first, None, self.prompt)
        self.assertEqual(cm.exception.details["code"], "image_too_large")
        with patch.object(h3, "MAX_BODY_BYTES", 5), self.assertRaises(h3.SafeError) as cm:
            h3.prepare(self.first, None, self.prompt)
        self.assertEqual(cm.exception.details["code"], "request_body_too_large")

    def test_ffprobe_output_is_whitelisted_and_errors_do_not_echo_stderr(self):
        # Exercise the real probe wrapper underneath this class's image-probe mock.
        original_probe = self.probe.temp_original
        raw = copy.deepcopy(VIDEO_PROBE)
        raw["format"]["filename"] = KEY
        raw["streams"][0]["tags"] = {"private": SIGNED_URL}
        completed = argparse.Namespace(returncode=0, stdout=json.dumps(raw).encode(), stderr=b"")
        with patch.object(h3.subprocess, "run", return_value=completed):
            value = original_probe(self.first, count_frames=True)
        self.assert_private(value)
        completed.stderr = KEY.encode()
        with patch.object(h3.subprocess, "run", return_value=completed), self.assertRaises(h3.SafeError) as cm:
            original_probe(self.first)
        self.assertEqual(cm.exception.details, {"code": "ffprobe_failed"})

    def test_cli_errors_and_failed_exit_codes_are_safe(self):
        stderr = io.StringIO()
        with patch("sys.stderr", stderr):
            self.assertEqual(h3.main(["status", "--job", "missing", "--not-an-option", KEY]), 2)
        self.assert_private(stderr.getvalue())
        self.assertEqual(json.loads(stderr.getvalue())["error"]["code"], "arguments_invalid")
        result = {"status": "failed", "submission": "accepted"}
        with patch.object(h3, "status", return_value=result), patch("sys.stdout", io.StringIO()):
            self.assertEqual(h3.main(["status", "--job", "unused"]), 3)


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "offline media smoke needs ffmpeg/ffprobe")
class OfflineMediaTests(unittest.TestCase):
    def test_real_png_cli_dry_run_and_decoded_mp4_download_with_audio(self):
        """Synthetic solid frames only; no artwork, game files, key, or API."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first, prompt, source = root / "fixture.png", root / "prompt.txt", root / "fixture.mp4"

            def chunk(kind, raw):
                return struct.pack(">I", len(raw)) + kind + raw + struct.pack(">I", zlib.crc32(kind + raw))

            width, height = 1536, 864
            raw = (b"\0" + b"\x20\x40\x60" * width) * height
            first.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))
            prompt.write_text(PROMPT)
            script = Path(h3.__file__).resolve()
            # An explicitly minimal child environment has no MINIMAX_API_KEY.
            result = subprocess.run([sys.executable, str(script), "submit", "--first-frame", str(first), "--prompt-file", str(prompt), "--state-dir", str(root / "unused-jobs"), "--env-file", str(root / "never-read.env"), "--dry-run"], env={"PATH": "/usr/bin:/bin"}, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            preview = json.loads(result.stdout)
            self.assertTrue(preview["dry_run"])
            self.assertEqual(preview["inputs"][0]["width"], 1536)
            self.assertFalse((root / "unused-jobs").exists())
            subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i", "color=c=black:s=1366x768:r=24:d=8", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-shortest", "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-c:a", "aac", str(source)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
            body, record = h3.prepare(first, None, prompt)
            record["task_id"] = "task_123"
            record["submission"]["state"] = "accepted"
            path = root / "job.json"
            h3.save_job(path, record)
            client = h3.Client(KEY)
            client.api_opener = Opener(json_response(task()))
            client.media_opener = Opener(Response(source.read_bytes(), {"Content-Type": "video/mp4", "Content-Length": str(source.stat().st_size)}))
            args = argparse.Namespace(job=path, output=root / "download.mp4", env_file=None, timeout=60, max_bytes=h3.MAX_DOWNLOAD_BYTES)
            with patch.dict(os.environ, {"MINIMAX_API_KEY": KEY}, clear=True), patch.object(request.OpenerDirector, "open", side_effect=AssertionError("real HTTP forbidden")):
                output = h3.download(args, lambda *_: client)
            self.assertEqual(output["output"]["sha256"], h3.file_digest(source))
            self.assertTrue(output["output"]["audio_removal_required"])
            video = next(s for s in output["output"]["ffprobe"]["streams"] if s["codec_type"] == "video")
            self.assertEqual(video["nb_read_frames"], "192")
            self.assertEqual(video["avg_frame_rate"], "24/1")
            for forbidden in [KEY, SIGNED_URL, PROMPT, "base64"]:
                self.assertNotIn(forbidden, path.read_text())


if __name__ == "__main__":
    unittest.main()
