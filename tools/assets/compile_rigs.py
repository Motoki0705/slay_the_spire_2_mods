#!/usr/bin/env python3
"""Compile production rig variants without changing the artist-owned source rigs."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path

CHARACTERS = ("ironclad", "silent", "regent", "necrobinder", "defect")


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
    for character in CHARACTERS:
        source_root = assets / "PopSpireWomen" / "art" / character
        default_source = source_root / "rig.json"
        for surface in ("combat", "merchant", "select", "rest"):
            source = source_root / f"{surface}_rig.json"
            if not source.exists():
                if surface == "rest":
                    continue
                source = default_source
            source_bytes = source.read_bytes()
            source_data = json.loads(source_bytes)
            if source_data.get("schema") != 1:
                raise ValueError(f"Invalid source rig: {source}")
            common = overrides.get("common", {})
            per_character = overrides.get("characters", {}).get(character, {})
            result = merge(source_data, common)
            result = merge(result, per_character.get("all", {}))
            result = merge(result, per_character.get(surface, {}))
            target = output_root / character / f"{surface}.json"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            receipts.append({
                "character": character,
                "surface": surface,
                "source": str(source.relative_to(assets)),
                "source_sha256": hashlib.sha256(source_bytes).hexdigest(),
                "output": str(target.relative_to(assets)),
                "output_sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
            })
    receipt = {"schema": 1, "overrides_sha256": hashlib.sha256(overrides_path.read_bytes()).hexdigest(), "rigs": receipts}
    (output_root / "build-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipts


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets", type=Path, default=Path("mod/assets"))
    parser.add_argument("--overrides", type=Path, default=Path("tools/assets/rig-overrides.json"))
    args = parser.parse_args()
    result = compile_rigs(args.assets.resolve(), args.overrides.resolve())
    print(f"Compiled {len(result)} production rigs from preserved artist sources.")
