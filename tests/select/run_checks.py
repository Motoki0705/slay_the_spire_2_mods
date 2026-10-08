#!/usr/bin/env python3
"""Real Godot playback with generated technical fixtures, isolated from shipping assets."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def run(command, log, env=None, timeout=60):
    result = subprocess.run([str(arg) for arg in command], text=True, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, env=env, timeout=timeout)
    log.write_text(result.stdout)
    if result.returncode or any(marker in result.stdout for marker in ["SCRIPT ERROR", "instances leaked", "still in use at exit"]):
        raise RuntimeError(f"Check failed ({result.returncode}): {log}\n{result.stdout[-8000:]}")
    return result.stdout


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--godot", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--pck", required=True, type=Path)
    args = parser.parse_args()
    godot = args.godot.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="psw-select-") as folder:
        project = Path(folder)
        shutil.copytree(ROOT / "mod/assets", project, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns(".godot"))
        # Keep both the UI harness and all synthesis out of mod/assets and the exported PCK.
        fixture = project / "PopSpireWomen/test-fixtures"
        fixture.mkdir()
        for name in ["overlay.gd", "overlay.tscn"]:
            shutil.copyfile(HERE / name, fixture / name)
        for name in ["a", "b"]:
            source = "testsrc2=size=96x64:rate=24:duration=1" if name == "a" else "color=c=blue:size=96x64:rate=24:duration=1"
            run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i", source,
                 "-an", "-c:v", "libtheora", "-q:v", "6", "-pix_fmt", "yuv420p", fixture / f"{name}.ogv"], output / f"encode-{name}.log")
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i", "color=c=darkblue:size=96x64",
             "-frames:v", "1", "-threads", "1", fixture / "poster.png"], output / "poster.log")
        (fixture / "broken.ogv").write_bytes(b"deliberately invalid Theora technical fixture")
        (fixture / "wrong_type.tres").write_text('[gd_resource type="Gradient" format=3]\n[resource]\n')
        manifest = {}
        for path in sorted(fixture.glob("*.ogv")):
            item = {"sha256": digest(path), "bytes": path.stat().st_size, "synthetic": True}
            if path.stem != "broken":
                result = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-of", "json", str(path)],
                                        capture_output=True, text=True, check=True)
                item["streams"] = json.loads(result.stdout)["streams"]
                assert len(item["streams"]) == 1 and item["streams"][0]["codec_name"] == "theora"
            manifest[path.name] = item
        manifest["poster.png"] = {"sha256": digest(fixture / "poster.png"), "synthetic": True}
        (output / "fixtures.json").write_text(json.dumps(manifest, indent=2) + "\n")
        # Exercise the actual release gate with a real video+audio file, then remove it.
        audio_fixture = project / "audio-negative"
        audio_fixture.mkdir()
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i", "color=size=96x64:duration=0.2",
             "-f", "lavfi", "-i", "sine=duration=0.2", "-c:v", "libtheora", "-c:a", "libvorbis", "-shortest",
             audio_fixture / "with-audio.ogv"], output / "audio-negative.log")
        spec = importlib.util.spec_from_file_location("build_mod", ROOT / "scripts/build_mod.py")
        build = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(build)
        try:
            build.check_videos(audio_fixture, "ffprobe")
        except build.BuildError:
            (output / "audio-gate.txt").write_text("PASS: real Theora+Vorbis file rejected by production audio gate\n")
        else:
            raise RuntimeError("Release gate accepted video with audio")
        shutil.rmtree(audio_fixture)
        originals = project / "scenes/screens/char_select"
        originals.mkdir(parents=True)
        for character in ["ironclad", "silent", "regent", "necrobinder", "defect"]:
            shutil.copyfile(HERE / "original_stub.tscn", originals / f"char_select_bg_{character}.tscn")
        shutil.copyfile(HERE / "playback_checks.gd", project / "playback_checks.gd")
        run([godot, "--headless", "--path", project, "--editor", "--import"], output / "import.log")
        # Export the separate technical project. The rendered suite below runs only from this PCK.
        technical_pack = output / "technical-fixtures.pck"
        run([godot, "--headless", "--path", project, "--export-pack", "Resources", technical_pack], output / "fixture-export.log")
        env = dict(os.environ, PSW_SELECT_OUTPUT=str(output))
        empty_host = project / "empty-host"
        empty_host.mkdir()
        playback = run(["xvfb-run", "-a", godot, "--path", empty_host, "--main-pack", technical_pack, "--rendering-method", "gl_compatibility",
                       "--audio-driver", "Dummy", "--max-fps", "60", "--script", "res://playback_checks.gd"],
                       output / "playback.log", env)
        if "FAILURES=0" not in playback:
            raise RuntimeError("Playback suite did not finish")
    # No source tree exists in this second host: loading must come from the actual pack.
    with tempfile.TemporaryDirectory(prefix="psw-pack-") as folder:
        host = Path(folder)
        (host / "project.godot").write_text('config_version=5\n[application]\nconfig/name="PCK test host"\n')
        shutil.copyfile(ROOT / "mod/tools/verify_pack.gd", host / "verify_pack.gd")
        pack = run([godot, "--headless", "--path", host, "--script", "res://verify_pack.gd", "--", args.pck.resolve()],
                   output / "pack.log")
        if "PACK_CHECKS=5" not in pack:
            raise RuntimeError("Pack suite did not finish")
    print(f"Real playback and isolated PCK checks passed. Evidence: {output}")


if __name__ == "__main__":
    main()
