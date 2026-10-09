#!/usr/bin/env python3
"""Regent overlay's rendered, isolated Godot checks. Never launches the game."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def run(command, log, env=None):
    result = subprocess.run([str(x) for x in command], env=env, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=120)
    log.write_text(result.stdout)
    if result.returncode or any(x in result.stdout for x in
                               ("SCRIPT ERROR", "ERROR:", "instances leaked", "still in use at exit")):
        raise RuntimeError(f"Failed: {log}\n{result.stdout[-8000:]}")
    return result.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--godot", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    godot = args.godot.resolve()
    inputs = [ROOT / "mod/assets/PopSpireWomen/select/regent.tscn"]
    for folder in ("select/overlays/regent", "animation", "art/regent"):
        inputs.extend(p for p in (ROOT / "mod/assets/PopSpireWomen" / folder).rglob("*")
                      if p.is_file() and not p.name.endswith(".import"))
    inputs.extend((ROOT / "mod/assets/PopSpireWomen/select").glob("select_background.*"))
    inputs.extend(HERE.glob("*.gd"))
    inputs.append(Path(__file__))
    hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(inputs)}
    with tempfile.TemporaryDirectory(prefix="psw-regent-overlay-") as folder:
        project = Path(folder)
        shutil.copytree(ROOT / "mod/assets", project, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns(".godot", "*.import"))
        fixture = project / "PopSpireWomen/test-fixtures"
        fixture.mkdir(parents=True)
        (fixture / "sky.svg").write_text('''<svg xmlns="http://www.w3.org/2000/svg" width="2560" height="1200">
<defs><radialGradient id="sky" cx="67%" cy="43%" r="82%"><stop stop-color="#253d59"/>
<stop offset="0.53" stop-color="#14263d"/><stop offset="1" stop-color="#080f20"/></radialGradient></defs>
<rect width="2560" height="1200" fill="url(#sky)"/></svg>''')
        shutil.copyfile(HERE / "overlay_checks.gd", project / "overlay_checks.gd")
        original = project / "scenes/screens/char_select/char_select_bg_regent.tscn"
        original.parent.mkdir(parents=True)
        shutil.copyfile(ROOT / "tests/select/original_stub.tscn", original)
        run([godot, "--headless", "--path", project, "--editor", "--import"], output / "import.log")
        pack = output / "standalone-test-only.pck"
        run([godot, "--headless", "--path", project, "--export-pack", "Resources", pack], output / "export.log")
        host = project / "empty-host"
        host.mkdir()
        env = dict(os.environ, PSW_REGENT_OUTPUT=str(output), LIBGL_ALWAYS_SOFTWARE="1")
        log = run(["xvfb-run", "-a", "-s", "-screen 0 2560x1440x24", godot, "--path", host, "--main-pack", pack,
                   "--rendering-method", "gl_compatibility", "--audio-driver", "Dummy",
                   "--max-fps", "60", "--script", "res://overlay_checks.gd"], output / "checks.log", env)
        match = re.search(r"CHECKS=(\d+) FAILURES=0", log)
        if not match:
            raise RuntimeError("Overlay checks did not finish successfully")
    screenshots = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(output.glob("*.png"))}
    (output / "validation.json").write_text(json.dumps({
        "suite": "regent-overlay", "checks": int(match[1]), "failures": 0,
        "godot": "4.5.1.stable.official.f62fdbde1", "renderer": "GL Compatibility / software Mesa",
        "game_launched": False, "validator_runs": 0,
        "base_commit": "30bcf1ba4b9d8986a58bca5382d2e4205779b7b7",
        "inputs_sha256": hashes, "screenshots_sha256": screenshots,
        "fixture_scope": "Original sky and UI stand-ins; production overlay and delegated Regent body/rig. Test-only PCK, no game resources.",
    }, indent=2) + "\n")
    print(f"Regent overlay: {match[1]} checks passed; rendered evidence: {output}. Game not launched.")


if __name__ == "__main__":
    main()
