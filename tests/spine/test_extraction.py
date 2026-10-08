"""Synthetic inputs only. Set STS2_SPINE_GODOT to also exercise real PNG decoding."""

import base64
import hashlib
import json
import os
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch
import zlib

from tools.spine.extract import COMBAT, extract, publish
from tools.spine import formats
from tools.spine.pck import ExtractionError, Pck, resource_path


# Our 2x3 RGBA test pixels, encoded losslessly with Godot 4.5.1 Image.
# No game texture, skeleton, scene, or DLL is part of these fixtures.
WEBP = base64.b64decode(
    "UklGRjoAAABXRUJQVlA4TC0AAAAvAYAAEC8w/wKCIv9HExAU+T8aQbbNUDaT+0s9+Aaxc8ogEEhDTBnMcET/4wAA")
PIXELS = bytes([255, 0, 0, 255, 0, 255, 0, 128, 0, 0, 255, 255,
                255, 255, 0, 64, 255, 0, 255, 255, 0, 255, 255, 32])


def synthetic_png():
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))
    rows = b"".join(b"\0" + PIXELS[i:i + 8] for i in range(0, 24, 8))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 2, 3, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(rows)) + chunk(b"IEND", b""))


def texture(payload=WEBP, encoding=2):
    return (b"GST2" + struct.pack("<8I", 1, 2, 3, 0x0D000000, 0xFFFFFFFF, 0, 0, 0)
            + struct.pack("<IHHIII", encoding, 2, 3, 0, 5, len(payload)) + payload)


def graph(character="silent", names=("page.png",)):
    root = f"animations/characters/{character}"
    skel, atlas = f"{root}/{character}.skel", f"{root}/{character}.atlas"
    skel_target = f".godot/imported/{character}.skel-synthetic.spskel"
    atlas_target = f".godot/imported/{character}.atlas-synthetic.spatlas"
    # Deliberately not a full Spine skeleton: tests cover immutable handoff and prefix checks.
    skeleton = (bytes(range(8)) + b"\x074.2.43" + struct.pack(">5f", 0, 0, 2, 3, 100)
                + b"\x01" + b"synthetic opaque skeleton payload")
    atlas_text = "\n\n".join(
        f"{name}\nsize:2,3\nfilter:Linear,Linear\nscale:0.32\nregion/body\nbounds:0,0,2,3\n"
        for name in names)
    resources = {
        f"scenes/creature_visuals/{character}.tscn": (
            '[gd_scene format=3]\n'
            '[ext_resource type="SpineSkeletonDataResource" path="res://unrelated/weapon.tres" id="weapon"]\n'
            f'[ext_resource type="SpineSkeletonDataResource" path="res://{root}/{character}_skel_data.tres" id="main"]\n'
            '[node name="actor" type="Node2D"]\n').encode(),
        f"{root}/{character}_skel_data.tres": (
            '[gd_resource type="SpineSkeletonDataResource" format=3]\n'
            f'[ext_resource type="SpineAtlasResource" path="res://{atlas}" id="atlas"]\n'
            f'[ext_resource type="SpineSkeletonFileResource" path="res://{skel}" id="skel"]\n'
            '[resource]\natlas_res = ExtResource("atlas")\nskeleton_file_res = ExtResource("skel")\n'
            'default_mix = 0.05\n').encode(),
        skel + ".import": (
            '[remap]\nimporter="spine.skel"\ntype="SpineSkeletonFileResource"\n'
            f'path="res://{skel_target}"\n\0').encode(),
        atlas + ".import": (
            '[remap]\nimporter="spine.atlas"\ntype="SpineAtlasResource"\n'
            f'path="res://{atlas_target}"\n\0').encode(),
        skel_target: skeleton,
        atlas_target: json.dumps({"atlas_data": atlas_text, "source_path": "res://" + atlas,
                                  "normal_texture_prefix": "n", "specular_texture_prefix": "s"}).encode(),
        "unrelated/weapon.tres": b"not selected",
        ".godot/imported/weapon.skel-synthetic.spskel": b"not selected either",
    }
    for number, name in enumerate(names):
        target = f".godot/imported/page-{number}.ctex"
        resources[f"{root}/{name}.import"] = (
            '[remap]\nimporter="texture"\ntype="CompressedTexture2D"\n'
            f'path="res://{target}"\n\0').encode()
        resources[target] = texture()
    return resources


def pack_bytes(resources):
    payload = bytearray(112)
    locations = {}
    for name, data in resources.items():
        locations[name] = {"payload": len(payload), "size": len(data)}
        payload.extend(data)
    directory = len(payload)
    payload.extend(struct.pack("<I", len(resources)))
    for name, data in resources.items():
        path = name.encode() + b"\0"
        payload.extend(struct.pack("<I", len(path)))
        payload.extend(path)
        row = locations[name]
        row["offset_field"] = len(payload)
        payload.extend(struct.pack("<QQ", row["payload"] - 112, len(data)))
        row["md5_field"] = len(payload)
        payload.extend(hashlib.md5(data).digest())
        row["flags_field"] = len(payload)
        payload.extend(struct.pack("<I", 0))
    payload[:40] = b"GDPC" + struct.pack("<5IQQ", 3, 4, 5, 1, 2, 112, directory)
    return payload, locations, directory


class ExtractionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="sts2-spine-fixture-")
        self.root = Path(self.temporary.name)
        self.game = self.root / "game"
        self.game.mkdir()
        (self.game / "release_info.json").write_text(
            json.dumps({"version": "v0.107.1", "commit": "59260271"}))
        self.output = self.root / "result"

    def tearDown(self):
        self.temporary.cleanup()

    def write_pack(self, resources=None):
        self.resources = resources or graph()
        self.raw, self.locations, self.directory = pack_bytes(self.resources)
        self.pck = self.game / "SlayTheSpire2.pck"
        self.pck.write_bytes(self.raw)

    def run_extract(self, character="silent", **kwargs):
        return extract(self.game, character, self.output, texture_mode="embedded", **kwargs)

    def test_selected_payloads_hashes_atlas_and_source_unchanged(self):
        self.write_pack()
        source_before = self.pck.read_bytes()
        release_before = (self.game / "release_info.json").read_bytes()
        result = self.run_extract()
        manifest = json.loads((self.output / "manifest.json").read_bytes())
        self.assertEqual(result["resources"], 8)
        self.assertEqual((self.output / "authoring/silent.skel").read_bytes(),
                         self.resources[manifest["mapping"]["spskel"]])
        self.assertEqual((self.output / "authoring/silent.atlas").read_bytes(),
                         json.loads(self.resources[manifest["mapping"]["spatlas"]])["atlas_data"].encode())
        self.assertEqual(manifest["png_decode"]["status"], "not_requested")
        self.assertFalse((self.output / "authoring/page.png").exists())
        for item in manifest["outputs"]:
            data = (self.output / item["path"]).read_bytes()
            self.assertEqual(hashlib.md5(data).hexdigest(), item["md5"])
            self.assertEqual(hashlib.sha256(data).hexdigest(), item["sha256"])
        self.assertFalse(any("weapon" in item["path"] for item in manifest["resources"]))
        self.assertEqual(manifest["pages"][0]["ctex_resource"], ".godot/imported/page-0.ctex")
        self.assertEqual(self.pck.read_bytes(), source_before)
        self.assertEqual((self.game / "release_info.json").read_bytes(), release_before)

    def test_explicit_main_mapping_for_all_five(self):
        for character in ("ironclad", "silent", "regent", "necrobinder", "defect"):
            with self.subTest(character=character):
                root = f"animations/characters/{character}"
                self.assertEqual(COMBAT[character], (f"scenes/creature_visuals/{character}.tscn",
                                 f"{root}/{character}_skel_data.tres", f"{root}/{character}.atlas",
                                 f"{root}/{character}.skel"))
                self.write_pack(graph(character))
                self.output = self.root / character
                self.run_extract(character)

    def test_multiple_pages_preserve_order_and_nested_paths(self):
        self.write_pack(graph(names=("page.png", "death/page2.png", "slash.png")))
        self.run_extract()
        manifest = json.loads((self.output / "manifest.json").read_bytes())
        self.assertEqual([p["name"] for p in manifest["pages"]], ["page.png", "death/page2.png", "slash.png"])
        self.assertTrue((self.output / "sources/embedded/death/page2.png.webp").is_file())

    def test_refuse_existing_output_with_content(self):
        self.write_pack()
        self.output.mkdir()
        keep = self.output / "keep.txt"
        keep.write_text("keep")
        with self.assertRaisesRegex(ExtractionError, "already exists"):
            self.run_extract()
        self.assertEqual(keep.read_text(), "keep")

    def test_refuse_existing_empty_output(self):
        self.write_pack()
        self.output.mkdir()
        with self.assertRaisesRegex(ExtractionError, "already exists"):
            self.run_extract()
        self.assertEqual(list(self.output.iterdir()), [])

    def test_refuse_output_within_game(self):
        self.write_pack()
        self.output = self.game / "result"
        with self.assertRaisesRegex(ExtractionError, "outside.*game"):
            self.run_extract()

    def test_refuse_symlink_destination_parent(self):
        self.write_pack()
        link = self.root / "link"
        link.symlink_to(self.game, target_is_directory=True)
        self.output = link / "result"
        with self.assertRaisesRegex(ExtractionError, "symlink"):
            self.run_extract()

    def test_refuse_git_working_tree_output(self):
        self.write_pack()
        (self.root / ".git").write_text("gitdir: synthetic")
        with self.assertRaisesRegex(ExtractionError, "Git working tree"):
            self.run_extract()

    def test_publication_refuses_concurrently_created_directory(self):
        self.write_pack()
        def competing_publish(stage, destination):
            destination.mkdir()
            (destination / "keep").write_text("other writer")
            publish(stage, destination)
        with patch("tools.spine.extract.publish", side_effect=competing_publish):
            with self.assertRaises(FileExistsError):
                self.run_extract()
        self.assertEqual((self.output / "keep").read_text(), "other writer")
        self.assertEqual(list(self.output.iterdir()), [self.output / "keep"])

    def test_md5_corruption_leaves_no_output(self):
        self.write_pack()
        row = self.locations[".godot/imported/silent.skel-synthetic.spskel"]
        self.raw[row["payload"] + row["size"] - 1] ^= 1
        self.pck.write_bytes(self.raw)
        with self.assertRaisesRegex(ExtractionError, "MD5 mismatch"):
            self.run_extract()
        self.assertFalse(self.output.exists())
        self.assertFalse(list(self.root.glob(".result-*")))

    def test_unknown_texture_format_leaves_no_output(self):
        resources = graph()
        raw = bytearray(resources[".godot/imported/page-0.ctex"])
        struct.pack_into("<I", raw, 36, 3)
        resources[".godot/imported/page-0.ctex"] = bytes(raw)
        self.write_pack(resources)
        with self.assertRaisesRegex(ExtractionError, "CTEX data format 3"):
            self.run_extract()
        self.assertFalse(self.output.exists())

    def test_missing_page_import_leaves_no_output(self):
        resources = graph()
        del resources["animations/characters/silent/page.png.import"]
        self.write_pack(resources)
        with self.assertRaisesRegex(ExtractionError, "required PCK resource is missing"):
            self.run_extract()
        self.assertFalse(self.output.exists())

    def test_scene_and_data_mapping_are_checked(self):
        for name, old, new in (
            ("scenes/creature_visuals/silent.tscn", b"silent_skel_data.tres", b"wrong_data.tres"),
            ("animations/characters/silent/silent_skel_data.tres", b"silent.skel", b"wrong.skel"),
        ):
            with self.subTest(name=name):
                resources = graph()
                resources[name] = resources[name].replace(old, new)
                self.write_pack(resources)
                with self.assertRaisesRegex(ExtractionError, "explicit"):
                    self.run_extract()
                self.assertFalse(self.output.exists())

    def test_unknown_release_rejected(self):
        self.write_pack()
        (self.game / "release_info.json").write_text('{"version":"new","commit":"different"}')
        with self.assertRaisesRegex(ExtractionError, "unsupported game release"):
            self.run_extract()

    @unittest.skipUnless(os.environ.get("STS2_SPINE_GODOT"), "set STS2_SPINE_GODOT for buffer decoder integration")
    def test_godot_webp_and_png_decode_keep_rgba_pixels_and_alpha(self):
        for encoding, payload in ((2, WEBP), (1, synthetic_png())):
            with self.subTest(encoding=encoding):
                resources = graph()
                resources[".godot/imported/page-0.ctex"] = texture(payload, encoding)
                self.write_pack(resources)
                self.output = self.root / f"decoded-{encoding}"
                result = extract(self.game, "silent", self.output, godot=os.environ["STS2_SPINE_GODOT"])
                manifest = json.loads((self.output / "manifest.json").read_bytes())
                self.assertEqual(result["png_decode"], "complete")
                verified = manifest["pages"][0]["pixel_verification"]
                self.assertEqual(verified["pixels_sha256"], hashlib.sha256(PIXELS).hexdigest())
                self.assertTrue(verified["png_pixels_equal"])
                self.assertGreater(verified["alpha"], 0)
                self.assertEqual(formats.png_dimensions((self.output / "authoring/page.png").read_bytes()), [2, 3])

    @unittest.skipUnless(os.environ.get("STS2_SPINE_GODOT"), "set STS2_SPINE_GODOT for buffer decoder integration")
    def test_corrupt_webp_decode_fails_without_partial_output_or_fallback(self):
        resources = graph()
        resources[".godot/imported/page-0.ctex"] = texture(b"RIFF\x04\0\0\0WEBP")
        self.write_pack(resources)
        with self.assertRaisesRegex(ExtractionError, "Godot buffer decode failed"):
            extract(self.game, "silent", self.output, godot=os.environ["STS2_SPINE_GODOT"])
        self.assertFalse(self.output.exists())
        self.assertFalse(list(self.root.glob(".result-*")))


class IndexTests(unittest.TestCase):
    def reject(self, raw, message):
        with tempfile.TemporaryDirectory(prefix="sts2-spine-index-") as directory:
            path = Path(directory) / "test.pck"
            path.write_bytes(raw)
            with self.assertRaisesRegex(ExtractionError, message):
                with Pck(path):
                    pass

    def test_truncated_header_and_directory(self):
        self.reject(b"GDPC", "truncated")
        raw, _, _ = pack_bytes({"safe": b"data"})
        self.reject(raw[:-4], "truncated")

    def test_unknown_magic_version_engine_and_flags(self):
        for offset, value, message in ((0, 0, "magic"), (4, 2, "PCK version"),
                                       (12, 6, "Godot version"), (20, 3, "encrypted.*directory"),
                                       (20, 6, "PCK flags")):
            with self.subTest(offset=offset, value=value):
                raw, _, _ = pack_bytes({"safe": b"data"})
                struct.pack_into("<I", raw, offset, value)
                self.reject(raw, message)

    def test_traversal_absolute_windows_and_embedded_null_paths(self):
        for name in ("../evil", "a/../../evil", "/absolute", "C:/file", "a\\b", "a/./b", "a//b", "a\0b"):
            with self.subTest(name=name):
                raw, _, _ = pack_bytes({name: b"data"})
                self.reject(raw, "unsafe resource path")

    def test_duplicate_normalized_resource_paths(self):
        raw, _, _ = pack_bytes({"safe": b"data", "res://safe": b"data"})
        self.reject(raw, "duplicate PCK")

    def test_directory_and_filebase_out_of_range(self):
        for offset in (24, 32):
            raw, _, _ = pack_bytes({"safe": b"data"})
            struct.pack_into("<Q", raw, offset, len(raw) + 1)
            self.reject(raw, "out of range")

    def test_entry_offset_size_and_directory_overlap(self):
        for field, value, message in ((0, 2**64 - 1, "out of range"),
                                       (8, 2**64 - 1, "out of range"),
                                       (0, 0, "overlaps directory")):
            raw, rows, directory = pack_bytes({"safe": b"data"})
            if message == "overlaps directory":
                value = directory - 112
            struct.pack_into("<Q", raw, rows["safe"]["offset_field"] + field, value)
            self.reject(raw, message)

    def test_encrypted_removal_and_unknown_entry_flags(self):
        for flags in (1, 2, 4):
            raw, rows, _ = pack_bytes({"safe": b"data"})
            struct.pack_into("<I", raw, rows["safe"]["flags_field"], flags)
            self.reject(raw, "entry flags")

    def test_overlapping_entry_ranges(self):
        raw, rows, _ = pack_bytes({"first": b"abcdef", "second": b"def"})
        struct.pack_into("<Q", raw, rows["second"]["offset_field"], rows["first"]["payload"] - 112 + 3)
        self.reject(raw, "overlapping PCK resources")

    def test_unreasonable_path_length_and_count(self):
        for relative_offset, value, message in ((4, 2**32 - 1, "path length"),
                                                (0, 2**32 - 1, "count")):
            raw, _, directory = pack_bytes({"safe": b"data"})
            struct.pack_into("<I", raw, directory + relative_offset, value)
            self.reject(raw, message)

    def test_resource_limit_and_changed_input(self):
        raw, _, _ = pack_bytes({"safe": b"data"})
        with tempfile.TemporaryDirectory(prefix="sts2-spine-index-") as directory:
            path = Path(directory) / "test.pck"
            path.write_bytes(raw)
            with Pck(path) as pack:
                with self.assertRaisesRegex(ExtractionError, "exceeds"):
                    pack.read("safe", max_size=3)
                path.write_bytes(bytes(raw) + b"changed")
                with self.assertRaisesRegex(ExtractionError, "changed"):
                    pack.assert_unchanged()

    def test_bounded_reads_skip_unselected_payload(self):
        selected = b"s" * (2 * Pck.CHUNK_SIZE + 7)
        raw, rows, _ = pack_bytes({"selected": selected, "unselected": b"u" * (5 * Pck.CHUNK_SIZE)})
        with tempfile.TemporaryDirectory(prefix="sts2-spine-bounded-") as directory:
            path = Path(directory) / "test.pck"
            path.write_bytes(raw)
            file = path.open("rb")
            reads = []
            class GuardedFile:
                def __getattr__(self, name):
                    return getattr(file, name)
                def read(inner, size=-1):
                    self.assertGreaterEqual(size, 0, "no read-all call")
                    self.assertLessEqual(size, Pck.CHUNK_SIZE)
                    reads.append((file.tell(), size))
                    return file.read(size)
            with patch("tools.spine.pck.Path.open", return_value=GuardedFile()):
                with Pck(path) as pack:
                    self.assertEqual(pack.read("selected")[0], selected)
            unused_start = rows["unselected"]["payload"]
            unused_end = unused_start + rows["unselected"]["size"]
            self.assertFalse(any(start < unused_end and start + size > unused_start for start, size in reads))


class FormatTests(unittest.TestCase):
    def test_json_unescaping_preserves_atlas_line_endings(self):
        source = "animations/characters/silent/silent.atlas"
        value = 'page.png\r\nsize:2,3\r\nfilter:Linear,Linear\r\nregion\r\nbounds:0,0,2,3\r\n'
        raw, _, pages = formats.atlas(json.dumps({"source_path": "res://" + source, "atlas_data": value}).encode(), source)
        self.assertEqual(raw, value.encode())
        self.assertEqual(pages[0]["size"], [2, 3])

    def test_unsafe_and_duplicate_atlas_pages(self):
        for name in ("../page.png", "/page.png", "C:/page.png", "res://page.png"):
            raw = json.dumps({"source_path": "a.atlas", "atlas_data": f"{name}\nsize:2,3\n"}).encode()
            with self.assertRaises(ExtractionError):
                formats.atlas(raw, "a.atlas")
        raw = json.dumps({"source_path": "a.atlas", "atlas_data": "page.png\nsize:2,3\n\nPAGE.png\nsize:2,3\n"}).encode()
        with self.assertRaisesRegex(ExtractionError, "duplicate atlas"):
            formats.atlas(raw, "a.atlas")

    def test_spatlas_is_json_and_requires_matching_source(self):
        with self.assertRaisesRegex(ExtractionError, "malformed JSON"):
            formats.atlas(b"page.png\nsize:2,3\n", "a.atlas")
        with self.assertRaisesRegex(ExtractionError, "source_path"):
            formats.atlas(b'{"source_path":"other.atlas","atlas_data":"x"}', "a.atlas")
        with self.assertRaisesRegex(ExtractionError, "duplicate JSON"):
            formats.json_object(b'{"atlas_data":"a","atlas_data":"b"}')
        with self.assertRaisesRegex(ExtractionError, "non-JSON constant"):
            formats.json_object(b'{"atlas_data":NaN}')

    def test_importer_and_resource_reference_validation(self):
        with self.assertRaisesRegex(ExtractionError, "importer"):
            formats.import_target(b'[remap]\nimporter="unknown"\ntype="CompressedTexture2D"\n',
                                  "texture", "CompressedTexture2D", ".ctex")
        with self.assertRaisesRegex(ExtractionError, "unsafe"):
            resource_path("res://.godot/../escape")
        with self.assertRaisesRegex(ExtractionError, "reference"):
            formats.skeleton_references(b'[resource]\natlas_res=ExtResource("missing")\n')

    def test_skeleton_unknown_version_and_truncated_prefix(self):
        good = graph()[".godot/imported/silent.skel-synthetic.spskel"]
        with self.assertRaisesRegex(ExtractionError, "unsupported Spine"):
            formats.skeleton_header(good.replace(b"4.2.43", b"4.3.00"))
        for end in (0, 8, 10, 20, 35):
            with self.subTest(end=end):
                with self.assertRaisesRegex(ExtractionError, "truncated"):
                    formats.skeleton_header(good[:end])

    def test_ctex_lengths_formats_dimensions_and_payload_envelope(self):
        for offset, value, message in ((4, 99, "CTEX version"), (36, 0, "data format"),
                                       (48, 99, "pixel format"), (8, 4, "dimensions"),
                                       (52, 2**32 - 1, "payload length")):
            raw = bytearray(texture())
            struct.pack_into("<I", raw, offset, value)
            with self.assertRaisesRegex(ExtractionError, message):
                formats.ctex(raw)
        with self.assertRaisesRegex(ExtractionError, "trailing"):
            formats.ctex(texture() + b"extra")
        with self.assertRaisesRegex(ExtractionError, "RIFF"):
            formats.ctex(texture(b"not WebP"))
        self.assertEqual(formats.ctex(texture())[0], WEBP)
        self.assertEqual(formats.ctex(texture(synthetic_png(), 1))[0], synthetic_png())


if __name__ == "__main__":
    unittest.main()
