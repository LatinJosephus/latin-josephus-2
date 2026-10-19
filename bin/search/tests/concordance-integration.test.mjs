/** Real Cardwell controls independently counted from the accepted plain corpus. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createRequire} from 'node:module';
import {createCollection} from '../collection.mjs';
import {buildConcordance,exportConcordance} from '../concordance.mjs';

const require=createRequire(import.meta.url);
const lunr=require('../vendor/lunr.cjs');
const directory=new URL('../',import.meta.url);
const catalog=JSON.parse(readFileSync(new URL('catalog.json',directory),'utf8'));
const corpus=JSON.parse(readFileSync(new URL('corpus.json',directory),'utf8'));
const collection=createCollection(catalog,lunr,{
  baseURL:new URL('https://qa.example/assets/search/'),
  fetchImpl:async url=>{
    const relative=new URL(url).pathname.replace('/assets/search/','');
    assert.match(relative,/^data\/bellum-latin-cardwell\/book-0[1-7]\.bundle\.json$/);
    return new Response(readFileSync(new URL(relative,directory)));
  },
});
const readerBase='https://latinjosephus.github.io/';
async function run(query,options={}){
  const result=await collection.search(query,{
    collections:['bellum-latin-cardwell'],books:'all',scope:'section',fold:false,...options,
  });
  return {result,model:buildConcordance(result,result.records,{readerBase,contextWords:10})};
}

for(const control of [
  {query:'et',prefix:false,byBook:[844,670,395,436,448,364,278],total:3435},
  {query:'sacerdot*',prefix:true,byBook:[3,7,1,4,10,8,2],total:35},
]){
  test(`${control.query}: every real occurrence survives section grouping and complete export`,async()=>{
    const {result,model}=await run(control.query);
    assert.equal(model.countKind,'word');
    assert.equal(model.occurrenceCount,control.total);
    assert.equal(model.rows.length,control.total);
    const byBook=Array(7).fill(0);
    for(const row of model.rows){
      byBook[row.book-1]++;
      assert.equal(row.records.length,1);
      assert.equal(row.spans.length,1);
      const span=row.spans[0],record=row.records[0];
      assert.equal(row.match,record.text.slice(span.start,span.end));
      assert.equal(row.edition,'Cardwell (1837)');
      assert.match(row.readerURL,/\/bellum-judaicum\/\?book=[1-7]&niese=\d+$/);
    }
    assert.deepEqual(byBook,control.byBook);
    // This literal-text scan does not invoke the engine's parser, tokenizer,
    // wildcard matcher, or index. It also detects a vacuous count fixture.
    const term=control.query.replace('*','');
    let direct=0,sections=0;
    for(const record of corpus){
      const words=record.text.toLowerCase().match(/[\p{L}\p{M}\p{N}]+/gu)||[];
      const found=words.filter(word=>control.prefix?word.startsWith(term):word===term).length;
      direct+=found;if(found)sections++;
    }
    assert.equal(direct,control.total);
    assert.equal(result.matchingUnits,sections);
    assert.ok(model.occurrenceCount>result.matchingUnits);
    const exported=exportConcordance(model,result,{
      catalog,searchURL:`${readerBase}search/?q=${encodeURIComponent(control.query)}&work=bellum-latin-cardwell&book=all&view=concordance`,
      exportedAt:'2026-10-18T23:00:00Z',
    });
    assert.equal(exported.rowCount,control.total);
    assert.ok(exported.text.startsWith('\uFEFF'));
    assert.ok(exported.text.includes(model.rows[0].citation));
    assert.ok(exported.text.includes(model.rows.at(-1).citation));
  });
}

test('real exact and wildcard phrases retain the same single occurrence in I.87',async()=>{
  for(const query of ['"At Theodorus repente"','"At Theodor* repente"']){
    const {model}=await run(query);
    assert.equal(model.occurrenceCount,1);
    assert.equal(model.countKind,'phrase');
    assert.equal(model.rows[0].citation,'Bellum I.87');
    assert.equal(model.rows[0].match,'At Theodorus repente');
  }
  for(const query of ['Theodorus','Theodorus*']){
    const {model}=await run(query);
    assert.equal(model.occurrenceCount,1);
    assert.equal(model.rows[0].match,'Theodorus');
  }
});

test('the I.86–87 phrase remains one occurrence and preserves punctuation between sections',async()=>{
  const query='"habebantur At Theodorus"';
  const {model}=await run(query,{scope:'book',books:['bellum-latin-cardwell:1']});
  assert.equal(model.rows.length,1);
  assert.equal(model.occurrenceCount,1);
  assert.equal(model.rows[0].citation,'Bellum I.86–87');
  assert.equal(model.rows[0].match,'habebantur. At Theodorus');
  assert.deepEqual(model.rows[0].records.map(record=>record.section),[86,87]);
  assert.equal(model.rows[0].spans.length,2);
  const restricted=await run(query,{scope:'section',books:['bellum-latin-cardwell:1']});
  assert.equal(restricted.model.occurrenceCount,0);
});

test('Boolean evidence and negative-only books never become invented occurrence counts',async()=>{
  const compound=await run('(Theodor* OR Zenon*) AND Alexander');
  assert.equal(compound.result.matchingUnits,3);
  assert.equal(compound.model.countKind,'evidence');
  assert.equal(compound.model.occurrenceCount,null);
  const negative=await run('NOT zzzznonoccurrit',{scope:'book'});
  assert.equal(negative.result.matchingUnits,7);
  assert.equal(negative.model.rows.length,0);
  assert.equal(negative.model.occurrenceCount,null);
  assert.equal(negative.model.unhighlightedUnits.length,7);
  const exported=exportConcordance(negative.model,negative.result,{
    catalog,searchURL:`${readerBase}search/?q=NOT+zzzznonoccurrit&work=bellum-latin-cardwell&book=all&scope=book`,
    exportedAt:'2026-10-18T23:00:00Z',
  });
  assert.equal(exported.rowCount,7);
  assert.ok(exported.text.includes('matching-unit'));
});
