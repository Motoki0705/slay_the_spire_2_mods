// Read-only structure analysis of already-extracted, MD5-checked game resources.
// Not a Godot/game execution, renderer, or Spine Editor import test.
// Run: node spine_features.mjs <motion-evidence-dir> <spine-core-package-dir> <output-json>
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {pathToFileURL} from 'node:url';
const [source, packageDir, output] = process.argv.slice(2);
if (!source || !packageDir || !output) throw new Error('motion evidence directory, package directory, output json required');
const core = await import(pathToFileURL(path.resolve(packageDir, 'dist/index.js')));
const {SkeletonBinary, BinaryInput, AtlasAttachmentLoader, TextureAtlasRegion} = core;
const fakeAtlas = {findRegion(name) { const r = new TextureAtlasRegion({regions:[],texture:null}); r.name=name; r.width=r.height=r.originalWidth=r.originalHeight=1; return r; }};
const parser = new SkeletonBinary(new AtlasAttachmentLoader(fakeAtlas));
const hash = b => crypto.createHash('sha256').update(b).digest('hex');
const counts = items => items.reduce((r,x)=>(r[x]=(r[x]||0)+1,r),{});
function constraint(c) {
 const out={};
 for(const [k,v] of Object.entries(c)) {
  if(v===null || ['string','number','boolean'].includes(typeof v)) out[k]=v;
  else if (k==='bones') out[k]=v.map(b=>b.name);
  else if(k==='bone' || k==='target') out[k]=v.name;
 }
 if ('target' in c) out.target=c.target?.name ?? null;
 if ('bone' in c) out.bone=c.bone?.name ?? null;
 return out;
}
function weightedBones(bones, skeleton) {
 if(!bones) return {boneNames:[],influenceCount:0,maxInfluencesPerVertex:0};
 let i=0,total=0,max=0; const names=new Set();
 while(i<bones.length) { const n=bones[i++]; total+=n; max=Math.max(max,n); for(let j=0;j<n;j++)names.add(skeleton.bones[bones[i++]].name); }
 if(i!==bones.length) throw new Error('weighted vertex bone data overrun');
 return {boneNames:[...names],influenceCount:total,maxInfluencesPerVertex:max};
}
const result=[];
const resources=path.join(source,'resources');
const dir=path.join(resources,'.godot/imported');
for(const name of fs.readdirSync(dir).filter(x=>x.endsWith('.spskel')).sort()) {
 const bytes=fs.readFileSync(path.join(dir,name));
 const array=new Uint8Array(bytes);
 const input=new BinaryInput(array);input.readInt32();input.readInt32();input.readString();
 for(let i=0;i<5;i++)input.readFloat();const nonessential=input.readBoolean();
 const s=parser.readSkeletonData(array);
 const attachments=s.skins.flatMap(skin=>skin.getAttachments().map(a=>({
  skin:skin.name,slot:s.slots[a.slotIndex].name,name:a.name,type:a.attachment.constructor.name,
  path:a.attachment.path ?? null,vertexCount:(a.attachment.worldVerticesLength??0)/2,
  weighted:!!a.attachment.bones,...weightedBones(a.attachment.bones,s),
  triangleCount:(a.attachment.triangles?.length??0)/3,
  linkedParent:a.attachment.parentMesh?.name??null,
  manualEdges:a.attachment.edges?.length??0,
  regionDimensions:{width:a.attachment.width??null,height:a.attachment.height??null},
  sequence:a.attachment.sequence ? {count:a.attachment.sequence.regions.length,start:a.attachment.sequence.start,digits:a.attachment.sequence.digits}:null,
  x:a.attachment.x??null,y:a.attachment.y??null,rotation:a.attachment.rotation??null,
 })));
 const animations=s.animations.map(a=>({name:a.name,duration:a.duration,
  counts:counts(a.timelines.map(t=>t.constructor.name)),
  timelines:a.timelines.map(t=>({type:t.constructor.name,frames:t.getFrameCount?.()??null,
   bone:t.boneIndex===undefined?undefined:s.bones[t.boneIndex]?.name,
   slot:t.slotIndex===undefined?undefined:s.slots[t.slotIndex]?.name,
   attachment:t.attachment?.name,attachmentVertexCount:t.attachment ? t.attachment.worldVerticesLength/2:undefined,
   keyedAttachmentNames:t.attachmentNames,
   constraintIndex:t.ikConstraintIndex??t.transformConstraintIndex??t.pathConstraintIndex??t.physicsConstraintIndex,
   events:t.events?.map(e=>({name:e.data.name,time:e.time,int:e.intValue,float:e.floatValue,string:e.stringValue}))
  }))
 }));
 const timelineCounts=counts(animations.flatMap(a=>a.timelines.map(t=>t.type)));
 result.push({resource:'.godot/imported/'+name,sha256:hash(bytes),spineExportVersion:s.version,
  nonessential,fps:s.fps,imagesPath:s.imagesPath,audioPath:s.audioPath,referenceScale:s.referenceScale,
  setupBounds:{x:s.x,y:s.y,width:s.width,height:s.height},
  counts:{bones:s.bones.length,slots:s.slots.length,skins:s.skins.length,animations:s.animations.length,
   attachments:attachments.length,attachmentTypes:counts(attachments.map(a=>a.type)),
   weightedMeshes:attachments.filter(a=>a.type==='MeshAttachment'&&a.weighted).length,
   unweightedMeshes:attachments.filter(a=>a.type==='MeshAttachment'&&!a.weighted).length,
   linkedMeshes:attachments.filter(a=>a.linkedParent).length,
   ik:s.ikConstraints.length,transform:s.transformConstraints.length,path:s.pathConstraints.length,physics:s.physicsConstraints.length,
   timelineTypes:timelineCounts,deformTimelines:timelineCounts.DeformTimeline??0},
  bones:s.bones.map(b=>({name:b.name,parent:b.parent?.name??null,index:b.index,length:b.length,x:b.x,y:b.y,rotation:b.rotation,scaleX:b.scaleX,scaleY:b.scaleY,shearX:b.shearX,shearY:b.shearY,inherit:b.inherit,skinRequired:b.skinRequired})),
  slots:s.slots.map(sl=>({name:sl.name,bone:sl.boneData.name,setupAttachment:sl.attachmentName,blendMode:sl.blendMode})),
  attachments,constraints:{ik:s.ikConstraints.map(constraint),transform:s.transformConstraints.map(constraint),path:s.pathConstraints.map(constraint),physics:s.physicsConstraints.map(constraint)},animations
 });
}
const data={date:'2026-10-09',method:'Spine core binary parser; dummy 1x1 atlas regions for structural metadata only; no pixel/render bounds measured',parserPackage:JSON.parse(fs.readFileSync(path.join(packageDir,'package.json'))).version,parserSourceSha256:hash(fs.readFileSync(path.join(packageDir,'dist/SkeletonBinary.js'))),resources:result};
fs.writeFileSync(output,JSON.stringify(data,null,2)+'\n');
for(const s of result)console.log(path.basename(s.resource),JSON.stringify(s.counts));
