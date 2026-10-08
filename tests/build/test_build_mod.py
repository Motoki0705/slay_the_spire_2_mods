import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("build_mod", ROOT / "scripts/build_mod.py")
build = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(build)


class GameReferences(unittest.TestCase):
    def test_unspecified_game_has_actionable_diagnostic(self):
        with self.assertRaisesRegex(build.BuildError, "PSW001.*STS2_GAME_DIR"):
            build.check_game(None)

    def test_missing_game_reference_is_not_downloaded(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(build.BuildError, "PSW002"):
                build.check_game(folder)
            self.assertEqual(list(Path(folder).iterdir()), [])

    def test_reference_drift_is_detected_without_writing_game_files(self):
        with tempfile.TemporaryDirectory(prefix="psw game with spaces ") as folder:
            root = Path(folder)
            game = root / "game"
            game.mkdir()
            reference = game / "reference.dll"
            reference.write_bytes(b"fixture")
            expected = hashlib.sha256(reference.read_bytes()).hexdigest()
            pins = root / "pins.props"
            pins.write_text('<Project><ItemGroup><PinnedGameFile Include="$(Sts2GameDir)/reference.dll" '
                            f'ExpectedSha256="{expected}" /></ItemGroup></Project>')
            actual_game, hashes = build.check_game(str(game), pins)
            self.assertEqual(actual_game, game)
            self.assertEqual(hashes, {"reference.dll": expected})
            reference.write_bytes(b"changed")
            with self.assertRaisesRegex(build.BuildError, "PSW003"):
                build.check_game(str(game), pins)
            self.assertEqual(reference.read_bytes(), b"changed")


class GodotDiagnostics(unittest.TestCase):
    def test_zero_exit_with_script_error_is_still_a_failed_build(self):
        result = build.subprocess.CompletedProcess([], 0, stdout="SCRIPT ERROR: Parse Error: invalid script\n")
        with tempfile.TemporaryDirectory() as folder, patch.object(build.subprocess, "run", return_value=result):
            log = Path(folder) / "godot.log"
            with self.assertRaisesRegex(build.BuildError, "verification failed"):
                build.run_godot(["godot"], log)
            self.assertEqual(log.read_text(), result.stdout)


class Export(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.output = self.root / "bin"
        self.output.mkdir()
        (self.output / "PopSpireWomen.dll").write_bytes(b"mod assembly fixture")
        self.manifest = self.root / "PopSpireWomen.json"
        self.manifest.write_text(json.dumps({"id": "PopSpireWomen", "version": "0.1.0", "has_pck": False}))
        self.readme = self.root / "README.md"
        self.readme.write_text("bootstrap fixture")
        self.dist = self.root / "dist"

    def export(self):
        return build.export_package(self.output, self.dist, self.manifest, self.readme)

    def test_allowlist_excludes_game_and_dependency_dlls(self):
        for name in ["sts2.dll", "GodotSharp.dll", "0Harmony.dll", "STS2-RitsuLib.dll", "PopSpireWomen.pdb"]:
            (self.output / name).write_bytes(b"must not ship")
        with zipfile.ZipFile(self.export()) as archive:
            self.assertEqual(set(archive.namelist()), {
                "PopSpireWomen/PopSpireWomen.dll", "PopSpireWomen/PopSpireWomen.json", "PopSpireWomen/README.md"})
            self.assertEqual(archive.read("PopSpireWomen/PopSpireWomen.dll"), b"mod assembly fixture")

    def test_export_is_repeatable(self):
        first = self.export().read_bytes()
        self.assertEqual(self.export().read_bytes(), first)

    def test_optional_pck_manifest_and_return_to_asset_free_export(self):
        pck = self.root / "PopSpireWomen.pck"
        pck.write_bytes(b"pack fixture")
        archive = build.export_package(self.output, self.dist, self.manifest, self.readme, pck)
        with zipfile.ZipFile(archive) as package:
            self.assertEqual(len(package.namelist()), 4)
            self.assertTrue(json.loads(package.read("PopSpireWomen/PopSpireWomen.json"))["has_pck"])
            self.assertEqual(package.read("PopSpireWomen/PopSpireWomen.pck"), b"pack fixture")
        self.assertFalse(json.loads(self.manifest.read_text())["has_pck"])
        with zipfile.ZipFile(self.export()) as package:
            self.assertEqual(len(package.namelist()), 3)
            self.assertFalse(json.loads(package.read("PopSpireWomen/PopSpireWomen.json"))["has_pck"])
        self.assertFalse((self.dist / "PopSpireWomen/PopSpireWomen.pck").exists())

    def test_missing_pck_cannot_be_advertised(self):
        with self.assertRaisesRegex(build.BuildError, "missing PCK"):
            build.export_package(self.output, self.dist, self.manifest, self.readme, self.root / "missing.pck")
        self.assertFalse(self.dist.exists())

    def test_stale_unexpected_files_are_not_deleted_or_shipped(self):
        self.export()
        stale = self.dist / "PopSpireWomen/sts2.dll"
        stale.write_bytes(b"unexpected")
        with self.assertRaisesRegex(build.BuildError, "Unexpected files"):
            self.export()
        self.assertEqual(stale.read_bytes(), b"unexpected")

    def test_export_cannot_follow_symlink_to_installation(self):
        game = self.root / "game"
        game.mkdir()
        self.dist.symlink_to(game, target_is_directory=True)
        with self.assertRaisesRegex(build.BuildError, "symlink"):
            self.export()
        self.assertEqual(list(game.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
