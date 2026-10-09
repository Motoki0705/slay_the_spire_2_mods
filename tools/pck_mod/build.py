"""Public source bundle -> pinned local compat PCK -> explicit, owned installation."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile

from tools.spine.pck import ExtractionError, Pck, resource_path
from .compat import (CHARACTERS, PREFIX, SURFACES, import_targets, overlay_scene,
                     scene_path, selection_alias, selection_router, settings, texture_remap, ui_paths)

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
MOD_ID = "PopSpireWomen"
PIN_FILE = HERE / "game-version.json"
SOURCE_DIRS = {"animation", "art", "rigs", "select", "ui", "config"}
SOURCE_EXTENSIONS = {".gd", ".tscn", ".json", ".png", ".webp", ".ogv", ".uid"}
RUNTIME_FILES = ("animation/driver_overlay.gd", "animation/driver_overlay.tscn",
                 "animation/driver_reader.gd", "animation/puppet.gd", "animation/rig_schema.gd",
                 "animation/motion_library.gd", "animation/binding_lease.gd", "animation/draw_lease.gd",
                 "animation/selection_video.gd", "select/select_background.gd", "select/select_background.tscn",
                 "config/settings.gd", "config/select_router.gd")
PACKAGE_FILES = (MOD_ID + ".json", MOD_ID + ".pck", "LOCAL_ONLY.txt")
LOCAL_NOTICE = "Locally generated from your owned game. Contains scene scaffolds. Do not redistribute this folder or PCK. Distribute the source bundle instead.\n"


class BuildError(ValueError):
    pass


def digest(path):
    with Path(path).open("rb") as file:
        return hashlib.file_digest(file, "sha256").hexdigest()


def fingerprints(game, pins):
    return {name: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns)
            for name in pins["files"] for s in [(game / name).stat()]}


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def no_symlinks(path):
    path = Path(path).absolute()
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise BuildError(f"Symlink paths are not accepted: {path}")
    return path.resolve()


def new_output(path, protected=()):
    output = no_symlinks(path)
    if output.exists():
        raise BuildError(f"Output already exists; use a new output directory: {output}")
    if any(output == p or output.is_relative_to(p) or p.is_relative_to(output) for p in protected):
        raise BuildError("Output must be separate from the source assets and game")
    output.parent.mkdir(parents=True, exist_ok=True)
    return output


def check_game(game):
    game = no_symlinks(game)
    pins = json.loads(PIN_FILE.read_text())
    for name, expected in pins["files"].items():
        path = no_symlinks(game / resource_path(name))
        if not path.is_file() or digest(path) != expected:
            raise BuildError(f"Game differs from pinned {pins['version']} / {pins['build']}: {name}. Remove the mod after an update; review compatibility before regenerating.")
    return game, pins


def asset_sources(assets):
    """Only self-authored namespaces and resource types; no extracted compat or host settings."""
    assets = no_symlinks(assets)
    base = assets / MOD_ID
    if not base.is_dir():
        raise BuildError(f"Missing asset namespace: {base}")
    files = {}
    for path in sorted(base.rglob("*")):
        if path.is_symlink():
            raise BuildError(f"Symlink asset refused: {path}")
        if not path.is_file():
            continue
        relative = path.relative_to(base)
        if relative.parts[0] not in SOURCE_DIRS:
            raise BuildError(f"Unexpected asset namespace (local compat is not distributable): {relative}")
        if path.suffix in {".import", ".md"}:
            continue
        if path.suffix not in SOURCE_EXTENSIONS:
            raise BuildError(f"Unsupported asset type: {relative}")
        if relative.parts[0] == "config" and relative.as_posix().removesuffix(".uid") not in RUNTIME_FILES:
            raise BuildError(f"Generated/unknown config may not enter a public source bundle: {relative}")
        if ".provenance." in path.name or path.name == "build-receipt.json":
            continue
        files[PREFIX + relative.as_posix()] = path
    # The build tool's runtime version must match its generated routing contract.
    # This also permits read-only testing against a parent's pending production assets.
    for name in RUNTIME_FILES:
        files[PREFIX + name] = ROOT / "mod/assets" / PREFIX / name
    return files


def loader_manifest(source):
    value = json.loads(Path(source).read_text(encoding="utf-8"))
    if value.get("id") != MOD_ID:
        raise BuildError("Manifest id must be PopSpireWomen")
    value.update(has_dll=False, has_pck=True, dependencies=[], affects_gameplay=False)
    return value


def run_godot(godot, stage, arguments, log):
    result = subprocess.run([str(godot), "--headless", "--path", str(stage), *map(str, arguments)],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=180)
    Path(log).write_text(result.stdout, encoding="utf-8")
    if result.returncode or "SCRIPT ERROR" in result.stdout:
        raise BuildError(f"Godot failed; see {log}:\n{result.stdout[-3500:]}")
    return result.stdout


def stage_project(assets, stage):
    sources = asset_sources(assets)
    for name, source in sources.items():
        target = stage / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    (stage / "project.godot").write_text('config_version=5\n[application]\nconfig/name="PopSpireWomen PCK build"\n[rendering]\nrenderer/rendering_method="gl_compatibility"\n', encoding="utf-8")
    return {name: digest(stage / name) for name in sources}


def collect_imports(stage, files):
    unavailable = []
    for name in list(files):
        # Theora is streamed directly from its .ogv bytes (no .import/remap sidecar).
        if Path(name).suffix not in {".png", ".webp"}:
            continue
        imported = stage / (name + ".import")
        targets = import_targets(imported.read_bytes()) if imported.is_file() else []
        if not targets or any(not (stage / target).is_file() for target in targets):
            # Preflight has already rejected every surface using this image. Do not ship
            # a broken import; leave it absent so runtime fallbacks remain effective.
            del files[name]
            unavailable.append(name)
            continue
        files[name + ".import"] = imported
        for target in targets:
            files[target] = stage / target
    return unavailable


def generate_compat(pack, stage, files, preferences, preflight):
    sources, generated, skipped = {}, {}, []

    def original(path):
        data, receipt = pack.read(path, max_size=4 * 1024 * 1024)
        sources[path] = receipt
        return data

    def put(path, data, reason):
        path = resource_path(path)
        if path in files:
            raise BuildError(f"Unexpected duplicate generated path: {path}")
        target = stage / "local-compat" / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data.encode("utf-8") if isinstance(data, str) else data)
        files[path] = target
        generated[path] = {"sha256": digest(target), "reason": reason}

    for character in CHARACTERS:
        if not preferences["Enabled"] or character.upper() not in preferences["EnabledCharacters"]:
            skipped.append(f"{character}: disabled; no original paths overridden")
            continue
        checks = preflight[character]
        for surface in SURFACES:
            if not checks["surfaces"][surface]["ok"]:
                skipped.append(f"{character}/{surface}: {checks['surfaces'][surface]['reason']}")
                continue
            path = scene_path(character, surface)
            put(path, overlay_scene(original(path).decode("utf-8"), character, surface), "local_original_scaffold_plus_overlay")
        if checks["surfaces"]["select"]["ok"]:
            path = scene_path(character, "select")
            alias = PREFIX + f"compat/original_select/{character}.tscn"
            put(alias, selection_alias(original(path).decode("utf-8"), path), "local_original_selection_without_root_uid")
            put(path, selection_router(character), "self_authored_selection_router")
        else:
            skipped.append(f"{character}/select: {checks['surfaces']['select']['reason']}")
        for name, path in ui_paths(character).items():
            if not checks["ui"][name]["ok"]:
                skipped.append(f"{character}/ui/{name}: missing, wrong type or wrong dimensions")
                continue
            own_name = PREFIX + f"ui/{character}/{name}.png"
            own_target, = import_targets((stage / (own_name + ".import")).read_bytes())
            original_import = original(path + ".import")
            put(path + ".import", texture_remap(original_import, own_target), "self_authored_texture_remap_original_uid")
            # Also cover direct references and feature-specific exported remaps. Bytes are ours.
            for original_target in import_targets(original_import):
                put(original_target, (stage / own_target).read_bytes(), "self_authored_ctex_at_original_import_target")
        if checks["ui"]["icon"]["ok"] and checks["ui"]["top"]["ok"]:
            icon = (stage / PREFIX / f"ui/{character}/icon.tscn").read_text(encoding="utf-8")
            if 'uid="' in icon.split("\n", 1)[0]:
                raise BuildError("Self-authored icon scene must not reuse a root UID")
            put(scene_path(character, "icon"), icon, "self_authored_texturerect_icon")
    pack.assert_unchanged()
    return {"source_resources": sources, "generated_resources": generated, "skipped": skipped}


def verify_pack(path, expected):
    with Pck(path) as pack:
        if set(pack.entries) != set(expected):
            raise BuildError("Packed resource set differs from the allowlisted file map")
        for name, value in expected.items():
            _, receipt = pack.read(name)
            if receipt["sha256"] != value:
                raise BuildError(f"Packed resource differs: {name}")
        pack.assert_unchanged()


def build(args):
    assets = no_symlinks(args.assets)
    # Capture before hashing to reject a game update racing the build as well.
    initial_pins = json.loads(PIN_FILE.read_text())
    initial_game = no_symlinks(args.game_dir)
    initial_fingerprints = fingerprints(initial_game, initial_pins)
    game, pins = check_game(args.game_dir)
    output = new_output(args.output, (assets, game))
    godot = shutil.which(str(args.godot)) or str(Path(args.godot).resolve())
    version = subprocess.check_output([godot, "--version"], text=True, timeout=20).strip()
    if not version.startswith("4.5.1.stable."):
        raise BuildError(f"Use standard Godot 4.5.1 stable for import/packing, got: {version}")
    preferences, warning = settings(Path(args.settings).read_bytes().decode("utf-8", errors="replace") if args.settings else None)
    if warning:
        print(warning, file=sys.stderr)
    with tempfile.TemporaryDirectory(prefix=".psw-local-", dir=output.parent) as temp:
        workspace = Path(temp)
        result = workspace / "result"
        result.mkdir()
        stage = workspace / "stage"
        stage.mkdir()
        source_hashes = stage_project(assets, stage)
        run_godot(godot, stage, ["--editor", "--import"], result / "import.log")
        shutil.copyfile(HERE / "preflight.gd", stage / "preflight.gd")
        run_godot(godot, stage, ["--script", "res://preflight.gd", "--", result / "preflight.json"], result / "preflight.log")
        preflight = json.loads((result / "preflight.json").read_text())
        files = {name: stage / name for name in source_hashes}
        unavailable_imports = collect_imports(stage, files)
        settings_path = stage / PREFIX / "config/settings.json"
        write_json(settings_path, preferences)
        files[PREFIX + "config/settings.json"] = settings_path
        build_marker = stage / PREFIX / "config/pck-build.json"
        write_json(build_marker, {"schema": 1, "game": pins["version"], "build": pins["build"], "source_pck_sha256": pins["files"]["SlayTheSpire2.pck"]})
        files[PREFIX + "config/pck-build.json"] = build_marker
        with Pck(game / "SlayTheSpire2.pck") as pack:
            compat = generate_compat(pack, stage, files, preferences, preflight)
        if fingerprints(game, pins) != initial_fingerprints:
            raise BuildError("Game files changed during build; no PCK was published")
        package = result / MOD_ID
        package.mkdir()
        write_json(package / (MOD_ID + ".json"), loader_manifest(args.manifest))
        (package / "LOCAL_ONLY.txt").write_text(LOCAL_NOTICE, encoding="utf-8")
        file_map = workspace / "file-map.json"
        files = dict(sorted(files.items()))
        write_json(file_map, {name: str(path) for name, path in files.items()})
        hashes = {name: digest(path) for name, path in files.items()}
        shutil.copyfile(HERE / "pack.gd", stage / "pack.gd")
        pck = package / (MOD_ID + ".pck")
        run_godot(godot, stage, ["--script", "res://pack.gd", "--", file_map, pck], result / "pack.log")
        verify_pack(pck, hashes)
        packed_media = readback_media(godot, pck, preflight, workspace / "readback", result)
        receipt = {"schema": 1, "kind": "PopSpireWomen-local-pck", "redistributable": False,
                   "game_pins": pins, "godot": version, "settings": preferences, "settings_warning": warning,
                   "tool_sources": {"tools/pck_mod/" + p.name: digest(p) for p in sorted(HERE.iterdir()) if p.is_file()},
                   "unavailable_imports": unavailable_imports,
                   "packed_selection_media": packed_media,
                   "source_assets": source_hashes, **compat, "packed_resources": hashes,
                   "package_files": {name: digest(package / name) for name in PACKAGE_FILES},
                   "custom_dlls": [], "game_launched": False}
        write_json(result / "build-receipt.json", receipt)
        result.rename(output)
    print(f"Built local-only PCK: {output / MOD_ID}\nNo game installation or launch performed.")
    for skipped in receipt["skipped"]:
        print("Original retained: " + skipped)
    return output


def readback_media(godot, pck, preflight, host, result):
    """Load/decode referenced valid movies from the PCK in a host with no loose assets."""
    videos = sorted({c["surfaces"]["select"].get("video", {}).get("path")
                     for c in preflight.values()
                     if c["surfaces"]["select"].get("video", {}).get("ok")})
    host.mkdir()
    (host / "project.godot").write_text('config_version=5\n[rendering]\nrenderer/rendering_method="gl_compatibility"\n')
    shutil.copyfile(HERE / "readback.gd", host / "readback.gd")
    request = host / "videos.json"
    write_json(request, videos)
    report = result / "video-readback.json"
    run_godot(godot, host, ["--script", "res://readback.gd", "--", pck, request, report], result / "video-readback.log")
    payload = json.loads(report.read_text())
    if set(payload) != set(videos) or any(not v["ok"] for v in payload.values()):
        raise BuildError(f"Packed video readback failed; see {report}")
    return payload


def bundle(args):
    """A public archive contains only our inputs/tools, never anything read from the game."""
    output = new_output(args.output, (no_symlinks(args.assets),))
    source_files = {"mod/assets/" + name: path for name, path in asset_sources(args.assets).items()}
    for path in HERE.iterdir():
        if path.is_file() and path.suffix in {".py", ".gd", ".json"}:
            source_files["tools/pck_mod/" + path.name] = path
    for name in ["scripts/build_pck_mod.py", "tools/spine/pck.py", "docs/development/pck-only.md", "docs/development/selection-video-v02.md", "docs/development/source-bundle-readme.md", "mod/README.md", "mod/settings.example.json"]:
        source_files[name] = ROOT / name
    source_files["README.md"] = ROOT / "docs/development/source-bundle-readme.md"
    with tempfile.TemporaryDirectory(prefix=".psw-bundle-", dir=output.parent) as temp:
        staged = Path(temp) / "bundle.zip"
        hashes = {}
        with zipfile.ZipFile(staged, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for name, path in sorted(source_files.items()):
                contents = path.read_bytes()
                hashes[name] = hashlib.sha256(contents).hexdigest()
                archive.writestr(name, contents)
            archive.writestr("mod/PopSpireWomen.json", json.dumps(loader_manifest(args.manifest), indent=2) + "\n")
            archive.writestr("SOURCE_BUNDLE.json", json.dumps({"schema": 1, "redistributable": True, "source_files": hashes}, indent=2) + "\n")
        staged.rename(output)
    print(f"Public source bundle (no game resources, DLLs or local PCK): {output}")


def check_package(build_dir, game):
    _, pins = check_game(game)
    build_dir = no_symlinks(build_dir)
    receipt = json.loads(no_symlinks(build_dir / "build-receipt.json").read_text(encoding="utf-8"))
    if receipt.get("kind") != "PopSpireWomen-local-pck" or receipt.get("game_pins") != pins or set(receipt.get("package_files", {})) != set(PACKAGE_FILES):
        raise BuildError("Local build receipt is missing, incompatible or malformed")
    package = build_dir / MOD_ID
    if {p.name for p in package.iterdir()} != set(PACKAGE_FILES):
        raise BuildError("Local package contains unexpected files")
    for name, expected in receipt["package_files"].items():
        if digest(no_symlinks(package / name)) != expected:
            raise BuildError(f"Local package was modified: {name}")
    manifest = json.loads((package / (MOD_ID + ".json")).read_text())
    if manifest.get("has_dll") is not False or manifest.get("has_pck") is not True or manifest.get("dependencies") != []:
        raise BuildError("Package manifest is not DLL-free")
    verify_pack(package / (MOD_ID + ".pck"), receipt["packed_resources"])
    return package, receipt


def check_owned_install(destination):
    destination = no_symlinks(destination)
    receipt_path = no_symlinks(destination / "psw-install.receipt")
    if not receipt_path.is_file():
        raise BuildError("Existing folder has no ownership receipt; refusing to adopt/delete it")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if receipt.get("kind") != "PopSpireWomen-owned-install" or set(receipt.get("files", {})) != set(PACKAGE_FILES):
        raise BuildError("Unrecognized installation receipt")
    if {p.name for p in destination.iterdir()} != set(PACKAGE_FILES) | {receipt_path.name}:
        raise BuildError("Installation contains unowned files; refusing to change it")
    for name, expected in receipt["files"].items():
        if digest(no_symlinks(destination / name)) != expected:
            raise BuildError(f"Installed file changed; retain it manually before replacement/removal: {name}")
    return receipt


def install(args):
    package, receipt = check_package(args.build_dir, args.game_dir)
    mods = no_symlinks(args.mods_dir)
    if not mods.exists() and mods.parent.is_dir():
        mods.mkdir()
    if not mods.is_dir():
        raise BuildError("Explicit --mods-dir must be a directory with an existing parent")
    destination = no_symlinks(mods / MOD_ID)
    if destination.exists():
        check_owned_install(destination)
    with tempfile.TemporaryDirectory(prefix=".psw-install-", dir=mods) as temp:
        staged = Path(temp) / MOD_ID
        staged.mkdir()
        for name in PACKAGE_FILES:
            shutil.copyfile(package / name, staged / name)
        write_json(staged / "psw-install.receipt", {"schema": 1, "kind": "PopSpireWomen-owned-install", "files": receipt["package_files"], "game_pins": receipt["game_pins"]})
        check_owned_install(staged)
        previous = Path(temp) / "previous"
        if destination.exists():
            check_owned_install(destination)
            destination.rename(previous)
        try:
            staged.rename(destination)
        except BaseException:
            if previous.exists(): previous.rename(destination)
            raise
    print(f"Installed only owned PCK files: {destination}. Restart the game; enable the mod in its existing mod UI.")


def uninstall(args):
    destination = no_symlinks(args.mods_dir) / MOD_ID
    check_owned_install(destination)
    shutil.rmtree(destination)
    print(f"Removed only the verified owned installation: {destination}. No saves/settings changed.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ["build", "bundle"]:
        command = commands.add_parser(name)
        command.add_argument("--assets", type=Path, default=ROOT / "mod/assets")
        command.add_argument("--manifest", type=Path, default=ROOT / "mod/PopSpireWomen.json")
        command.add_argument("--output", type=Path, required=True, help="New output directory (build) or ZIP file (bundle); existing paths refused")
        if name == "build":
            command.add_argument("--game-dir", type=Path, required=True)
            command.add_argument("--godot", default="godot")
            command.add_argument("--settings", type=Path)
    for name in ["install", "verify"]:
        command = commands.add_parser(name)
        command.add_argument("--build-dir", type=Path, required=True)
        command.add_argument("--game-dir", type=Path, required=True)
        if name == "install": command.add_argument("--mods-dir", type=Path, required=True)
    command = commands.add_parser("uninstall")
    command.add_argument("--mods-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "verify":
            check_package(args.build_dir, args.game_dir)
            print("Package contents, loader manifest and pinned game match.")
        else:
            globals()[args.command](args)
    except (BuildError, ExtractionError, OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        print(f"build_pck_mod: {error}", file=sys.stderr)
        return 1
    return 0
