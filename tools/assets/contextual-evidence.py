#!/usr/bin/env python3
"""Collect current, hash-matching standalone Godot context renders (never PNG inputs)."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from PIL import Image

ROOT=Path(__file__).resolve().parents[2]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runs',nargs='+',type=Path,required=True,help='Successful QA directories; later runs replace earlier poses')
    parser.add_argument('--output',type=Path,default=ROOT/'tests/assets/contextual-evidence')
    args=parser.parse_args()
    poses={};runs=[]
    for run in args.runs:
        metrics=json.loads((run/'metrics.json').read_text())
        if metrics['failures']:
            raise ValueError(f'Failing numeric run: {run.name}')
        inputs=json.loads((run/'inputs.json').read_text())
        geometry=json.loads((run/'geometry.json').read_text())
        neutral=json.loads((run/'neutral.json').read_text())
        runs.append({'id':run.name,'checks':metrics['checks'],'failures':metrics['failures'],
                     'metrics_sha256':digest(run/'metrics.json'),'inputs_sha256':digest(run/'inputs.json')})
        for name,values in metrics['poses'].items():
            c,s=name.split('-')
            poses[name]={'character':c,'surface':s,'metrics':values,'neutral':neutral[name],
                         'geometry':geometry[c+'/'+s],'run':run,'inputs':inputs['inputs']}
    expected={c+'-'+s for c in ('ironclad','silent','regent','necrobinder','defect') for s in ('combat','merchant','rest')}
    if set(poses)!=expected:
        raise ValueError('Expected every one of the 15 context poses')
    # Check the complete set before copying any evidence.
    for name,entry in poses.items():
        relative=f"mod/assets/PopSpireWomen/rigs/{entry['character']}/{entry['surface']}.json"
        wanted=next(item['sha256'] for item in entry['inputs'] if item['path']==relative)
        if digest(ROOT/relative)!=wanted:
            raise ValueError(f'Stale rendered rig: {name}')
    output=args.output.resolve();output.mkdir(parents=True,exist_ok=True)
    manifest={'schema':1,'issue':53,'recorded_at_utc':datetime.now(timezone.utc).isoformat(),
              'capture':'Godot 4.5.1 / standalone PCK / immutable production textures / no game resources',
              'motion_encoding':'24 actual renderer frames, 170ms per frame, animated WebP quality85. Normalized-phase inspection, not game timing or performance evidence.',
              'game_launched':False,'validator':{'specified':0,'attempted':0,'completed':0},
              'runs':runs,'poses':{},'known_integration_test':'tests/animation/test_compile_rigs.py:62 assumes every production rig is legacy_v01; current assets intentionally contain 15 contextual_v02 rigs and 5 legacy selections. Parent owns this assertion update.'}
    for name,entry in sorted(poses.items()):
        run=entry.pop('run');inputs=entry.pop('inputs')
        source=ROOT/f"mod/assets/PopSpireWomen/art/{entry['character']}/{entry['surface']}_rig.json"
        rig=json.loads(source.read_text())
        references={"mod/assets/"+rig['body'].removeprefix('res://')}
        references.update("mod/assets/"+m['texture'].removeprefix('res://') for field in ('meshes','layers') for m in rig[field])
        references.add(f"mod/assets/PopSpireWomen/rigs/{entry['character']}/{entry['surface']}.json")
        selected=list({item['path']:item for item in inputs if item['path'] in references}.values())
        entry.update(run=run.name,inputs=selected,source_rig_sha256=digest(source),visual_review='Author inspected the states image: combat idle/hurt/attack/die; merchant and rest ambient/attack/die. Not independent validation.')
        still=output/(name+'-states.webp')
        Image.open(run/(name+'-states.png')).save(still,lossless=True)
        frames=[Image.open(run/f'{name}-frame-{i:02d}.png').convert('RGB') for i in range(24)]
        motion=output/(name+'-motion.webp')
        frames[0].save(motion,save_all=True,append_images=frames[1:],duration=170,loop=0,quality=85,method=4)
        entry['media']=[{'path':still.name,'sha256':digest(still),'format':'lossless static WebP'},
                        {'path':motion.name,'sha256':digest(motion),'format':'animated WebP','frames':24}]
        manifest['poses'][name]=entry
    (output/'validation.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
    print(f'Collected 15 current pose renders and loops: {output}')


if __name__=='__main__':main()
