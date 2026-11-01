import test from 'node:test';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {buildBundle,createEngine,tokenizeRecord} from '../engine.mjs';
import {buildConcordance,exportConcordance} from '../concordance.mjs';
import {readerURL} from '../ui-utils.mjs';
const lunr=createRequire(import.meta.url)('../vendor/lunr.cjs');
const source=(text,extra={})=>({id:'i1',work:'deh',book:1,section:1,language:'Italian',edition:'test',normalizationProfile:'early-print-it-v1',text,...extra});
test('Italian long s, literal sharp s, accents, elisions and explicit joins retain exact geometry',()=>{
  const r=source('ſuo eßere è citta l’hiſtoria bre¬\nue bon-heur');
  assert.deepEqual(tokenizeRecord(r).map(t=>t.term),['suo','eßere','è','citta','l','historia','breue','bon','heur']);
  const engine=createEngine(buildBundle([r],lunr),lunr);
  for(const q of ['ſuo','suo','eßere','"l historia"','"l’hiſtoria"','breue','"bre* bon h*"'])assert.equal(engine.search(q).occurrences,1,q);
  for(const q of ['essere','città','bonheur'])assert.equal(engine.search(q).occurrences,0,q);
  const hit=engine.search('breue').hitGroups[0].hits[0].spans[0];
  assert.equal(r.text.slice(hit.start,hit.end),'bre¬\nue');
});
test('Only explicitly admitted bracketed supplies join the word; source brackets remain',()=>{
  const text='appreſtoſ[ſi] e partì',start=text.indexOf('['),end=text.indexOf(']')+1;
  const r=source(text,{suppliedTextRanges:[{start,end,text:'[ſi]'}],sourceAnnotations:[{kind:'supplied',editoriallySuppliedNotPrinted:true}]});
  const tokens=tokenizeRecord(r);assert.equal(tokens[0].term,'apprestossi');
  assert.equal(text.slice(tokens[0].start,tokens[0].end),'appreſtoſ[ſi]');
  const engine=createEngine(buildBundle([r],lunr),lunr);
  assert.equal(engine.search('apprestossi').occurrences,1);
  assert.equal(engine.search('appreſtoſſi').occurrences,1);
  assert.equal(engine.search('"apprestos si"').occurrences,0);
  assert.equal(createEngine(buildBundle([source(text)],lunr),lunr).search('apprestossi').occurrences,0);
  assert.throws(()=>tokenizeRecord(source(text,{suppliedTextRanges:[{start,end,text:'[xx]'}]})),/supplied/);
});
test('Italian source gaps and Prologue/book boundaries remain phrase barriers',()=>{
  const a=source('primo secondo',{textGaps:[{kind:'tei-gap',start:6,end:6}],phraseBreaks:[6]});
  const engine=createEngine(buildBundle([a],lunr),lunr);
  assert.equal(engine.search('"primo secondo"').occurrences,0);
  assert.equal(engine.search('primo AND secondo').matchingUnits,1);
  const parts=[source('uno'),source('due',{id:'i2',section:2,breakBefore:true}),source('tre',{id:'i3',book:2,section:1})];
  const separate=createEngine(buildBundle(parts,lunr),lunr);
  assert.equal(separate.search('"uno due"',{scope:'book'}).occurrences,0);
  assert.equal(separate.search('"due tre"',{scope:'book'}).occurrences,0);
});
test('Several canonical targets do not multiply Italian hits, exports or witness destinations',()=>{
  const r=source('parola parola',{collectionId:'deh-italian-lauro1544',citationScheme:'source-span',citationLabel:'Book 1, f. 1r',
    sourceOccurrence:'physical-one',sourcePieces:[{line:'L1',image:1,recordStart:0,recordEnd:13,sourceStart:0,sourceEnd:13}],
    canonicalCorrespondences:[{mappingId:'A'},{mappingId:'B'}],readerLink:{path:'deh/',params:{italian:'lauro1544'}}});
  const result={...createEngine(buildBundle([r],lunr),lunr).search('parola OR parola'),records:[r],selectedCollections:['deh-italian-lauro1544']};
  assert.equal(result.occurrences,2);
  const model=buildConcordance(result,[r],{readerBase:'https://qa.invalid/'});
  const catalog={collections:[{id:'deh-italian-lauro1544',language:'Italian',citationScheme:'source-span'}]};
  const csv=exportConcordance(model,result,{catalog});assert.equal(csv.rowCount,2);
  assert(csv.text.includes('italian_source_references_json'));assert(!csv.text.includes('french_source_references_json'));
  const url=new URL(readerURL(r,'https://qa.invalid/'));assert.equal(url.searchParams.get('italian'),'lauro1544');assert.equal(url.searchParams.get('lauro-page'),'1');
});
test('Italian matching cannot be activated on French or legacy bundle records',()=>{
  assert.throws(()=>tokenizeRecord({...source('ſuo'),language:'French'}),/language/);
  assert.deepEqual(tokenizeRecord({...source('ſuo bre¬\nue'),normalizationProfile:undefined}).map(t=>t.term),['ſuo','bre','ue']);
});
