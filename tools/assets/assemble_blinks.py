#!/usr/bin/env python3
"""Assemble generated eye pixels into runtime layers without redrawing the source art.

Run with: uv run --no-project --with pillow python tools/assets/assemble_blinks.py
The versioned provenance file is the recipe; this command does not call any image API.
"""
from pathlib import Path
import hashlib
import json

from PIL import Image, ImageChops, ImageFilter

ROOT = Path(__file__).resolve().parents[2]
CHARACTERS = ("ironclad", "regent", "necrobinder", "defect")


def checked_image(path: str, expected: str) -> Image.Image:
    source = ROOT / path
    if hashlib.sha256(source.read_bytes()).hexdigest() != expected:
        raise ValueError(f"Source changed; update the production recipe deliberately: {path}")
    return Image.open(source).convert("RGBA")


def main() -> None:
    for character in CHARACTERS:
        recipe = json.loads((ROOT / f"output/imagegen/{character}/{character}-blink-builtin-v01.provenance.json").read_text())
        body = checked_image(recipe["source"], recipe["source_sha256"])
        generated = checked_image(recipe["generated_output"], recipe["generated_sha256"])
        left, top, right, bottom = recipe["crop_xyxy"]
        mask = Image.open(ROOT / recipe["mask"]).convert("RGBA").getchannel("A")
        if mask.size != body.size or not (0 <= left < right <= body.width and 0 <= top < bottom <= body.height):
            raise ValueError(f"Invalid registration geometry: {character}")
        mask = mask.point(lambda a: 255 - a).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(1.0))
        mask = ImageChops.multiply(mask, body.getchannel("A"))
        layer = Image.new("RGBA", body.size)
        layer.paste(generated.resize((right - left, bottom - top), Image.Resampling.LANCZOS), (left, top))
        layer.putalpha(mask)
        target = ROOT / recipe["runtime"]
        target.parent.mkdir(parents=True, exist_ok=True)
        layer.save(target)
        print(f"Assembled {character}: {mask.getbbox()}")


if __name__ == "__main__":
    main()
