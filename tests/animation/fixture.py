"""Deterministic, original geometric artwork for rendering tests; never release assets."""
import json
from pathlib import Path


def create(folder: Path):
    folder.mkdir(parents=True, exist_ok=True)
    prefix = "res://PopSpireWomen/test-fixtures/"
    start = '<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1536" viewBox="0 0 1024 1536">'
    (folder / "body.svg").write_text(start + '''
<path d="M426 858 L475 858 L453 1430 L398 1430Z M553 858 L606 858 L625 1430 L570 1430Z" fill="#6b75c9"/>
<path d="M390 494 Q512 450 634 494 L596 930 L422 930Z" fill="#83cad0"/>
<path d="M392 500 L326 540 L292 820 L345 834 L433 558Z M630 500 L695 540 L742 820 L689 834 L591 558Z" fill="#ffd3ab"/>
<rect x="461" y="373" width="92" height="151" rx="25" fill="#ffd3ab"/>
<ellipse cx="509" cy="287" rx="118" ry="152" fill="#ffe4c7"/>
<path d="M390 298 Q337 76 512 105 Q678 78 628 299 Q590 141 393 285Z" fill="#51355b"/>
<path d="M449 300 L478 300 M541 300 L570 300" stroke="#392e54" stroke-width="14"/>
<path d="M484 361 Q509 378 535 361" fill="none" stroke="#a45668" stroke-width="7"/>
<path d="M685 832 L824 1136 L840 1127 L734 807Z" fill="#fff0b6"/>
</svg>''')
    (folder / "hair.svg").write_text(start + '<path d="M420 192 Q294 280 376 691 L417 794 Q317 434 472 281Z" fill="#51355b"/></svg>')
    (folder / "cloth.svg").write_text(start + '<path d="M597 625 Q728 704 718 1287 L559 1334 Q679 839 563 722Z" fill="#396b88"/></svg>')
    (folder / "eyes.svg").write_text(start + '<path d="M432 283 L488 283 L488 319 L432 319Z M531 283 L586 283 L586 319 L531 319Z" fill="#ffe4c7"/><path d="M449 305 L478 305 M541 305 L570 305" stroke="#392e54" stroke-width="6"/></svg>')
    (folder / "poster.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600"><rect width="800" height="600" fill="#243047"/><path d="M0 540 L800 540" stroke="#a3b4c8" stroke-width="3"/></svg>')
    rig = {
        "schema": 1, "canvas": [1024, 1536], "origin": [512, 1430], "display_height": 420,
        "body": prefix + "body.svg",
        "markers": {"hip": [512, 902], "chest": [512, 542], "head": [509, 290],
                    "hand_l": [320, 802], "hand_r": [719, 802], "foot_l": [426, 1417],
                    "foot_r": [594, 1417], "hair": [394, 382], "cloth": [639, 876]},
        "layers": [{"id": "hair_back", "texture": prefix + "hair.svg", "bone": "hair", "z": -1},
                   {"id": "cloth", "texture": prefix + "cloth.svg", "bone": "cloth", "z": -1},
                   {"id": "eyes", "texture": prefix + "eyes.svg", "bone": "head", "z": 1, "expression": "blink"}],
        "anchors": {"face": {"bone": "head", "position": [509, 290]},
                    "weapon": {"bone": "hand_r", "position": [719, 802]}},
        "clips": {}, "weapon_hand": "hand_r"
    }
    (folder / "rig.json").write_text(json.dumps(rig, indent=2) + "\n")
    return rig
