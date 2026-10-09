#!/usr/bin/env python3
"""Exercise the real allowlist/import/preflight/PCK readback using no owned-game inputs."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/'tests/select'))
from video_fixture import create_video
from tools.pck_mod import build as builder


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--godot',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    output=args.output.resolve()
    output.mkdir(parents=True,exist_ok=True)
    godot=args.godot.resolve()
    with tempfile.TemporaryDirectory(prefix='psw-video-pack-') as temp:
        work=Path(temp)
        source=work/'source'
        shutil.copytree(ROOT/'mod/assets/PopSpireWomen',source/'PopSpireWomen')
        movie=create_video(source/'PopSpireWomen/art/video-fixtures')
        prefix='res://PopSpireWomen/art/video-fixtures/'
        for character in builder.CHARACTERS:
            video=prefix+('invalid.ogv' if character=='silent' else 'missing.ogv' if character=='defect' else 'movie.ogv')
            poster=prefix+('missing.png' if character in ('regent','necrobinder') else 'video-poster.png')
            rig=f'res://PopSpireWomen/rigs/{character}/select.json' if character not in ('silent','necrobinder') else 'res://PopSpireWomen/rigs/missing.json'
            (source/f'PopSpireWomen/select/production/{character}.tscn').write_text(f'''[gd_scene load_steps=2 format=3]
[ext_resource type="PackedScene" path="res://PopSpireWomen/select/select_background.tscn" id="1"]
[node name="Fixture" instance=ExtResource("1")]
character_entry = "{character.upper()}"
video_path = "{video}"
poster_path = "{poster}"
rig_path = "{rig}"
''')
        stage=work/'stage'; stage.mkdir()
        source_hashes=builder.stage_project(source,stage)
        builder.run_godot(godot,stage,['--editor','--import'],output/'import.log')
        shutil.copyfile(builder.HERE/'preflight.gd',stage/'preflight.gd')
        builder.run_godot(godot,stage,['--script','res://preflight.gd','--',output/'preflight.json'],output/'preflight.log')
        preflight=json.loads((output/'preflight.json').read_text())
        selections={c:p['surfaces']['select'] for c,p in preflight.items()}
        assert selections['ironclad']['ok'] and selections['ironclad']['video']['ok']
        assert selections['silent']['ok'] and not selections['silent']['video']['ok'] and not selections['silent']['rig_ok'] and selections['silent']['poster_ok']
        assert selections['regent']['ok'] and not selections['regent']['poster_ok'] and selections['regent']['rig_ok']
        assert not selections['necrobinder']['ok'], 'Video-only descriptor must retain original: no reduced-motion fallback'
        assert selections['defect']['ok'] and not selections['defect']['video']['ok']
        files={name:stage/name for name in source_hashes}
        assert not builder.collect_imports(stage,files)
        movie_name='PopSpireWomen/art/video-fixtures/movie.ogv'
        assert movie_name in files and movie_name+'.import' not in files
        file_map=work/'map.json'
        builder.write_json(file_map,{name:str(path) for name,path in files.items()})
        shutil.copyfile(builder.HERE/'pack.gd',stage/'pack.gd')
        pck=output/'synthetic-selection.pck'
        builder.run_godot(godot,stage,['--script','res://pack.gd','--',file_map,pck],output/'pack.log')
        hashes={name:builder.digest(path) for name,path in files.items()}
        builder.verify_pack(pck,hashes)
        readback=builder.readback_media(godot,pck,preflight,work/'empty-host',output)
        assert readback[prefix+'movie.ogv']['ok']
        assert readback[prefix+'movie.ogv']['size']==[1360,768]
        # Changing one staged byte must be caught by exact-byte PCK verification.
        bad=hashes.copy(); bad[movie_name]='0'*64
        try: builder.verify_pack(pck,bad)
        except builder.BuildError: pass
        else: raise AssertionError('Video hash mismatch accepted')
        builder.write_json(output/'validation.json',{
            'kind':'synthetic-pck-only-selection','game_launched':False,'game_inputs':False,
            'source_movie_sha256':builder.digest(movie),'packed_movie_sha256':hashes[movie_name],
            'pck_sha256':builder.digest(pck),'preflight':selections,'readback':readback,
            'checks':['allowlist','runtime pinning','imported PNG poster','direct Theora bytes','five descriptor fallback combinations','packed resource map/hash verification','empty-host packed decoder advance','deliberate hash mismatch refusal']})
    print(f'Synthetic PCK video checks passed: {output}. No owned-game input, launch or install.')


if __name__=='__main__': main()
