#!/usr/bin/env python3
"""Compile production rig variants without changing the artist-owned source rigs."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path

CHARACTERS = ("ironclad", "silent", "regent", "necrobinder", "defect")
SURFACES = ("combat", "merchant", "select", "rest")


def validate_context(data: dict, surface: str, source: Path) -> None:
    """Fail on a present invalid context instead of silently picking another pose.

    Godot's rig_schema remains the full mesh/weights/clip validator at PCK preflight.
    This authoring check catches incomplete rigs and unsafe references before any writes.
    """
    if not isinstance(data, dict) or data.get("schema") != 1:
        raise ValueError(f"Expected complete schema-1 rig: {source}")
    if data.get("surface", surface) != surface:
        raise ValueError(f"Rig surface mismatch ({surface}): {source}")
    if data.get("motion_profile", "legacy_v01") not in {"legacy_v01", "contextual_v02"}:
        raise ValueError(f"Unknown motion_profile: {source}")

    def vector(value):
        return (isinstance(value, list) and len(value) == 2 and
                all(type(n) in (int, float) and math.isfinite(n) for n in value))

    if not vector(data.get("canvas")) or any(n <= 0 or n > 8192 for n in data["canvas"]):
        raise ValueError(f"Invalid rig canvas: {source}")
    if not vector(data.get("origin")) or not isinstance(data.get("markers"), dict):
        raise ValueError(f"Incomplete rig origin/markers: {source}")
    for marker in ("hip", "chest", "head", "hand_l", "hand_r", "foot_l", "foot_r", "hair", "cloth"):
        if not vector(data["markers"].get(marker)):
            raise ValueError(f"Invalid {marker} marker: {source}")
    height = data.get("display_height")
    if type(height) not in (int, float) or not math.isfinite(height) or not 0 < height <= 4096:
        raise ValueError(f"Invalid display_height: {source}")
    paths = [data.get("body")]
    for field in ("layers", "meshes"):
        values = data.get(field, [])
        if not isinstance(values, list) or any(not isinstance(v, dict) for v in values):
            raise ValueError(f"Invalid {field}: {source}")
        paths.extend(v.get("texture") for v in values)
    for path in paths:
        if (not isinstance(path, str) or not path.startswith("res://PopSpireWomen/") or
                "\\" in path or any(p in ("", ".", "..") for p in path[6:].split("/"))):
            raise ValueError(f"Texture reference outside owned namespace: {source}")


def merge(base: dict, overrides: dict) -> dict:
    result = deepcopy(base)
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = merge(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


def compile_rigs(assets: Path, overrides_path: Path) -> list[dict]:
    overrides = json.loads(overrides_path.read_text(encoding="utf-8"))
    if overrides.get("schema") != 1:
        raise ValueError("Expected production rig override schema 1")
    output_root = assets / "PopSpireWomen" / "rigs"
    receipts = []
    outputs = []
    for character in CHARACTERS:
        source_root = assets / "PopSpireWomen" / "art" / character
        default_source = source_root / "rig.json"
        for surface in SURFACES:
            source = source_root / f"{surface}_rig.json"
            if source.is_symlink():
                raise ValueError(f"Symlink rig input refused: {source}")
            if not source.exists():
                if surface == "rest":
                    continue
                source = default_source
            if source.is_symlink() or not source.resolve().is_relative_to(assets.resolve()):
                raise ValueError(f"Rig input escapes assets: {source}")
            source_bytes = source.read_bytes()
            source_data = json.loads(source_bytes)
            validate_context(source_data, surface, source)
            common = overrides.get("common", {})
            per_character = overrides.get("characters", {}).get(character, {})
            result = merge(source_data, common)
            result = merge(result, per_character.get("all", {}))
            result = merge(result, per_character.get(surface, {}))
            validate_context(result, surface, source)
            result["surface"] = surface
            target = output_root / character / f"{surface}.json"
            if target.is_symlink() or not target.resolve().is_relative_to(assets.resolve()):
                raise ValueError(f"Rig output escapes assets: {target}")
            payload = (json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")
            outputs.append((target, payload))
            receipts.append({
                "character": character,
                "surface": surface,
                "source": str(source.relative_to(assets)),
                "source_sha256": hashlib.sha256(source_bytes).hexdigest(),
                "output": str(target.relative_to(assets)),
                "output_sha256": hashlib.sha256(payload).hexdigest(),
                "source_kind": "surface" if source.name == f"{surface}_rig.json" else "legacy_default",
                "motion_profile": result.get("motion_profile", "legacy_v01"),
            })
    receipt_path = output_root / "build-receipt.json"
    if receipt_path.is_symlink() or not receipt_path.resolve().is_relative_to(assets.resolve()):
        raise ValueError("Rig receipt escapes assets")
    # No partial rewrite when a later character contains a bad input.
    for target, payload in outputs:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
    receipt = {"schema": 1, "overrides_sha256": hashlib.sha256(overrides_path.read_bytes()).hexdigest(), "rigs": receipts}
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipts


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets", type=Path, default=Path("mod/assets"))
    parser.add_argument("--overrides", type=Path, default=Path("tools/assets/rig-overrides.json"))
    args = parser.parse_args()
    result = compile_rigs(args.assets.resolve(), args.overrides.resolve())
    print(f"Compiled {len(result)} production rigs from preserved artist sources.")
