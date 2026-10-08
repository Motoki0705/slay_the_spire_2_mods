// Read animation metadata only; never instantiate Godot or execute the game.
// dependency: npm install --prefix /tmp/sts2-motion-tools @esotericsoftware/spine-core@4.2.43
import fs from 'node:fs';
import path from 'node:path';
import {SkeletonBinary, AtlasAttachmentLoader, TextureAtlasRegion} from '/tmp/sts2-motion-tools/node_modules/@esotericsoftware/spine-core/dist/index.js';
const root=path.dirname(new URL(import.meta.url).pathname);
const dir=path.join(root,'resources/.godot/imported');
const atlas={findRegion(name){const r=new TextureAtlasRegion({regions:[],texture:null});r.name=name;r.width=r.height=r.originalWidth=r.originalHeight=1;return r;}};
const parser=new SkeletonBinary(new AtlasAttachmentLoader(atlas));
const out=[];
for(const file of fs.readdirSync(dir).filter(x=>x.endsWith('.spskel'))){
 try{
  const s=parser.readSkeletonData(new Uint8Array(fs.readFileSync(path.join(dir,file))));
  out.push({resource:'.godot/imported/'+file,version:s.version,bounds:{x:s.x,y:s.y,width:s.width,height:s.height},skins:s.skins.map(x=>x.name),bones:s.bones.map(x=>x.name),slots:s.slots.map(x=>x.name),animations:s.animations.map(a=>({name:a.name,duration:a.duration,timelines:a.timelines.map(t=>({type:t.constructor.name,bone:t.boneIndex===undefined?undefined:s.bones[t.boneIndex]?.name,slot:t.slotIndex===undefined?undefined:s.slots[t.slotIndex]?.name,events:t.events?.map(e=>({name:e.data.name,time:e.time,int:e.intValue,float:e.floatValue,string:e.stringValue}))}))}))});
 }catch(e){out.push({resource:'.godot/imported/'+file,error:String(e),stack:e.stack});}
}
fs.writeFileSync(path.join(root,'spine-inventory.json'),JSON.stringify(out,null,2)+'\n');
for(const s of out)console.log(s.resource,s.error||s.animations.map(a=>`${a.name}(${a.duration.toFixed(3)}s)`).join(', '));
