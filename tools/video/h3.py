#!/usr/bin/env python3
"""MiniMax-H3 / 768P keyframe production CLI; POST is never retried.

Python 3.10+ standard library, ffprobe, and POSIX advisory file locks (WSL/Linux).
API keys, prompts, media data, error messages, and signed URLs are not recorded.
"""

from __future__ import annotations

import argparse
import base64
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import http.client
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time
from urllib import error, parse, request


MODEL = "MiniMax-H3"
RESOLUTION = "768P"
BILLING_KEYS = {"payg": "MINIMAX_API_KEY", "credits": "MINIMAX_SUBSCRIPTION_KEY"}
CREDITS_PER_USD = 1000
OUTPUT_CREDITS_PER_SECOND = 80
BASE_URL = "https://api.minimax.io"
CREATE_URL = BASE_URL + "/v2/video_generation"
QUERY_URL = BASE_URL + "/v2/query/video_generation/"
STATES = {"queued", "running", "succeeded", "failed", "cancelled"}
TERMINAL = {"succeeded", "failed", "cancelled"}
MAX_IMAGE_BYTES = 30_000_000  # Conservative decimal MB for the published limits.
MAX_BODY_BYTES = 64_000_000
MAX_JSON_BYTES = 1024 * 1024
MAX_DOWNLOAD_BYTES = 256 * 1024 * 1024
TASK_ID = re.compile(r"[A-Za-z0-9_-]{1,128}\Z", re.ASCII)
TAKE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}\Z", re.ASCII)
NUMERIC_CODE = re.compile(r"[0-9]{1,12}\Z", re.ASCII)
USAGE_FIELDS = (
    "total_seconds", "input_seconds", "output_seconds", "input_image_count",
    "input_audio_seconds", "total_tokens", "prompt_tokens", "completion_tokens",
)


class SafeError(Exception):
    """Only fixed local codes and numeric provider/HTTP codes reach the caller."""

    def __init__(self, code, *, http_status=None, provider_code=None, task_id=None):
        super().__init__(code)
        self.details = {"code": code}
        if type(http_status) is int and 100 <= http_status <= 599:
            self.details["http_status"] = http_status
        if isinstance(provider_code, str) and NUMERIC_CODE.fullmatch(provider_code):
            self.details["provider_code"] = provider_code
        if isinstance(task_id, str) and TASK_ID.fullmatch(task_id):
            self.details["task_id"] = task_id


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_digest(path):
    sha = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()


def billing_metadata(mode):
    if not isinstance(mode, str) or mode not in BILLING_KEYS:
        raise SafeError("billing_invalid")
    return {"mode": mode, "key_env": BILLING_KEYS[mode]}


def job_billing(record, selected=None):
    """Missing metadata means legacy payg; malformed/conflicting metadata fails closed."""
    metadata = record.get("billing", billing_metadata("payg"))
    if not isinstance(metadata, dict):
        raise SafeError("job_billing_invalid")
    mode = metadata.get("mode")
    if not isinstance(mode, str) or mode not in BILLING_KEYS or metadata.get("key_env") != BILLING_KEYS[mode]:
        raise SafeError("job_billing_invalid")
    if selected is not None:
        billing_metadata(selected)
        if selected != mode:
            raise SafeError("billing_mismatch")
    return billing_metadata(mode)  # Retain only these fixed, non-secret values.


def read_key(env_file=None, billing="payg"):
    """Parse only the selected billing key; no evaluation or other-key fallback."""
    key_env = billing_metadata(billing)["key_env"]
    value = os.environ.get(key_env)
    if not value and env_file is not None:
        try:
            lines = Path(env_file).read_text(encoding="utf-8-sig").splitlines()
        except (OSError, UnicodeError):
            raise SafeError("env_file_unreadable") from None
        matches = []
        for line in lines:
            match = re.fullmatch(r"\s*(?:export\s+)?" + re.escape(key_env) + r"\s*=(.*)", line)
            if not match:
                continue  # Ignore every other assignment, without evaluating it.
            item = match.group(1).strip()
            if item.startswith(("'", '"')):
                quote = item[0]
                end = item.find(quote, 1)
                if end < 0 or (item[end + 1:].strip() and not item[end + 1:].strip().startswith("#")):
                    raise SafeError("env_file_invalid")
                item = item[1:end]  # Literal contents; deliberately no escape expansion.
            else:
                item = re.split(r"\s+#", item, maxsplit=1)[0].strip()
            matches.append(item)
        if len(matches) != 1:
            raise SafeError("env_file_invalid")
        value = matches[0]
    if not value:
        raise SafeError("api_key_missing")
    if len(value) > 8192 or any(c.isspace() or ord(c) < 32 or ord(c) == 127 for c in value):
        raise SafeError("api_key_invalid")
    return value


class NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None  # Never replay a POST or forward API authorization on redirects.


def media_url(value):
    if not isinstance(value, str):
        raise SafeError("download_url_invalid")
    try:
        parts = parse.urlsplit(value)
    except ValueError:
        raise SafeError("download_url_invalid") from None
    if parts.scheme != "https" or not parts.hostname or parts.username or parts.password or parts.fragment:
        raise SafeError("download_url_invalid")
    return value


class MediaRedirect(request.HTTPRedirectHandler):
    def __init__(self, api_key=None):
        super().__init__()
        self.api_key = api_key

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        media_url(newurl)
        if self.api_key and self.api_key in newurl:
            raise SafeError("download_url_invalid")
        # An explicit new GET with no API headers, including after CDN redirects.
        return request.Request(newurl, method="GET", headers={"Accept": "video/mp4, application/octet-stream"})


def provider_code(value):
    if not isinstance(value, dict):
        return None
    detail = value.get("error", {})
    if not isinstance(detail, dict):
        return None
    code = detail.get("code")
    if isinstance(code, str) and NUMERIC_CODE.fullmatch(code):
        return code
    # The H3 HTTP error schema puts its numeric code at the end of message.
    message = detail.get("message")
    if isinstance(message, str):
        match = re.search(r"\(([0-9]{1,12})\)\s*\Z", message)
        if match:
            return match.group(1)  # Never retain the message itself.
    return None


class Client:
    def __init__(self, api_key, timeout=60):
        self.api_key = api_key
        self.timeout = timeout
        self.api_opener = request.build_opener(NoRedirect())
        self.media_opener = request.build_opener(MediaRedirect(api_key))

    def api(self, method, url, body=None):
        # This tool has no endpoint override; the key goes only to the official host.
        if url != CREATE_URL and not url.startswith(QUERY_URL):
            raise SafeError("api_url_invalid")
        headers = {"Authorization": "Bearer " + self.api_key, "Accept": "application/json"}
        if body is not None:
            headers["Content-Type"] = "application/json"
        req = request.Request(url, data=body, headers=headers, method=method)
        try:
            with self.api_opener.open(req, timeout=self.timeout) as response:
                raw = response.read(MAX_JSON_BYTES + 1)
                if len(raw) > MAX_JSON_BYTES:
                    raise SafeError("api_response_too_large")
                value = json.loads(raw)
        except error.HTTPError as exc:
            code = None
            try:
                raw = exc.read(MAX_JSON_BYTES + 1)
                if len(raw) <= MAX_JSON_BYTES:
                    code = provider_code(json.loads(raw))
            except (ValueError, OSError, http.client.HTTPException):
                pass
            finally:
                exc.close()
            raise SafeError("api_http_error", http_status=exc.code, provider_code=code) from None
        except (error.URLError, OSError, http.client.HTTPException):
            raise SafeError("api_transport_error") from None
        except (ValueError, UnicodeError):
            raise SafeError("api_response_invalid") from None
        if not isinstance(value, dict) or value.get("type") == "error":
            raise SafeError("api_response_invalid", provider_code=provider_code(value))
        return value

    def create(self, body):
        value = self.api("POST", CREATE_URL, body)
        task_id = value.get("task_id")
        if not isinstance(task_id, str) or not TASK_ID.fullmatch(task_id):
            raise SafeError("create_task_id_missing")
        return task_id

    def query(self, task_id):
        if not isinstance(task_id, str) or not TASK_ID.fullmatch(task_id):
            raise SafeError("task_id_invalid")
        return self.api("GET", QUERY_URL + task_id)

    def download(self, url, destination, max_bytes=MAX_DOWNLOAD_BYTES):
        media_url(url)
        if self.api_key in url:
            raise SafeError("download_url_invalid")
        req = request.Request(url, method="GET", headers={"Accept": "video/mp4, application/octet-stream"})
        sha, size = hashlib.sha256(), 0
        try:
            with self.media_opener.open(req, timeout=self.timeout) as response:
                declared = response.headers.get("Content-Length")
                if declared is not None and (not declared.isdigit() or int(declared) > max_bytes):
                    raise SafeError("download_length_invalid")
                kind = response.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
                if kind and kind not in {"video/mp4", "video/quicktime", "application/octet-stream", "binary/octet-stream"}:
                    raise SafeError("download_content_type_invalid")
                with destination.open("wb") as target:
                    while True:
                        chunk = response.read(1024 * 1024)
                        if not chunk:
                            break
                        size += len(chunk)
                        if size > max_bytes:
                            raise SafeError("download_too_large")
                        target.write(chunk)
                        sha.update(chunk)
                    target.flush()
                    os.fsync(target.fileno())
                if not size or (declared is not None and size != int(declared)):
                    raise SafeError("download_truncated")
        except error.HTTPError as exc:
            status = exc.code
            exc.close()
            raise SafeError("download_http_error", http_status=status) from None
        except (error.URLError, OSError, http.client.HTTPException):
            raise SafeError("download_transport_error") from None
        return {"sha256": sha.hexdigest(), "size_bytes": size}


def probe(path, *, count_frames=False):
    fields = "stream=codec_type,codec_name,width,height,r_frame_rate,avg_frame_rate,duration,nb_read_frames,sample_rate,channels:format=duration,format_name"
    command = ["ffprobe", "-v", "error"]
    if count_frames:
        command.append("-count_frames")
    command += ["-show_entries", fields, "-of", "json", "-i", str(path.resolve())]
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120, check=False)
    except FileNotFoundError:
        raise SafeError("ffprobe_missing") from None
    except (OSError, subprocess.TimeoutExpired):
        raise SafeError("ffprobe_failed") from None
    if result.returncode or result.stderr.strip() or len(result.stdout) > MAX_JSON_BYTES:
        raise SafeError("ffprobe_failed")
    try:
        value = json.loads(result.stdout)
    except (ValueError, UnicodeError):
        raise SafeError("ffprobe_failed") from None
    if not isinstance(value, dict) or not isinstance(value.get("streams"), list):
        raise SafeError("ffprobe_failed")
    # Strip filenames, tags, arbitrary stream metadata, and every unneeded field.
    streams = []
    for stream in value["streams"]:
        if not isinstance(stream, dict):
            raise SafeError("ffprobe_failed")
        clean = {}
        for key in ["codec_type", "codec_name"]:
            item = stream.get(key)
            if isinstance(item, str) and re.fullmatch(r"[a-zA-Z0-9_]{1,40}", item):
                clean[key] = item
        for key in ["width", "height", "channels"]:
            item = stream.get(key)
            if type(item) is int and 0 < item <= 100000:
                clean[key] = item
        for key in ["r_frame_rate", "avg_frame_rate", "duration", "nb_read_frames", "sample_rate"]:
            item = stream.get(key)
            if isinstance(item, str) and re.fullmatch(r"[0-9./]{1,40}", item):
                clean[key] = item
        streams.append(clean)
    clean_format = {}
    source_format = value.get("format", {})
    if isinstance(source_format, dict):
        for key, pattern in [("duration", r"[0-9.]{1,40}"), ("format_name", r"[a-zA-Z0-9_,]{1,80}")]:
            item = source_format.get(key)
            if isinstance(item, str) and re.fullmatch(pattern, item):
                clean_format[key] = item
    return {"streams": streams, "format": clean_format}


def image(path, role):
    try:
        if path.stat().st_size > MAX_IMAGE_BYTES:
            raise SafeError("image_too_large")
        raw = path.read_bytes()
    except OSError:
        raise SafeError("image_unreadable") from None
    if not raw or len(raw) > MAX_IMAGE_BYTES:
        raise SafeError("image_size_invalid")
    if raw.startswith(b"\x89PNG\r\n\x1a\n"):
        mime = "image/png"
    elif raw.startswith(b"\xff\xd8\xff"):
        mime = "image/jpeg"
    elif raw.startswith(b"RIFF") and raw[8:12] == b"WEBP":
        mime = "image/webp"
    elif raw[4:8] == b"ftyp" and raw[8:12] in {b"heic", b"heix", b"hevc", b"hevx", b"heim", b"heis", b"mif1", b"msf1"}:
        mime = "image/heic" if raw[8:12].startswith(b"he") else "image/heif"
    else:
        raise SafeError("image_format_invalid")
    data = probe(path)
    videos = [s for s in data["streams"] if s.get("codec_type") == "video"]
    if len(videos) != 1:
        raise SafeError("image_stream_invalid")
    width, height = videos[0].get("width", 0), videos[0].get("height", 0)
    if not (256 <= width <= 5760 and 256 <= height <= 5760 and 0.4 <= width / height <= 2.5):
        raise SafeError("image_dimensions_invalid")
    if abs(width - height * 16 / 9) > 1:
        raise SafeError("image_requires_16_by_9")
    return {"type": "image_url", "image_url": {"url": "data:" + mime + ";base64," + base64.b64encode(raw).decode("ascii")}, "role": role}, {
        "role": role, "sha256": digest(raw), "size_bytes": len(raw), "mime_type": mime, "width": width, "height": height,
    }


def prepare(first_frame, last_frame, prompt_file, duration=8, take_id="take-01", billing="payg"):
    if type(duration) is not int or duration not in range(4, 16):
        raise SafeError("duration_invalid")
    if not TAKE_ID.fullmatch(take_id):
        raise SafeError("take_id_invalid")
    billing_info = billing_metadata(billing)
    try:
        prompt_bytes = prompt_file.read_bytes()
        text = prompt_bytes.decode("utf-8")
    except (OSError, UnicodeError):
        raise SafeError("prompt_unreadable") from None
    if not text.strip() or len(text) > 7000:
        raise SafeError("prompt_length_invalid")
    opening, first_meta = image(first_frame, "first_frame")
    # Same image bytes are sent with both documented roles; this is a loop attempt.
    closing, last_meta = image(last_frame or first_frame, "last_frame")
    if (first_meta["width"], first_meta["height"]) != (last_meta["width"], last_meta["height"]):
        raise SafeError("frame_dimensions_mismatch")
    body = canonical({"model": MODEL, "content": [{"type": "text", "text": text}, opening, closing], "resolution": RESOLUTION, "duration": duration, "ratio": "adaptive"})
    if len(body) > MAX_BODY_BYTES:
        raise SafeError("request_body_too_large")
    record = {
        "schema_version": 1, "request_fingerprint": digest(body), "take_id": take_id,
        "billing": billing_info,
        "requested": {"model": MODEL, "resolution": RESOLUTION, "duration": duration, "ratio": "adaptive", "target_ratio": "16:9"},
        "inputs": [first_meta, last_meta], "prompt": {"sha256": digest(prompt_bytes), "characters": len(text)},
        "estimated_cost": {"currency": "USD", "output_per_second": 0.08, "total": round(duration * 0.08, 2), "credits_per_usd": CREDITS_PER_USD, "output_credits_per_second": OUTPUT_CREDITS_PER_SECOND, "total_credits": duration * OUTPUT_CREDITS_PER_SECOND, "input_images": 2, "price_checked_jst": "2026-10-09"},
        "task_id": None, "submission": {"state": "prepared"}, "errors": [],
    }
    return body, record


@contextmanager
def locked(directory):
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    fd = os.open(directory / ".h3.lock", os.O_RDWR | os.O_CREAT, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        os.close(fd)  # The OS releases this lock, including on process termination.


def sync_directory(directory):
    fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def save_job(path, record):
    record["updated_at"] = now()
    fd, name = tempfile.mkstemp(prefix=".h3-record-", dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(fd, "wb") as target:
            target.write(json.dumps(record, ensure_ascii=False, indent=2).encode("utf-8") + b"\n")
            target.flush()
            os.fsync(target.fileno())
        os.replace(temporary, path)
        sync_directory(path.parent)
    finally:
        temporary.unlink(missing_ok=True)


def load_job(path):
    if path.is_symlink():
        raise SafeError("job_invalid")
    try:
        value = json.loads(path.read_bytes())
    except (OSError, ValueError, UnicodeError):
        raise SafeError("job_unreadable") from None
    if not isinstance(value, dict) or value.get("schema_version") != 1:
        raise SafeError("job_invalid")
    wanted = value.get("requested", {})
    if not isinstance(wanted, dict) or wanted.get("model") != MODEL or wanted.get("resolution") != RESOLUTION or type(wanted.get("duration")) is not int or wanted["duration"] not in range(4, 16):
        raise SafeError("job_invalid")
    if not isinstance(value.get("request_fingerprint"), str) or not re.fullmatch(r"[0-9a-f]{64}", value["request_fingerprint"]):
        raise SafeError("job_invalid")
    task_id = value.get("task_id")
    if task_id is not None and (not isinstance(task_id, str) or not TASK_ID.fullmatch(task_id)):
        raise SafeError("job_invalid")
    value["billing"] = job_billing(value)
    return value


def note_error(record, operation, exc):
    record["errors"] = (record.get("errors", []) + [{"at": now(), "operation": operation, **exc.details}])[-100:]


def summary(path, record, **extras):
    return {"job": str(path), "request_fingerprint": record["request_fingerprint"], "billing": job_billing(record), "task_id": record.get("task_id"), "submission": record["submission"]["state"], "status": record.get("observed", {}).get("status"), **extras}


def submit(args, client_factory=Client):
    body, record = prepare(args.first_frame, args.last_frame, args.prompt_file, args.duration, args.take_id, getattr(args, "billing", "payg"))
    path = args.state_dir.resolve() / (record["request_fingerprint"] + "-" + args.take_id + ".json")
    if args.dry_run:
        return summary(path, record, dry_run=True, requested=record["requested"], inputs=record["inputs"], prompt=record["prompt"], estimated_cost=record["estimated_cost"])
    with locked(path.parent):
        if path.exists():
            existing = load_job(path)
            if existing["request_fingerprint"] != record["request_fingerprint"] or existing.get("take_id") != args.take_id:
                raise SafeError("job_fingerprint_mismatch")
            job_billing(existing, record["billing"]["mode"])
            return summary(path, existing, reused_existing=True)
        client = client_factory(read_key(args.env_file, record["billing"]["mode"]), args.timeout)
        record["created_at"] = now()
        record["submission"] = {"state": "submitting", "started_at": now()}
        # Durable reservation is committed before any possibly paid POST.
        save_job(path, record)
        try:
            record["task_id"] = client.create(body)
        except BaseException as exc:
            safe = exc if isinstance(exc, SafeError) else SafeError("submission_interrupted" if isinstance(exc, KeyboardInterrupt) else "submission_unknown")
            rejected = safe.details.get("http_status") in {400, 401, 402, 403, 404, 405, 422, 429}
            record["submission"]["state"] = "rejected" if rejected else "unknown"
            note_error(record, "submit", safe)
            save_job(path, record)
            raise safe from None
        record["submission"].update(state="accepted", accepted_at=now())
        try:
            save_job(path, record)
        except OSError:
            raise SafeError("job_write_failed_after_accept", task_id=record["task_id"]) from None
        return summary(path, record, estimated_cost=record["estimated_cost"])


def observe(value, record, task_id):
    task = value.get("task")
    if not isinstance(task, dict) or task.get("id") != task_id or task.get("status") not in STATES:
        raise SafeError("task_response_invalid")
    wanted = record["requested"]
    if task.get("model") != MODEL:
        raise SafeError("task_model_mismatch")
    for key in ["resolution", "duration"]:
        if key in task and task[key] != wanted[key]:
            raise SafeError("task_settings_mismatch")
    if "duration" in task and type(task["duration"]) is not int:
        raise SafeError("task_settings_mismatch")
    if task.get("task_type", "generation") != "generation" or task.get("modality", "video") != "video":
        raise SafeError("task_type_mismatch")
    if task.get("ratio", "adaptive") not in {"adaptive", "16:9", ""}:
        raise SafeError("task_ratio_mismatch")
    if task["status"] == "succeeded" and any(key not in task for key in ["resolution", "duration"]):
        raise SafeError("task_settings_missing")
    clean = {"status": task["status"], "model": MODEL, "checked_at": now()}
    for key in ["resolution", "duration", "ratio"]:
        if key in task:
            clean[key] = task[key]
    for key in ["created_at", "updated_at"]:
        if type(task.get(key)) is int and task[key] >= 0:
            clean[key] = task[key]
    usage = task.get("usage", {})
    if isinstance(usage, dict):
        clean["usage"] = {k: usage[k] for k in USAGE_FIELDS if type(usage.get(k)) in {int, float} and math.isfinite(usage[k]) and usage[k] >= 0}
    if task["status"] in {"failed", "cancelled"}:
        clean["provider_code"] = provider_code({"error": task.get("error")})
    content = task.get("content", {})
    url = content.get("url") if isinstance(content, dict) else None
    clean["download_available"] = isinstance(url, str) and bool(url)
    record["observed"] = clean
    return url  # Kept in memory only; never saved or printed.


def refresh(path, record, client, *, attach_id=None):
    task_id = attach_id or record.get("task_id")
    if not task_id:
        raise SafeError("task_id_unknown_use_attach")
    try:
        url = observe(client.query(task_id), record, task_id)
    except SafeError as exc:
        note_error(record, "status", exc)
        save_job(path, record)
        raise
    if attach_id:
        record["task_id"] = attach_id
        record["submission"].update(state="accepted", recovered_at=now())
    save_job(path, record)
    return url


def status(args, client_factory=Client, *, sleep=time.sleep, monotonic=time.monotonic):
    path = args.job.resolve()
    client = None
    selected = getattr(args, "billing", None)
    started = monotonic()
    while True:
        with locked(path.parent):
            record = load_job(path)
            billing = job_billing(record, selected)
            if client is None:
                selected = billing["mode"]  # Keep this key type fixed throughout polling.
                client = client_factory(read_key(args.env_file, selected), args.timeout)
            refresh(path, record, client)
            observed = record["observed"]["status"]
            result = summary(path, record, observed=record["observed"])
        if observed in TERMINAL or not args.wait:
            return result
        remaining = args.max_wait - (monotonic() - started)
        if remaining <= 0:
            raise SafeError("poll_deadline_reached")
        sleep(min(args.interval, remaining))


def attach(args, client_factory=Client):
    if not TASK_ID.fullmatch(args.task_id):
        raise SafeError("task_id_invalid")
    path = args.job.resolve()
    with locked(path.parent):
        record = load_job(path)
        billing = job_billing(record, getattr(args, "billing", None))
        if record.get("task_id"):
            raise SafeError("task_already_attached")
        client = client_factory(read_key(args.env_file, billing["mode"]), args.timeout)
        refresh(path, record, client, attach_id=args.task_id)
        return summary(path, record, observed=record["observed"])


def verify_output(path, wanted):
    data = probe(path, count_frames=True)
    videos = [s for s in data["streams"] if s.get("codec_type") == "video"]
    if len(videos) != 1:
        raise SafeError("output_video_stream_invalid")
    video = videos[0]
    width, height = video.get("width", 0), video.get("height", 0)
    if not width or not height or abs(width / height / (16 / 9) - 1) > 0.01:
        raise SafeError("output_ratio_invalid")
    try:
        duration = float(data["format"]["duration"])
        frames = int(video["nb_read_frames"])
        rate = video["avg_frame_rate"].split("/")
        fps = int(rate[0]) / int(rate[1])
    except (KeyError, ValueError, ZeroDivisionError, IndexError):
        raise SafeError("output_timing_invalid") from None
    if not math.isfinite(duration) or abs(duration - wanted["duration"]) > 0.5 or frames <= 0 or fps <= 0:
        raise SafeError("output_timing_invalid")
    if not any(kind in data["format"].get("format_name", "").split(",") for kind in ["mp4", "mov"]):
        raise SafeError("output_container_invalid")
    return data


def download(args, client_factory=Client):
    path, output = args.job.resolve(), args.output.absolute()
    with locked(path.parent):
        record = load_job(path)
        billing = job_billing(record, getattr(args, "billing", None))
        if output.exists():
            receipt = record.get("output", {})
            if output.is_file() and receipt.get("sha256") == file_digest(output) and receipt.get("size_bytes") == output.stat().st_size:
                return summary(path, record, output=receipt, reused_existing=True)
            raise SafeError("output_exists")
        client = client_factory(read_key(args.env_file, billing["mode"]), args.timeout)
        url = refresh(path, record, client)  # Get a fresh signed URL on every download attempt.
        observed = record["observed"]["status"]
        if observed != "succeeded":
            raise SafeError("task_not_succeeded")
        if not url:
            raise SafeError("download_url_missing")
        output.parent.mkdir(parents=True, exist_ok=True)
        fd, name = tempfile.mkstemp(prefix=".h3-download-", suffix=".part", dir=output.parent)
        os.close(fd)
        temporary = Path(name)
        try:
            receipt = client.download(url, temporary, args.max_bytes)
            receipt["ffprobe"] = verify_output(temporary, record["requested"])
            receipt["audio_removal_required"] = any(s.get("codec_type") == "audio" for s in receipt["ffprobe"]["streams"])
            receipt["downloaded_at"] = now()
            receipt["file"] = str(output)
            # Hard link publishes atomically without overwriting an existing file.
            os.link(temporary, output)
            sync_directory(output.parent)
            record["output"] = receipt
            save_job(path, record)
            return summary(path, record, output=receipt)
        except SafeError as exc:
            note_error(record, "download", exc)
            save_job(path, record)
            raise
        finally:
            temporary.unlink(missing_ok=True)


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise SafeError("arguments_invalid")  # argparse normally echoes raw input.


def positive(value):
    try:
        number = float(value)
    except ValueError:
        raise argparse.ArgumentTypeError("positive number required") from None
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError("positive number required")
    return number


def main(argv=None):
    parser = Parser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True, parser_class=Parser)
    p = commands.add_parser("submit", help="One paid POST, or --dry-run; last frame defaults to first")
    p.add_argument("--first-frame", type=Path, required=True)
    p.add_argument("--last-frame", type=Path)
    p.add_argument("--prompt-file", type=Path, required=True)
    p.add_argument("--state-dir", type=Path, required=True, help="Use one persistent directory for all takes")
    p.add_argument("--duration", type=int, default=8)
    p.add_argument("--take-id", default="take-01", help="Explicit new ID permits another paid take")
    p.add_argument("--dry-run", action="store_true")
    p = commands.add_parser("status", help="GET only; --wait resumes polling an existing task")
    p.add_argument("--job", type=Path, required=True)
    p.add_argument("--wait", action="store_true")
    p.add_argument("--interval", type=positive, default=10)
    p.add_argument("--max-wait", type=positive, default=600)
    p = commands.add_parser("download", help="Fresh GET status, then verified source MP4; never a POST")
    p.add_argument("--job", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--max-bytes", type=int, default=MAX_DOWNLOAD_BYTES)
    p = commands.add_parser("attach", help="Associate an operator-identified task after an ambiguous POST")
    p.add_argument("--job", type=Path, required=True)
    p.add_argument("--task-id", required=True)
    for child in commands.choices.values():
        child.add_argument("--billing", choices=BILLING_KEYS, default="payg" if child is commands.choices["submit"] else None, help="Key type: submit defaults to payg; other commands use recorded job billing")
        child.add_argument("--env-file", type=Path, help="Optional literal dotenv selected key; existing env key takes precedence")
        child.add_argument("--timeout", type=positive, default=60)
    try:
        args = parser.parse_args(argv)
        if args.command == "status" and args.interval < 1:
            raise SafeError("poll_interval_too_short")
        if args.command == "download" and args.max_bytes <= 0:
            raise SafeError("download_limit_invalid")
        result = {"submit": submit, "status": status, "download": download, "attach": attach}[args.command](args)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        if result.get("status") in {"failed", "cancelled"}:
            return 3
        if result.get("submission") in {"unknown", "submitting", "rejected"}:
            return 2
        return 0
    except SafeError as exc:
        print(json.dumps({"error": exc.details}, sort_keys=True), file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print('{"error":{"code":"interrupted_resume_existing_job"}}', file=sys.stderr)
        return 130
    except Exception:
        # Local failures must not echo key-bearing paths, URLs, payloads, or traceback.
        print('{"error":{"code":"local_operation_failed"}}', file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
