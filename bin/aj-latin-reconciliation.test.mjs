// Source corruption, path drift and certification tampering must fail closed.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {fileURLToPath} from 'node:url';
import {execFileSync, spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import test from 'node:test';
const root=fileURLToPath(new URL('../',import.meta.url));
const sha=b=>createHash('sha256').update(b).digest('hex');
const run=(script,args=[])=>execFileSync(process.execPath,[path.join(root,'bin',script),...args],{encoding:'utf8'});
const layer=JSON.parse(fs.readFileSync(path.join(root,'assets/data/deh-aj-display.v1.json')));
const certPath='_docs/aj-latin-reconciliation/certified-boundaries.json';
const originalCert=JSON.parse(fs.readFileSync(path.join(root,certPath)));

test('strict AJ gate and deterministic audited regeneration pass',()=>{
 assert.equal(JSON.parse(run('deh-aj-display-qa.mjs')).status,'PASS');
 const result=execFileSync(process.env.PYTHON||'python',[path.join(root,'bin/aj-latin-reconcile.py')],{encoding:'utf8'});
 assert(result.includes('"mode": "check"'));
});

test('all 44 components retain every witness boundary, qualifier and frozen target',()=>{
 assert.equal(layer.records.length,31);
 assert.equal(originalCert.components.length,44);
 for(const c of originalCert.components){
  const record=layer.records.find(r=>r.id===c.deh_id);
  const actual=record.components.find(x=>x.component_id===c.id);
  assert.deepEqual(actual.frozen_target,c.target);
  assert.deepEqual(actual.sections.Latin,c.sections.map(s=>s.boundary));
 }
 assert.equal(originalCert.summary.adjusted_dom_paths_or_sides,0);
 assert.equal(originalCert.summary.changed_selected_texts,1);
 assert.equal(originalCert.summary.absolute_boundary_offsets_changed,164);
 const changed=originalCert.components.flatMap(c=>c.sections.filter(s=>s.selected_text_changed).map(s=>({c,s})));
 assert.equal(changed.length,1);assert.equal(changed[0].c.id,'deh-2-12-3-aj-2');
 assert(changed[0].s.old.text.includes('Hoc ergo tibi'));
 assert(!changed[0].s.current.text.includes('Hoc ergo tibi'));
 assert.equal(layer.source_sha256['assets/js/renderTei.js'],'39ded95fc3b7fdf39d9827cf513e6fc6c88922bb039435446b48b22ec4192848');
 const renderer=fs.readFileSync(path.join(root,'assets/js/renderTei.js'),'utf8');
 assert(renderer.includes('const antiquitiesBookNumberingDisplayCopy = '));
 assert(renderer.includes('const data = antiquitiesBookNumberingDisplayCopy(language, sourceData);'));
});

test('32 source corruptions plus concordance, layer, include and certificate tampering are rejected',()=>{
 const temp=fs.mkdtempSync(path.join(os.tmpdir(),'aj-latin-negative-'));
 const files=[...Object.keys(layer.source_sha256),'assets/data/deh-josephus-concordance.json',
  'assets/data/deh-aj-display.v1.json','_includes/deh-parallels.html',certPath];
 try{
  for(const f of files){fs.mkdirSync(path.dirname(path.join(temp,f)),{recursive:true});fs.copyFileSync(path.join(root,f),path.join(temp,f));}
  for(const f of files){
   const target=path.join(temp,f),saved=fs.readFileSync(target);
   const body=f==='_includes/deh-parallels.html'?Buffer.from(saved.toString().replace('data-aj-alignment-sha="','data-aj-alignment-sha="0')):Buffer.concat([saved,Buffer.from('\nUNAUTHORIZED CORRUPTION')]);
   fs.writeFileSync(target,body);
   const result=spawnSync(process.execPath,[path.join(root,'bin/deh-aj-display-qa.mjs'),temp],{encoding:'utf8'});
   assert.notEqual(result.status,0,'Corruption accepted: '+f);
   assert(result.stderr.includes('AssertionError')||result.stderr.includes('SyntaxError'),'Unexpected failure: '+result.stderr);
   fs.writeFileSync(target,saved);
  }
  // An attacker can repin the include after changing a well-formed layer.
  // The independent certification still rejects path, note and exclusion drift.
  for(const mutation of ['path','note','exclusion']){
   const changed=structuredClone(layer);
   const section=changed.records[0].components[0].sections.Latin[0];
   if(mutation==='path')section.spans[0].start.path[0]+=1;
   if(mutation==='note')section.note='Unapproved witness interpretation';
   if(mutation==='exclusion')section.excludedParagraphs=['latin-book14-num54'];
   const raw=Buffer.from(JSON.stringify(changed,null,2)+'\n');
   fs.writeFileSync(path.join(temp,'assets/data/deh-aj-display.v1.json'),raw);
   const include=fs.readFileSync(path.join(root,'_includes/deh-parallels.html'),'utf8').replace(/data-aj-alignment-sha="[a-f0-9]{64}"/,`data-aj-alignment-sha="${sha(raw)}"`);
   fs.writeFileSync(path.join(temp,'_includes/deh-parallels.html'),include);
   const result=spawnSync(process.execPath,[path.join(root,'bin/deh-aj-display-qa.mjs'),temp],{encoding:'utf8'});
   assert.notEqual(result.status,0,'Repinned unauthorized boundary accepted: '+mutation);
   assert(result.stderr.includes('Frozen targets, witness notes, exclusions or section boundaries changed'));
  }
 }finally{fs.rmSync(temp,{recursive:true,force:true});}
});
