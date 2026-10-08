#!/usr/bin/env python3
"""Build/test/export the pinned bootstrap. Never writes into a game installation."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile


ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT / "mod"
PROJECT = MOD / "PopSpireWomen.csproj"
BUILD_OUTPUT = MOD / ".godot/mono/temp/bin/ExportRelease"


class BuildError(Exception):
    pass


def sha256(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def check_game(game_dir, pins_file=MOD / "GameReferences.props"):
    if not game_dir:
        raise BuildError("PSW001: set --game-dir or STS2_GAME_DIR to the local Slay the Spire 2 directory (v0.107.1 / 59260271).")
    game = Path(game_dir).expanduser().resolve()
    pins = ET.parse(pins_file).findall(".//PinnedGameFile")
    if not pins:
        raise BuildError("No game reference pins found.")
    hashes = {}
    for pin in pins:
        relative = pin.attrib["Include"].removeprefix("$(Sts2GameDir)/")
        path = game / relative
        if not path.is_file():
            raise BuildError(f"PSW002: missing local reference: {path}. Expected the Windows x64 v0.107.1 installation.")
        actual = sha256(path)
        if actual != pin.attrib["ExpectedSha256"].lower():
            raise BuildError(f"PSW003: reference differs from pinned v0.107.1 / 59260271: {path}. Review compatibility before changing pins.")
        hashes[relative] = actual
    return game, hashes


def dotnet_environment(tools_dir):
    env = os.environ.copy()
    env.update({
        "DOTNET_CLI_HOME": str(tools_dir / "cli-home"),
        "NUGET_PACKAGES": str(tools_dir / "nuget-packages"),
        "NUGET_HTTP_CACHE_PATH": str(tools_dir / "nuget-http-cache"),
        "DOTNET_CLI_TELEMETRY_OPTOUT": "1",
        "DOTNET_NOLOGO": "1",
        "DOTNET_SKIP_FIRST_TIME_EXPERIENCE": "1",
        "DOTNET_GENERATE_ASPNET_CERTIFICATE": "false",
        "DOTNET_CLI_WORKLOAD_UPDATE_NOTIFY_DISABLE": "1",
    })
    return env


def run(command, env):
    # cwd matters: global.json under mod/ must also select the SDK for tests/build/.
    subprocess.run([str(arg) for arg in command], cwd=MOD, env=env, check=True)


def check_sdk(dotnet, env):
    expected = json.loads((MOD / "global.json").read_text())["sdk"]["version"]
    result = subprocess.run([dotnet, "--version"], cwd=MOD, env=env, text=True, capture_output=True)
    if result.returncode or result.stdout.strip() != expected:
        raise BuildError(f"Need .NET SDK {expected} (global.json disables roll-forward). Use --dotnet /path/to/dotnet.\n{result.stderr.strip()}")


def check_manifest():
    manifest = json.loads((MOD / "PopSpireWomen.json").read_text())
    project = ET.parse(PROJECT)
    if manifest["id"] != project.findtext(".//AssemblyName") or manifest["version"] != project.findtext(".//Version"):
        raise BuildError("Assembly ID/version and loader manifest must match.")
    if manifest["has_pck"] or not manifest["has_dll"] or manifest["affects_gameplay"]:
        raise BuildError("Bootstrap export expects a cosmetic DLL-only manifest.")
    return manifest


def build(dotnet, env, game, hashes):
    check_manifest()
    game_property = f"-p:Sts2GameDir={game}"
    run([dotnet, "restore", PROJECT, "--locked-mode", "--configfile", MOD / "NuGet.Config", game_property], env)
    run([dotnet, "build", PROJECT, "--no-restore", "-c", "ExportRelease", game_property], env)
    dll = BUILD_OUTPUT / "PopSpireWomen.dll"
    if not dll.is_file():
        raise BuildError("Build returned success without the expected MOD assembly.")
    leaked = [p.name for p in BUILD_OUTPUT.glob("*.dll") if p.name != dll.name]
    if leaked:
        raise BuildError(f"Unexpected dependency DLLs in build output: {leaked}")
    receipt = {
        "game_version": "v0.107.1",
        "game_commit": "59260271",
        "game_references_sha256": hashes,
        "sdk": json.loads((MOD / "global.json").read_text())["sdk"]["version"],
        "godot_sdk": "4.5.1",
        "ritsulib_compat": "STS2.RitsuLib.Compat.0.107.1/0.6.7",
        "packages_lock_sha256": sha256(MOD / "packages.lock.json"),
        "mod_dll_sha256": sha256(dll),
        "game_launched": False,
        "game_installation_modified": False,
    }
    receipt_path = MOD / "build/build-receipt.json"
    receipt_path.parent.mkdir(exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(f"Build receipt: {receipt_path}", flush=True)


def export_package(build_output, dist, manifest_path, readme_path):
    manifest = json.loads(manifest_path.read_text())
    mod_id = manifest["id"]
    if mod_id != "PopSpireWomen" or manifest["has_pck"]:
        raise BuildError("Only the PopSpireWomen DLL-only bootstrap can be exported here.")
    if dist.is_symlink():
        raise BuildError("Refusing a symlink as export directory.")
    dist.mkdir(parents=True, exist_ok=True)
    destination = dist / mod_id
    # Explicit allowlist, independent of whatever the SDK leaves next to the DLL.
    sources = {
        f"{mod_id}.dll": build_output / f"{mod_id}.dll",
        f"{mod_id}.json": manifest_path,
        "README.md": readme_path,
    }
    if destination.is_symlink():
        raise BuildError("Refusing a symlink as package directory.")
    if destination.exists():
        unexpected = [p.name for p in destination.iterdir()
                      if p.name not in sources or not p.is_file() or p.is_symlink()]
        if unexpected:
            raise BuildError(f"Unexpected files in previous export; move them out before exporting: {unexpected}")
    archive = dist / f"{mod_id}-{manifest['version']}.zip"
    with tempfile.TemporaryDirectory(prefix=".psw-export-", dir=dist) as temp:
        temp = Path(temp)
        staged = temp / mod_id
        staged.mkdir()
        for name, source in sources.items():
            shutil.copyfile(source, staged / name)
        staged_zip = temp / archive.name
        with zipfile.ZipFile(staged_zip, "w", compression=zipfile.ZIP_DEFLATED) as package:
            for name in sorted(sources):
                info = zipfile.ZipInfo(f"{mod_id}/{name}", date_time=(1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                package.writestr(info, (staged / name).read_bytes())
        if destination.exists():
            shutil.rmtree(destination)  # Only our allowlisted generated files, checked above.
        staged.replace(destination)
        staged_zip.replace(archive)
    return archive


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["build", "test", "export"])
    parser.add_argument("--game-dir", default=os.environ.get("STS2_GAME_DIR"))
    parser.add_argument("--dotnet", default=os.environ.get("DOTNET", "dotnet"))
    parser.add_argument("--tools-dir", type=Path,
                        default=Path(tempfile.gettempdir()) / "sts2-tools/issue-7")
    args = parser.parse_args()
    try:
        # Diagnose game paths before any SDK/NuGet work.
        game, hashes = check_game(args.game_dir) if args.command != "test" else (None, {})
        env = dotnet_environment(args.tools_dir.expanduser().resolve())
        check_sdk(args.dotnet, env)
        if args.command == "test":
            run([sys.executable, "-m", "unittest", "discover", "-s", ROOT / "tests/build", "-p", "test_*.py", "-v"], env)
            test_project = ROOT / "tests/build/BootstrapChecks.csproj"
            run([args.dotnet, "restore", test_project, "--configfile", MOD / "NuGet.Config"], env)
            run([args.dotnet, "run", "--project", test_project, "--no-restore", "-c", "Release"], env)
        else:
            build(args.dotnet, env, game, hashes)
            if args.command == "export":
                archive = export_package(BUILD_OUTPUT, ROOT / "dist", MOD / "PopSpireWomen.json", MOD / "README.md")
                print(f"Exported: {archive}\nSHA-256: {sha256(archive)}\nNo game installation or launch performed.")
    except (BuildError, OSError, subprocess.CalledProcessError) as ex:
        print(f"build_mod: {ex}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
