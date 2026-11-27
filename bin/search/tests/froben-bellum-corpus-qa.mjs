/** Independent Unicode/postings/Boolean oracle for accepted Froben Bellum. */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {createRequire} from 'node:module';
import {createEngine} from '../engine.mjs';
import {createCollection} from '../collection.mjs';
import {buildConcordance,exportConcordance} from '../concordance.mjs';
import {readerURL} from '../ui-utils.mjs';
import {validateFrobenBellumSourceProjection} from '../froben-bellum-publication.mjs';
const root=fileURLToPath(new URL('../../../',import.meta.url)),base=path.join(root,'bin/search'),id='bellum-latin-froben1524';
const read=p=>fs.readFileSync(path.join(root,p)),json=p=>JSON.parse(read(p));
const sha=b=>createHash('sha256').update(b).digest('hex');
const evidence=p=>{const b=read(p);return {path:p,bytes:b.length,sha256:sha(b)};};
const lunr=createRequire(import.meta.url)('../vendor/lunr.cjs'),pilot=process.argv.includes('--pilot');
const manifest=json(`bin/search/config/${id}.json`),catalog=json('bin/search/catalog.json');
const collection=createCollection(catalog,lunr,{baseURL:'https://qa.invalid/',fetchImpl:async url=>new Response(read('bin/search'+new URL(url).pathname))});
let assertions=0,totalQueries=0;const examples=[],books=[],verifiedBooks=[],allRecords=[];
const check=(a,b,message)=>{assertions++;assert.deepEqual(a,b,message);};
const norm=(s,fold=false)=>{let v=s.normalize('NFC').toLowerCase().replaceAll('ς','σ').replaceAll('æ','ae');if(fold)v=v.replaceAll('v','u').replaceAll('j','i');return v.normalize('NFC');};
function scan(text){
  const result=[];let begin=-1,value='',offset=0;
  const finish=()=>{if(begin>=0){result.push({term:norm(value),start:begin,end:offset});begin=-1;value='';}};
  for(const char of text){if(/[\p{L}\p{N}]/u.test(char)||(begin>=0&&/\p{M}/u.test(char))){if(begin<0)begin=offset;value+=char;}else finish();offset+=char.length;}finish();return result;
}
const leaf=pattern=>({op:'leaf',patterns:Array.isArray(pattern)?pattern:[pattern]});
const and=(a,b)=>({op:'and',a,b}),or=(a,b)=>({op:'or',a,b}),not=a=>({op:'not',a});
const print=tree=>tree.op==='leaf'?(tree.patterns.length>1?'"'+tree.patterns.join(' ')+'"':tree.patterns[0]):tree.op==='not'?'NOT ('+print(tree.a)+')':'('+print(tree.a)+' '+tree.op.toUpperCase()+' '+print(tree.b)+')';
const hitKey=spans=>spans.map(s=>`${s.recordId}:${s.start}-${s.end}`).join('|');
const unique=hits=>[...new Map(hits.map(spans=>[hitKey(spans),spans])).values()];
function oracle(records,tokens){
  const streams=tokens.flatMap((list,ri)=>list.map((token,ti)=>({...token,ri,ti,recordId:records[ri].id}))),postings=[new Map(),new Map()];
  for(let i=0;i<streams.length;i++)for(const fold of [0,1]){const term=norm(streams[i].term,fold);if(!postings[fold].has(term))postings[fold].set(term,[]);postings[fold].get(term).push(i);}
  function matches(tree,scope,fold){
    const universe=scope==='book'?['book']:records.map(r=>r.id);
    if(tree.op==='leaf'){
      const patterns=tree.patterns.map(p=>norm(p,fold));
      const regex=p=>new RegExp('^'+p.replace(/[.*+?^${}()|[\]\\]/g,'\\$&').replaceAll('\\*','.*')+'$','u');
      const tests=patterns.map(regex),indices=[];
      for(const [term,positions] of postings[Number(fold)])if(tests[0].test(term))indices.push(...positions);
      const out=new Map();
      for(const index of indices){
        const run=streams.slice(index,index+patterns.length);
        if(run.length!==patterns.length||!run.every((t,i)=>tests[i].test(norm(t.term,fold)))||(scope==='section'&&run.some(t=>t.ri!==run[0].ri)))continue;
        const spans=[];
        for(const t of run){const last=spans.at(-1);if(last?.recordId===t.recordId)last.end=t.end;else spans.push({recordId:t.recordId,start:t.start,end:t.end});}
        const key=scope==='book'?'book':run[0].recordId;if(!out.has(key))out.set(key,[]);out.get(key).push(spans);
      }
      return out;
    }
    const left=matches(tree.a,scope,fold);
    if(tree.op==='not')return new Map(universe.filter(k=>!left.has(k)).map(k=>[k,[]]));
    const right=matches(tree.b,scope,fold),out=new Map();
    for(const key of universe){if(tree.op==='and'?!left.has(key)||!right.has(key):!left.has(key)&&!right.has(key))continue;out.set(key,unique([...(left.get(key)||[]),...(right.get(key)||[])]));}return out;
  }
  return {streams,postings,matches};
}
for(const spec of manifest.books){
  const name=`bin/search/data/${id}/book-${String(spec.number).padStart(2,'0')}`,records=json(name+'.corpus.json'),report=json(name+'.extraction-report.json'),bundle=json(name+'.bundle.json');
  const accounting=validateFrobenBellumSourceProjection(records,report,manifest,spec,root);assertions++;
  const tokens=records.map(r=>scan(r.text)),control=oracle(records,tokens),engine=createEngine(bundle,lunr);
  for(let i=0;i<records.length;i++)check(bundle.tokens[i],tokens[i],'Every serialized token and UTF-16 offset matches an independent character scanner');
  check(tokens.reduce((n,t)=>n+t.length,0),report.counts.runningWordTokens,'Independent per-book word count');
  function query(tree,scope='section',fold=false){
    const q=print(tree),expected=control.matches(tree,scope,fold),result=engine.search(q,{scope,fold});totalQueries++;
    check(result.matchingUnits,expected.size,'Independent Boolean scope: '+q);
    const actual=result.hitGroups.flatMap(g=>g.hits.map(h=>hitKey(h.spans))).sort();
    const wanted=[...expected.values()].flatMap(h=>h.map(hitKey)).sort();
    check(actual,wanted,'Independent physical occurrence geometry: '+q);
    check(result.occurrences,wanted.length,'Physical occurrence count: '+q);
    return result;
  }
  for(const fold of [false,true])for(const term of control.postings[Number(fold)].keys())query(leaf(term),'section',fold);
  for(let i=0;i<records.length;i++){
    const first=tokens[i].slice(0,4).map(t=>t.term);if(first.length>1)query(leaf(first));
    if(i){const seam=[tokens[i-1].at(-1).term,tokens[i][0].term];query(leaf(seam),'section');query(leaf(seam),'book');}
    for(const token of tokens[i]){
      const pieces=records[i].sourcePieces.filter(p=>p.recordStart<token.end&&p.recordEnd>token.start);
      check(pieces.length>0,true,'Every word has physical Froben coordinates');
      check(records[i].text.slice(token.start,token.end).length,token.end-token.start,'Word geometry addresses original search text');
    }
    for(const join of records[i].frobenSource.joins){
      const before=records[i].sourcePieces.findLast(piece=>piece.image===join.marker[0]&&piece.line===join.marker[1]&&piece.projection==='literal');
      check(tokens[i].some(t=>t.start<before.recordEnd&&t.end>before.recordEnd),join.wordContinuation,'Word continuations join; retained punctuation continues to separate tokens');
    }
    const u=new URL(readerURL(records[i],'https://qa.invalid/preview/'));
    check(u.pathname,'/preview/bellum-judaicum/','Correct reader work');
    check(Object.fromEntries(u.searchParams),{book:String(spec.number),niese:String(i+1),froben:'1'},'Every result opens the Froben witness at the accepted Niese section');
    const bookURL=new URL(readerURL(records[i],'https://qa.invalid/preview/',{section:false}));
    check(Object.fromEntries(bookURL.searchParams),{book:String(spec.number),froben:'1'},'Whole-book routes retain reader scope without switching to native printed-book scope');
    const changes=records[i].sourcePieces.filter((p,j,a)=>j&&p.image!==a[j-1].image);
    for(const piece of changes){
      const right=tokens[i].findIndex(t=>t.start>=piece.recordStart);
      if(right>0&&right<tokens[i].length-1)query(leaf(tokens[i].slice(Math.max(0,right-2),right+2).map(t=>t.term)));
    }
  }
  const trees=[leaf('Iudae*'),leaf('*orum'),leaf('Hieros*'),leaf('zzzzfrobenabsent'),not(leaf('zzzzfrobenabsent')),
    and(leaf('Iudae*'),not(leaf('Roman*'))),or(leaf('Iudae*'),leaf('Roman*')),
    and(or(leaf('Iudae*'),leaf('Roman*')),not(leaf('zzzzfrobenabsent'))),or(leaf('Iudae*'),leaf('Iudae*')),
    and(leaf('Iudae*'),not(leaf('Iudae*'))),leaf(['quoniam','bellum'])];
  for(const tree of trees)for(const scope of ['section','book'])for(const fold of [false,true])query(tree,scope,fold);
  for(const [q,scope,fold] of [['Iudae*','section',false],['NOT zzzzfrobenabsent','book',false],['zzzzfrobenabsent','section',false],['"quoniam bellum"','section',false]]){
    const result={...engine.search(q,{scope,fold}),records,selectedCollections:[id],selectedBooks:[`${id}:${spec.number}`]};totalQueries++;const model=buildConcordance(result,records,{readerBase:'https://qa.invalid/preview/'});
    const csv=exportConcordance(model,result,{catalog,exportedAt:'2026-11-27T18:00:00Z'});
    check(csv.rowCount,result.occurrences||result.matchingUnits,'Complete CSV rows reflect every occurrence or unhighlighted matching unit');
    check(csv.text.split('\r\n')[0].includes('froben_source_references_json'),true,'CSV separates native Froben references');
    check(csv.text.split('\r\n')[0].includes('source_version'),true,'CSV declares accepted source version');
    for(const row of model.rows)check(new URL(row.readerURL).searchParams.get('froben'),'1','Every concordance/CSV occurrence links to Froben');
    examples.push({book:spec.number,q,scope,fold,units:result.matchingUnits,occurrences:result.occurrences,exportRows:csv.rowCount});
  }
  books.push({...accounting,tokens:bundle.stats.tokens});allRecords.push(...records);
  verifiedBooks.push({book:spec.number,bundle:evidence(name+'.bundle.json'),corpus:evidence(name+'.corpus.json'),source:evidence(spec.source),extractionReport:evidence(name+'.extraction-report.json')});
}
const selectedBooks=manifest.books.map(b=>`${id}:${b.number}`),selected=await collection.search('Iudae*',{collections:[id],books:selectedBooks,scope:'section',fold:false});totalQueries++;
check(selected.records.every(r=>r.collectionId===id),true,'Collection loading retains witness identity');
for(const fold of [false,true]){
  const mixed=await collection.search('Iudae*',{collections:[id,'bellum-latin-cardwell','bellum-english-whiston','bellum-english-lodge1602','antiquities-latin-froben1524'],
    books:[`${id}:1`,'bellum-latin-cardwell:1','bellum-english-whiston:1','bellum-english-lodge1602:1','antiquities-latin-froben1524:1'],scope:'section',fold});totalQueries++;
  const alone=await collection.search('Iudae*',{collections:[id],books:[`${id}:1`],scope:'section',fold});totalQueries++;
  check(mixed.hitGroups.filter(g=>g.collectionId===id).map(g=>g.hits.map(h=>hitKey(h.spans))),alone.hitGroups.map(g=>g.hits.map(h=>hitKey(h.spans))),'Other witnesses and the same printed edition in another work cannot change Froben Bellum occurrences');
}
for(const [edition,q] of [[id,'"qvoniam bellum"'],['bellum-english-whiston','"whereas the war"']]){
  const positive=await collection.search(q,{collections:[edition],books:[`${edition}:1`],scope:'book'});totalQueries++;
  check(positive.matchingUnits,1,'Both cross-witness Boolean operands have genuine positive controls');
}
const noBridge=await collection.search('"qvoniam bellum" AND "whereas the war"',{collections:[id,'bellum-english-whiston'],books:[`${id}:1`,'bellum-english-whiston:1'],scope:'book'});totalQueries++;
check(noBridge.matchingUnits,0,'Boolean expressions do not combine separate witnesses');
for(let i=1;i<manifest.books.length;i++){
  const left=allRecords.filter(r=>r.book===i).at(-1),right=allRecords.find(r=>r.book===i+1),phrase=[...scan(left.text).slice(-4),...scan(right.text).slice(0,4)].map(t=>t.term);
  const result=await collection.search('"'+phrase.join(' ')+'"',{collections:[id],books:selectedBooks,scope:'book'});totalQueries++;
  check(result.occurrences,0,'Exact phrases stop at reader book boundaries');
}
const totals={books:manifest.books.length,sections:allRecords.length,tokens:books.reduce((n,b)=>n+b.tokens,0)};
const names={corpus:`data/${id}/corpus.json`,catalog:'catalog.json',engine:'engine.mjs',collection:'collection.mjs',concordance:'concordance.mjs',uiUtils:'ui-utils.mjs',
  extractor:'extract-froben-bellum.py',manifest:`config/${id}.json`,verifier:'tests/froben-bellum-corpus-qa.mjs',sourceGate:'froben-bellum-publication.mjs'};
const report={status:'PASS',source:totals,books,assertions,totalQueries,failedAssertions:0,examples,
  readerBaseline:{publicationInput:false},verifiedFiles:{...Object.fromEntries(Object.entries(names).map(([k,p])=>[k,evidence('bin/search/'+p)])),
    originalReader:evidence('assets/js/renderTei.js'),books:verifiedBooks},
  method:'Independent accepted-span/source geometry control plus Unicode character scanner, independent literal/folded postings and Boolean/phrase/wildcard oracle; all vocabulary, Niese seams, physical page transitions, original offsets, reader routes, exports and mixed-witness isolation.',
  limitations:['Engineering validation of the already accepted transcription and correspondence; no new editorial or alignment decisions. Actual browser and native downloads are verified separately.']};
fs.writeFileSync(path.join(base,`data/${id}/${pilot?'pilot-qa':'qa-report'}.json`),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({status:report.status,source:totals,books,totalQueries,assertions},null,2));
