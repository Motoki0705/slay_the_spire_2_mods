#!/usr/bin/env python3
"""Offline asset/time/cost model; does not render or call generation APIs."""
from __future__ import annotations

import csv
from decimal import Decimal
import hashlib
import json
import math
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
MOTION = ROOT / "docs/research/motion/evidence"
CHARACTERS = ["ironclad", "silent", "regent", "necrobinder", "defect"]


def read_json(path: Path):
    return json.loads(path.read_text())


def dump(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    policy = read_json(HERE / "production-policy.json")
    providers = read_json(HERE / "provider-specs.json")
    summaries = read_json(MOTION / "spine-summary.json")
    assets = []
    sizing = []
    input_paths = {MOTION / "spine-summary.json", MOTION.parent / "inventory.md"}
    eps = policy["source_duration_ceiling_epsilon"]

    def spine(stem: str) -> dict:
        return next(row for row in summaries if row["resource"].split("/")[-1].startswith(stem + ".skel-"))

    def scene_path(scene: str) -> Path:
        return MOTION / "resources" / scene

    def add(owner: str, entity: str, group: str, stem: str, animation: str,
            loop: bool, scene: str, canvas: list[int], profile: str, notes: str = "") -> None:
        skel = spine(stem)
        motion = next(x for x in skel["animations"] if x["name"] == animation)
        shared_uses = "one entity/animation reused across runtime instances; not duplicated per player/card/target"
        if group == "combat_core":
            shared_uses = {
                "idle_loop": "combat initial idle and player revive fade-to-idle",
                "attack": "normal and multi-hit card actions; TheArchitect player attack",
                "cast": "skill cast; PowerUp also shares cast except Defect",
                "hurt": "combat damage and event combat-layout Hit",
                "die": "combat death; rest/event game-over creates combat visual and shares die",
                "process": "Defect PowerUp; its cast remains separate",
            }.get(animation, "character-specific trigger shared across its card callers")
        elif group == "merchant":
            shared_uses = "combat counterpart may share a generated master if appearance, camera, and pixel density match; shop atlas currently separate"
        elif group == "rest":
            shared_uses = "three act loops may share a pose master if lighting and texture differences can be composited; not assumed in C"
        assets.append({
            "asset_id": f"{group}/{entity}/{animation}",
            "owner": owner, "entity": entity, "group": group,
            "source_animation": animation,
            "source_seconds": motion["duration_seconds"], "loop": loop,
            "source_spine": skel["resource"], "source_scene": scene,
            "target_sprite_canvas": canvas,
            "generation_profile": profile, "shared_runtime_uses": shared_uses, "notes": notes,
        })
        input_paths.add(scene_path(scene))

    extra = {"ironclad": "attack_heavy", "silent": "shiv", "regent": "attack_sovereign",
             "necrobinder": "cast_mighty", "defect": "process"}
    for c in CHARACTERS:
        add(c, c, "select", "characterselect_" + c, "animation", True,
            f"scenes/screens/char_select/char_select_bg_{c}.tscn", [1920,1080], "select",
            "UI and interactive Regent constellation overlay remain separate")
        scene = f"scenes/creature_visuals/{c}.tscn"
        for name in ["idle_loop", "attack", "cast", "hurt", "die", extra[c]]:
            add(c, c, "combat_core", c, name, name.endswith("_loop"), scene,
                policy["sprite_canvases"]["combat"][c], "portrait",
                "die also covers rest/event game-over fallback; maintain independent FX/events")
        add(c, c, "combat_relaxed", c, "relaxed_loop", True, scene,
            policy["sprite_canvases"]["combat"][c], "portrait",
            "Collected Relaxed branch; not a verified victory animation")
        for name in ["relaxed_loop", "die"]:
            add(c, c, "merchant", c, name, name.endswith("_loop"),
                f"scenes/merchant/characters/{c}_merchant.tscn",
                policy["sprite_canvases"]["merchant"][c], "portrait",
                "Same skeleton, separate shop atlas; upper case keeps room appearance separate")
        for name in ["overgrowth_loop", "hive_loop", "glory_loop"]:
            add(c, c, "rest", "restsite_" + c, name, True,
                f"scenes/rest_site/characters/{c}_rest_site.tscn",
                policy["sprite_canvases"]["rest"][c], "portrait",
                "Environment-specific loop; zero-duration light tracks are not videos")
    for name in ["idle_loop", "attack", "attack_poke", "hurt", "die", "dead_loop", "revive"]:
        add("necrobinder", "osty", "osty_combat", "osty", name, name.endswith("_loop"),
            "scenes/creature_visuals/osty.tscn", policy["sprite_canvases"]["combat"]["osty"], "square",
            "Separate actor, HP and state; no unrecorded cast")
    for name in ["overgrowth_loop", "hive_loop", "glory_loop"]:
        add("necrobinder", "osty", "rest", "restsite_osty", name, True,
            "scenes/rest_site/characters/necrobinder_rest_site.tscn",
            policy["sprite_canvases"]["rest"]["osty"], "rest_osty",
            "Separate movable/flippable rest actor")
    for name in ["attack", "attack2"]:
        add("regent", "regent_weapon", "regent_weapon", "regent_weapon", name, False,
            "scenes/creature_visuals/regent.tscn", policy["sprite_canvases"]["regent_weapon"], "portrait",
            "WeaponAnim1 and WeaponAnim2 have distinct tracks; remain independent of main body")
    for name in ["idle_loop", "attack"]:
        add("regent", "sovereign_blade", "sovereign_local", "soveriegn_blade", name, name.endswith("_loop"),
            "scenes/vfx/sovereign_blade.tscn", policy["sprite_canvases"]["sovereign_blade"], "portrait",
            "Optional local sword texture motion only; orbit/target/Forge paths remain code-driven")
    for orb in ["lightning", "frost", "dark", "plasma", "glass"]:
        add("defect", orb + "_orb", "orb_idle", orb + "_orb", "idle_loop", True,
            f"scenes/orbs/orb_visuals/{orb}_orb.tscn", policy["sprite_canvases"]["orb"], "square",
            "Optional orb surface pattern only; do not bake channel/evoke/values into Defect")

    # Static export bounds multiplied by local scene scale, not screen renders
    # or the union of all animated poses. Record line numbers for provenance.
    for c in CHARACTERS + ["osty"]:
        skel = spine(c)
        p = scene_path(f"scenes/creature_visuals/{c}.tscn")
        lines = p.read_text().splitlines()
        start = next(i for i, line in enumerate(lines) if '[node name="Visuals" type="SpineSprite"' in line)
        end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("[node ")), len(lines))
        scale_line = next(i for i in range(start + 1, end) if lines[i].startswith("scale = "))
        scale = [float(x) for x in re.search(r"Vector2\(([^)]+)\)", lines[scale_line]).group(1).split(",")]
        bounds = skel["bounds"]
        sizing.append({"entity": c, "scene": str(p.relative_to(ROOT)),
                       "spine": skel["resource"], "visuals_node_line": start + 1,
                       "scale_line": scale_line + 1, "scale": scale,
                       "serialized_setup_bounds": bounds,
                       "setup_width_height_scene_units": [round(bounds["width"] * scale[0], 3),
                                                          round(bounds["height"] * scale[1], 3)],
                       "target_canvas_pixels": policy["sprite_canvases"]["combat"][c],
                       "status": "Static setup/export reference, not measured display pixels or animation envelope"})

    def plan(source_seconds: float, model: str) -> list[int]:
        limits = providers[model]["duration_seconds"]
        n = max(1, math.ceil((source_seconds - eps) / (limits["maximum"] - policy["handles_seconds"])))
        seconds = max(limits["minimum"], math.ceil(source_seconds / n + policy["handles_seconds"] - eps))
        assert seconds <= limits["maximum"]
        return [seconds] * n

    jobs = []
    for asset in assets:
        prof = policy["generation_profiles"][asset["generation_profile"]]
        for model in ["minimax_h3", "seedance_2_5"]:
            durations = plan(asset["source_seconds"], model)
            res = prof["minimax_resolution" if model == "minimax_h3" else "seedance_resolution"]
            ratio = prof["ratio"]
            if model == "seedance_2_5":
                w, h = providers[model]["output_pixel_dimensions"][res][ratio]
                tps = Decimal(w * h * providers[model]["fps_for_estimation"]) / Decimal(1024)
                rate = Decimal(str(providers[model]["usd_per_million_tokens_without_video"][res])) / Decimal(1000000)
                cost = tps * sum(durations) * rate
                estimate_tokens = tps * sum(durations)
                pixel_status = "official ModelArk dimension table; actual adaptive input may differ"
            else:
                # Pixel dimensions are provisioned targets, not an assertion that
                # every global API result has this exact raster size.
                h3_nominal = {"16:9": [2560,1440], "3:4": [768,1024], "1:1": [768,768], "4:3": [1024,768]}
                w, h = h3_nominal[ratio]
                cost = Decimal(sum(durations)) * Decimal(str(providers[model]["output_usd_per_second"][res]))
                estimate_tokens = Decimal(0)
                pixel_status = "2K16:9 official sample verified; 768P exact API dimensions unconfirmed"
            jobs.append({
                "asset_id": asset["asset_id"], "owner": asset["owner"], "entity": asset["entity"],
                "group": asset["group"], "source_animation": asset["source_animation"],
                "source_seconds": round(asset["source_seconds"], 9), "loop": asset["loop"],
                "model": model, "resolution": res, "ratio": ratio,
                "generation_jobs": len(durations), "requested_seconds_each": "+".join(map(str, durations)),
                "total_output_seconds": sum(durations),
                "production_handles_seconds_per_job": policy["handles_seconds"],
                "target_canvas_width": asset["target_sprite_canvas"][0],
                "target_canvas_height": asset["target_sprite_canvas"][1],
                "generated_frame_width": w, "generated_frame_height": h,
                "generated_frame_dimensions_status": pixel_status,
                "estimated_output_tokens": float(estimate_tokens),
                "output_cost_usd_one_attempt": float(cost),
                "floor_overhead_seconds": round(max(0, limits_min(model) - asset["source_seconds"] - policy["handles_seconds"]), 6) if len(durations) == 1 else 0,
                "source_scene": asset["source_scene"], "source_spine": asset["source_spine"],
                "shared_runtime_uses": asset["shared_runtime_uses"],
                "notes": asset["notes"],
            })

    summaries_out = []
    character_out = []
    for scenario, included in policy["scenario_assets"].items():
        selected_assets = [a for a in assets if a["group"] in included]
        for model in ["minimax_h3", "seedance_2_5"]:
            selected = [x for x in jobs if x["model"] == model and x["group"] in included]
            for attempts in policy["attempt_multipliers"]:
                token_totals = {res: sum(Decimal(str(x["estimated_output_tokens"])) for x in selected if x["resolution"] == res) * attempts
                                for res in ["480p", "720p", "1080p"]}
                totals = {
                    "scenario": scenario, "model": model, "attempt_multiplier": attempts,
                    "distinct_assets": len(selected_assets),
                    "generation_tasks": sum(x["generation_jobs"] for x in selected) * attempts,
                    "requested_output_seconds": sum(x["total_output_seconds"] for x in selected) * attempts,
                    "select_seconds": sum(x["total_output_seconds"] for x in selected if x["group"] == "select") * attempts,
                    "sprite_seconds": sum(x["total_output_seconds"] for x in selected if x["group"] != "select") * attempts,
                    "estimated_720p_tokens": float(token_totals["720p"]),
                    "estimated_1080p_tokens": float(token_totals["1080p"]),
                    "output_cost_usd": float(sum(Decimal(str(x["output_cost_usd_one_attempt"])) for x in selected) * attempts),
                    "reference_image_count_per_task": policy["base_reference_images_per_task"],
                    "reference_video_seconds_per_task": 0,
                    "reference_input_cost_usd": 0,
                }
                summaries_out.append(totals)
            for owner in CHARACTERS:
                own = [x for x in selected if x["owner"] == owner]
                character_out.append({"scenario": scenario, "model": model, "character": owner,
                                      "distinct_assets": len(own),
                                      "generation_tasks_one_attempt": sum(x["generation_jobs"] for x in own),
                                      "output_seconds_one_attempt": sum(x["total_output_seconds"] for x in own),
                                      "output_cost_usd_one_attempt": float(sum(Decimal(str(x["output_cost_usd_one_attempt"])) for x in own))})

    # Useful bounded variants, not extra required assets.
    variants = []
    for model in ["minimax_h3", "seedance_2_5"]:
        select_jobs = [x for x in jobs if x["model"] == model and x["group"] == "select"]
        source_price = sum(Decimal(str(x["output_cost_usd_one_attempt"])) for x in select_jobs)
        for attempts in [1,3,5]:
            if model == "minimax_h3":
                short_cost = Decimal(35) * Decimal("0.13")
            else:
                short_cost = Decimal(35) * Decimal(1920 * 1080 * 24) / Decimal(1024) * Decimal("11.7") / Decimal(1000000)
            poc = [x for x in jobs if x["model"] == model and x["group"] == "combat_core" and x["owner"] == "ironclad"
                   and x["source_animation"] in ["idle_loop", "attack", "hurt", "die"]]
            poc_cost = sum(Decimal(str(x["output_cost_usd_one_attempt"])) for x in poc)
            variants.extend([
                {"variant": "A_short_loop_6s_plus_handles", "model": model, "attempt_multiplier": attempts,
                 "assets": 5, "tasks": 5 * attempts, "output_seconds": 35 * attempts, "output_cost_usd": float(short_cost * attempts)},
                {"variant": "A_plus_Ironclad_four_motion_PoC", "model": model, "attempt_multiplier": attempts,
                 "assets": 9, "tasks": 9 * attempts, "output_seconds": 68 * attempts,
                 "output_cost_usd": float((source_price + poc_cost) * attempts)},
            ])

    write_csv(HERE / "asset-costs.csv", jobs)
    write_csv(HERE / "scenario-totals.csv", summaries_out)
    write_csv(HERE / "character-totals.csv", character_out)
    write_csv(HERE / "variant-totals.csv", variants)
    dump(HERE / "assets.json", assets)
    dump(HERE / "static-size-evidence.json", sizing)
    dump(HERE / "scenario-totals.json", summaries_out)
    input_paths.update([HERE / "provider-specs.json", HERE / "production-policy.json", Path(__file__).resolve(),
                        HERE / "read_official_docs.py", HERE / "source-reads.json"])
    dump(HERE / "input-hashes.json", {str(path.relative_to(ROOT)): sha(path) for path in sorted(input_paths)})
    observed = {(x["scenario"], x["model"]): (x["distinct_assets"], x["generation_tasks"], x["requested_output_seconds"])
                for x in summaries_out if x["attempt_multiplier"] == 1}
    assert observed[("A", "minimax_h3")] == (5,5,52)
    assert observed[("B", "minimax_h3")] == (35,36,201)
    assert observed[("B", "seedance_2_5")] == (35,35,200)
    assert observed[("C", "minimax_h3")] == (84,88,625)
    assert observed[("C", "seedance_2_5")] == (84,84,621)
    assert len({a["asset_id"] for a in assets}) == len(assets)
    assert {a["source_animation"] for a in assets}.isdisjoint({"block", "victory", "cast_osty", "smith", "sleep"})
    dump(HERE / "validation.json", {"offline_calculation": "passed", "asset_rows": len(assets),
                                    "cost_rows": len(jobs), "scenario_rows": len(summaries_out),
                                    "counts_one_attempt": {s + "/" + m: list(v) for (s,m),v in observed.items()},
                                    "generation_api_calls": 0, "game_render_or_display_measurements": 0})
    print(json.dumps({"assets": len(assets), "scenario_totals_one_attempt":
                      [x for x in summaries_out if x["attempt_multiplier"] == 1]}, ensure_ascii=False, indent=2))


def limits_min(model: str) -> int:
    return 4  # Both explicitly selected base models have a four-second floor.


if __name__ == "__main__":
    main()
