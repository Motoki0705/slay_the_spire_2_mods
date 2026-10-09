#!/usr/bin/env python3
"""Stage unmodified production textures and run the real Godot weapon renderer."""

import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from PIL import Image, ImageChops
import numpy as np
import shapely
from shapely.geometry import Point, Polygon, box
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("animation_checks", ROOT / "tests/animation/run_checks.py")
# run_checks also imports its sibling fixture.
import sys
sys.path.insert(0, str(ROOT / "tests/animation"))
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
spec = importlib.util.spec_from_file_location("weapon_mesh", ROOT / "tools/assets/weapon_mesh.py")
weapon = importlib.util.module_from_spec(spec)
spec.loader.exec_module(weapon)


def mesh_locations(mesh):
    faces = [Polygon([mesh["uv"][i] for i in triangle]) for triangle in mesh["triangles"]]
    return shapely.STRtree(faces), faces


def location(mesh, tree, point):
    candidates = tree.query(Point(point), predicate="intersects")
    if not len(candidates):
        raise AssertionError(f"Point not covered by mesh: {point}")
    indices = mesh["triangles"][int(min(candidates))]
    a, b, c = [mesh["uv"][i] for i in indices]
    cross = lambda u, v: u[0]*v[1]-u[1]*v[0]
    sub = lambda u, v: (u[0]-v[0],u[1]-v[1])
    den = cross(sub(b,a),sub(c,a))
    v = cross(sub(point,a),sub(c,a))/den
    w = cross(sub(b,a),sub(point,a))/den
    return {"indices": indices, "factors": [1-v-w,v,w]}


def geometry_checks(rules, output):
    report, samples = {}, {}
    for character, rule in rules["characters"].items():
        source = ROOT / "mod/assets/PopSpireWomen/art" / character
        rig = json.loads((source / "rig.json").read_text())
        assert weapon.sha256((source / "body.png").read_bytes()) == rule["source_sha256"]
        expected = dict(rig, meshes=[weapon.generate_mesh(rig,rule)]+weapon.generate_underlays(rig,rule))
        assert weapon.rig_text(expected).encode() == (source / "rig.json").read_bytes(), f"Stale mesh: {character}"
        metadata = {key: value for key, value in rig.items() if key != "meshes"}
        regenerated = json.loads(weapon.rig_text(expected))
        assert metadata == {key: value for key, value in regenerated.items() if key != "meshes"}
        base = weapon.starter_mesh(rig)
        mesh = rig["meshes"][0]
        assert mesh["vertices"] == mesh["uv"], "Body and weapon must retain their source pixels"
        tree, faces = mesh_locations(mesh)
        base_tree, _ = mesh_locations(base)
        covered = unary_union(faces)
        canvas = box(0,0,*rig["canvas"])
        missing = canvas.symmetric_difference(covered).area
        overlap = sum(face.area for face in faces)-covered.area
        assert missing < 0.01 and abs(overlap) < 0.01, (character,missing,overlap)
        rigid, grip, support = weapon.regions(rule)
        rigid_triangles = 0
        for face, triangle in zip(faces,mesh["triangles"]):
            assert face.area > 1e-9
            if rigid.covers(face.representative_point()):
                rigid_triangles += 1
                assert all(mesh["weights"][i] == {rule["bone"]:1.0} for i in triangle)
        assert rigid_triangles > 0
        for part in rig["meshes"]:
            assert 3 <= len(part["vertices"]) <= 4096 and 0 < len(part["triangles"]) <= 8192
            for weights in part["weights"]:
                assert all(value >= 0 for value in weights.values()) and abs(sum(weights.values())-1)<1e-9
        underlays = []
        for part in rig["meshes"][1:]:
            area = unary_union([Polygon([part["vertices"][i] for i in t]) for t in part["triangles"]])
            uv = unary_union([Polygon([part["uv"][i] for i in t]) for t in part["triangles"]])
            assert area.difference(rigid.buffer(0.000002)).area < 0.001, "Underlay escapes occluded weapon region"
            # No blade/shaft may be copied into the cloth underlay.
            assert uv.intersection(rigid).area < 0.001, (character,part["id"],"underlay samples weapon")
            assert canvas.covers(uv), "Underlay UVs escape source canvas"
            underlays.append({"id":part["id"],"covered_source_area_px2":area.area})
        pixels = Image.open(source / "body.png").convert("RGBA")
        sites = []
        for y in range(6,rig["canvas"][1],12):
            for x in range(6,rig["canvas"][0],12):
                point = Point(x,y)
                if pixels.getpixel((x,y))[3] < 128 or point.distance(rigid) < 2 or point.distance(support) < 2:
                    continue
                sites.append([location(base,base_tree,(x,y)),location(mesh,tree,(x,y)),[x,y]])
        assert len(sites)>500, "Too few visible body samples"
        samples[character] = sites
        report[character] = {"source_sha256":rule["source_sha256"],"rig_sha256":weapon.sha256((source/"rig.json").read_bytes()),
                             "metadata_sha256":weapon.sha256(weapon.canonical(metadata)),"uncovered_area_px2":missing,
                             "overlap_area_px2":overlap,"rigid_triangles":rigid_triangles,"dense_body_samples":len(sites),
                             "vertices":sum(len(m["vertices"]) for m in rig["meshes"]),
                             "triangles":sum(len(m["triangles"]) for m in rig["meshes"]),"underlays":underlays}
    (output/"geometry.json").write_text(json.dumps(report,indent=2)+"\n")
    return samples


def image_checks(rules, output):
    report = {}
    for character in rules["characters"]:
        before = Image.open(output/f"{character}-neutral-before.png").convert("RGB")
        after = Image.open(output/f"{character}-neutral-after.png").convert("RGB")
        assert before.size == after.size == (1024,1536)
        difference = np.asarray(ImageChops.difference(before,after)).max(axis=2)
        # Small edge differences come from changed triangle rasterization and
        # bilinear texture sampling. A visible cloth patch at rest must fail.
        changed = int((difference>16).sum())
        assert changed < 10, (character,"neutral pixels changed by >16/255",changed)
        assert Image.open(output/f"{character}-before-after.png").size == (1800,1180)
        report[character] = {"pixels_delta_over_16":changed,"max_channel_delta":int(difference.max()),
                             "mean_max_channel_delta":float(difference.mean())}
    (output/"neutral-images.json").write_text(json.dumps(report,indent=2)+"\n")


def input_guard_check(output):
    # A late-character PNG mismatch must fail before writing ANY earlier rig.
    with tempfile.TemporaryDirectory(prefix="input-guard-",dir=output) as folder:
        assets = Path(folder)
        original = {}
        for character in weapon.CHARACTERS:
            source = ROOT/"mod/assets/PopSpireWomen/art"/character
            target = assets/"PopSpireWomen/art"/character
            target.mkdir(parents=True)
            for name in ("body.png","rig.json"):
                shutil.copyfile(source/name,target/name)
            original[character] = (target/"rig.json").read_bytes()
        changed = assets/"PopSpireWomen/art/necrobinder/body.png"
        changed.write_bytes(changed.read_bytes()+b"changed input")
        command = [sys.executable,ROOT/"tools/assets/weapon_mesh.py","--assets",assets,"--write"]
        result = subprocess.run([str(p) for p in command],capture_output=True,text=True,timeout=30)
        assert result.returncode != 0 and "Source PNG changed for necrobinder" in result.stderr
        assert all((assets/"PopSpireWomen/art"/c/"rig.json").read_bytes()==data for c,data in original.items())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--godot", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    rules = json.loads((ROOT/"tools/assets/weapon-rules.json").read_text())
    input_guard_check(output)
    samples = geometry_checks(rules,output)
    with tempfile.TemporaryDirectory(prefix="stage-", dir=output) as folder:
        stage = Path(folder)
        shutil.copyfile(ROOT / "mod/assets/project.godot", stage / "project.godot")
        shutil.copyfile(ROOT / "mod/assets/export_presets.cfg", stage / "export_presets.cfg")
        animation = stage / "PopSpireWomen/animation"
        animation.mkdir(parents=True)
        for name in ("puppet.gd","rig_schema.gd","motion_library.gd"):
            shutil.copyfile(ROOT/"mod/assets/PopSpireWomen/animation"/name,animation/name)
        for character in ("ironclad", "silent", "necrobinder"):
            source = ROOT / "mod/assets/PopSpireWomen/art" / character
            target = stage / "PopSpireWomen/art" / character
            target.mkdir(parents=True)
            for name in ("body.png", "rig.json"):
                shutil.copyfile(source / name, target / name)
            shutil.copytree(source / "layers", target / "layers")
        shutil.copyfile(ROOT / "tools/assets/weapon-rules.json", stage / "weapon-rules.json")
        shutil.copyfile(ROOT / "tests/assets/weapon_render.gd", stage / "weapon_render.gd")
        (stage/"weapon-body-samples.json").write_text(json.dumps(samples))
        helper.run([args.godot, "--headless", "--path", stage, "--editor", "--import"], output / "import.log")
        pack = output / "weapon-fixtures.pck"
        helper.run([args.godot,"--headless","--path",stage,"--export-pack","Resources",pack],output/"export.log")
        host = stage / "empty-host"
        host.mkdir()
        text = helper.run(["xvfb-run", "-a", args.godot, "--path", host, "--main-pack",pack,"--rendering-method", "gl_compatibility",
                           "--audio-driver", "Dummy", "--max-fps", "60", "--script", "res://weapon_render.gd"],
                          output / "weapon-render.log", dict(os.environ, PSW_WEAPON_OUTPUT=str(output)))
        if "FAILURES=0" not in text:
            raise RuntimeError("Godot weapon checks did not complete")
    image_checks(rules,output)
    print(f"Weapon checks passed: {output}; game not launched")


if __name__ == "__main__":
    main()
