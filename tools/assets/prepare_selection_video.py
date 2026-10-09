#!/usr/bin/env python3
"""Prepare reviewed H3 sources for silent Godot playback, retaining native pixels."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess

CHARACTERS = ("ironclad", "silent", "regent", "necrobinder", "defect")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(args):
    subprocess.run([str(a) for a in args], check=True)


def probe(path):
    return json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-count_frames", "-show_entries",
        "stream=codec_type,codec_name,width,height,avg_frame_rate,nb_read_frames:format=duration",
        "-of", "json", str(path)], text=True))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.root.resolve()
    records = []
    # Blend the last eight frames into the first eight, then play frames 8..183.
    # Start/end then become adjacent source frames 183/184 instead of a hard cut.
    # Source remains 8s; the delivered 184-frame loop is 7 2/3s at 24fps.
    loop = ("[0:v]split=3[t0][h0][m0];"
            "[t0]trim=start_frame=184:end_frame=192,setpts=PTS-STARTPTS[t];"
            "[h0]trim=start_frame=0:end_frame=8,setpts=PTS-STARTPTS[h];"
            "[t][h]blend=all_expr='A*(1-min(1,T*24/7))+B*min(1,T*24/7)'[join];"
            "[m0]trim=start_frame=8:end_frame=184,setpts=PTS-STARTPTS[m];"
            "[join][m]concat=n=2:v=1:a=0,setsar=1,format=yuv420p[v]")
    for character in CHARACTERS:
        folder = root / "output/videogen" / character
        source = folder / "selection-h3-v02-take01.mp4"
        meta = probe(source)
        video = next(s for s in meta["streams"] if s["codec_type"] == "video")
        if (video["width"], video["height"], video["avg_frame_rate"], video["nb_read_frames"]) != (1344, 768, "24/1", "192"):
            raise ValueError(f"Unreviewed source geometry/timing: {character}")
        target = root / "mod/assets/PopSpireWomen/art" / character
        movie, poster = target / "select_loop.ogv", target / "select_poster.png"
        preview = folder / "selection-h3-v02-loop.mp4"
        if any(p.exists() for p in (movie, poster, preview)):
            raise FileExistsError(f"Refusing to overwrite existing video delivery: {character}")
        common = ["ffmpeg", "-v", "error", "-i", source, "-filter_complex", loop, "-map", "[v]", "-an", "-map_metadata", "-1", "-r", "24"]
        run([*common, "-c:v", "libtheora", "-q:v", "9", movie])
        run([*common, "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-movflags", "+faststart", preview])
        run(["ffmpeg", "-v", "error", "-i", movie, "-an", "-frames:v", "1", poster])
        for file in (movie, preview):
            result = probe(file)
            if len(result["streams"]) != 1 or result["streams"][0]["codec_type"] != "video":
                raise ValueError(f"Unexpected audio/multiple streams: {file.name}")
            v = result["streams"][0]
            if (v["width"], v["height"], v["nb_read_frames"]) != (1344, 768, "184"):
                raise ValueError(f"Unexpected loop frame geometry: {file.name}")
        # Media properties are project-owned and keep their existing fallback rig.
        scene = root / "mod/assets/PopSpireWomen/select/production" / f"{character}.tscn"
        text = scene.read_text()
        if "video_path =" in text or "poster_path =" in text:
            raise ValueError("Scene already has an explicit video/poster; review before changing")
        text += (f'video_path = "res://PopSpireWomen/art/{character}/select_loop.ogv"\n'
                 f'poster_path = "res://PopSpireWomen/art/{character}/select_poster.png"\n')
        scene.write_text(text)
        record = {"character": character, "source": str(source.relative_to(root)),
                  "source_sha256": digest(source), "source_probe": meta, "source_seconds": 8,
                  "loop_frames": 184, "fps": 24, "overlap_frames": 8,
                  "loop_edit": "tail184..191 blended into head0..7, followed by source8..183",
                  "native_dimensions_preserved": [1344, 768], "audio_removed": True,
                  "display": "Godot aspect-cover; no anisotropic stretching",
                  "files": {str(p.relative_to(root)): {"sha256": digest(p), "bytes": p.stat().st_size}
                            for p in (movie, poster, preview)}, "movie_probe": probe(movie)}
        (folder / "selection-h3-v02-production.json").write_text(json.dumps(record, indent=2) + "\n")
        records.append(record)
        print(character + ": 184-frame silent Theora loop, matching poster and MP4 preview", flush=True)
    (root / "output/videogen/production-v02.json").write_text(json.dumps({"schema": 1, "clips": records}, indent=2) + "\n")


if __name__ == "__main__":
    main()
