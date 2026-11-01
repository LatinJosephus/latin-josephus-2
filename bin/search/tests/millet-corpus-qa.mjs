/** Independent physical-source, Unicode-scanner, occurrence and export control. */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {createRequire} from 'node:module';
import {buildBundle, createEngine, tokenizeRecord} from '../engine.mjs';
import {buildConcordance, exportConcordance} from '../concordance.mjs';
import {readerURL} from '../ui-utils.mjs';
import {validateMilletSourceProjection} from '../millet-publication.mjs';
import {createCollection} from '../collection.mjs';
const root=fileURLToPath(new URL('../../../',import.meta.url)), base=path.join(root,'bin/search');
const id='deh-french-millet1556', pilot=process.argv.includes('--pilot');
const read=name=>JSON.parse(fs.readFileSync(path.join(base,name),'utf8'));
const digest=bytes=>createHash('sha256').update(bytes).digest('hex');
const evidence=name=>{const bytes=fs.readFileSync(path.join(root,name));return {path:name,sha256:digest(bytes),bytes:bytes.length};};
const lunr=createRequire(import.meta.url)('../vendor/lunr.cjs');
let assertions=0,totalQueries=0;
const check=(a,b,message)=>{assertions++;assert.deepEqual(a,b,message);};
const norm=value=>value.normalize('NFC').toLowerCase().replaceAll('ſ','s').replaceAll('ς','σ').normalize('NFC');

// Character scanner with a state machine, independent of the engine's word regexp.
function scan(text) {
  const result=[]; let begin=null, value='', offset=0;
  const finish=()=>{if(begin!==null){result.push({term:norm(value),start:begin,end:offset});begin=null;value='';}};
  while(offset<text.length) {
    const c=String.fromCodePoint(text.codePointAt(offset));
    if(/[\p{L}\p{N}]/u.test(c)||(begin!==null&&/\p{M}/u.test(c))){
      if(begin===null)begin=offset;value+=c;offset+=c.length;continue;
    }
    if(c==='¬'&&begin!==null){
      let right=offset+1;while(right<text.length&&/\s/u.test(text[right]))right++;
      if(/[\p{L}\p{N}]/u.test(text[right]||'')){offset=right;continue;}
    }
    finish();offset+=c.length;
  }
  finish();return result;
}
const manifest=read(`config/${id}.json`), report=read(`data/${id}/extraction-report.json`);
const catalog=pilot?{collections:[{...manifest,books:manifest.books.map(book=>`${id}:${book.number}`)}],books:manifest.books.map(book=>({id:`${id}:${book.number}`,collectionId:id,number:book.number}))}:read('catalog.json');
const examples=[], verifiedBooks=[], totals={books:0,sections:0,tokens:0}, bookData=[];
for(const spec of manifest.books) {
  const name=`data/${id}/book-${String(spec.number).padStart(2,'0')}`;
  const raw=read(name+'.corpus.json'), extracted=read(name+'.extraction-report.json');
  const accounting=validateMilletSourceProjection(raw,extracted,manifest,spec,root);assertions++;
  const records=raw.map(record=>({...record,collectionId:id,readerPath:'deh/',citationPrefix:'Millet',citationUnitLabel:'French passage',citationUnitLabelPlural:'French passages'}));
  const bundle=pilot?buildBundle(records,lunr):read(name+'.bundle.json');
  for(let i=0;i<raw.length;i++)check(bundle.tokens[i],scan(raw[i].text),'Independent token and raw-offset comparison');
  const engine=createEngine(bundle,lunr);
  const query=(q,scope='section')=>{totalQueries++;const result=engine.search(q,{scope});return {...result,records,selectedCollections:[id],selectedBooks:[`${id}:${spec.number}`],matchingBooks:result.matchingUnits?[`${id}:${spec.number}`]:[]};};
  const one=(q,scope='section')=>{const result=query(q,scope);const model=buildConcordance(result,records,{readerBase:'https://latinjosephus.github.io/'});const csv=exportConcordance(model,result,{catalog,exportedAt:'2026-11-01T00:00:00Z'});
    check(csv.rowCount,model.rows.length+model.unhighlightedUnits.length,'Complete export including negative-only units');
    if(!csv.rowCount)check(csv.text.includes('search-summary'),true,'Zero-result summary metadata');
    check(csv.text.includes('french_source_references_json'),true,'French location CSV column');
    check(csv.text.includes('deh_correspondences_json'),true,'Canonical correspondence CSV column');
    for(const row of model.rows){check(new URL(row.readerURL).searchParams.get('french'),'millet1556','French reader destination');
      for(const span of row.spans){const record=records.find(item=>item.id===span.recordId);check(record.text.slice(span.start,span.end).length>0,true);}}
    return {result,model,csv};};
  const words=bundle.tokens.flatMap(tokens=>tokens.map(token=>token.term));
  const vocabulary=[...new Set(words)].filter(word=>word.length>2);
  for(let i=0;i<vocabulary.length;i+=37){const word=vocabulary[i];check(query(word).occurrences,words.filter(item=>item===word).length,'Independent complete word count');
    check(query(word+'*').occurrences>=query(word).occurrences,true,'Zero length wildcard');}
  for(let i=0;i<records.length;i++){
    const tokens=bundle.tokens[i];if(tokens.length<4)continue;
    const phrase='"'+tokens.slice(0,4).map(token=>token.term).join(' ')+'"';
    check(query(phrase).hitGroups.some(group=>group.recordIds.includes(records[i].id)),true,'Every physical passage is searchable');
  }
  for(let i=1;i<records.length;i++){
    const a=bundle.tokens[i-1].at(-1),b=bundle.tokens[i][0];if(!a||!b)continue;
    const q=`"${a.term} ${b.term}"`, result=query(q,'book');
    check(result.hitGroups.some(group=>group.hits.some(hit=>hit.spans.length===2&&hit.spans[0].recordId===records[i-1].id&&hit.spans[1].recordId===records[i].id)),!records[i].breakBefore,'Physical passage seam / Prologue barrier');
  }
  const joined=bundle.tokens.flatMap((tokens,index)=>tokens.filter(token=>raw[index].text.slice(token.start,token.end).includes('¬')).map(token=>({token,index})));
  check(joined.length>0,true,'Real encoded continuations present');
  for(const {token,index} of joined.filter((_,i)=>i%83===0)){
    const r=query(token.term);check(r.hitGroups.some(group=>group.hits.some(hit=>hit.spans[0].recordId===raw[index].id&&hit.spans[0].start===token.start&&hit.spans[0].end===token.end)),true,'Encoded continuation maps to exact original characters');
  }
  for(const q of ['de','"l histoire"','"les quatre liu*"','(Iuifs OR Romains) AND NOT zzzmilletabsent','Iuifs OR Romains AND zzzmilletabsent','NOT zzzmilletabsent','zzzmilletabsent']){
    const {result,model,csv}=one(q);examples.push({book:spec.number,q,units:result.matchingUnits,occurrences:result.occurrences,exportRows:csv.rowCount});
    if(q==='de')check(model.rows.length>20,true,'Download exceeds one displayed page');
  }
  check(query('de AND NOT de').matchingUnits,0,'Negation conflict');
  check(query('de OR zzzmilletabsent AND de').occurrences,query('de').occurrences,'Boolean precedence');
  check(query('de de').occurrences,query('de').occurrences,'Repeated operand deduplicates same physical geometry');
  check(query('Iuifs').occurrences,query('Iuifſ').occurrences,'Long s query equivalence');
  const elisionA=query('"l histoire"'),elisionB=query('"l’histoire"');check(elisionA.hitGroups.map(g=>g.hits.map(h=>h.spans)),elisionB.hitGroups.map(g=>g.hits.map(h=>h.spans)),'Curly apostrophe tokenization');
  check(readerURL(records[0],'http://127.0.0.1:8791/').includes('french=millet1556'),true);
  totals.books++;totals.sections+=raw.length;totals.tokens+=words.length;
  verifiedBooks.push({book:spec.number,bundle:pilot?null:evidence('bin/search/'+name+'.bundle.json'),corpus:evidence('bin/search/'+name+'.corpus.json'),source:evidence(spec.source)});
  bookData.push({book:spec.number,...accounting,tokens:words.length,joinedTokens:joined.length});
}
if(!pilot){
  const collection=createCollection(catalog,lunr,{baseURL:'https://qa.invalid/',fetchImpl:async url=>new Response(fs.readFileSync(path.join(base,new URL(url).pathname.slice(1))))});
  const books=[`${id}:1`,'deh-latin-ussani:1','deh-english-pollard:1'];
  for(const q of ['captiuité','Iuifs','iusques','voul*']){
    const frenchOnly=await collection.search(q,{collections:[id],books:[books[0]],scope:'section',fold:false});
    const mixed=await collection.search(q,{collections:[id,'deh-latin-ussani','deh-english-pollard'],books,scope:'section',fold:true});totalQueries+=2;
    check(mixed.hitGroups.filter(g=>g.collectionId===id).flatMap(g=>g.hits.map(h=>h.spans)),frenchOnly.hitGroups.flatMap(g=>g.hits.map(h=>h.spans)),'Mixed Latin option preserves French occurrence geometry');
  }
  const split=await collection.search('"les quatre liures des Roys" AND "quattuor libros regnorum"',{collections:[id,'deh-latin-ussani','deh-english-pollard'],books,scope:'book'});totalQueries++;
  check(split.matchingUnits,0,'No cross-witness Boolean manufacture');
}
const result={status:'PASS',source:totals,bookData,assertions,totalQueries,failedAssertions:0,examples,
  readerBaseline:{publicationInput:false},verifiedFiles:{...Object.fromEntries(Object.entries({corpus:`data/${id}/corpus.json`,catalog:'catalog.json',engine:'engine.mjs',collection:'collection.mjs',verifier:'tests/millet-corpus-qa.mjs'}).map(([k,v])=>[k,evidence('bin/search/'+v)])),books:verifiedBooks},
  limitations:['This is engineering verification of accepted provisional text and correspondence, not new editorial certification. Browser checks are recorded separately.']};
fs.writeFileSync(path.join(base,`data/${id}/${pilot?'pilot-qa':'qa-report'}.json`),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({status:result.status,source:totals,bookData,assertions,totalQueries},null,2));
