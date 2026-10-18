/**
 * Real-data integration between the qualified collection API and display helpers.
 * Run from any directory: node /path/to/bin/search/tests/integration.test.mjs
 * These four queries make 35 explicit assertions. This is Node verification;
 * it does not simulate a browser or claim visual/interaction coverage.
 */
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createRequire} from 'node:module';
import test from 'node:test';
import {createCollection} from '../collection.mjs';
import {
  buildResultCards, citationFor, readerURL, locationState, searchURL,
  mergedRanges, excerptWindows,
} from '../ui-utils.mjs';

const require=createRequire(import.meta.url);
const lunr=require('../vendor/lunr.cjs');
const searchDirectory=new URL('../',import.meta.url);
const catalog=JSON.parse(readFileSync(new URL('catalog.json',searchDirectory),'utf8'));
const base=new URL('https://qa.example/LatinJosephus/');
const collection=createCollection(catalog,lunr,{
  baseURL:new URL('assets/search/',base),
  fetchImpl:async url=>{
    const match=new URL(url).pathname.match(/^\/LatinJosephus\/assets\/search\/(data\/bellum-latin-cardwell\/book-0[1-7]\.bundle\.json)$/);
    if(!match)throw new Error(`Unexpected test resource: ${url}`);
    return new Response(readFileSync(new URL(match[1],searchDirectory)));
  },
});

for(const sample of [
  {query:'"habebantur At Theodorus"',book:1,sections:[86,87],citation:'Bellum I.86–87'},
  {query:'"facinus invitabat Cum olim"',book:7,sections:[322,323],citation:'Bellum VII.322–323'},
  {query:'"Magna vero haec multitudo"',book:6,sections:[427],citation:'Bellum VI.427'},
]) {
  test(`${sample.citation}: real phrase results retain citations, ranges, edition, and baseurl`,async()=>{
    const result=await collection.search(sample.query,{
      collections:['bellum-latin-cardwell'],books:[`bellum-latin-cardwell:${sample.book}`],
      scope:'book',fold:false,
    });
    const cards=buildResultCards(result,result.records);
    assert.equal(cards.length,1);
    assert.deepEqual(cards[0].records.map(r=>r.section),sample.sections);
    assert.equal(citationFor(cards[0].records),sample.citation);
    for(const record of cards[0].records) {
      assert.equal(readerURL(record,base),
        `https://qa.example/LatinJosephus/bellum-judaicum/?book=${sample.book}&niese=${record.section}`);
      const ranges=mergedRanges(cards[0].ranges[record.id],record.text.length);
      const windows=excerptWindows(record.text,ranges);
      assert.ok(ranges.length>0&&ranges.every(r=>windows.some(w=>w.start<=r.start&&w.end>=r.end)));
      assert.equal(record.language,'Latin');
      assert.equal(record.edition,'Cardwell (1837)');
    }
  });
}

test('Negative-only book metadata and saved links preserve qualified identity and baseurl',async()=>{
  const result=await collection.search('NOT zzzznonoccurrit',{
    collections:['bellum-latin-cardwell'],books:['bellum-latin-cardwell:6'],
    scope:'book',fold:false,
  });
  assert.equal(result.matchingUnits,1);
  assert.deepEqual(buildResultCards(result,result.records),[]);
  assert.equal(result.hitGroups[0].bookId,'bellum-latin-cardwell:6');
  assert.equal(readerURL(result.hitGroups[0],base,{section:false}),
    'https://qa.example/LatinJosephus/bellum-judaicum/?book=6');
  const shared={query:'"facinus invitabat Cum olim"',work:'bellum-latin-cardwell',
    book:'bellum-latin-cardwell:7',scope:'book',fold:true};
  const shareURL=searchURL(shared,new URL('search/',base));
  assert.equal(shareURL.pathname,'/LatinJosephus/search/');
  assert.deepEqual(locationState(shareURL.search,catalog,'unused'),shared);
});
