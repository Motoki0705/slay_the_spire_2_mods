#!/usr/bin/env python3
"""Rendered Godot + PCK tests, using only original synthetic geometry and mock driver data."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from fixture import create

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def run(command, log, env=None):
    result = subprocess.run([str(x) for x in command], env=env, text=True, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, timeout=90)
    log.write_text(result.stdout)
    if result.returncode or any(x in result.stdout for x in ['SCRIPT ERROR', 'ERROR:', 'instances leaked', 'still in use at exit']):
        raise RuntimeError(f"Failed: {log}\n{result.stdout[-10000:]}")
    return result.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--godot', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--pck', type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    godot = args.godot.resolve()
    with tempfile.TemporaryDirectory(prefix='psw-animation-') as folder:
        project = Path(folder)
        shutil.copytree(ROOT / 'mod/assets', project, dirs_exist_ok=True, ignore=shutil.ignore_patterns('.godot'))
        fixture = project / 'PopSpireWomen/test-fixtures'
        create(fixture)
        for name in ['overlay.gd', 'overlay.tscn']:
            shutil.copyfile(ROOT / 'tests/select' / name, fixture / name)
        shutil.copyfile(HERE / 'mock_driver.gd', fixture / 'mock_driver.gd')
        for name in ['animation_checks.gd']:
            shutil.copyfile(HERE / name, project / name)
        shutil.copyfile(ROOT / 'tests/select/playback_checks.gd', project / 'playback_checks.gd')
        originals = project / 'scenes/screens/char_select'
        originals.mkdir(parents=True)
        for character in ['ironclad', 'silent', 'regent', 'necrobinder', 'defect']:
            shutil.copyfile(ROOT / 'tests/select/original_stub.tscn', originals / f'char_select_bg_{character}.tscn')
        manifest = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(fixture.iterdir())}
        (output / 'fixtures.json').write_text(json.dumps(manifest, indent=2)+'\n')
        run([godot, '--headless', '--path', project, '--editor', '--import'], output / 'import.log')
        pack = output / 'technical-fixtures.pck'
        run([godot, '--headless', '--path', project, '--export-pack', 'Resources', pack], output / 'export.log')
        host = project / 'empty-host'
        host.mkdir()
        env = dict(os.environ, PSW_ANIMATION_OUTPUT=str(output))
        for suite in ['animation_checks', 'playback_checks']:
            text = run(['xvfb-run', '-a', godot, '--path', host, '--main-pack', pack, '--rendering-method',
                        'gl_compatibility', '--audio-driver', 'Dummy', '--max-fps', '60',
                        '--script', f'res://{suite}.gd'], output / f'{suite}.log', env)
            if 'FAILURES=0' not in text:
                raise RuntimeError(f'{suite} did not finish')
    if args.pck:
        with tempfile.TemporaryDirectory(prefix='psw-verify-') as folder:
            host = Path(folder)
            (host / 'project.godot').write_text('config_version=5\n')
            shutil.copyfile(ROOT / 'mod/tools/verify_pack.gd', host / 'verify_pack.gd')
            run([godot, '--headless', '--path', host, '--script', 'res://verify_pack.gd', '--', args.pck.resolve()], output / 'pack.log')
    print(f'Rendered animation, selection and PCK checks passed: {output}. Game not launched.')


if __name__ == '__main__':
    main()
