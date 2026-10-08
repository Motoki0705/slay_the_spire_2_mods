"""Bounded, seek-based reader for standalone, unencrypted Godot PCK v3."""

from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
import struct


class ExtractionError(ValueError):
    """An unsupported or unsafe input; safe to display at the CLI."""


def resource_path(value: str) -> str:
    """Validate before using a resource name as a relative filesystem path."""
    if not isinstance(value, str):
        raise ExtractionError("resource path must be a string")
    name = value.removeprefix("res://")
    if (not name or "\\" in name or ":" in name
            or any(ord(c) < 32 or ord(c) == 127 for c in name)
            or any(part in ("", ".", "..") for part in name.split("/"))):
        raise ExtractionError(f"unsafe resource path: {value!r}")
    return name


def hashes(data: bytes) -> dict:
    return {"md5": hashlib.md5(data).hexdigest(),
            "sha256": hashlib.sha256(data).hexdigest()}


@dataclass(frozen=True)
class Entry:
    archive_path: str
    path: str
    offset: int
    size: int
    md5: str
    flags: int


class Pck:
    HEADER_SIZE = 104
    CHUNK_SIZE = 1024 * 1024
    MAX_RESOURCE_SIZE = 64 * 1024 * 1024

    def __init__(self, path: Path):
        self.path = Path(path).resolve(strict=True)
        self.file = self.path.open("rb")
        self.initial_stat = os.fstat(self.file.fileno())
        self.size = self.initial_stat.st_size
        try:
            self._index()
        except BaseException:
            self.file.close()
            raise

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.file.close()

    def _exact(self, size: int) -> bytes:
        data = self.file.read(size)
        if len(data) != size:
            raise ExtractionError("truncated PCK header/directory/resource")
        return data

    def _index(self):
        header = self._exact(self.HEADER_SIZE)
        if header[:4] != b"GDPC":
            raise ExtractionError("unknown PCK magic; only standalone GDPC is supported")
        version, major, minor, patch, flags = struct.unpack_from("<5I", header, 4)
        if version != 3:
            raise ExtractionError(f"unsupported PCK version {version}; expected 3")
        if flags & 1:
            raise ExtractionError("encrypted PCK directory is unsupported")
        if flags != 2:
            raise ExtractionError(f"unsupported PCK flags 0x{flags:x}; expected REL_FILEBASE (2)")
        if (major, minor, patch) != (4, 5, 1):
            raise ExtractionError(f"unsupported Godot version {major}.{minor}.{patch}; expected 4.5.1")
        if any(header[40:]):
            raise ExtractionError("unknown PCK reserved header fields")
        base, directory = struct.unpack_from("<QQ", header, 24)
        if not self.HEADER_SIZE <= base <= self.size:
            raise ExtractionError("PCK file_base is out of range")
        if not self.HEADER_SIZE <= directory <= self.size - 4:
            raise ExtractionError("PCK directory offset is out of range")
        self.file.seek(directory)
        directory_hash = hashlib.sha256()

        def read(size):
            data = self._exact(size)
            directory_hash.update(data)
            return data

        count = struct.unpack("<I", read(4))[0]
        if count > min(1_000_000, (self.size - directory - 4) // 40):
            raise ExtractionError("PCK directory count exceeds its possible range")
        self.entries = {}
        for _ in range(count):
            length = struct.unpack("<I", read(4))[0]
            if not 1 <= length <= 4096:
                raise ExtractionError("PCK path length is outside 1..4096 bytes")
            try:
                archive_path = read(length).rstrip(b"\0").decode("utf-8")
            except UnicodeDecodeError as error:
                raise ExtractionError("invalid UTF-8 in PCK path") from error
            name = resource_path(archive_path)
            offset, size, digest, entry_flags = struct.unpack("<QQ16sI", read(36))
            if entry_flags:
                raise ExtractionError(f"encrypted/removal/unknown PCK entry flags 0x{entry_flags:x}: {name}")
            absolute = base + offset
            if absolute < self.HEADER_SIZE or absolute > self.size or size > self.size - absolute:
                raise ExtractionError(f"PCK resource offset/size is out of range: {name}")
            if name in self.entries:
                raise ExtractionError(f"duplicate PCK resource path: {name}")
            self.entries[name] = Entry(archive_path, name, absolute, size, digest.hex(), entry_flags)
        directory_end = self.file.tell()
        previous = None
        for entry in sorted(self.entries.values(), key=lambda item: (item.offset, item.size)):
            end = entry.offset + entry.size
            if entry.size and entry.offset < directory_end and end > directory:
                raise ExtractionError(f"PCK resource overlaps directory: {entry.path}")
            if previous and entry.size and entry.offset < previous.offset + previous.size:
                # Godot can share an identical payload; partial/contradictory aliases are unsafe.
                if (entry.offset, entry.size, entry.md5) != (previous.offset, previous.size, previous.md5):
                    raise ExtractionError(f"overlapping PCK resources: {entry.path}")
            if entry.size:
                previous = entry
        self.info = {
            "path": str(self.path), "size": self.size, "pck_version": version,
            "godot_version": f"{major}.{minor}.{patch}", "flags": flags,
            "file_base": base, "directory_offset": directory, "entry_count": count,
            "header_sha256": hashlib.sha256(header).hexdigest(),
            "directory_sha256": directory_hash.hexdigest(),
            "whole_file_hash": "not_computed; hashes cover header, directory, and selected resources",
        }

    def assert_unchanged(self):
        def identity(stat):
            return stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns
        if (identity(os.fstat(self.file.fileno())) != identity(self.initial_stat)
                or identity(self.path.stat()) != identity(self.initial_stat)):
            raise ExtractionError("input PCK changed during extraction")

    def read(self, name: str, max_size: int = MAX_RESOURCE_SIZE) -> tuple[bytes, dict]:
        name = resource_path(name)
        try:
            entry = self.entries[name]
        except KeyError as error:
            raise ExtractionError(f"required PCK resource is missing: {name}") from error
        if entry.size > max_size:
            raise ExtractionError(f"selected resource exceeds {max_size} bytes: {name}")
        self.file.seek(entry.offset)
        md5, sha256 = hashlib.md5(), hashlib.sha256()
        chunks, remaining = [], entry.size
        while remaining:
            data = self._exact(min(remaining, self.CHUNK_SIZE))
            chunks.append(data)
            md5.update(data)
            sha256.update(data)
            remaining -= len(data)
        if md5.hexdigest() != entry.md5:
            raise ExtractionError(f"PCK MD5 mismatch: {name}")
        return b"".join(chunks), {
            "archive_path": entry.archive_path, "path": name, "offset": entry.offset,
            "size": entry.size, "flags": entry.flags, "indexed_md5": entry.md5,
            "md5": md5.hexdigest(), "sha256": sha256.hexdigest(),
        }
