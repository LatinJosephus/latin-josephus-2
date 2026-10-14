import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
const root=path.resolve(process.argv[2]||fileURLToPath(new URL('../',import.meta.url)));
const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p)));
const frozenPath='assets/data/deh-josephus-concordance.json';
assert.equal(sha(fs.readFileSync(path.join(root,frozenPath))),'c8f59a9bdfd8c49350b4d2656d1c685f4c4a63bd96450ddfd218ac3c07ca743c');
const frozen=read(frozenPath),raw=fs.readFileSync(path.join(root,'assets/data/deh-aj-display.v1.json')),layer=JSON.parse(raw);
assert.equal(layer.kind,'derived_aj_display_alignment');
assert.equal(layer.concordance_sha256,sha(fs.readFileSync(path.join(root,frozenPath))));
const html=fs.readFileSync(path.join(root,'_includes/deh-parallels.html'),'utf8');
assert(html.includes(`data-aj-alignment-sha="${sha(raw)}"`),'AJ display layer pin differs');
const records=frozen.records.filter(r=>r.josephus.targets.some(t=>t.work==='AJ'));assert.equal(records.length,31);assert.equal(layer.records.length,31);
let components=0,closed=0,rawOpen=0,qualified=0,gaps=0,sectionOccurrences=0;
layer.records.forEach((r,i)=>{
 const f=records[i];assert.equal(r.id,f.id);assert.equal(r.deh_xml_id,f.deh.xml_id);
 const targets=f.josephus.targets.filter(t=>t.work==='AJ');assert.deepEqual(r.components.map(c=>c.frozen_target),targets);
 r.components.forEach((c,j)=>{
  const t=targets[j];components++;
  assert.equal(c.component_id,`${r.id}-aj-${t.order}`);assert.equal(c.frozen_target_order,t.order);
  const raw=f.josephus.segments.find(s=>s.order===t.segment_order);assert.deepEqual(c.raw_segment,raw);assert.equal(c.raw_open_ended,raw.unparenthesized_reference.open_ended);
  if(c.raw_open_ended){rawOpen++;assert.equal(t.editorial_decision,'P4-D07');assert(c.display_note.includes('endpoint unspecified')&&c.display_note.includes('P4-D07'));}else closed++;
  const notes=f.josephus.annotations.filter(a=>a.target_orders.includes(t.order));assert.deepEqual(c.annotations,notes);if(notes.length)qualified++;
  for(const language of ['Greek','Latin','English']){
   const sections=c.sections[language];assert.deepEqual(sections.map(s=>s.number),Array.from({length:t.section_end-t.section_start+1},(_,k)=>t.section_start+k));
   let last=[];
   for(const s of sections){sectionOccurrences++;
    if(!s.available){gaps++;assert(s.note);assert.equal(s.spans.length,0);continue;}
    assert(s.spans.length);
    for(const span of s.spans){for(const p of [span.start,span.end]){assert(p.path.every(n=>Number.isInteger(n)&&n>=0));assert(['before','after','start','end'].includes(p.side));}
     assert(JSON.stringify(span.start)!==JSON.stringify(span.end));
    }
   }
  }
 });
});
assert.equal(components,44);assert.equal(rawOpen,1);assert.equal(qualified,2);assert.equal(gaps,1);
for(const [p,h] of Object.entries(layer.source_sha256))assert.equal(sha(fs.readFileSync(path.join(root,p))),h,'Current certified AJ source changed: '+p);
console.log(JSON.stringify({status:'PASS',AJ_units:31,AJ_components:components,raw_closed_components:closed,raw_open_with_prior_approval:rawOpen,qualified_components:qualified,genuine_witness_gaps:gaps,section_occurrences:sectionOccurrences,all_source_hashes_verified:Object.keys(layer.source_sha256).length,original_order_and_frozen_targets_exact:true,no_new_scholarly_authority:true},null,2));
