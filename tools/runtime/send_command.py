#!/usr/bin/env python3
"""Send a complete, atomically published command to the isolated Godot QA harness."""

import argparse
import json
from pathlib import Path
import re
import time

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--root", type=Path, required=True)
parser.add_argument("--id", required=True)
parser.add_argument("--timeout", type=float, default=20)
parser.add_argument("command", help="JSON command object, without transport metadata")
args = parser.parse_args()
if not re.fullmatch(r"[A-Za-z0-9_-]+", args.id):
    parser.error("id must be a simple filename component")
command = json.loads(args.command)
if not isinstance(command, dict):
    parser.error("command must be an object")
command["id"] = args.id
target = args.root / "commands" / (args.id + ".json")
result = args.root / "results" / (args.id + ".json")
if target.exists() or Path(str(target) + ".done").exists() or result.exists():
    raise SystemExit("Command id already used; refusing stale replay")
temporary = target.with_suffix(".pending")
temporary.write_text(json.dumps(command) + "\n", encoding="utf-8")
temporary.replace(target)
deadline = time.monotonic() + min(max(args.timeout, 1), 55)
while time.monotonic() < deadline:
    try:
        response = json.loads(result.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        time.sleep(0.1)
        continue
    print(json.dumps(response, ensure_ascii=False))
    raise SystemExit(0 if response.get("ok") else 1)
raise SystemExit("Command response timed out; inspect the owned QA game logs")
