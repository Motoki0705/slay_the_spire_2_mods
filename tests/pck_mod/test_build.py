"""Behavior checks for settings, local scaffold transforms and installation ownership."""
import argparse
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools.pck_mod import build as builder
from tools.pck_mod.compat import (CHARACTERS, import_targets, overlay_scene, selection_alias,
                                  settings, texture_remap)


class SettingsChecks(unittest.TestCase):
    def test_missing_and_empty_enable_all_five(self):
        for source in [None, "{}"]:
            value, warning = settings(source)
            self.assertTrue(value["Enabled"])
            self.assertEqual(value["EnabledCharacters"], [c.upper() for c in CHARACTERS])
            self.assertIsNone(warning)

    def test_explicit_disable_and_partial_opt_out(self):
        self.assertFalse(settings('{"Enabled":false}')[0]["Enabled"])
        self.assertEqual(settings('{"EnabledCharacters":[]}')[0]["EnabledCharacters"], [])
        self.assertEqual(settings('{"EnabledCharacters":["SILENT"]}')[0]["EnabledCharacters"], ["SILENT"])

    def test_corruption_and_unknown_fields_fail_closed(self):
        for data in ['{', 'null', '[]', '{"Enabled":1}', '{"ReducedMotion":"yes"}',
                     '{"EnabledCharacters":["silent"]}', '{"SchemaVersion":true}',
                     '{"EnabledCharacters":["SILENT","SILENT"]}', '{"typo":true}']:
            with self.subTest(data=data):
                value, warning = settings(data)
                self.assertFalse(value["Enabled"])
                self.assertEqual(value["EnabledCharacters"], [])
                self.assertTrue(warning)


class ScaffoldChecks(unittest.TestCase):
    def test_disabled_or_missing_surfaces_do_not_override_any_original_path(self):
        class NoReads:
            def read(self, *_args, **_kwargs):
                raise AssertionError("Disabled/missing surfaces must not extract originals")
            def assert_unchanged(self): pass
        preflight = {c: {"surfaces": {s: {"ok":False, "reason":"fixture missing"} for s in ["combat","merchant","rest","select"]}, "ui": {s:{"ok":False} for s in ["top","outline","portrait","locked","map","icon"]}} for c in CHARACTERS}
        with tempfile.TemporaryDirectory() as directory:
            for raw in ['{"Enabled":false}', '{broken', None]:
                files = {}
                result = builder.generate_compat(NoReads(), Path(directory), files, settings(raw)[0], preflight)
                self.assertEqual(files, {})
                self.assertEqual(result['source_resources'], {})
                self.assertEqual(result['generated_resources'], {})
                self.assertTrue(result['skipped'])

    def test_overlay_only_adds_last_child_and_resource(self):
        # Synthetic structure, not an extracted game scene.
        original = '''[gd_scene load_steps=2 format=3 uid="uid://original"]
[ext_resource type="Script" path="res://src/Core/Nodes/Screens/Shops/NMerchantCharacter.cs" id="1"]
[node name="Fixture" type="Node2D"]
script = ExtResource("1")
[node name="SpineSprite" type="SpineSprite" parent="."]
[node name="IndependentWeapon" type="Node2D" parent="."]
'''
        result = overlay_scene(original, "regent", "merchant")
        self.assertIn('load_steps=3', result)
        self.assertLess(result.index('name="IndependentWeapon"'), result.index('name="PopSpireWomenOverlay"'))
        # Recovering the original leaves every original script/property/node byte intact.
        changed = result[:result.index('\n[node name="PopSpireWomenOverlay"')].rstrip() + '\n'
        changed = changed.replace('\n[ext_resource type="PackedScene" path="res://PopSpireWomen/animation/driver_overlay.tscn" id="psw_overlay"]\n', '', 1)
        self.assertEqual(changed.replace('load_steps=3', 'load_steps=2', 1), original)

    def test_alias_drops_only_root_uid(self):
        source = '[gd_scene format=3 uid="uid://old"]\n[ext_resource uid="uid://dependency" path="res://original.tres" id="1"]\n'
        value = selection_alias(source, 'scenes/select.tscn')
        self.assertNotIn('uid://old', value)
        self.assertIn('uid://dependency', value)
        with self.assertRaises(ValueError):
            selection_alias(source.replace('original.tres', 'scenes/select.tscn'), 'scenes/select.tscn')

    def test_texture_feature_targets_and_original_uid(self):
        data = b'[remap]\ntype="CompressedTexture2D"\nuid="uid://original"\npath.bptc="res://.godot/imported/a.bptc.ctex"\npath.etc2="res://.godot/imported/a.etc2.ctex"\n\0'
        self.assertEqual(len(import_targets(data)), 2)
        remap = texture_remap(data, '.godot/imported/ours.ctex')
        self.assertIn('uid="uid://original"', remap)
        self.assertEqual(import_targets(remap.encode()), ['.godot/imported/ours.ctex'])
        with self.assertRaises(ValueError):
            import_targets(data.replace(b'.godot/imported/a.bptc.ctex', b'../outside.ctex'))


class OwnershipChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def install_fixture(self):
        dest = self.root / builder.MOD_ID
        dest.mkdir()
        for name in builder.PACKAGE_FILES: (dest / name).write_text(name)
        builder.write_json(dest / 'psw-install.receipt', {'kind': 'PopSpireWomen-owned-install', 'files': {n: builder.digest(dest/n) for n in builder.PACKAGE_FILES}})
        return dest

    def test_unknown_install_not_adopted(self):
        dest = self.root / builder.MOD_ID
        dest.mkdir()
        (dest / 'PopSpireWomen.dll').write_text('old DLL')
        with self.assertRaises(builder.BuildError): builder.check_owned_install(dest)
        self.assertTrue((dest / 'PopSpireWomen.dll').exists())

    def test_edited_and_foreign_files_block_removal(self):
        dest = self.install_fixture()
        builder.check_owned_install(dest)
        (dest / 'user-notes.txt').write_text('keep')
        with self.assertRaises(builder.BuildError): builder.uninstall(argparse.Namespace(mods_dir=self.root))
        (dest / 'user-notes.txt').unlink()
        (dest / builder.PACKAGE_FILES[0]).write_text('edited')
        with self.assertRaises(builder.BuildError): builder.check_owned_install(dest)

    def test_only_owned_install_removed(self):
        dest = self.install_fixture()
        (self.root / 'OtherMod').mkdir()
        builder.uninstall(argparse.Namespace(mods_dir=self.root))
        self.assertFalse(dest.exists())
        self.assertTrue((self.root / 'OtherMod').exists())

    def test_installer_exposes_only_the_manifest_to_json_mod_scan(self):
        package = self.root / 'package'
        package.mkdir()
        for name in builder.PACKAGE_FILES:
            (package / name).write_text('{}' if name.endswith('.json') else name)
        receipt = {'package_files': {n: builder.digest(package/n) for n in builder.PACKAGE_FILES}, 'game_pins': {}}
        mods = self.root / 'mods'
        mods.mkdir()
        with patch.object(builder, 'check_package', return_value=(package, receipt)):
            builder.install(argparse.Namespace(build_dir=self.root, game_dir=self.root, mods_dir=mods))
        # Native ModManager treats every recursive *.json as a mod manifest.
        self.assertEqual([p.name for p in mods.rglob('*.json')], ['PopSpireWomen.json'])
        builder.check_owned_install(mods / builder.MOD_ID)

    def test_source_namespace_rejects_raw_compat_and_dlls(self):
        base = self.root / 'PopSpireWomen'
        (base / 'compat').mkdir(parents=True)
        (base / 'compat/original.tscn').write_text('raw')
        with self.assertRaises(builder.BuildError): builder.asset_sources(self.root)
        (base / 'compat/original.tscn').unlink()
        (base / 'animation').mkdir()
        (base / 'animation/unexpected.dll').write_text('DLL')
        with self.assertRaises(builder.BuildError): builder.asset_sources(self.root)

    def test_symlink_and_source_output_refused(self):
        link = self.root / 'link'
        link.symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(builder.BuildError): builder.new_output(link / 'build')
        with self.assertRaises(builder.BuildError): builder.new_output(self.root / 'build', (self.root,))

    def test_unimportable_image_is_omitted_instead_of_shipping_broken_remap(self):
        name = 'PopSpireWomen/art/silent/body.png'
        path = self.root / name
        path.parent.mkdir(parents=True)
        path.write_bytes(b'not a PNG')
        files = {name: path}
        self.assertEqual(builder.collect_imports(self.root, files), [name])
        self.assertEqual(files, {})

    def test_generated_script_uid_is_a_permitted_source_sidecar(self):
        base = self.root / 'PopSpireWomen/config'
        base.mkdir(parents=True)
        (base / 'settings.gd.uid').write_text('uid://fixture')
        sources = builder.asset_sources(self.root)
        self.assertIn('PopSpireWomen/config/settings.gd.uid', sources)

    def test_manifest_keeps_parent_name_and_drops_dll_dependency(self):
        file = self.root / 'manifest.json'
        builder.write_json(file, {'id':builder.MOD_ID, 'name':'Parent name', 'description':'Parent description', 'has_dll':True, 'dependencies':[{'id':'RitsuLib'}]})
        result = builder.loader_manifest(file)
        self.assertEqual(result['name'], 'Parent name')
        self.assertEqual(result['description'], 'Parent description')
        self.assertEqual(result['dependencies'], [])
        self.assertFalse(result['has_dll'])
        self.assertTrue(result['has_pck'])

    def test_game_hash_mismatch_fails_before_generation(self):
        from unittest.mock import patch
        game = self.root / 'game'
        game.mkdir()
        (game / 'fixture.pck').write_bytes(b'expected')
        pin_file = self.root / 'pins.json'
        builder.write_json(pin_file, {'schema':1, 'version':'test', 'build':'fixture', 'files':{'fixture.pck':builder.digest(game/'fixture.pck')}})
        with patch.object(builder, 'PIN_FILE', pin_file):
            self.assertEqual(builder.check_game(game)[0], game)
            (game / 'fixture.pck').write_bytes(b'updated')
            with self.assertRaisesRegex(builder.BuildError, 'Remove the mod after an update'):
                builder.check_game(game)
            self.assertEqual((game / 'fixture.pck').read_bytes(), b'updated')


if __name__ == '__main__':
    unittest.main()
