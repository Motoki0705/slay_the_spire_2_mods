"""Narrow parsers for the export formats observed in StS2 v0.107.1."""

import json
import math
from pathlib import PurePosixPath
import re
import struct
import zlib

from .pck import ExtractionError, resource_path


def text(data: bytes) -> str:
    try:
        value = data.rstrip(b"\0").decode("utf-8")
    except UnicodeDecodeError as error:
        raise ExtractionError("resource is not UTF-8 text") from error
    if "\0" in value:
        raise ExtractionError("embedded NUL in text resource")
    return value


def json_object(data: bytes) -> dict:
    def constant(value):
        raise ExtractionError(f"non-JSON constant: {value}")

    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ExtractionError(f"duplicate JSON key: {key}")
            result[key] = value
        return result
    try:
        value = json.loads(text(data), object_pairs_hook=pairs, parse_constant=constant)
    except json.JSONDecodeError as error:
        raise ExtractionError("malformed JSON resource") from error
    except RecursionError as error:
        raise ExtractionError("JSON nesting exceeds the supported parser depth") from error
    if not isinstance(value, dict):
        raise ExtractionError("expected a JSON object")
    return value


def sections(data: bytes) -> list[tuple[str, list[str]]]:
    result = []
    for line in text(data).splitlines():
        line = line.strip()
        if line.startswith("[") and line.endswith("]"):
            result.append((line[1:-1], []))
        elif line and not line.startswith(";"):
            if not result:
                raise ExtractionError("expected a Godot text resource section")
            result[-1][1].append(line)
    return result


def quoted(value: str) -> str:
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as error:
        raise ExtractionError("unsupported Godot quoted string") from error
    if not isinstance(parsed, str):
        raise ExtractionError("expected Godot string")
    return parsed


def properties(lines: list[str]) -> dict:
    result = {}
    for line in lines:
        key, sep, value = line.partition("=")
        if not sep:
            continue
        key = key.strip()
        if key in result:
            raise ExtractionError(f"duplicate Godot property: {key}")
        result[key] = value.strip()
    return result


def ext_resources(data: bytes) -> dict:
    result = {}
    for header, _ in sections(data):
        if not header.startswith("ext_resource "):
            continue
        attrs = re.findall(r'(\w+)=("(?:[^"\\]|\\.)*")', header)
        fields = {key: quoted(value) for key, value in attrs}
        if len(fields) != len(attrs) or not {"type", "path", "id"} <= fields.keys():
            raise ExtractionError("unsupported/duplicate ext_resource attributes")
        fields["path"] = resource_path(fields["path"])
        if fields["id"] in result:
            raise ExtractionError("duplicate ext_resource id")
        result[fields["id"]] = fields
    return result


def skeleton_references(data: bytes) -> dict:
    refs = ext_resources(data)
    resource_sections = [lines for header, lines in sections(data) if header == "resource"]
    if len(resource_sections) != 1:
        raise ExtractionError("expected one skeleton data [resource] section")
    props = properties(resource_sections[0])
    result = {}
    for key, expected_type in (("atlas_res", "SpineAtlasResource"),
                               ("skeleton_file_res", "SpineSkeletonFileResource")):
        match = re.fullmatch(r'ExtResource\("([^"\\]+)"\)', props.get(key, ""))
        ref = refs.get(match[1]) if match else None
        if not ref or ref["type"] != expected_type:
            raise ExtractionError(f"invalid skeleton data reference: {key}")
        result[key] = ref["path"]
    return result


def import_target(data: bytes, importer: str, resource_type: str, suffix: str) -> str:
    remaps = [properties(lines) for header, lines in sections(data) if header == "remap"]
    if len(remaps) != 1:
        raise ExtractionError("expected one import [remap] section")
    remap = remaps[0]
    for key, expected in (("importer", importer), ("type", resource_type)):
        if quoted(remap.get(key, '""')) != expected:
            raise ExtractionError(f"unsupported import {key}; expected {expected}")
    target = resource_path(quoted(remap.get("path", '""')))
    if not target.startswith(".godot/imported/") or not target.endswith(suffix):
        raise ExtractionError(f"unexpected imported resource path: {target}")
    return target


def skeleton_header(data: bytes) -> dict:
    # Inspect the 4.2 binary prefix only. Never decode/re-encode weights or timelines.
    if len(data) < 9:
        raise ExtractionError("truncated Spine binary header")
    cursor, length = 8, 0
    for shift in range(0, 35, 7):
        if cursor >= len(data):
            raise ExtractionError("truncated Spine version varint")
        value = data[cursor]
        cursor += 1
        length |= (value & 127) << shift
        if not value & 128:
            break
    else:
        raise ExtractionError("invalid Spine version varint")
    if not 2 <= length <= 64 or cursor + length - 1 + 21 > len(data):
        raise ExtractionError("truncated/invalid Spine version header")
    try:
        version = data[cursor:cursor + length - 1].decode("ascii")
    except UnicodeDecodeError as error:
        raise ExtractionError("invalid Spine version string") from error
    if version != "4.2.43":
        raise ExtractionError(f"unsupported Spine binary version {version!r}; expected 4.2.43")
    cursor += length - 1
    x, y, width, height, reference_scale = struct.unpack_from(">5f", data, cursor)
    nonessential = data[cursor + 20]
    if (not all(math.isfinite(v) for v in (x, y, width, height, reference_scale))
            or width < 0 or height < 0 or reference_scale <= 0 or nonessential not in (0, 1)):
        raise ExtractionError("invalid Spine binary bounds/scale/nonessential header")
    return {"version": version, "export_hash_hex": data[:8].hex(),
            "bounds": {"x": x, "y": y, "width": width, "height": height},
            "reference_scale": reference_scale, "nonessential": bool(nonessential),
            "validation_scope": "binary prefix only; not a full skeleton or timeline parser"}


def atlas(data: bytes, expected_source: str) -> tuple[bytes, dict, list[dict]]:
    wrapper = json_object(data)
    if resource_path(wrapper.get("source_path", "")) != expected_source:
        raise ExtractionError("spatlas source_path does not match the explicit target")
    value = wrapper.get("atlas_data")
    if not isinstance(value, str) or not value.strip() or "\0" in value:
        raise ExtractionError("spatlas has no valid atlas_data string")
    pages, current, page_header = [], None, False
    for line in value.splitlines():
        stripped = line.strip()
        if not stripped:
            current, page_header = None, False
        elif current is None:
            name = resource_path(stripped)
            if stripped != name or not name.endswith(".png"):
                raise ExtractionError(f"unsupported/unsafe atlas page name: {stripped!r}")
            current = {"name": name, "metadata": {}}
            pages.append(current)
            page_header = True
        elif page_header:
            key, sep, val = stripped.partition(":")
            if sep:
                if key in current["metadata"]:
                    raise ExtractionError(f"duplicate atlas page metadata: {key}")
                current["metadata"][key] = val.strip()
            else:
                page_header = False  # First region. Region names may include '/' and spaces.
    if not pages:
        raise ExtractionError("atlas has no pages")
    names = set()
    for page in pages:
        if page["name"].casefold() in names:
            raise ExtractionError("duplicate atlas page name")
        names.add(page["name"].casefold())
        size = page["metadata"].get("size", "")
        if not re.fullmatch(r"\d+\s*,\s*\d+", size):
            raise ExtractionError(f"atlas page has no valid size: {page['name']}")
        page["size"] = [int(part) for part in size.split(",")]
        if not all(0 < v <= 16384 for v in page["size"]):
            raise ExtractionError("atlas page dimensions are outside 1..16384")
        page["texture_path"] = resource_path(str(PurePosixPath(expected_source).parent / page["name"]))
    metadata = {key: wrapper.get(key) for key in
                ("source_path", "normal_texture_prefix", "specular_texture_prefix")}
    return value.encode("utf-8"), metadata, pages


def ctex(data: bytes) -> tuple[bytes, dict]:
    if len(data) < 56 or data[:4] != b"GST2":
        raise ExtractionError("unknown/truncated texture format; expected GST2 CTEX")
    version, width, height, flags = struct.unpack_from("<4I", data, 4)
    if version != 1:
        raise ExtractionError(f"unsupported CTEX version {version}; expected 1")
    allowed_flags = (1 << 22) | (1 << 23) | (1 << 24) | (1 << 26) | (1 << 27)
    if flags & ~allowed_flags or any(data[24:36]):
        raise ExtractionError("unknown CTEX flags/reserved fields")
    encoding, image_width, image_height, mipmaps, image_format = struct.unpack_from("<IHHII", data, 36)
    if encoding not in (1, 2):
        raise ExtractionError(f"unsupported CTEX data format {encoding}; only embedded PNG/WebP supported")
    if image_format not in (4, 5):
        raise ExtractionError(f"unsupported CTEX pixel format {image_format}; only RGB8/RGBA8 supported")
    if [width, height] != [image_width, image_height] or not all(0 < v <= 16384 for v in (width, height)):
        raise ExtractionError("CTEX stored/display dimensions differ or are invalid")
    if mipmaps > max(width, height).bit_length() - 1:
        raise ExtractionError("invalid CTEX mipmap count")
    cursor, base = 52, None
    for _ in range(mipmaps + 1):
        if cursor + 4 > len(data):
            raise ExtractionError("truncated CTEX mipmap length")
        size = struct.unpack_from("<I", data, cursor)[0]
        cursor += 4
        if size == 0 or size > len(data) - cursor:
            raise ExtractionError("CTEX payload length is out of range")
        payload = data[cursor:cursor + size]
        if encoding == 2:
            if (len(payload) < 12 or payload[:4] != b"RIFF" or payload[8:12] != b"WEBP"
                    or struct.unpack_from("<I", payload, 4)[0] + 8 != size):
                raise ExtractionError("invalid CTEX WebP RIFF payload")
        elif len(payload) < 24 or payload[:8] != b"\x89PNG\r\n\x1a\n":
            raise ExtractionError("invalid CTEX PNG payload")
        if base is None:
            base = payload
        cursor += size
    if cursor != len(data):
        raise ExtractionError("unexpected trailing CTEX data")
    return base, {"container": "GST2", "version": version,
                  "encoding": "png" if encoding == 1 else "webp",
                  "size": [width, height], "flags": flags,
                  "pixel_format": "RGB8" if image_format == 4 else "RGBA8",
                  "godot_pixel_format": image_format, "mipmaps": mipmaps,
                  "authoring_mipmap": 0}


def png_dimensions(data: bytes) -> list[int]:
    """Validate the decoder's PNG envelope, IHDR CRC, and dimensions."""
    if (len(data) < 33 or data[:8] != b"\x89PNG\r\n\x1a\n"
            or data[8:16] != b"\0\0\0\rIHDR"
            or zlib.crc32(data[12:29]) != struct.unpack_from(">I", data, 29)[0]):
        raise ExtractionError("invalid decoded PNG header")
    return list(struct.unpack_from(">II", data, 16))
