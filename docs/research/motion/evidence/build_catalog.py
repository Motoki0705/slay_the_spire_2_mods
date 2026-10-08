"""Rebuild derived catalogs and verify every selected PCK resource's MD5."""
from pathlib import Path
import hashlib, json, re
root=Path(__file__).resolve().parent
ix=json.loads((root/'pck-index.json').read_text())
xs=json.loads((root/'spine-inventory.json').read_text())
summary=[]
for x in xs:
    assert 'error' not in x, x
    summary.append({k:v for k,v in x.items() if k in ['resource','version','skins','bounds']})
    summary[-1]['animations']=[{'name':a['name'],'duration_seconds':a['duration'],'events':[e for t in a['timelines'] for e in t.get('events',[])]} for a in x['animations']]
(root/'spine-summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
manifest=[]
rows=[]
for f in sorted((root/'resources').rglob('*')):
    if not f.is_file():continue
    p=f.relative_to(root/'resources').as_posix()
    d=f.read_bytes()
    assert len(d)==ix[p]['size']
    assert hashlib.md5(d).hexdigest()==ix[p]['md5']
    manifest.append({'resource':p,**ix[p],'sha256':hashlib.sha256(d).hexdigest()})
    if f.suffix!='.tscn':continue
    nodes=[]
    ext=[]
    for n,line in enumerate(d.decode().splitlines(),1):
        if line.startswith('[ext_resource '):ext.append({'line':n,'text':line})
        if line.startswith('[node ') and any(t in line for t in ['SpineSprite','SpineSlotNode','AnimationPlayer','Particles2D','name="Visuals"','name="SpineSword"','name="Necro"','name="Osty"']):nodes.append({'line':n,'text':line})
    rows.append({'resource':p,'md5':ix[p]['md5'],'nodes':nodes,'ext_resources':ext})
(root/'resource-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
(root/'scene-map.json').write_text(json.dumps(rows,indent=2)+'\n')
game=Path('/mnt/c/Program Files (x86)/Steam/steamapps/common/Slay the Spire 2/data_sts2_windows_x86_64')
source=[]
for name in ['sts2.dll','sts2.xml']:
    f=game/name
    source.append({'path':str(f),'size':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
release=game.parent/'release_info.json'
source.append({'path':str(release),'size':release.stat().st_size,'sha256':hashlib.sha256(release.read_bytes()).hexdigest()})
(root/'release_info.json').write_bytes(release.read_bytes())
(root/'source-binaries.json').write_text(json.dumps(source,indent=2)+'\n')
print('verified',len(manifest),'selected resources',sum(x['size'] for x in manifest),'bytes;',len(xs),'Spine binaries;',len(rows),'scenes')
print('dll',source[0]['sha256'])
