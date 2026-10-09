#!/usr/bin/env python3
"""Build a PCK-only mod from owned resources and a pinned local game; never launches the game."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.pck_mod.build import main

if __name__ == "__main__":
    sys.exit(main())
