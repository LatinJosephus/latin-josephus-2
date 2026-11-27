import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
import {buildBundle,createEngine} from '../engine.mjs';
import {readerURL} from '../ui-utils.mjs';
import {buildConcordance,exportConcordance} from '../concordance.mjs';
import {validateFrobenBellumSourceProjection} from '../froben-bellum-publication.mjs';
const root=fileURLToPath(new URL('../../../',import.meta.url)),id='bellum-latin-froben1524';
const read=p=>JSON.parse(fs.readFileSync(new URL('../'+p,import.meta.url),'utf8'));
const records=read(`data/${id}/book-01.corpus.json`),report=read(`data/${id}/book-01.extraction-report.json`),manifest=read(`config/${id}.json`);
const lunr=createRequire(import.meta.url)('../vendor/lunr.cjs');
test('Froben Bellum links use reader books and always select the printed witness',()=>{
  const r={...records[0],book:6,section:1,sourceId:'niese-bellum6-1',readerLink:{params:{book:6,niese:1,froben:'1'}}};
  assert.deepEqual(Object.fromEntries(new URL(readerURL(r,'https://qa.invalid/base/')).searchParams),{book:'6',niese:'1',froben:'1'});
  assert.deepEqual(Object.fromEntries(new URL(readerURL(r,'https://qa.invalid/base/',{section:false})).searchParams),{book:'6',froben:'1'});
  assert.throws(()=>readerURL({...r,language:'English'},'https://qa.invalid/'),/Froben Bellum/);
});
test('Froben exports retain native printed references and do not alter later legacy CSV columns',()=>{
  const r=records[0],engine=createEngine(buildBundle([r],lunr),lunr),result={...engine.search('qvoniam'),records:[r],selectedCollections:[id]};
  assert.equal(engine.search('quoniam').occurrences,0);assert.equal(engine.search('quoniam',{fold:true}).occurrences,1);
  const model=buildConcordance(result,[r],{readerBase:'https://qa.invalid/'}),catalog={collections:[{id,language:'Latin',citationScheme:'niese'}]};
  const csv=exportConcordance(model,result,{catalog});assert.equal(csv.rowCount,1);
  assert(csv.text.split('\r\n')[0].includes('froben_source_references_json'));assert(csv.text.includes('Froben prologue'));
  assert(csv.text.includes('niese-bellum1-1'));assert(csv.text.includes('7817b7bc22def448'));
  const legacy={...r,id:'legacy',collectionId:'bellum-latin-cardwell',edition:'Cardwell (1837)',sourceId:'legacy',readerLink:undefined,frobenSource:undefined};
  const oldResult={...createEngine(buildBundle([legacy],lunr),lunr).search('qvoniam'),records:[legacy],selectedCollections:['bellum-latin-cardwell']};
  const oldModel=buildConcordance(oldResult,[legacy],{readerBase:'https://qa.invalid/'});
  const oldCSV=exportConcordance(oldModel,oldResult,{catalog:{collections:[{id:'bellum-latin-cardwell',language:'Latin'}]}});
  assert(!oldCSV.text.split('\r\n')[0].includes('froben_source_references_json'));
});
test('Independent Froben source gate accepts the released Book I projection',()=>{
  assert.equal(validateFrobenBellumSourceProjection(records,report,manifest,manifest.books[0],root).sections,673);
});
test('Independent source gate refuses changed text and false native correspondence',()=>{
  const changed=structuredClone(records);changed[0].text+=' invented';
  assert.throws(()=>validateFrobenBellumSourceProjection(changed,report,manifest,manifest.books[0],root),/source spelling|source order/);
  const wrong=structuredClone(records);wrong[0].frobenSource.printedBooks[0].label='Froben Book VII';
  assert.throws(()=>validateFrobenBellumSourceProjection(wrong,report,manifest,manifest.books[0],root),/Native Froben/);
});
test('Independent source gate refuses false source-coordinate geometry',()=>{
  const changed=structuredClone(records);changed[0].sourcePieces[0].sourceStart++;
  assert.throws(()=>validateFrobenBellumSourceProjection(changed,report,manifest,manifest.books[0],root),/offset|geometry/);
});
