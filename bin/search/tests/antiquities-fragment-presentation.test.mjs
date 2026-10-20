/** Presentation of registered physical portions, insertions and source gaps. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createRequire} from 'node:module';
import {buildBundle, createEngine} from '../engine.mjs';
import {createCollection} from '../collection.mjs';
import {buildConcordance, exportConcordance} from '../concordance.mjs';
import {buildResultCards, citationFor, sectionCitation, excerptCitation, passageDivisionLabel, readerURL} from '../ui-utils.mjs';

const lunr=createRequire(import.meta.url)('../vendor/lunr.cjs');
const ANT='antiquities-latin-bamberg78',readerBase='https://example.org/project/';
const registry=JSON.parse(readFileSync(new URL('../../../assets/xml/antiquities/niese/book-11.json',import.meta.url),'utf8'));
const provenance={path:'assets/xml/antiquities/niese/book-11.json',normalizedSHA256:'a'.repeat(64)};

function record(section,text,order,extra={}) {
  return {
    id:`${ANT}-11-${section}`,collectionId:ANT,bookId:`${ANT}:11`,work:'antiquities',
    book:11,section,language:'Latin',edition:'Bamberg Msc. Class. 78',citationScheme:'niese',
    citationLabel:`XI.${section}`,citationUnitId:`${ANT}-11-${section}`,citationUnitCitation:`XI.${section}`,
    readerPath:'antiquities/',readerLink:{path:'antiquities/',params:{book:11,niese:section}},
    sourceId:`latin-book11-num${section}`,sourceIds:[`latin-book11-num${section}`],
    sourcePath:'assets/xml/antiquities/Latin/book11.xml',identityRegistry:provenance,
    text,order,...extra,
  };
}
function portion(section,rank,text,order) {
  const sourceOccurrence=`Latin-XI-${section}-${rank}`;
  return record(section,text,order,{
    id:`${ANT}-11-${section}-${sourceOccurrence}`,sourceOccurrence,continuationRank:rank,fragmentCount:3,
    citationLabel:`XI.${section} (portion ${rank} of 3)`,
  });
}
function insertion(suffix='a',order=0) {
  const section=`BJ.IV.105${suffix}`,sourcePassage=registry.sourcePassages.find(item=>item.identity===section);
  assert.ok(sourcePassage,'the insertion fixture uses its actual accepted registry association');
  return record(section,'uerba belli',order,{
    citationLabel:`XI, interpolated Bellum IV.105${suffix}`,citationUnitCitation:`XI, interpolated Bellum IV.105${suffix}`,
    sourcePassage,sourceOccurrence:sourcePassage.occurrence,
    readerLink:{path:'antiquities/',params:{book:11,niese:sourcePassage.association}},
  });
}
// The text is synthetic; the ordering mirrors XI.72's displaced portions.
const physical=[portion(72,2,'septem cantores.',0),record(69,'alia narrantur.',1),record(71,'nunc finit.',2),
  portion(72,1,'mancipia cuncta.',3),portion(72,3,'subiugalia multa.',4),record(73,'postea ueniunt.',5)];

function search(records,query,{scope='section',contextWords=10}={}) {
  const result={...createEngine(buildBundle(records,lunr),lunr).search(query,{scope}),records,
    selectedCollections:[ANT],selectedBooks:[`${ANT}:11`]};
  return {result,model:buildConcordance(result,records,{readerBase,contextWords})};
}
function csv(model,result,catalog={}) {
  const exported=exportConcordance(model,result,{catalog,exportedAt:'2026-10-20T00:00:00.000Z'});
  assert.equal(exported.text[0],'\uFEFF');
  const rows=[],current=[];let cell='',quoted=false;
  for(let index=1;index<exported.text.length;index++) {
    const character=exported.text[index];
    if(character==='"') {
      if(quoted&&exported.text[index+1]==='"'){cell+='"';index++;}else quoted=!quoted;
    }else if(!quoted&&character===','){current.push(cell);cell='';}
    else if(!quoted&&character==='\r'&&exported.text[index+1]==='\n'){
      current.push(cell);rows.push(current.splice(0));cell='';index++;
    }else cell+=character;
  }
  assert.equal(quoted,false);assert.equal(cell,'');
  const headers=rows.shift();
  return {headers,rows:rows.map(values=>{
    assert.equal(values.length,headers.length);
    const row=Object.fromEntries(headers.map((name,index)=>[name,values[index]]));
    for(const name of JSON.parse(row.escaped_columns_json))row[name]=row[name].slice(1);
    return row;
  })};
}

test('portion and Bellum insertion citations remain explicit in cards, excerpts and division labels',()=>{
  const fragment=physical[0];
  assert.equal(citationFor([fragment]),'Antiquities XI.72 (portion 2 of 3)');
  assert.equal(sectionCitation(fragment),'XI.72 (portion 2 of 3)');
  assert.equal(excerptCitation(fragment),'XI.72 (portion 2 of 3)');
  assert.equal(passageDivisionLabel([fragment]),'Niese section XI.72 (portion 2 of 3)');
  for(const suffix of ['a','b']) {
    const inserted=insertion(suffix);
    assert.equal(citationFor([inserted]),`Antiquities XI, interpolated Bellum IV.105${suffix}`);
    assert.equal(excerptCitation(inserted),`XI, interpolated Bellum IV.105${suffix}`);
    assert.equal(passageDivisionLabel([inserted]),`XI, interpolated Bellum IV.105${suffix}`);
  }
  const ordinary=record(72,'Latin',0);
  assert.equal(citationFor([ordinary]),'Antiquities XI.72');
  assert.equal(excerptCitation(ordinary),'§72');
  assert.equal(passageDivisionLabel([ordinary]),'Niese section 72');
});

test('only consecutive ordinary citations produce numeric ranges',()=>{
  assert.equal(citationFor([record(71,'a',0),record(72,'b',1)]),'Antiquities XI.71–72');
  assert.equal(passageDivisionLabel([record(71,'a',0),record(72,'b',1)]),'Niese sections 71–72');
  assert.equal(citationFor([record(73,'a',0),record(69,'b',1)]),'Antiquities XI.73; XI.69');
  assert.equal(passageDivisionLabel([record(73,'a',0),record(69,'b',1)]),'Niese sections 73; 69');
  assert.equal(citationFor([record(247,'finis',0),record(249,'initium',1)]),'Antiquities XI.247; XI.249');
  assert.equal(citationFor(physical.slice(2)),
    'Antiquities XI.71; XI.72 (portion 1 of 3); XI.72 (portion 3 of 3); XI.73');
  assert.equal(citationFor([portion(312,1,'ante',0),insertion('a',1),portion(312,2,'post',2)]),
    'Antiquities XI.312 (portion 1 of 3); XI, interpolated Bellum IV.105a; XI.312 (portion 2 of 3)');
});

test('Bellum insertions use only their accepted numeric Antiquities reader association',()=>{
  for(const suffix of ['a','b']) {
    const inserted=insertion(suffix);
    assert.equal(readerURL(inserted,readerBase),`${readerBase}antiquities/?book=11&niese=312`);
    assert.equal(readerURL(inserted,readerBase,{section:false}),`${readerBase}antiquities/?book=11`);
    const conflicts=[
      {...inserted,readerLink:{params:{book:11,niese:311}}},
      {...inserted,readerLink:{params:{book:11,niese:inserted.section}}},
      {...inserted,sourceOccurrence:'unrelated'},
      {...inserted,sourcePassage:{...inserted.sourcePassage,association:313}},
      {...inserted,sourcePassage:{...inserted.sourcePassage,identity:'BJ.IV.999'}},
      {...inserted,sourcePassage:{...inserted.sourcePassage,AntiquitiesIdentity:true}},
      {...inserted,sourcePassage:{...inserted.sourcePassage,primaryAntiquitiesFragment:true}},
      {...inserted,sourcePassage:{...inserted.sourcePassage,editorialStatus:'OPEN'}},
      {...inserted,sourcePassage:{...inserted.sourcePassage,span:{...inserted.sourcePassage.span,role:'unknown'}}},
      {...inserted,sourcePassage:undefined},
    ];
    for(const conflict of conflicts)assert.throws(()=>readerURL(conflict,readerBase),/association|numeric citation/);
  }
  assert.equal(readerURL(physical[0],readerBase),`${readerBase}antiquities/?book=11&niese=72`);
  const proem={...record(1,'Latin',0),book:1,division:'proem',readerLink:{params:{book:'preface',niese:1}}};
  assert.equal(readerURL(proem,readerBase),`${readerBase}antiquities/?book=preface&niese=1`);
});

test('one logical section can retain all portions while each Boolean evidence row retains only its source slice',()=>{
  const {result,model}=search(physical,'cantores AND mancipia');
  assert.equal(result.matchingUnits,1);
  assert.equal(result.matchingSections,1);
  const fragments=[physical[0],physical[3],physical[4]];
  assert.deepEqual(result.hitGroups[0].recordIds,fragments.map(item=>item.id));
  const cards=buildResultCards(result,physical);
  assert.equal(cards.length,1);
  assert.deepEqual(cards[0].records,fragments);
  assert.equal(citationFor(cards[0].records),
    'Antiquities XI.72 (portion 2 of 3); XI.72 (portion 1 of 3); XI.72 (portion 3 of 3)');
  assert.deepEqual(model.rows.map(row=>row.match),['cantores','mancipia']);
  assert.deepEqual(model.rows.map(row=>row.records.map(item=>item.id)),[[physical[0].id],[physical[3].id]]);
  assert.deepEqual(model.rows.map(row=>row.citation),['Antiquities XI.72 (portion 2 of 3)','Antiquities XI.72 (portion 1 of 3)']);
  for(const row of model.rows) {
    assert.equal(row.left+row.match+row.right,row.records[0].text);
    assert.equal(row.records[0].text.slice(row.spans[0].start,row.spans[0].end),row.match);
  }
});

test('phrases follow actual physical adjacency without jumping or inventing a numeric citation range',()=>{
  for(const scope of ['section','book'])assert.equal(search(physical,'"cantores mancipia"',{scope}).model.rows.length,0);
  const adjacent=search(physical,'"cuncta subiugalia"').model.rows[0];
  assert.equal(adjacent.match,'cuncta. subiugalia');
  assert.deepEqual(adjacent.records,[physical[3],physical[4]]);
  assert.equal(adjacent.citation,'Antiquities XI.72 (portion 1 of 3); XI.72 (portion 3 of 3)');
  const across=search(physical,'"cantores alia narrantur nunc finit mancipia"',{scope:'book'}).model.rows[0];
  assert.equal(across.match,'cantores. alia narrantur. nunc finit. mancipia');
  assert.deepEqual(across.records,physical.slice(0,4));
  assert.equal(across.citation,'Antiquities XI.72 (portion 2 of 3); XI.69; XI.71; XI.72 (portion 1 of 3)');
  const continuous=[record(247,'finis',0),record(249,'initium',1)];
  const skipped=search(continuous,'"finis initium"',{scope:'book'}).model.rows[0];
  assert.equal(skipped.match,'finis initium','an unavailable citation alone is not a physical text gap');
  assert.equal(skipped.citation,'Antiquities XI.247; XI.249');
});

test('concordance rejects inconsistent logical units and fabricated jumps between displaced portions',()=>{
  const first=physical[0],second=physical[3];
  for(const conflict of [{citationUnitId:'different'},{citationUnitId:undefined},{section:73},
    {edition:'another'},{language:'Greek'},{book:12},{work:'bellum'},{collectionId:'another'}]) {
    const altered={...second,...conflict},records=[first,altered];
    const result={query:'NOT absent',scope:'section',hitGroups:[{recordIds:records.map(item=>item.id),hits:[]}]};
    assert.throws(()=>buildConcordance(result,records,{readerBase}),/explicit citation unit/);
    assert.throws(()=>buildResultCards(result,records),/explicit citation unit/);
  }
  const duplicate={query:'NOT absent',scope:'section',hitGroups:[{recordIds:[first.id,first.id],hits:[]}]};
  assert.throws(()=>buildConcordance(duplicate,[first],{readerBase}),/distinct source records/);
  const result={query:'"cantores mancipia"',scope:'section',hitGroups:[{
    recordIds:[first.id,second.id,physical[4].id],hits:[{kind:'phrase',spans:[
      {recordId:first.id,start:first.text.indexOf('cantores'),end:first.text.length-1},
      {recordId:second.id,start:0,end:'mancipia'.length},
    ]}],
  }]};
  assert.throws(()=>buildConcordance(result,physical,{readerBase}),/jump between displaced portions/);
});

test('zero-width TEI gaps split context words without changing source text or offsets',()=>{
  const text='ante ress fuerant post',offset=text.indexOf('ress')+3;
  const source=record(393,text,0,{phraseBreaks:[offset],
    textGaps:[{kind:'tei-gap',start:offset,end:offset,text:'',sourceAttributes:{reason:'fading'}}]});
  const {result,model}=search([source],'fuerant',{contextWords:1});
  assert.equal(model.rows[0].left,'s ');
  assert.equal(model.rows[0].match,'fuerant');
  assert.equal(model.rows[0].right,' post');
  assert.equal(model.rows[0].contextSpans[0].start,offset);
  const segment=JSON.parse(csv(model,result).rows[0].source_segments_json)[0];
  assert.equal(segment.text,'s fuerant post');
  assert.equal(segment.text,text.slice(segment.start,segment.end));
  assert.deepEqual(segment.textGaps,source.textGaps);
  assert.equal(search([source],'ress').model.rows.length,0);
  assert.equal(search([source],'"res s"').model.rows.length,0);
  assert.equal(search([source],'"s fuerant"').model.rows[0].match,'s fuerant');
});

test('CSV retains source portions, insertion associations, registry provenance and selected coverage',()=>{
  const metadata={coverageMode:'registered-source-spans',canonicalSections:4,citationUnits:4,primarySourceSpans:6,
    interpolatedSourcePassages:0,fragmentedSections:[72],unavailableSections:[70],sectionRange:[69,73],
    identityRegistry:'assets/xml/antiquities/niese/book-11.json',additionalSources:['assets/xml/antiquities/niese/book-11.json']};
  const catalog={collections:[{id:ANT,work:'antiquities'}],books:[{id:`${ANT}:11`,collectionId:ANT,number:11,...metadata}]};
  const {result,model}=search(physical,'NOT absent');
  const exported=csv(model,result,catalog);
  assert.equal(exported.headers.length,56);
  const row=exported.rows.find(item=>item.citation.includes('portion 2 of 3'));
  assert.equal(row.row_type,'matching-unit');
  const segments=JSON.parse(row.source_segments_json);
  assert.deepEqual(segments.map(item=>item.continuationRank),[2,1,3]);
  for(const segment of segments) {
    const source=physical.find(item=>item.id===segment.recordId);
    assert.equal(segment.text,source.text);
    assert.equal(segment.joinBefore,'','separate displaced portions do not receive a fabricated joining space');
    for(const field of ['citationLabel','citationUnitId','citationUnitCitation','sourceOccurrence','continuationRank','fragmentCount','identityRegistry']) {
      assert.deepEqual(segment[field],source[field],field);
    }
  }
  const selected=JSON.parse(exported.rows[0].selected_sources_json).books[0];
  for(const [field,value] of Object.entries(metadata))assert.deepEqual(selected[field],value,field);
  assert.match(exported.rows[0].editorial_notes,/Books I–XX/);
  assert.match(exported.rows[0].editorial_notes,/do not themselves mark physical gaps/);
  for(const suffix of ['a','b']) {
    const inserted=insertion(suffix),found=search([inserted],'belli');
    const insertedRow=csv(found.model,found.result,catalog).rows[0];
    const segment=JSON.parse(insertedRow.source_segments_json)[0];
    assert.deepEqual(segment.sourcePassage,inserted.sourcePassage);
    assert.equal(segment.citationLabel,inserted.citationLabel);
    assert.equal(segment.sourceOccurrence,inserted.sourceOccurrence);
    assert.equal(insertedRow.reader_url,`${readerBase}antiquities/?book=11&niese=312`);
  }
  const ordinary=record(73,'uerba',0);delete ordinary.identityRegistry;
  const found=search([ordinary],'uerba'),ordinarySegment=JSON.parse(csv(found.model,found.result,catalog).rows[0].source_segments_json)[0];
  assert.equal(ordinarySegment.identityRegistry,undefined,'per-record registry metadata remains optional');
  assert.equal(ordinarySegment.citationUnitId,ordinary.citationUnitId);
});

// These tests use the complete production bundles through the same collection
// loader as the browser, retaining real source order and catalogue provenance.
const directory=new URL('../',import.meta.url);
const readJSON=path=>JSON.parse(readFileSync(new URL(path,directory),'utf8'));
const realCatalog=readJSON('catalog.json');
const xviRegistry=readJSON('../../assets/xml/antiquities/niese/book-16.json');
const realCollection=createCollection(realCatalog,lunr,{
  baseURL:new URL('https://qa.example/assets/search/'),
  fetchImpl:async url=>{
    const path=new URL(url).pathname.replace('/assets/search/','');
    assert.match(path,/^data\/antiquities-latin-bamberg78\/book-(?:16|20)\.bundle\.json$/);
    return new Response(readFileSync(new URL(path,directory)));
  },
});
async function realSearch(book,query,{scope='section'}={}) {
  const result=await realCollection.search(query,{collections:[ANT],books:[`${ANT}:${book}`],scope,fold:false});
  return {result,model:buildConcordance(result,result.records,{readerBase,contextWords:100})};
}

test('real XVI.294, 295 and 351 portions remain one Boolean card with separately cited and reversible CSV evidence',async()=>{
  const cases=[
    {section:294,phrases:['Aestuabat etiam de fileo','Interea obado moriente dinea']},
    {section:295,phrases:['conabatur defuncto obabo rege','Caesar autem aretae minabatur']},
    {section:351,phrases:['perissent qui conturbatus erras','hac oratione caesar per motus']},
  ];
  for(const {section,phrases} of cases) {
    const query=phrases.map(phrase=>`"${phrase}"`).join(' AND ');
    const {result,model}=await realSearch(16,query);
    assert.deepEqual([result.matchingUnits,result.matchingSections,result.occurrences],[1,1,2],`XVI.${section}`);
    const fragments=result.records.filter(record=>record.section===section);
    assert.equal(fragments.length,2);
    const accepted=xviRegistry.sections.find(item=>item.number===section).Latin.spans;
    assert.deepEqual(fragments.map(record=>record.sourceOccurrence),accepted.map(span=>span.start.target));
    assert.deepEqual(fragments.map(record=>record.continuationRank),[1,2]);
    assert.ok(fragments.every(record=>record.fragmentCount===2&&record.citationUnitCitation===`XVI.${section}`));
    const cards=buildResultCards(result,result.records);
    assert.equal(cards.length,1);
    assert.deepEqual(cards[0].records,fragments);
    assert.equal(citationFor(cards[0].records),`Antiquities XVI.${section} (portion 1 of 2); XVI.${section} (portion 2 of 2)`);
    assert.deepEqual(model.rows.map(row=>row.records.map(record=>record.id)),fragments.map(record=>[record.id]));
    const exported=csv(model,result,realCatalog);
    assert.equal(exported.rows.length,2);
    for(const [index,row] of exported.rows.entries()) {
      const source=fragments[index],segments=JSON.parse(row.source_segments_json);
      assert.equal(row.citation,`Antiquities XVI.${section} (portion ${index+1} of 2)`);
      assert.equal(row.reader_url,`${readerBase}antiquities/?book=16&niese=${section}`);
      assert.equal(excerptCitation(source),`XVI.${section} (portion ${index+1} of 2)`);
      assert.equal(readerURL(source,readerBase),row.reader_url);
      assert.equal(segments.length,1);
      const segment=segments[0];
      for(const field of ['citationLabel','citationUnitId','citationUnitCitation','sourceOccurrence','continuationRank','fragmentCount','sourcePath','sourceIds']) {
        assert.deepEqual(segment[field],source[field],`${row.citation}: ${field}`);
      }
      assert.equal(segment.text,source.text.slice(segment.start,segment.end));
      const match=model.rows[index].spans[0];
      assert.equal(row.matched_text,source.text.slice(match.start,match.end));
      assert.equal(segment.text,source.text,'the full, short source fragment fits the selected context');
    }
    const selected=JSON.parse(exported.rows[0].selected_sources_json).books[0];
    assert.equal(selected.id,`${ANT}:16`);
    assert.deepEqual(selected.fragmentedSections,[294,295,351]);
    assert.equal(selected.identityRegistry,'assets/xml/antiquities/niese/book-16.json');
    assert.deepEqual([selected.canonicalSections,selected.primarySourceSpans],[380,383]);
    assert.equal((await realSearch(16,`"${phrases[0]}" AND NOT "${phrases[1]}"`)).model.rows.length,0,
      'NOT evaluates the complete accepted citation unit, including its displaced second portion');
  }
});

test('real interwoven XVI portions preserve physical phrase order and explicit excerpt citations',async()=>{
  const impossible=[
    'qui presens romae Interea obado moriente',
    'in aula potentibus Caesar autem aretae',
    'quae latrocinia criminabantur hac oratione caesar',
  ];
  for(const query of impossible)for(const scope of ['section','book']) {
    assert.equal((await realSearch(16,`"${query}"`,{scope})).model.rows.length,0,query);
  }
  const {result,model}=await realSearch(16,'"qui presens romae conabatur defuncto obabo"',{scope:'book'});
  assert.equal(model.rows.length,1);
  const row=model.rows[0];
  assert.equal(row.match,'qui presens romae conabatur defuncto obabo');
  assert.equal(row.citation,'Antiquities XVI.294 (portion 1 of 2); XVI.295 (portion 1 of 2)');
  assert.deepEqual(row.records.map(record=>[record.section,record.continuationRank]),[[294,1],[295,1]]);
  const segments=JSON.parse(csv(model,result,realCatalog).rows[0].source_segments_json);
  assert.deepEqual(segments.map(segment=>segment.sourceOccurrence),['niese-latin-book16-294','niese-latin-book16-295']);
  for(const segment of segments) {
    const source=result.records.find(record=>record.id===segment.recordId);
    assert.equal(segment.text,source.text.slice(segment.start,segment.end));
  }
});

test('real XVI.200 and XX.37 CSV rows retain the complete evidence for their explicit source barriers',async()=>{
  const cases=[
    {book:16,before:188,after:200,phrase:'Nam multi ex regis ira',jump:'herodes constitutus affligebatur Nam multi ex',
      reason:'Literal [...] notation occurs after XVI.188 and before XVI.200 in the accepted transcription.',
      endAnchor:'niese-latin-book16-end188',excluded:['[...]','[...]']},
    {book:20,before:26,after:37,phrase:'Darta banem particum destinauit',jump:'in hac regione Darta banem particum',
      reason:'The accepted XX.26 end anchor precedes an inherited missing-text annotation before XX.37.',
      endAnchor:'niese-latin-book20-end26',excluded:['[Niese sections 26–37 largely missing; cf. Blatt, p. 68]']},
  ];
  for(const expected of cases) {
    const {book,before,after,phrase,jump}=expected;
    const {result,model}=await realSearch(book,`"${phrase}"`);
    assert.equal(model.rows.length,1);
    const source=model.rows[0].records[0],index=result.records.findIndex(record=>record.id===source.id);
    assert.equal(source.section,after);
    assert.equal(result.records[index-1].section,before);
    assert.equal(source.breakBefore,true);
    assert.equal(source.breakReason,expected.reason);
    const evidence=source.sourceBoundaryEvidence;
    assert.equal(evidence.kind,'registered-source-discontinuity');
    assert.deepEqual([evidence.precedingSection,evidence.followingSection],[before,after]);
    assert.equal(evidence.precedingEnd.sourceAttributes['{http://www.w3.org/XML/1998/namespace}id'],expected.endAnchor);
    assert.deepEqual(evidence.excludedSourceSpans.map(span=>span.text),expected.excluded);
    const exported=csv(model,result,realCatalog),row=exported.rows[0];
    const segments=JSON.parse(row.source_segments_json);
    assert.equal(segments.length,1);
    assert.equal(segments[0].text,source.text.slice(segments[0].start,segments[0].end));
    assert.equal(segments[0].breakBefore,true);
    assert.equal(segments[0].breakReason,source.breakReason);
    assert.deepEqual(segments[0].sourceBoundaryEvidence,evidence,
      'CSV keeps controlling anchors, original excluded spans, their offsets and hashes, and qualification');
    assert.equal(row.reader_url,`${readerBase}antiquities/?book=${book}&niese=${after}`);
    assert.match(row.editorial_notes,/between XVI\.188 and 200 and between XX\.26 and 37/);
    assert.match(row.editorial_notes,/do not themselves mark physical gaps/);
    for(const scope of ['section','book'])assert.equal((await realSearch(book,`"${jump}"`,{scope})).model.rows.length,0);
    if(book===20) {
      const selected=JSON.parse(row.selected_sources_json).books[0];
      assert.deepEqual(selected.sectionRange,[1,268]);
      assert.equal(selected.canonicalSections,257);
      assert.deepEqual(selected.unavailableSections,[27,28,29,30,31,32,33,34,35,36,238]);
    }
  }
});
