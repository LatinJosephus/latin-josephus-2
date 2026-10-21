import test from 'node:test';
import assert from 'node:assert/strict';
import {mergedRanges,excerptWindows,buildResultCards,citationFor,romanBook,readerURL,locationState,searchURL} from '../ui-utils.mjs';

test('overlapping term and phrase highlights merge without duplicating text',()=>{
  assert.deepEqual(mergedRanges([{start:8,end:12},{start:0,end:10},{start:0,end:4},{start:30,end:31}],20),[{start:0,end:12}]);
});
test('dispersed positive terms all remain in the visible excerpts',()=>{
  const text='alpha '+('intermedium '.repeat(60))+'omega';
  const ranges=[{start:0,end:5},{start:text.length-5,end:text.length}];
  const windows=excerptWindows(text,ranges,25);
  assert.equal(windows.length,2);
  for(const r of ranges)assert.ok(windows.some(w=>w.start<=r.start&&w.end>=r.end));
});
test('a boundary phrase produces one card with both Niese references',()=>{
  const records=[{id:'a',book:1,order:0,section:86,text:'habebantur.'},{id:'b',book:1,order:1,section:87,text:'At Theodorus repente'}];
  const result={scope:'book',hitGroups:[{unitLabel:'Book I',recordIds:['a','b'],hits:[{kind:'phrase',spans:[{recordId:'a',start:0,end:10},{recordId:'b',start:0,end:12}]}]}]};
  const cards=buildResultCards(result,records);
  assert.equal(cards.length,1);assert.equal(citationFor(cards[0].records),'Bellum I.86–87');
  assert.deepEqual(cards[0].ranges.a,[{start:0,end:10}]);assert.deepEqual(cards[0].ranges.b,[{start:0,end:12}]);
});
test('all seven books have distinct Roman-numeral citations',()=>{
  for(let book=1;book<=7;book++){
    const numeral=['I','II','III','IV','V','VI','VII'][book-1];
    assert.equal(romanBook(book),numeral);
    assert.equal(citationFor([{book,section:3}]),`Bellum ${numeral}.3`);
    assert.equal(citationFor([{book,section:3},{book,section:4}]),`Bellum ${numeral}.3–4`);
  }
});
test('identical section numbers in separate books remain separate cards in source order',()=>{
  const records=[{id:'i',book:1,section:3,order:2,text:'bellum'},{id:'vii',book:7,section:3,order:3548,text:'bellum'}];
  const result={scope:'section',hitGroups:[
    {book:7,recordIds:['vii'],hits:[{spans:[{recordId:'vii',start:0,end:6}]}]},
    {book:1,recordIds:['i'],hits:[{spans:[{recordId:'i',start:0,end:6}]}]}
  ]};
  const cards=buildResultCards(result,records);
  assert.equal(cards.length,2);
  assert.deepEqual(cards.map(c=>citationFor(c.records)),['Bellum I.3','Bellum VII.3']);
  assert.deepEqual(cards[1].ranges,{vii:[{start:0,end:6}]});
});
test('a successful negative-only section query retains its passage without fabricated highlights',()=>{
  const records=[{id:'a',order:0,section:1,text:'bellum'}];
  const cards=buildResultCards({scope:'section',hitGroups:[{recordIds:['a'],hits:[]}]},records);
  assert.equal(cards.length,1);assert.equal(cards[0].hitCount,0);assert.deepEqual(cards[0].ranges,{});
});
test('a successful negative-only book query does not fabricate 673 result excerpts',()=>{
  const records=[{id:'a',order:0,section:1,text:'bellum'}];
  assert.deepEqual(buildResultCards({scope:'book',hitGroups:[{recordIds:['a'],hits:[]}]},records),[]);
});

const catalog={collections:[{id:'bellum-latin-cardwell'},{id:'antiquities-latin-edition'}],books:[
  {id:'bellum-latin-cardwell:1',collectionId:'bellum-latin-cardwell',number:1},
  {id:'bellum-latin-cardwell:7',collectionId:'bellum-latin-cardwell',number:7},
  {id:'antiquities-latin-edition:1',collectionId:'antiquities-latin-edition',number:1},
  {id:'antiquities-latin-edition:20',collectionId:'antiquities-latin-edition',number:20}
]};
test('citations distinguish works and support the later books of Antiquities',()=>{
  assert.equal(romanBook(20),'XX');
  assert.equal(citationFor([{book:1,section:3,work:'antiquities',citationPrefix:'Antiquities'}]),'Antiquities I.3');
  assert.equal(citationFor([{book:20,section:5,work:'antiquities'},{book:20,section:6,work:'antiquities'}]),'Antiquities XX.5–6');
});
test('reader links preserve a deployment subpath and select the correct work',()=>{
  const record={book:20,section:5,work:'antiquities',readerPath:'antiquities/'};
  assert.equal(readerURL(record,'https://example.org/project/'),'https://example.org/project/antiquities/?book=20&niese=5');
  assert.equal(readerURL(record,'https://example.org/',{section:false}),'https://example.org/antiquities/?book=20');
});
test('Whiston reader links select the matching English work for sections and whole books',()=>{
  for(const [work,readerPath,collectionId,book,section] of [
    ['bellum','bellum-judaicum/','bellum-english-whiston',6,301],
    ['antiquities','antiquities/','antiquities-english-whiston',20,200],
    ['contra-apionem','contra-apionem/','contra-apionem-english-whiston',1,38],
    ['contra-apionem','contra-apionem/','contra-apionem-english-whiston',2,109],
  ]){
    const record={work,readerPath,collectionId,language:'English',edition:'Whiston',book,section};
    assert.equal(readerURL(record,'https://example.org/project/'),`https://example.org/project/${readerPath}?book=${book}&niese=${section}&english=whiston`);
    assert.equal(readerURL(record,'https://example.org/project/',{section:false}),`https://example.org/project/${readerPath}?book=${book}&english=whiston`);
  }
});
test('Whiston reader links reject a conflicting work, collection, language or edition',()=>{
  const record={work:'bellum',collectionId:'bellum-english-whiston',language:'English',edition:'Whiston',book:7,section:209,readerLink:{params:{english:'whiston'}}};
  for(const change of [{work:'antiquities'},{collectionId:'antiquities-english-whiston'},
    {work:'contra-apionem'},{collectionId:'contra-apionem-english-whiston'},{language:'Latin'},
    {edition:'Lodge (1602)'},{readerLink:{params:{english:'lodge1602'}}}]){
    assert.throws(()=>readerURL({...record,...change},'https://example.org/'),/matching English work and edition/);
  }
  assert.equal(readerURL({work:'bellum',language:'Latin',edition:'Cardwell (1837)',book:7,section:209},'https://example.org/'),
    'https://example.org/bellum-judaicum/?book=7&niese=209');
});
test('old Book I and seven-book pilot links retain their original search coverage',()=>{
  assert.deepEqual(locationState('?q=bellum',catalog,'default'),{query:'bellum',work:'bellum-latin-cardwell',book:'bellum-latin-cardwell:1',scope:'section',fold:false,view:'passages'});
  assert.equal(locationState('?q=bellum&book=all',catalog,'default').work,'bellum-latin-cardwell');
  assert.equal(locationState('?q=bellum&book=all',catalog,'default').book,'all');
  assert.equal(locationState('?q=bellum&book=7',catalog,'default').book,'bellum-latin-cardwell:7');
});
test('qualified links round-trip work, book, phrase, scope and spelling equivalence',()=>{
  const state={query:'"uirtus et iustitia"',work:'antiquities-latin-edition',book:'antiquities-latin-edition:20',scope:'book',fold:true,view:'passages'};
  const url=searchURL(state,'https://example.org/project/search/?unrelated=old');
  assert.equal(url.pathname,'/project/search/');assert.equal(url.searchParams.has('unrelated'),false);
  assert.deepEqual(locationState(url.search,catalog,'default'),state);
});
test('concordance links preserve the query and filters while passage links keep the established URL shape',()=>{
  const state={query:'"habebantur At Theodorus"',work:'bellum-latin-cardwell',book:'bellum-latin-cardwell:1',scope:'book',fold:false,view:'concordance'};
  const url=searchURL(state,'https://example.org/search/');
  assert.equal(url.searchParams.get('view'),'concordance');
  assert.deepEqual(locationState(url.search,catalog,'default'),state);
  const passages=searchURL({...state,view:'passages'},url);
  assert.equal(passages.searchParams.has('view'),false);
  assert.equal(locationState('?q=bellum&view=unavailable',catalog,'default').view,'passages');
});
test('unavailable or ambiguous saved filters fail instead of broadening the search',()=>{
  for(const search of ['?work=missing&q=bellum','?work=all&book=1&q=bellum','?work=bellum-latin-cardwell&book=antiquities-latin-edition:1&q=bellum','?q=bellum&book=8'])
    assert.throws(()=>locationState(search,catalog,'default'),/not available|needs a work/);
});
test('resultOrder keeps editions together when their source orders overlap',()=>{
  const records=[
    {id:'bj',work:'bellum',collectionId:'bellum-latin-cardwell',book:1,section:3,order:2,resultOrder:0,text:'bellum'},
    {id:'aj',work:'antiquities',collectionId:'antiquities-latin-edition',book:1,section:1,order:0,resultOrder:1,text:'bellum'}
  ];
  const result={scope:'section',hitGroups:records.slice().reverse().map(r=>({recordIds:[r.id],hits:[{spans:[{recordId:r.id,start:0,end:6}]}]}))};
  const cards=buildResultCards(result,records);
  assert.deepEqual(cards.map(c=>citationFor(c.records)),['Bellum I.3','Antiquities I.1']);
  assert.deepEqual(cards[1].ranges,{aj:[{start:0,end:6}]});
});
