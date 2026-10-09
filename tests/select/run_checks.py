#!/usr/bin/env python3
"""Compatibility entry point: selection checks now share the video-free animation fixtures."""
from pathlib import Path
import runpy
import sys

suite = Path(__file__).resolve().parents[1] / 'animation'
sys.path.insert(0, str(suite))
runpy.run_path(str(suite / 'run_checks.py'), run_name='__main__')
