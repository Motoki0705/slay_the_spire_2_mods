"""Small, deterministic edits of hash-pinned local scene scaffolds (never public assets)."""
import json
import re

from tools.spine.pck import ExtractionError, resource_path

CHARACTERS = ("ironclad", "silent", "regent", "necrobinder", "defect")
PREFIX = "PopSpireWomen/"
SURFACES = ("combat", "merchant", "rest")


def scene_path(character, surface):
    return {
        "combat": f"scenes/creature_visuals/{character}.tscn",
        "merchant": f"scenes/merchant/characters/{character}_merchant.tscn",
        "rest": f"scenes/rest_site/characters/{character}_rest_site.tscn",
        "select": f"scenes/screens/char_select/char_select_bg_{character}.tscn",
        "icon": f"scenes/ui/character_icons/{character}_icon.tscn",
    }[surface]


def ui_paths(character):
    return {
        "top": f"images/ui/top_panel/character_icon_{character}.png",
        "outline": f"images/ui/top_panel/character_icon_{character}_outline.png",
        "portrait": f"images/packed/character_select/char_select_{character}.png",
        "locked": f"images/packed/character_select/char_select_{character}_locked.png",
        "map": f"images/packed/map/icons/map_marker_{character}.png",
    }


def overlay_scene(original, character, surface):
    """Add a last child; preserve all existing node order, scripts, transforms and resources."""
    if character not in CHARACTERS or surface not in SURFACES:
        raise ExtractionError("Unknown character/surface")
    driver = "Visuals" if surface == "combat" else "SpineSprite"
    if surface == "rest":
        driver = {"regent": "SpineSprite2", "necrobinder": "Necro"}.get(character, driver)
    expected = f'[node name="{driver}" type="SpineSprite" parent="."]'
    if expected not in original or "PopSpireWomenOverlay" in original:
        raise ExtractionError("Original scene driver contract mismatch")
    script = {
        "combat": "src/Core/Nodes/Combat/NCreatureVisuals.cs",
        "merchant": "src/Core/Nodes/Screens/Shops/NMerchantCharacter.cs",
        "rest": "src/Core/Nodes/RestSite/NRestSiteCharacter.cs",
    }[surface]
    if f'path="res://{script}"' not in original:
        raise ExtractionError("Original scene C# type contract mismatch")
    if 'id="psw_overlay"' in original or "[connection " in original:
        raise ExtractionError("Unexpected scaffold structure; review this game version")
    changed, count = re.subn(r"\A\[gd_scene load_steps=(\d+)", lambda m: f"[gd_scene load_steps={int(m[1]) + 1}", original, count=1)
    if count != 1:
        raise ExtractionError("Unsupported scene header")
    index = changed.index("\n") + 1
    changed = changed[:index] + '\n[ext_resource type="PackedScene" path="res://PopSpireWomen/animation/driver_overlay.tscn" id="psw_overlay"]\n' + changed[index:]
    return changed.rstrip() + f'''

[node name="PopSpireWomenOverlay" parent="." instance=ExtResource("psw_overlay")]
character_entry = "{character.upper()}"
rig_path = "res://PopSpireWomen/rigs/{character}/{surface}.json"
driver_path = NodePath("../{driver}")
surface = "{surface}"
'''


def selection_alias(original, original_path):
    """No root UID: the original UID must continue resolving to the original VFS path."""
    first, separator, rest = original.partition("\n")
    if not first.startswith("[gd_scene ") or not separator:
        raise ExtractionError("Unsupported selection scene header")
    if f'path="res://{original_path}"' in rest:
        raise ExtractionError("Self-referencing original selection scene is unsupported")
    return re.sub(r' uid="uid://[a-z0-9]+"', "", first) + separator + rest


def selection_router(character):
    return f'''[gd_scene load_steps=2 format=3]

[ext_resource type="Script" path="res://PopSpireWomen/config/select_router.gd" id="1"]

[node name="PopSpireWomenSelection" type="Control"]
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
grow_horizontal = 2
grow_vertical = 2
mouse_filter = 2
script = ExtResource("1")
character_entry = "{character.upper()}"
'''


def import_targets(data):
    text = data.decode("utf-8").rstrip("\0")
    if 'type="CompressedTexture2D"' not in text:
        raise ExtractionError("Expected a CompressedTexture2D import")
    # Exported imports can use path.bptc; capture every variant, not only path=.
    targets = re.findall(r'^path(?:\.[a-zA-Z0-9_]+)?="(res://[^"\n]+)"\s*$', text, re.M)
    if not targets:
        raise ExtractionError("Texture import has no remap target")
    paths = [resource_path(p) for p in targets]
    if any(not p.startswith(".godot/imported/") or not p.endswith(".ctex") for p in paths):
        raise ExtractionError("Texture import target outside .godot/imported/*.ctex")
    return paths


def texture_remap(original_import, own_target):
    text = original_import.decode("utf-8").rstrip("\0")
    uid = re.search(r'^uid="(uid://[a-z0-9]+)"$', text, re.M)
    uid_line = f'uid="{uid[1]}"\n' if uid else ""
    return ('[remap]\n\nimporter="texture"\ntype="CompressedTexture2D"\n' + uid_line
            + f'path="res://{resource_path(own_target)}"\nmetadata={{"vram_texture": false}}\n')


def settings(data=None):
    """Missing document/fields enable all five; malformed or explicit disable fails closed."""
    defaults = {"SchemaVersion": 1, "Enabled": True, "EnabledCharacters": [c.upper() for c in CHARACTERS], "ReducedMotion": False}
    if data is None:
        return defaults, None
    try:
        value = json.loads(data)
        if not isinstance(value, dict) or set(value) - set(defaults):
            raise ValueError()
        value = defaults | value
        if type(value["SchemaVersion"]) is not int or value["SchemaVersion"] != 1:
            raise ValueError()
        if type(value["Enabled"]) is not bool or type(value["ReducedMotion"]) is not bool:
            raise ValueError()
        chars = value["EnabledCharacters"]
        if not isinstance(chars, list) or any(not isinstance(c, str) or c not in defaults["EnabledCharacters"] for c in chars) or len(chars) != len(set(chars)):
            raise ValueError()
        return value, None
    except (ValueError, TypeError):
        return defaults | {"Enabled": False, "EnabledCharacters": []}, "Invalid settings: all original appearances retained"
