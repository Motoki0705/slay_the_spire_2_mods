#!/usr/bin/env python3
"""Build measured context rigs from immutable art in a separate input root.

uv run --no-project --with pillow --with shapely==2.1.2 python tools/assets/build_contextual_rigs.py
No images are written. All inputs are checked before any rig is replaced.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path

from PIL import Image
import shapely
from shapely.geometry import Point, Polygon

from compile_rigs import validate_context
from weapon_mesh import generate_mesh, generate_underlays, polygon_parts, rig_text, starter_mesh

ROOT = Path(__file__).resolve().parents[2]
CHARACTERS = ("ironclad", "silent", "regent", "necrobinder", "defect")
SURFACES = ("combat", "merchant", "rest")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def owned(root: Path, relative: str) -> Path:
    path = root / relative
    if Path(relative).is_absolute() or ".." in Path(relative).parts or path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"Path escapes its root: {relative}")
    return path


def compact_weights(weights: dict) -> dict:
    values = {name: round(value, 12) for name, value in sorted(weights.items()) if value > 1e-10}
    total = sum(values.values())
    return {name: value / total for name, value in values.items()}


def protect_regions(mesh: dict, regions: list[dict], weapon_bone: str = "") -> dict:
    """Refine rigid cores and soft borders without welding the weapon's open seam.

    Face/boot/palm polygons use one bone, surrounded by a blended ring. Every
    triangle inside a core is rigid, not merely the sampled core vertices.
    """
    zones = []
    for region in regions:
        core = Polygon(region["polygon"])
        width = region["blend_px"]
        if not core.is_valid or core.area <= 0 or not math.isfinite(width) or width <= 0:
            raise ValueError("Invalid rigid region/border")
        zones.append((region["bone"], core, core.buffer(width, join_style="mitre", mitre_limit=2)))
    output = dict(mesh, vertices=[], uv=[], weights=[], triangles=[])
    lookup = {}
    for indices in mesh["triangles"]:
        vertices = [mesh["vertices"][i] for i in indices]
        source_weights = [mesh["weights"][i] for i in indices]
        cell = Polygon(vertices)
        if cell.area < 1e-9:
            raise ValueError("Degenerate input triangle")
        is_weapon = bool(weapon_bone) and all(w == {weapon_bone: 1.0} for w in source_weights)
        active = [] if is_weapon else [z for z in zones if cell.intersects(z[2])]
        pieces = [cell]
        for _, core, border in active:
            for boundary in (core, border):
                split = []
                for piece in pieces:
                    split.extend(polygon_parts(piece.intersection(boundary)))
                    split.extend(polygon_parts(piece.difference(boundary)))
                pieces = split
        a, b, c = vertices
        denominator = (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0])

        def vertex(point):
            x, y = point
            v = ((x-a[0])*(c[1]-a[1]) - (y-a[1])*(c[0]-a[0])) / denominator
            w = ((b[0]-a[0])*(y-a[1]) - (b[1]-a[1])*(x-a[0])) / denominator
            factors = [1-v-w, v, w]
            weights, uv = {}, [0.0, 0.0]
            for factor, index, source in zip(factors, indices, source_weights):
                for bone, weight in source.items():
                    weights[bone] = weights.get(bone, 0) + factor*weight
                for axis in (0, 1):
                    uv[axis] += factor*mesh["uv"][index][axis]
            location = Point(point)
            rigid = next((bone for bone,core,_ in active if location.distance(core)<0.000002), None)
            if rigid is not None:
                # A neighboring limb's soft border must not soften a rigid core.
                weights = {rigid: 1.0}
            else:
                for bone, core, border in active:
                    if border.covers(location):
                        inside, outside = location.distance(core), location.distance(border.boundary)
                        alpha = outside / (inside+outside)
                        weights = {key: value*(1-alpha) for key, value in weights.items()}
                        weights[bone] = weights.get(bone, 0) + alpha
            weights = compact_weights(weights)
            uv = [round(value, 6) for value in uv]
            key = (tuple(point), tuple(uv), tuple((k, round(v, 10)) for k, v in weights.items()))
            if key not in lookup:
                lookup[key] = len(output["vertices"])
                output["vertices"].append(point)
                output["uv"].append(uv)
                output["weights"].append(weights)
            return lookup[key]

        for piece in pieces:
            for face in shapely.constrained_delaunay_triangles(piece).geoms:
                points = [tuple(round(v, 6) for v in p) for p in list(face.exterior.coords)[:3]]
                if Polygon(points).area < 1e-9:
                    continue
                output["triangles"].append([vertex(p) for p in points])
    if len(output["vertices"]) > 4096 or len(output["triangles"]) > 8192:
        raise ValueError("Refined mesh exceeds runtime limits")
    return output


def channel(*keys):
    return [[0, 0, 0, 0], *[list(key) for key in keys], [1, 0, 0, 0]]


def action_clips(entry: dict) -> dict:
    """Local actions on a drawn pose; ambient remains contextual_v02.

    Explicit clips name measured hands, bypassing the legacy hand swap. Units
    scale from the 1536px canvas. No original timing/event/actor is changed.
    """
    rig = entry["rig"]
    action = entry.get("action", {})
    hand = action.get("hand", rig["weapon_hand"])
    free = "hand_r" if hand == "hand_l" else "hand_l"
    scale = rig["canvas"][1] / 1536
    seated = entry["surface"] != "combat" or entry["character"] == "regent"
    amplitude = action.get("amplitude", 1.0) * (0.35 if entry["surface"] != "combat" else 1.0)
    rotation = action.get("rotation", 4.0)

    def strike(power):
        clip = {
            "chest": channel((0.16,-4*amplitude,1,-0.45),(0.34,9*amplitude,-2,0.8*power)),
            hand: channel((0.16,-8*amplitude,-4,-rotation*0.5),(0.34,24*amplitude*power,-8*power,rotation*power),(0.72,5*amplitude,0,0.5)),
            "head": channel((0.34,-1,0,-0.6*power)),
        }
        if action.get("two_hands"):
            clip[free] = deepcopy(clip[hand])
        return clip

    cast = {
        "chest": channel((0.4,1,-4,-0.6)),
        free: channel((0.3,9*amplitude,-10,-2),(0.65,7*amplitude,-6,-1)),
        "head": channel((0.4,0,-1,-0.7)),
    }
    if action.get("kind") in ("command", "mechanical"):
        cast[hand] = cast.pop(free)
    death = {
        "chest": [[0,0,0,0],[0.5,0,8,3],[1,-4,16,7]],
        "head": [[0,0,0,0],[0.6,0,4,3],[1,2,8,6]],
        hand: [[0,0,0,0],[1,-3,10,2]], free: [[0,0,0,0],[1,1,12,-2]],
    }
    if not seated:
        sink = action.get("death_sink",40)
        death["hip"] = [[0,0,0,0],[0.45,0,sink*0.4,-0.3],[1,-6,sink,-1]]
    clips = {
        "attack": strike(1), "attack_heavy": strike(1.25), "attack_sovereign": strike(1.25),
        "shiv": {**strike(0.6), free: channel((0.16,-3,-3,-1),(0.34,20*amplitude,-7,2))},
        "cast": cast, "cast_mighty": deepcopy(cast), "process": deepcopy(cast),
        "hurt": {"chest": channel((0.18,-10,3,-1.8),(0.58,-3,1,-0.5)), "head": channel((0.18,-2,1,-1.2))},
        "die": death,
    }
    if action.get("two_hands"):
        # Paired-grip flattened artwork cannot reveal an independently released hand.
        for name, power in (("cast",0.45),("cast_mighty",0.6),("process",0.45)):
            clips[name] = strike(power)
    for clip in clips.values():
        for keys in clip.values():
            for key in keys:
                key[1] *= scale
                key[2] *= scale
    clips.update(deepcopy(rig.get("clips", {})))
    if action.get("grounded_weapon"):
        for clip in clips.values():
            clip.pop(rig["weapon_hand"], None)
    for bone in entry.get("fixed_bones", []):
        for clip in clips.values():
            clip.pop(bone, None)
    return clips


def make_rig(entry: dict) -> dict:
    rig = deepcopy(entry["rig"])
    rig.update(schema=1, body=f"res://PopSpireWomen/art/{entry['character']}/{entry['image']}",
               surface=entry["surface"], motion_profile="contextual_v02")
    rig["clips"] = action_clips(entry)
    if entry.get("weapon"):
        rule = dict(entry["weapon"], canvas=rig["canvas"], bone=rig["weapon_hand"])
        mesh, underlays = generate_mesh(rig, rule), generate_underlays(rig, rule)
    else:
        mesh, underlays = starter_mesh(rig), []
    regions = entry.get("rigid_regions", [])
    rig["meshes"] = [protect_regions(m, regions) for m in underlays]
    rig["meshes"].append(protect_regions(mesh, regions, rig["weapon_hand"] if entry.get("weapon") else ""))
    for support in entry.get("supports", []):
        width, height = rig["canvas"]
        uv = [[0,0], [width,0], [width,height], [0,height]]
        sx, sy = support["scale"]
        ox, oy = support["offset"]
        rig["meshes"].append({
            "id": support["id"], "texture": support["texture"], "z": -2,
            "vertices": [[x*sx+ox,y*sy+oy] for x,y in uv], "uv": uv,
            "weights": [{"root":1.0} for _ in uv], "triangles": [[0,1,2],[0,2,3]],
        })
    # Install custom parentage after the reusable generator's default-bone contract.
    if entry.get("bones"):
        rig["bones"] = deepcopy(entry["bones"])
    return rig


def build(input_root: Path, recipes: Path, output_root: Path | None = None) -> list[dict]:
    output_root = output_root or input_root
    data = json.loads(recipes.read_text())
    if data.get("schema") != 1 or not isinstance(data.get("poses"), list):
        raise ValueError("Unsupported context authoring schema")
    if shapely.__version__ != "2.1.2" or shapely.geos_version_string != "3.13.1":
        raise ValueError("Requires Shapely 2.1.2 / GEOS 3.13.1")
    receipts, pending, seen = [], [], set()
    for entry in data["poses"]:
        character, surface = entry["character"], entry["surface"]
        if character not in CHARACTERS or surface not in SURFACES or (character,surface) in seen:
            raise ValueError("Unexpected or duplicate character/surface")
        seen.add((character,surface))
        if Path(entry["image"]).name != entry["image"]:
            raise ValueError("Image must be a filename inside the character's art directory")
        relative = f"mod/assets/PopSpireWomen/art/{character}/{entry['image']}"
        texture = owned(input_root, relative)
        if digest(texture) != entry["image_sha256"]:
            raise ValueError(f"Artwork changed since marker authoring: {character}/{surface}")
        with Image.open(texture) as image:
            if image.mode != "RGBA" or image.size != tuple(entry["rig"]["canvas"]):
                raise ValueError("Expected RGBA matching measured canvas")
            low, high = image.getchannel("A").getextrema()
            if low != 0 or high < 250:
                raise ValueError("Expected transparent background and near-opaque subject")
        for support in entry.get("supports", []):
            reference = support["texture"]
            if not reference.startswith("res://PopSpireWomen/"):
                raise ValueError("Support texture outside owned namespace")
            path = owned(input_root, "mod/assets/"+reference.removeprefix("res://"))
            if digest(path) != support["sha256"]:
                raise ValueError("Support texture changed since registration")
            with Image.open(path) as image:
                if image.size != tuple(entry["rig"]["canvas"]):
                    raise ValueError("Support canvas does not match the body canvas")
        rig = make_rig(entry)
        rig_relative = f"mod/assets/PopSpireWomen/art/{character}/{surface}_rig.json"
        path = owned(output_root, rig_relative)
        validate_context(rig, surface, path)
        payload = rig_text(rig).encode("utf-8")
        pending.append((path, payload))
        receipts.append({"character":character,"surface":surface,"image":relative,"image_sha256":entry["image_sha256"],
                         "rig":rig_relative,"rig_sha256":hashlib.sha256(payload).hexdigest(),
                         "rigid_weapon":bool(entry.get("weapon")),"rigid_regions":[r["id"] for r in entry.get("rigid_regions",[])]})
    receipt = {"schema":1,"recipe_sha256":digest(recipes),"shapely":shapely.__version__,"geos":shapely.geos_version_string,"poses":receipts}
    receipt_path = owned(output_root, "tools/assets/contextual-rigs-receipt.json")
    for path, payload in pending:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, indent=2)+"\n", encoding="utf-8")
    return receipts


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", type=Path, default=ROOT)
    parser.add_argument("--output-root", type=Path, default=ROOT)
    parser.add_argument("--recipes", type=Path, default=ROOT/"tools/assets/contextual-poses.json")
    args = parser.parse_args()
    print(f"Built {len(build(args.input_root.resolve(),args.recipes.resolve(),args.output_root.resolve()))} context rigs; image bytes unchanged.")
