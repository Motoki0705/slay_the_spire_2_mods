#!/usr/bin/env python3
"""Check measured context art/mesh inputs and render real rigs with standalone Godot.

The input root may be another worktree. Its PNGs are copied byte-for-byte only
into a temporary Godot project. Logs/screens/GIFs are not gameplay evidence.
"""
import argparse
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from PIL import Image, ImageChops
from shapely.geometry import Polygon, Point

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/assets'))
from build_contextual_rigs import build, make_rig, digest


def run(command, log, env=None):
    result = subprocess.run([str(p) for p in command], env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=240)
    log.write_text(result.stdout)
    if result.returncode or any(s in result.stdout for s in ('SCRIPT ERROR','ERROR:','instances leaked','still in use at exit')):
        raise RuntimeError(f'{log}: {result.stdout[-8000:]}')
    return result.stdout


def geometry(entry, rig):
    mesh = next(m for m in rig['meshes'] if m['id']=='body')
    area = 0
    for triangle in mesh['triangles']:
        p = Polygon([mesh['vertices'][i] for i in triangle])
        assert p.is_valid and p.area > 1e-9
        area += p.area
    assert abs(area-rig['canvas'][0]*rig['canvas'][1]) < 0.02, 'Mesh must cover its source canvas exactly once'
    for weights in mesh['weights']:
        assert all(x >= 0 for x in weights.values()) and abs(sum(weights.values())-1) < 1e-9
    assert len(mesh['vertices'])<=4096 and len(mesh['triangles'])<=8192
    probes = dict(entry.get('probes',{}))
    if entry.get('weapon'):
        weapon = Polygon(entry['weapon']['polygon'])
        for name, p in entry['weapon']['probes'].items():
            assert weapon.covers(Point(p)), name
            probes['weapon_'+name] = {'position':p,'bone':rig['weapon_hand']}
    for name, site in probes.items():
        p=Point(site['position'])
        faces=[t for t in mesh['triangles'] if Polygon([mesh['vertices'][i] for i in t]).covers(p)]
        assert faces, f'{name} not in mesh'
        assert any(all(mesh['weights'][i]=={site['bone']:1.0} for i in t) for t in faces), f'{name} not wholly rigid'
    return {'vertices':len(mesh['vertices']),'triangles':len(mesh['triangles']),'canvas_area':area,'rigid_probes':len(probes)}


def input_guards(entries, input_root, output):
    # A bad late input must leave earlier outputs and the receipt untouched.
    if len(entries)<2: return
    with tempfile.TemporaryDirectory(prefix='guard-',dir=output) as folder:
        base=Path(folder)
        for e in entries:
            relatives=[Path('mod/assets/PopSpireWomen/art')/e['character']/e['image']]
            relatives += [Path('mod/assets')/s['texture'].removeprefix('res://') for s in e.get('supports',[])]
            for relative in relatives:
                target=base/relative
                target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(input_root/relative,target)
        recipe=base/'recipes.json'
        recipe.write_text(json.dumps({'schema':1,'poses':entries}))
        build(base,recipe,base)
        original={p:p.read_bytes() for p in base.rglob('*_rig.json')}
        receipt=base/'tools/assets/contextual-rigs-receipt.json'
        original[receipt]=receipt.read_bytes()
        last=entries[-1]
        image=base/'mod/assets/PopSpireWomen/art'/last['character']/last['image']
        image.write_bytes(image.read_bytes()+b'input changed')
        try:
            build(base,recipe,base)
            raise AssertionError('Accepted a changed source')
        except ValueError as exc:
            assert 'Artwork changed' in str(exc)
        assert all(p.read_bytes()==data for p,data in original.items())
        duplicate=deepcopy(entries)
        duplicate[-1]=deepcopy(entries[0])
        recipe.write_text(json.dumps({'schema':1,'poses':duplicate}))
        try:
            build(base,recipe,base)
            raise AssertionError('Accepted duplicate context')
        except ValueError as exc:
            assert 'duplicate' in str(exc)
        assert all(p.read_bytes()==data for p,data in original.items())


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-root',type=Path,default=ROOT)
    parser.add_argument('--godot',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--contexts',nargs='*',help='Only changed character/surface inputs need rerendering')
    parser.add_argument('--skip-guards',action='store_true',help='Skip already-passed pipeline guards when only art changed')
    args=parser.parse_args()
    output=args.output.resolve();output.mkdir(parents=True,exist_ok=True)
    input_root=args.input_root.resolve()
    entries=json.loads((ROOT/'tools/assets/contextual-poses.json').read_text())['poses']
    if args.contexts:
        requested=set(args.contexts)
        entries=[e for e in entries if e['character']+'/'+e['surface'] in requested]
        assert {e['character']+'/'+e['surface'] for e in entries}==requested
    if not args.skip_guards: input_guards(entries,input_root,output)
    inputs=[];shapes={}
    with tempfile.TemporaryDirectory(prefix='context-rigs-',dir=output) as folder:
        stage=Path(folder)
        for name in ('project.godot','export_presets.cfg'):
            shutil.copyfile(ROOT/'mod/assets'/name,stage/name)
        animation=stage/'PopSpireWomen/animation';animation.mkdir(parents=True)
        for name in ('puppet.gd','rig_schema.gd','motion_library.gd','binding_lease.gd'):
            shutil.copyfile(ROOT/'mod/assets/PopSpireWomen/animation'/name,animation/name)
        for entry in entries:
            c,s=entry['character'],entry['surface']
            source=ROOT/f'mod/assets/PopSpireWomen/art/{c}/{s}_rig.json'
            generated=ROOT/f'mod/assets/PopSpireWomen/rigs/{c}/{s}.json'
            rig=json.loads(generated.read_text())
            assert rig==json.loads(source.read_text()), 'Old overrides must not overwrite a measured source rig'
            shapes[c+'/'+s]=geometry(entry,rig)
            refs=[rig['body']]+[x['texture'] for f in ('layers','meshes') for x in rig[f]]
            for reference in set(refs):
                relative=Path(reference.removeprefix('res://'))
                target=stage/relative;target.parent.mkdir(parents=True,exist_ok=True)
                image=input_root/'mod/assets'/relative
                before=digest(image)
                shutil.copyfile(image,target)
                assert digest(target)==before
                inputs.append({'path':str(Path('mod/assets')/relative),'sha256':before})
            assert digest(input_root/'mod/assets'/rig['body'].removeprefix('res://'))==entry['image_sha256']
            with Image.open(input_root/'mod/assets'/rig['body'].removeprefix('res://')) as image:
                probes={name:site['position'] for name,site in entry.get('probes',{}).items()}
                probes.update(entry.get('weapon',{}).get('probes',{}))
                for name,point in probes.items():
                    assert image.getpixel(tuple(round(x) for x in point))[3]>=128, f'{c}/{s} probe {name} must measure visible painted pixels'
            target=stage/f'PopSpireWomen/rigs/{c}/{s}.json';target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(generated,target)
            inputs.append({'path':str(generated.relative_to(ROOT)),'sha256':digest(generated)})
        (stage/'contextual-inputs.json').write_text(json.dumps({'poses':entries}))
        shutil.copyfile(ROOT/'tests/assets/contextual_render.gd',stage/'contextual_render.gd')
        # Persist the fixture's identity even if a later visual/neutral check fails.
        (output/'inputs.json').write_text(json.dumps({'inputs':inputs,'renderer_sha256':digest(ROOT/'tests/assets/contextual_render.gd'),'game_launched':False,'validator':0},indent=2)+'\n')
        run([args.godot,'--headless','--path',stage,'--editor','--import'],output/'import.log')
        pack=output/'contextual-fixtures.pck'
        run([args.godot,'--headless','--path',stage,'--export-pack','Resources',pack],output/'export.log')
        host=stage/'empty-host';host.mkdir()
        text=run(['xvfb-run','-a',args.godot,'--path',host,'--main-pack',pack,'--rendering-method','gl_compatibility','--audio-driver','Dummy','--max-fps','60','--script','res://contextual_render.gd'],output/'render.log',dict(os.environ,PSW_CONTEXTUAL_OUTPUT=str(output)))
        assert 'FAILURES=0' in text
    neutral={}
    for entry in entries:
        id=entry['character']+'-'+entry['surface']
        before=Image.open(output/(id+'-neutral-original.png')).convert('RGB')
        after=Image.open(output/(id+'-neutral-mesh.png')).convert('RGB')
        difference=ImageChops.difference(before,after)
        changed=sum(max(p)>16 for p in difference.getdata())
        neutral[id]={'pixels_delta_over_16':changed,'total_pixels':before.width*before.height}
        assert changed<20, f'{id}: neutral atlas patch changes {changed} pixels'
        frames=[Image.open(output/f'{id}-frame-{i:02d}.png').convert('RGB') for i in range(24)]
        frames[0].save(output/f'{id}.gif',save_all=True,append_images=frames[1:],duration=100,loop=0)
        assert ImageChops.difference(frames[0],frames[12]).getbbox(), 'Rendered ambient must move'
        Image.open(output/(id+'-states.png')).save(output/(id+'-states.webp'),lossless=True)
    (output/'geometry.json').write_text(json.dumps(shapes,indent=2)+'\n')
    (output/'neutral.json').write_text(json.dumps(neutral,indent=2)+'\n')
    print(f'Passed {len(entries)} context rigs: {output}; game not launched.')


if __name__=='__main__': main()
