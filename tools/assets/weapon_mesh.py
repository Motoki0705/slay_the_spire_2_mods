#!/usr/bin/env python3
"""Constrain weapon outlines in the existing schema-1 body mesh; never write textures.

Run with: uv run --no-project --with shapely==2.1.2 python tools/assets/weapon_mesh.py
See docs/development/weapon-rig.md for the coordinate and deformation contract.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path

import shapely
from shapely.geometry import Point, Polygon

ROOT = Path(__file__).resolve().parents[2]
MARKERS = ("hip", "chest", "head", "hand_l", "hand_r", "foot_l", "foot_r", "hair", "cloth")
CHARACTERS = ("ironclad", "silent", "necrobinder")
EPS = 0.000002


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(data: object) -> bytes:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def auto_weights(point: tuple, rig: dict) -> dict:
    """The renderer's starter weights, in its stable marker tie order."""
    candidates = []
    for bone in MARKERS:
        distance = math.dist(point, rig["markers"][bone]) / rig["canvas"][1]
        weight = 1 / max(distance, 0.025) ** 4
        if bone in ("hair", "cloth"):
            weight *= 0.22
        candidates.append((bone, weight))
    candidates.sort(key=lambda item: -item[1])
    total = sum(value for _, value in candidates[:3])
    return {bone: value / total for bone, value in candidates[:3]}


def starter_mesh(rig: dict) -> dict:
    width, height = rig["canvas"]
    vertices = [(x * width / 12, y * height / 18) for y in range(19) for x in range(13)]
    triangles = []
    for y in range(18):
        for x in range(12):
            i = y * 13 + x
            triangles.extend(((i, i + 1, i + 13), (i + 1, i + 14, i + 13)))
    return {"id": "body", "texture": rig["body"], "vertices": vertices,
            "uv": vertices, "weights": [auto_weights(p, rig) for p in vertices],
            "triangles": triangles}


def base_weights(point: tuple, rig: dict, base: dict) -> dict:
    """Interpolate the old grid's weights, rather than reassigning nearest markers."""
    x = min(max(point[0] * 12 / rig["canvas"][0], 0), 12)
    y = min(max(point[1] * 18 / rig["canvas"][1], 0), 18)
    col, row = min(int(x), 11), min(int(y), 17)
    u, v = x - col, y - row
    i = row * 13 + col
    if u + v <= 1:
        terms = ((i, 1 - u - v), (i + 1, u), (i + 13, v))
    else:
        terms = ((i + 1, 1 - v), (i + 14, u + v - 1), (i + 13, 1 - u))
    result = {}
    for index, factor in terms:
        for bone, weight in base["weights"][index].items():
            result[bone] = result.get(bone, 0.0) + factor * weight
    return {bone: value for bone, value in result.items() if value > 1e-14}


def regions(rule: dict) -> tuple:
    rigid = Polygon(rule["polygon"])
    if not rigid.is_valid or rigid.is_empty or rigid.area <= 0:
        raise ValueError("Weapon outline must be a simple polygon")
    width = rule["blend_px"]
    if not math.isfinite(width) or width <= 0:
        raise ValueError("blend_px must be positive")
    # Keep the wrist transition local, including at acute outline corners.
    grip = Polygon(rule["grip_polygon"])
    if not grip.is_valid or grip.is_empty or not grip.covers(Point(rule["probes"]["grip"])):
        raise ValueError("Invalid grip outline")
    support = grip.buffer(width, join_style="mitre", mitre_limit=2)
    return rigid, grip, support


def polygon_parts(geometry):
    if geometry.geom_type == "Polygon":
        if geometry.area > 1e-10:
            yield geometry
    elif hasattr(geometry, "geoms"):
        for part in geometry.geoms:
            yield from polygon_parts(part)


def generate_mesh(rig: dict, rule: dict) -> dict:
    if shapely.__version__ != "2.1.2" or shapely.geos_version_string != "3.13.1":
        raise ValueError("Reproduction requires Shapely 2.1.2 / GEOS 3.13.1 (pinned binary wheel)")
    if rig["schema"] != 1 or rig.get("bones") or rig["canvas"] != rule["canvas"]:
        raise ValueError("Expected schema 1, default bones and the authored canvas")
    if rig.get("weapon_hand", "hand_r") != rule["bone"]:
        raise ValueError("Weapon rule and wielding hand disagree")
    base = starter_mesh(rig)
    rigid, grip, support = regions(rule)
    canvas = Polygon(((0, 0), (rig["canvas"][0], 0), tuple(rig["canvas"]), (0, rig["canvas"][1])))
    if not canvas.covers(rigid):
        raise ValueError("Weapon polygon escapes source canvas")
    for name, point in rule["probes"].items():
        if not rigid.covers(Point(point)):
            raise ValueError(f"Weapon probe outside outline: {name}")
    faces = []
    for triangle in base["triangles"]:
        cell = Polygon([base["vertices"][i] for i in triangle])
        body = cell.difference(rigid)
        pieces = (body.difference(support), body.intersection(support), cell.intersection(rigid))
        for kind, piece in enumerate(pieces):
            for part in polygon_parts(piece):
                for face in shapely.constrained_delaunay_triangles(part).geoms:
                    points = tuple((round(x, 6), round(y, 6)) for x, y in list(face.exterior.coords)[:3])
                    faces.append((kind, points))
    # The blade's edge is an open seam, not a skin bridge to nearby boots/clothes.
    # Duplicate UVs at that seam allow the same source texture on both sides with
    # independent transforms. Only the wrist has a continuous weight transition.
    keys = sorted({(kind == 2, point) for kind, points in faces for point in points},
                  key=lambda key: (key[0], key[1][1], key[1][0]))
    vertices = [point for _, point in keys]
    lookup = {key: i for i, key in enumerate(keys)}
    triangles = []
    for kind, points in faces:
        a, b, c = points
        cross = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
        if abs(cross) < 1e-9:
            raise ValueError("Degenerate triangle after coordinate rounding")
        indices = [lookup[(kind == 2,p)] for p in points]
        if cross < 0:
            indices.reverse()
        start = indices.index(min(indices))
        triangles.append((kind, indices[start:] + indices[:start]))
    triangles.sort(key=lambda pair: (pair[0], pair[1]))
    weights = []
    for is_weapon, vertex in keys:
        point = Point(vertex)
        if is_weapon or point.distance(grip) <= EPS:
            weights.append({rule["bone"]: 1.0})
            continue
        source = base_weights(vertex, rig, base)
        alpha = 0.0
        if support.covers(point):
            inside = point.distance(grip)
            outside = point.distance(support.boundary)
            alpha = outside / (inside + outside)
            if outside < EPS:
                alpha = 0.0
        weight = {bone: value * (1 - alpha) for bone, value in source.items()}
        weight[rule["bone"]] = weight.get(rule["bone"], 0.0) + alpha
        weight = {bone: round(value, 12) for bone, value in weight.items() if value > 1e-12}
        total = sum(weight.values())
        weights.append({bone: value / total for bone, value in sorted(weight.items())})
    if len(vertices) > 4096 or len(triangles) > 8192:
        raise ValueError("Generated mesh exceeds renderer limits")
    return {"id": "body", "texture": rig["body"], "vertices": vertices, "uv": vertices,
            "weights": weights, "triangles": [triangle for _, triangle in triangles]}


def rig_text(rig: dict) -> str:
    """Readable metadata and one vertex/weight/triangle per line for reviewable diffs."""
    metadata = deepcopy(rig)
    meshes = metadata.pop("meshes")
    lines = [json.dumps(metadata, indent=2, ensure_ascii=False)[:-2] + ',\n  "meshes": [']
    for mesh_index, mesh in enumerate(meshes):
        lines.append('    {')
        items = list(mesh.items())
        for i, (key, value) in enumerate(items):
            comma = ',' if i + 1 < len(items) else ''
            if isinstance(value, list):
                lines.append(f'      "{key}": [')
                lines.extend('        ' + json.dumps(item, separators=(',', ':')) + (',' if j + 1 < len(value) else '')
                             for j, item in enumerate(value))
                lines.append('      ]' + comma)
            else:
                lines.append(f'      "{key}": ' + json.dumps(value) + comma)
        lines.append('    }' + (',' if mesh_index + 1 < len(meshes) else ''))
    return '\n'.join(lines) + '\n  ]\n}\n'


def generate_underlays(rig: dict, rule: dict) -> list[dict]:
    """Borrow neighboring cloth UVs only underneath the weapon's old occlusion.

    An open seam cannot recover occluded pixels from a flattened PNG. These small,
    explicit atlas patches cover that gap without changing or generating a texture.
    They are hidden by the weapon at rest, and follow the body's starter weights.
    """
    rigid, _, _ = regions(rule)
    base = starter_mesh(rig)
    result = []
    for patch in rule.get("underlays", []):
        for field in ("uv_scale", "uv_offset"):
            if len(patch[field]) != 2 or not all(math.isfinite(value) for value in patch[field]):
                raise ValueError("Invalid underlay UV mapping")
        if min(patch["uv_scale"]) <= 0:
            raise ValueError("Underlay UV scales must be positive")
        area = rigid if "polygon" not in patch else rigid.intersection(Polygon(patch["polygon"]))
        faces = []
        for triangle in base["triangles"]:
            cell = Polygon([base["vertices"][i] for i in triangle])
            for part in polygon_parts(cell.intersection(area)):
                for face in shapely.constrained_delaunay_triangles(part).geoms:
                    points = tuple((round(x, 6), round(y, 6)) for x, y in list(face.exterior.coords)[:3])
                    faces.append(points)
        vertices = sorted({p for face in faces for p in face}, key=lambda p: (p[1], p[0]))
        indices = {p: i for i, p in enumerate(vertices)}
        uv = [[round(p[i] * patch["uv_scale"][i] + patch["uv_offset"][i], 6) for i in range(2)] for p in vertices]
        triangles = sorted([indices[p] for p in face] for face in faces)
        if not triangles or len(vertices) > 4096 or len(triangles) > 8192:
            raise ValueError("Invalid underlay size")
        result.append({"id": patch["id"], "texture": rig["body"], "z": -1,
                       "vertices": vertices, "uv": uv, "weights": [base_weights(p, rig, base) for p in vertices],
                       "triangles": triangles})
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets", type=Path, default=ROOT / "mod/assets")
    parser.add_argument("--rules", type=Path, default=Path(__file__).with_name("weapon-rules.json"))
    parser.add_argument("--write", action="store_true", help="Update only art/<character>/rig.json meshes (default: check)")
    parser.add_argument("--receipt", type=Path, help="Optional reproducible input/output hash receipt")
    args = parser.parse_args()
    rules_bytes = args.rules.read_bytes()
    rules = json.loads(rules_bytes)
    if rules.get("schema") != 1 or rules.get("grid") != [12, 18] or set(rules["characters"]) != set(CHARACTERS):
        raise ValueError("Unexpected weapon rule schema, starter grid or character set")
    pending = []
    receipts = []
    for character in CHARACTERS:
        source = args.assets / "PopSpireWomen/art" / character / "rig.json"
        rig = json.loads(source.read_bytes())
        rule = rules["characters"][character]
        if rig["body"] != f"res://PopSpireWomen/art/{character}/body.png":
            raise ValueError(f"Unexpected source texture for {character}")
        texture = source.with_name("body.png")
        if sha256(texture.read_bytes()) != rule["source_sha256"]:
            raise ValueError(f"Source PNG changed for {character}; re-author and inspect its outline")
        metadata = {key: value for key, value in rig.items() if key != "meshes"}
        mesh = generate_mesh(rig, rule)
        rig["meshes"] = [mesh] + generate_underlays(rig, rule)
        output = rig_text(rig).encode()
        pending.append((source, output))
        receipts.append({"character": character, "source_sha256": rule["source_sha256"],
                         "metadata_sha256": sha256(canonical(metadata)), "rig_sha256": sha256(output),
                         "vertices": sum(len(m["vertices"]) for m in rig["meshes"]),
                         "triangles": sum(len(m["triangles"]) for m in rig["meshes"]),
                         "underlays": len(rig["meshes"]) - 1})
    # Validate all inputs before writing any rig. Never compile or install production rigs here.
    for path, data in pending:
        if args.write:
            path.write_bytes(data)
        elif path.read_bytes() != data:
            raise ValueError(f"Stale weapon mesh: {path}; regenerate with --write")
    receipt = {"schema": 1, "generator_sha256": sha256(Path(__file__).read_bytes()),
               "rules_sha256": sha256(rules_bytes), "shapely": shapely.__version__,
               "geos": shapely.geos_version_string, "rigs": receipts}
    if args.receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
