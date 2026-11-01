import test from 'node:test';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {buildBundle,createEngine,tokenizeRecord} from '../engine.mjs';
const lunr=createRequire(import.meta.url)('../vendor/lunr.cjs');
const record=(text,extra={})=>({id:'f1',work:'deh',book:1,section:1,language:'French',edition:'test',normalizationProfile:'early-print-fr-v1',text,...extra});
test('French early-print tokens retain original geometry, elisions and accents',()=>{
  const r=record('Et ſainct l’hiſtoire ca¬\nptiuité bon-heur eſté été.');
  const tokens=tokenizeRecord(r);
  assert.deepEqual(tokens.map(t=>t.term),['et','sainct','l','histoire','captiuité','bon','heur','esté','été']);
  assert.equal(r.text.slice(tokens[4].start,tokens[4].end),'ca¬\nptiuité');
  const engine=createEngine(buildBundle([r],lunr),lunr);
  for(const query of ['sainct','ſainct','"l’histoire"','"l histoire"','"ca*é bon h*"','c*ptiuité','captiuité*'])assert.equal(engine.search(query).occurrences,1,query);
  assert.equal(engine.search('ete').occurrences,0);
  assert.equal(engine.search('esté').occurrences,1);
  assert.equal(engine.search('bonheur').occurrences,0);
});
test('French gaps stop words and phrases; translation metadata does not',()=>{
  const r=record('premier second', {phraseBreaks:[8],textGaps:[{kind:'tei-gap',start:8,end:8}]});
  const engine=createEngine(buildBundle([r],lunr),lunr);
  assert.equal(engine.search('"premier second"').occurrences,0);
  assert.equal(engine.search('premier AND second').matchingUnits,1);
  const intact=createEngine(buildBundle([record('premier second',{canonicalCorrespondences:[{kind:'Latin omission'}]})],lunr),lunr);
  assert.equal(intact.search('"premier second"').occurrences,1);
});
test('Source order and distinct repetitions survive many targets; scopes stay separate',()=>{
  const records=[record('mot mot',{canonicalCorrespondences:[{target:'A'},{target:'B'}]}),record('autre',{id:'f2',section:2}),record('mot',{id:'f3',section:3})];
  const engine=createEngine(buildBundle(records,lunr),lunr);
  assert.equal(engine.search('mot').occurrences,3);
  assert.equal(engine.search('mot OR mot').occurrences,3);
  assert.equal(engine.search('"mot mot"').occurrences,1);
  assert.equal(engine.search('mot AND autre').matchingUnits,0);
  assert.equal(engine.search('mot AND autre',{scope:'book'}).matchingUnits,1);
  assert.equal(engine.search('"autre mot"',{scope:'book'}).occurrences,1);
  assert.equal(engine.search('"mot autre"').occurrences,0);
});
test('French profile is opt-in; Latin and English tokens retain legacy behavior',()=>{
  assert.deepEqual(tokenizeRecord({...record('ſainct ca¬\nptiuité'),normalizationProfile:undefined}).map(t=>t.term),['ſainct','ca','ptiuité']);
});
