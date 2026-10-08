"""Summarize only the existing selected scenes; never load Godot/game resources."""
from pathlib import Path
import re,json,hashlib
root=Path(__file__).resolve().parent
sources=root.parents[2]/'motion'/'evidence'/'resources'
# root: implementation/evidence/rig-reuse; parents[2]: research
if not sources.exists(): raise SystemExit(f'Missing selected resources: {sources}')
physics_types={'RigidBody2D','CharacterBody2D','AnimatableBody2D','StaticBody2D','Area2D','CollisionShape2D','PhysicalBone2D','RigidBody3D','PhysicalBone3D'}
records=[]
for p in sorted((sources/'scenes').rglob('*.tscn')):
 text=p.read_text();nodes=[]
 matches=list(re.finditer(r'^\[node ([^\n]+)\]$',text,re.M))
 for i,m in enumerate(matches):
  attrs=dict(re.findall(r'(\w+)="([^\"]*)"',m.group(1)))
  body=text[m.end():matches[i+1].start() if i+1<len(matches) else len(text)]
  props=dict(re.findall(r'^([A-Za-z0-9_/]+) = (.+)$',body,re.M))
  nodes.append({'line':text[:m.start()].count('\n')+1,**attrs,'properties':{k:v for k,v in props.items() if k in {'position','scale','bone_name','slot_name','skeleton_data_res','script','gravity','amount','lifetime','process_material','offset_left','offset_right','offset_top','offset_bottom','mouse_filter','emitting','follow_bone'}}})
 types={}
 for n in nodes:types[n.get('type','inherited')]=types.get(n.get('type','inherited'),0)+1
 records.append({'source':str(p.relative_to(sources)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'node_types':types,'physics_body_nodes':[n for n in nodes if n.get('type') in physics_types],'named_nodes':[n for n in nodes if n.get('type') in {'SpineBoneNode','SpineSlotNode','SpineSprite','CPUParticles2D','GPUParticles2D'} or n.get('name') in {'Bounds','CenterPos','IntentPos','OrbPos','TalkPos','ControlRoot','Hitbox'}]})
index=json.loads((sources.parent/'pck-index.json').read_text())
result={'date':'2026-10-09','scope':'Existing 50 selected .tscn from motion investigation only. Dynamic nodes and unrelated game scenes are outside this scan.','scene_count':len(records),'physics_body_node_count':sum(len(r['physics_body_nodes']) for r in records),'source_project_query':{'pck_entries':len(index),'suffix':'.spine','matches':[p for p in index if p.lower().endswith('.spine')],'limitation':'Only the indexed distribution PCK; not proof that original authoring projects do not exist elsewhere.'},'scenes':records}
(root/'scene-features.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('scenes',result['scene_count'],'physics body nodes',result['physics_body_node_count'])
