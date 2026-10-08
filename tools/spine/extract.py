"""CLI: python3 -m tools.spine.extract --help (run from the repository root)."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from . import formats
from .pck import ExtractionError, Pck, hashes, resource_path


# Main combat actor only. Do not guess by basename or include Regent's weapon/Osty/Orbs.
COMBAT = {
    "ironclad": ("scenes/creature_visuals/ironclad.tscn",
                 "animations/characters/ironclad/ironclad_skel_data.tres",
                 "animations/characters/ironclad/ironclad.atlas",
                 "animations/characters/ironclad/ironclad.skel"),
    "silent": ("scenes/creature_visuals/silent.tscn",
               "animations/characters/silent/silent_skel_data.tres",
               "animations/characters/silent/silent.atlas",
               "animations/characters/silent/silent.skel"),
    "regent": ("scenes/creature_visuals/regent.tscn",
               "animations/characters/regent/regent_skel_data.tres",
               "animations/characters/regent/regent.atlas",
               "animations/characters/regent/regent.skel"),
    "necrobinder": ("scenes/creature_visuals/necrobinder.tscn",
                   "animations/characters/necrobinder/necrobinder_skel_data.tres",
                   "animations/characters/necrobinder/necrobinder.atlas",
                   "animations/characters/necrobinder/necrobinder.skel"),
    "defect": ("scenes/creature_visuals/defect.tscn",
               "animations/characters/defect/defect_skel_data.tres",
               "animations/characters/defect/defect.atlas",
               "animations/characters/defect/defect.skel"),
}
TOOL_DIR = Path(__file__).resolve().parent


def json_bytes(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        while chunk := file.read(Pck.CHUNK_SIZE):
            digest.update(chunk)
    return digest.hexdigest()


def output_path(path: Path, game: Path) -> Path:
    absolute = Path(os.path.abspath(path))
    for candidate in (absolute, *absolute.parents):
        if candidate.is_symlink():
            raise ExtractionError(f"output path contains a symlink: {candidate}")
    absolute = absolute.resolve()
    if absolute == game or game in absolute.parents:
        raise ExtractionError("output must be outside the input game directory")
    for candidate in (absolute, *absolute.parents):
        if (candidate / ".git").exists():
            raise ExtractionError("raw game resources must not be extracted inside a Git working tree")
    if absolute.exists():
        raise ExtractionError(f"output already exists; choose a new directory: {absolute}")
    if not absolute.parent.is_dir():
        raise ExtractionError("output parent must already exist")
    return absolute


class Sink:
    def __init__(self, root: Path):
        self.root, self.outputs, self.names = root, [], set()

    def reserve(self, name: str) -> Path:
        name = resource_path(name)
        if name.casefold() in self.names:
            raise ExtractionError(f"duplicate output path: {name}")
        self.names.add(name.casefold())
        destination = self.root / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        return destination

    def record(self, name: str, data: bytes, role: str, operation: str, inputs: list[str]):
        self.outputs.append({"path": name, "role": role, "operation": operation,
                             "inputs": inputs, "size": len(data), **hashes(data)})

    def write(self, name: str, data: bytes, role: str, operation: str, inputs: list[str]):
        with self.reserve(name).open("xb") as file:
            file.write(data)
        self.record(name, data, role, operation, inputs)


def publish(stage: Path, destination: Path):
    """Create exclusively, then link without replacing any existing path (same filesystem)."""
    directories, files = [], []
    try:
        destination.mkdir(mode=0o700)  # Also refuses a concurrent empty directory.
        directories.append(destination)
        for source in sorted(stage.rglob("*")):
            target = destination / source.relative_to(stage)
            if source.is_dir():
                target.mkdir(mode=0o700)
                directories.append(target)
            else:
                os.link(source, target)  # FileExistsError; never overwrite a file.
                files.append(target)
    except BaseException:
        for path in reversed(files):
            path.unlink()
        for path in reversed(directories):
            path.rmdir()
        raise


def resolve_godot(value: str | None) -> tuple[Path, dict]:
    binary = shutil.which(value or "godot")
    if not binary:
        raise ExtractionError("PNG decoding requires Godot 4.5.1: pass --godot or use --texture-mode embedded")
    path = Path(binary).resolve(strict=True)
    try:
        result = subprocess.run([str(path), "--version"], check=True,
                                capture_output=True, text=True, timeout=15)
    except (subprocess.SubprocessError, OSError) as error:
        raise ExtractionError(f"could not check Godot version: {type(error).__name__}") from error
    version = result.stdout.strip()
    if not version.startswith("4.5.1.stable."):
        raise ExtractionError(f"unsupported Godot decoder version {version!r}; expected 4.5.1.stable")
    return path, {"path": str(path), "version": version, "sha256": file_sha256(path)}


def decode_pages(binary: Path, sink: Sink, pages: list[dict]) -> dict:
    # Only our script and selected embedded image buffers enter this isolated project.
    # ResourceLoader, the game PCK, game scenes, DLLs, and extensions are never loaded.
    with tempfile.TemporaryDirectory(prefix=".decode-", dir=sink.root) as temporary:
        directory = Path(temporary)
        (directory / "project.godot").write_text(
            'config_version=5\n[application]\nconfig/name="StS2SpineBufferDecode"\n', encoding="utf-8")
        script = directory / "decode_pages.gd"
        script.write_bytes((TOOL_DIR / "decode_pages.gd").read_bytes())
        jobs = []
        for page in pages:
            output = "authoring/" + page["name"]
            jobs.append({"input": str(sink.root / page["embedded_output"]),
                         "output": str(sink.reserve(output)), "name": page["name"],
                         "encoding": page["ctex"]["encoding"], "size": page["size"],
                         "format": page["ctex"]["godot_pixel_format"]})
        job_path, result_path = directory / "jobs.json", directory / "results.json"
        job_path.write_bytes(json_bytes({"jobs": jobs, "result": str(result_path)}))
        command = [str(binary), "--headless", "--path", str(directory),
                   "--log-file", str(directory / "godot.log"), "--script", str(script),
                   "--", str(job_path)]
        try:
            process = subprocess.run(command, capture_output=True, text=True, timeout=60)
        except (subprocess.SubprocessError, OSError) as error:
            raise ExtractionError(f"Godot buffer decode failed: {type(error).__name__}") from error
        if process.returncode or not result_path.is_file():
            detail = (process.stderr + process.stdout)[-2000:].strip()
            raise ExtractionError(f"Godot buffer decode failed (exit {process.returncode}): {detail}")
        result = formats.json_object(result_path.read_bytes())
        records = result.get("pages")
        if not isinstance(records, list) or len(records) != len(pages):
            raise ExtractionError("Godot decoder returned an incomplete page list")
        for page, record in zip(pages, records):
            if (record.get("name") != page["name"] or record.get("size") != page["size"]
                    or not record.get("png_pixels_equal")
                    or len(record.get("pixels_sha256", "")) != 64):
                raise ExtractionError("Godot PNG pixel verification failed")
            output = "authoring/" + page["name"]
            png = (sink.root / output).read_bytes()
            if formats.png_dimensions(png) != page["size"]:
                raise ExtractionError("decoded PNG dimensions do not match atlas page")
            sink.record(output, png, "atlas_page_png", "Godot Image buffer to PNG; no rescale/alpha correction",
                        [page["ctex_resource"], page["embedded_output"]])
            page["png_output"], page["pixel_verification"] = output, record
        return {"status": "complete", "engine": result.get("engine"),
                "method": "Image.load_*_from_buffer -> CTEX RGB8/RGBA8 -> PNG; verified equal pixels"}


def extract(game_path: Path, character: str, output: Path,
            texture_mode: str = "png", godot: str | None = None) -> dict:
    if character not in COMBAT:
        raise ExtractionError(f"unsupported combat character: {character}")
    if texture_mode not in ("png", "embedded"):
        raise ExtractionError(f"unsupported texture mode: {texture_mode}")
    game = Path(game_path).resolve(strict=True)
    if not game.is_dir():
        raise ExtractionError("game path must be a directory")
    destination = output_path(Path(output), game)
    release_path = game / "release_info.json"
    release_stat = release_path.stat()
    if release_stat.st_size > 65536:
        raise ExtractionError("release_info.json exceeds 64 KiB")
    release_bytes = release_path.read_bytes()
    release = formats.json_object(release_bytes)
    if release.get("version") != "v0.107.1" or release.get("commit") != "59260271":
        raise ExtractionError("unsupported game release; expected v0.107.1 / 59260271")
    binary, decoder = resolve_godot(godot) if texture_mode == "png" else (None, None)
    scene_path, data_path, atlas_path, skeleton_path = COMBAT[character]
    with tempfile.TemporaryDirectory(prefix=f".{destination.name}-", dir=destination.parent) as temporary:
        stage, resources = Path(temporary), []
        sink = Sink(stage)
        sink.write("sources/release_info.json", release_bytes, "release_info", "byte_copy", [str(release_path)])
        with Pck(game / "SlayTheSpire2.pck") as pack:
            def read(path, role, local_path=None):
                payload, evidence = pack.read(path)
                output_name = local_path or "sources/" + path
                sink.write(output_name, payload, role, "byte_copy", [path])
                evidence.update({"role": role, "raw_output": output_name})
                resources.append(evidence)
                return payload

            scene = read(scene_path, "combat_scene")
            main_refs = [ref for ref in formats.ext_resources(scene).values()
                         if ref["type"] == "SpineSkeletonDataResource" and ref["path"] == data_path]
            if len(main_refs) != 1:
                raise ExtractionError("combat scene does not reference the explicit main skeleton data")
            data = read(data_path, "skeleton_data_with_animation_mixes")
            refs = formats.skeleton_references(data)
            if refs != {"atlas_res": atlas_path, "skeleton_file_res": skeleton_path}:
                raise ExtractionError("main skeleton data references differ from the explicit mapping")
            skel_import = read(skeleton_path + ".import", "skeleton_import")
            skel_target = formats.import_target(skel_import, "spine.skel", "SpineSkeletonFileResource", ".spskel")
            skeleton = read(skel_target, "raw_spine_binary", f"authoring/{character}.skel")
            header = formats.skeleton_header(skeleton)
            atlas_import = read(atlas_path + ".import", "atlas_import")
            atlas_target = formats.import_target(atlas_import, "spine.atlas", "SpineAtlasResource", ".spatlas")
            atlas_data = read(atlas_target, "spatlas_json")
            atlas_bytes, atlas_metadata, pages = formats.atlas(atlas_data, atlas_path)
            sink.write(f"authoring/{character}.atlas", atlas_bytes, "spine_atlas",
                       "UTF-8 encoding of spatlas JSON atlas_data (exact line endings)", [atlas_target])
            for page in pages:
                import_path = page["texture_path"] + ".import"
                texture_import = read(import_path, "page_texture_import")
                ctex_path = formats.import_target(texture_import, "texture", "CompressedTexture2D", ".ctex")
                raw = read(ctex_path, "raw_page_texture_ctex")
                embedded, container = formats.ctex(raw)
                if container["size"] != page["size"]:
                    raise ExtractionError(f"atlas/CTEX page size mismatch: {page['name']}")
                embedded_output = "sources/embedded/" + page["name"] + "." + container["encoding"]
                sink.write(embedded_output, embedded, "embedded_page_image", "CTEX base mip payload byte_copy", [ctex_path])
                page.update({"import_resource": import_path, "ctex_resource": ctex_path,
                             "ctex": container, "embedded_output": embedded_output,
                             "png_output": None})
            decoded = decode_pages(binary, sink, pages) if binary else {
                "status": "not_requested",
                "reason": "--texture-mode embedded; PNG decode and pixel validation have not run",
            }
            pack.assert_unchanged()
            current_release_stat = release_path.stat()
            if (any(getattr(current_release_stat, field) != getattr(release_stat, field)
                    for field in ("st_dev", "st_ino", "st_size", "st_mtime_ns"))
                    or release_path.read_bytes() != release_bytes):
                raise ExtractionError("input release_info.json changed during extraction")
            tool_hashes = {file.name: file_sha256(file) for file in sorted(TOOL_DIR.iterdir())
                           if file.suffix in (".py", ".gd") and file.is_file()}
            manifest = {
                "schema_version": 1, "tool": {"name": "sts2-spine-extraction", "version": "1", "sha256": tool_hashes},
                "created_utc": datetime.now(timezone.utc).isoformat(), "character": character, "context": "combat_main",
                "source": {"game_path": str(game), "release_info": release,
                           "release_info_file": {"path": str(release_path), **hashes(release_bytes)}, "pck": pack.info},
                "mapping": {"scene": scene_path, "skeleton_data": data_path,
                            "atlas": atlas_path, "skeleton": skeleton_path,
                            "spatlas": atlas_target, "spskel": skel_target},
                "skeleton_header": header, "atlas_metadata": atlas_metadata, "pages": pages,
                "resources": resources, "outputs": sink.outputs,
                "texture_mode": texture_mode, "decoder": decoder, "png_decode": decoded,
                "authoring": {
                    "editor_import_save_export": "not_tested", "original_editor_project": "not_recovered",
                    "original_high_resolution_psd": "not_recovered",
                    "limitations": ["Only main combat actor; select/rest/merchant/weapon/Osty/Orbs excluded",
                                    "Exported packed pixels only; no restoration of original resolution or PSD layers",
                                    "Atlas rotation/trim/scale/pma metadata preserved; no alpha or scale correction",
                                    "Binary prefix inspected; full parse/render/Editor round trip not performed"],
                },
            }
            (stage / "manifest.json").write_bytes(json_bytes(manifest))
            # No destination is created until all integrity/format/decode checks succeed.
            publish(stage, destination)
    return {"output": str(destination), "character": character, "pages": len(pages),
            "resources": len(resources), "png_decode": decoded["status"],
            "manifest_sha256": file_sha256(destination / "manifest.json")}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Extract supported StS2 main combat Spine assets without modifying the game.")
    parser.add_argument("--game-path", required=True, type=Path)
    parser.add_argument("--character", required=True, choices=tuple(COMBAT))
    parser.add_argument("--output", required=True, type=Path, help="New directory outside the game and Git working trees")
    parser.add_argument("--context", choices=("combat",), default="combat")
    parser.add_argument("--texture-mode", choices=("png", "embedded"), default="png")
    parser.add_argument("--godot", help="Godot 4.5.1 stable binary; otherwise looks up 'godot' on PATH")
    args = parser.parse_args(argv)
    try:
        result = extract(args.game_path, args.character, args.output, args.texture_mode, args.godot)
    except (ExtractionError, OSError) as error:
        print(f"spine-extraction: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
