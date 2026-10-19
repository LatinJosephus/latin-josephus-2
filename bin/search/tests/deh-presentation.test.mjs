/** Citation, source-mark, and complete CSV checks for the canonical DEH text. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createRequire} from 'node:module';
import {createCollection} from '../collection.mjs';
import {buildConcordance,exportConcordance} from '../concordance.mjs';
import {citationFor,citationUnitLabels,readerURL,locationState,searchURL,annotatedTextSegments,editorialMarksFor,editorialText} from '../ui-utils.mjs';

const lunr=createRequire(import.meta.url)('../vendor/lunr.cjs');
const directory=new URL('../',import.meta.url);
const catalog=JSON.parse(readFileSync(new URL('catalog.json',directory),'utf8'));
const corpus=JSON.parse(readFileSync(new URL('data/deh-latin-ussani/corpus.json',directory),'utf8'));
const DEH='deh-latin-ussani',BELLUM='bellum-latin-cardwell';
const collection=createCollection(catalog,lunr,{
  baseURL:new URL('https://qa.example/assets/search/'),
  fetchImpl:async url=>{
    const relative=new URL(url).pathname.replace('/assets/search/','');
    assert.match(relative,/^data\/(?:bellum-latin-cardwell|deh-latin-ussani)\/book-0[1-7]\.bundle\.json$/);
    return new Response(readFileSync(new URL(relative,directory)));
  },
});
const readerBase='https://latinjosephus.github.io/';
const exportedAt='2026-10-19T12:00:00.000Z';
async function run(query,options={}){
  const result=await collection.search(query,{collections:[DEH],books:'all',scope:'section',fold:false,...options});
  return {result,model:buildConcordance(result,result.records,{readerBase,contextWords:10})};
}

// Independent CSV parser: physical newlines may occur inside source text cells.
function parseCSV(text){
  assert.equal(text[0],'\uFEFF');
  const rows=[],row=[];let value='',quoted=false;
  for(let i=1;i<text.length;i++){
    const char=text[i];
    if(char==='"'){
      if(quoted&&text[i+1]==='"'){value+='"';i++;}else quoted=!quoted;
    }else if(!quoted&&char===','){row.push(value);value='';}
    else if(!quoted&&char==='\r'&&text[i+1]==='\n'){row.push(value);rows.push(row.splice(0));value='';i++;}
    else value+=char;
  }
  assert.equal(quoted,false);assert.equal(value,'');
  const headers=rows.shift();
  return {headers,rows:rows.map(values=>{
    assert.equal(values.length,headers.length);
    const result=Object.fromEntries(headers.map((header,index)=>[header,values[index]]));
    for(const column of JSON.parse(result.escaped_columns_json)){assert.ok(result[column].startsWith("'"));result[column]=result[column].slice(1);}
    return result;
  })};
}

test('adding DEH retains Bellum defaults, pilot links, and explicit mixed selections',()=>{
  const initial=locationState('',catalog,'default');
  assert.equal(initial.work,BELLUM);assert.equal(initial.book,'all');
  const pilot=locationState('?q=bellum',catalog,'default');
  assert.equal(pilot.work,BELLUM);assert.equal(pilot.book,`${BELLUM}:1`);
  assert.equal(locationState('?q=bellum&book=all',catalog,'default').work,BELLUM);
  for(const work of [DEH,'all']){
    const state={query:'"cognitio ueritatis"',work,book:'all',scope:'book',fold:true,view:'concordance'};
    assert.deepEqual(locationState(searchURL(state,'https://example.org/search/').search,catalog,'default'),state);
  }
  assert.deepEqual(citationUnitLabels(catalog.collections),{singular:'citation unit',plural:'citation units'});
  assert.deepEqual(citationUnitLabels(catalog.collections.filter(entry=>entry.id===BELLUM)),{singular:'Niese section',plural:'Niese sections'});
});

test('all 558 DEH units have exact chapter/paragraph citations and reader destinations',()=>{
  assert.equal(corpus.length,558);
  assert.deepEqual([1,2,3,4,5].map(book=>corpus.filter(record=>record.book===book).length),[215,73,70,79,121]);
  for(const record of corpus){
    assert.equal(citationFor([record]),`De excidio ${record.citationLabel}`);
    const expected=new URL(record.url,readerBase);
    assert.equal(readerURL(record,readerBase),expected.href);
    assert.equal(expected.searchParams.has('niese'),false);
    assert.equal(Number(expected.searchParams.get('chapter')),record.chapter);
    assert.equal(Number(expected.searchParams.get('unit')),record.paragraph);
    assert.equal(readerURL(record,'https://example.org/project/'),`https://example.org/project${record.url}`);
    for(const mark of editorialMarksFor(record))assert.equal(mark.text,record.text.slice(mark.start,mark.end));
  }
  assert.equal(citationFor(corpus.slice(0,2)),'De excidio Prol.1–Prol.2');
  const before=corpus.find(record=>record.citationLabel==='I.1.10'),after=corpus.find(record=>record.citationLabel==='I.2.1');
  assert.equal(citationFor([before,after]),'De excidio I.1.10–I.2.1');
});

test('editorial segmentation retains intra-word letters and UTF-16 source offsets',()=>{
  const supplied=corpus.find(record=>record.citationLabel==='II.14.5');
  const start=supplied.text.indexOf('Cenedaei');
  assert.equal(editorialText(supplied,start,start+8),'Ce[ne]daei');
  const segments=annotatedTextSegments(supplied,start,start+8,[{start,end:start+8}]);
  assert.equal(segments.map(segment=>segment.text).join(''),'Cenedaei');
  assert.ok(segments.every(segment=>segment.highlighted));
  assert.deepEqual(segments.filter(segment=>segment.marks.length).map(segment=>segment.text),['ne']);
  const deleted=corpus.find(record=>record.citationLabel==='I.34.2'),alexander=deleted.text.indexOf('Alexander');
  assert.equal(editorialText(deleted,alexander,alexander+9),'Alexan⟦der⟧');
  const astral={text:'𐌀x',editorialMarks:[{kind:'supplied',start:0,end:2,text:'𐌀'}]};
  assert.equal(editorialText(astral),'[𐌀]x');
  assert.throws(()=>editorialMarksFor({text:'𐌀x',editorialMarks:[{kind:'del',start:1,end:2,text:'\uDF00'}]}),/original-text span/);
  assert.throws(()=>editorialMarksFor({text:'abcd',editorialMarks:[{kind:'del',start:0,end:3,text:'abc'},{kind:'supplied',start:2,end:4,text:'cd'}]}),/not crossing/);
});

test('Cenedaei remains a complete searchable word and its supplied letters survive full export',async()=>{
  const {result,model}=await run('Cenedaei');
  assert.equal(model.occurrenceCount,1);
  const row=model.rows[0];
  assert.equal(row.citation,'De excidio II.14.5');assert.equal(row.match,'Cenedaei');
  assert.equal(row.readerURL,`${readerBase}deh/?book=2&chapter=14&unit=5`);
  assert.equal(row.unitLabel,'De excidio II.14.5');
  const {headers,rows}=parseCSV(exportConcordance(model,result,{catalog,exportedAt}).text);
  assert.equal(headers.length,56);assert.equal(rows.length,1);
  assert.equal(rows[0].matched_text,'Cenedaei');assert.equal(rows[0].matched_text_editorial,'Ce[ne]daei');
  assert.equal(rows[0].citation_scheme,'chapter-paragraph');assert.match(rows[0].editorial_notes,/supplied/);
  const segment=JSON.parse(rows[0].source_segments_json)[0],original=corpus.find(record=>record.id===segment.recordId);
  assert.equal(segment.text,original.text.slice(segment.start,segment.end));
  assert.equal(segment.citationLabel,'II.14.5');assert.deepEqual(segment.editorialMarks,original.editorialMarks);
  assert.deepEqual(JSON.parse(rows[0].hit_spans_json),row.spans);
});

test('an occurrence with deleted letters stays visibly marked in CSV and mixed-work results',async()=>{
  const {result,model}=await run('Alexander',{collections:[BELLUM,DEH]});
  assert.deepEqual(result.selectedCollections,[BELLUM,DEH]);
  assert.ok(model.rows.some(row=>row.collectionId===BELLUM));assert.ok(model.rows.some(row=>row.collectionId===DEH));
  const row=model.rows.find(row=>row.citation==='De excidio I.34.2');
  assert.ok(row);assert.equal(row.match,'Alexander');
  assert.deepEqual(row.editorialMarks.map(mark=>[mark.kind,mark.text]),[['del','der']]);
  const file=parseCSV(exportConcordance(model,result,{catalog,exportedAt}).text);
  assert.equal(file.headers.length,56);assert.equal(file.rows.length,model.rows.length);
  const exported=file.rows.find(item=>item.citation===row.citation);
  assert.equal(exported.matched_text,'Alexander');assert.equal(exported.matched_text_editorial,'Alexan⟦der⟧');
  assert.match(exported.editorial_notes,/deleted/);
  assert.ok(file.rows.filter(item=>item.collection_id===BELLUM).every(item=>item.citation_scheme==='niese'));
  const selected=JSON.parse(file.rows[0].selected_sources_json);
  assert.equal(selected.books.length,12);assert.deepEqual(selected.collections.map(item=>item.citationScheme),['niese','chapter-paragraph']);
});

test('the accepted Bellum-only export retains its 51 columns and 35 wildcard occurrences',async()=>{
  const {result,model}=await run('sacerdot*',{collections:[BELLUM]});
  assert.equal(model.occurrenceCount,35);assert.equal(result.matchingUnits,34);
  const file=parseCSV(exportConcordance(model,result,{catalog,exportedAt}).text);
  assert.equal(file.headers.length,51);assert.equal(file.headers.includes('editorial_notes'),false);
  assert.equal(file.rows.length,35);assert.ok(file.rows.every(row=>row.citation.startsWith('Bellum ')));
});

test('a real cross-chapter DEH phrase produces one exact range, while the Prologue boundary blocks joining',async()=>{
  const phrase='"diuturnos fore Nec fefellit"';
  const {model}=await run(phrase,{scope:'book',books:[`${DEH}:1`]});
  assert.equal(model.occurrenceCount,1);
  assert.equal(model.rows[0].citation,'De excidio I.1.10–I.2.1');
  assert.equal(model.rows[0].match,'diuturnos fore. Nec fefellit');
  assert.equal((await run(phrase,{scope:'section'})).model.occurrenceCount,0);
  assert.equal((await run('"sumam exordium Bello Parthico"',{scope:'book',books:[`${DEH}:1`]})).model.occurrenceCount,0);
  assert.equal((await run('"Hinc igitur sumam exordium"',{scope:'section'})).model.rows[0].citation,'De excidio Prol.3');
});

test('the source dagger remains visible when exact phrase matching treats it as punctuation',async()=>{
  const {result,model}=await run('"eius auctoritate uel conficiendo"');
  assert.equal(model.occurrenceCount,1);assert.equal(model.rows[0].citation,'De excidio I.17.2');
  assert.equal(model.rows[0].match,'eius auctoritate † uel conficiendo');
  assert.deepEqual(model.rows[0].editorialMarks.filter(mark=>mark.kind==='unclear').map(mark=>mark.text),['†']);
  const row=parseCSV(exportConcordance(model,result,{catalog,exportedAt}).text).rows[0];
  assert.equal(row.matched_text_editorial,'eius auctoritate † uel conficiendo');
  assert.match(row.editorial_notes,/unresolved/);
});

test('NOT-only DEH books retain five book citations without invented Niese references or occurrences',async()=>{
  const {result,model}=await run('NOT zzzznonoccurrit',{scope:'book'});
  assert.equal(model.occurrenceCount,null);assert.equal(model.rows.length,0);assert.equal(model.unhighlightedUnits.length,5);
  assert.deepEqual(model.unhighlightedUnits.map(row=>row.citation),['De excidio I','De excidio II','De excidio III','De excidio IV','De excidio V']);
  assert.ok(model.unhighlightedUnits.every(row=>!row.readerURL.includes('niese')&&!row.readerURL.includes('chapter')));
  const file=parseCSV(exportConcordance(model,result,{catalog,exportedAt}).text);
  assert.equal(file.rows.length,5);assert.equal(file.headers.length,56);
  assert.ok(file.rows.every(row=>row.row_type==='matching-unit'&&row.matched_text===''&&row.occurrence_count===''));
  assert.ok(file.rows.every(row=>JSON.parse(row.source_segments_json).length===0));
});

test('a no-result DEH export still describes its citation system and selected source fingerprints',async()=>{
  const {result,model}=await run('zzzznonoccurrit');
  const output=exportConcordance(model,result,{catalog,exportedAt}),file=parseCSV(output.text);
  assert.equal(output.rowCount,0);assert.equal(file.headers.length,56);assert.equal(file.rows[0].row_type,'search-summary');
  assert.match(file.rows[0].editorial_notes,/supplied text/);
  assert.equal(JSON.parse(file.rows[0].selected_sources_json).collections[0].citationScheme,'chapter-paragraph');
  assert.equal(parseCSV(exportConcordance(model,result,{exportedAt}).text).headers.length,56,'the source records identify DEH even without a supplied catalog');
});
