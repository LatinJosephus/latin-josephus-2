import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {codepoints,utf16Offset,indexBook,lineAtoms,visibleLines,canonicalIds,locationFromUrl,updateMilletUrl,createMilletLoader,flowSeparator,flowGroups,readingParts,folioLabels,readingView} from '../assets/js/milletCore.js';
const folder=fileURLToPath(new URL('../assets/data/deh-millet1556/',import.meta.url));
const read=name=>JSON.parse(fs.readFileSync(folder+name,'utf8'));
const manifest=read('manifest.json'),books=manifest.books.map(b=>read(b.path));
const hash=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
test('every asset binds certified provenance and book-scoped hashes',()=>{
 assert.equal(manifest.authority.status,'INTEGRATION_READY');assert.equal(manifest.counts.canonical_units,558);
 for(const b of [...manifest.books,manifest.preliminary,manifest.editorial])assert.equal(hash(fs.readFileSync(folder+b.path)),b.sha256);
 for(const [name,entry]of Object.entries(read('provenance.json').assets))assert.equal(hash(fs.readFileSync(folder+name)),entry.sha256);
});
test('all558 targets and all19104 source payloads survive with exact primary coverage',()=>{
 const targets=new Set(),lines=new Set();let characters=0,primary=0;
 for(const d of books){
  const index=indexBook(d),covered=new Map();
  for(const m of d.mappings){
   assert(!targets.has(m.canonical.xml_id));targets.add(m.canonical.xml_id);
   const passage=m.fragments.map(f=>{
    const l=index.lines.get(f.line);if(!covered.has(f.line))covered.set(f.line,[]);covered.get(f.line).push([f.start_cp,f.end_cp]);
    const exact=codepoints(l.text_exact).slice(f.start_cp,f.end_cp).join('');assert.equal(l.text_exact.slice(f.start_utf16,f.end_utf16),exact);assert.equal(hash(Buffer.from(exact)),f.fragment_sha256);return exact;
   }).join('\n');assert.equal(hash(Buffer.from(passage)),m.source_passage_sha256);
  }
  for(const l of d.lines){assert(!lines.has(l.TEI_line_id));lines.add(l.TEI_line_id);assert.equal(hash(Buffer.from(l.text_exact)),l.text_sha256);
   const atoms=lineAtoms(l,index.byLine.get(l.TEI_line_id)||[]);assert.equal(atoms.map(a=>a.text).join(''),l.text_exact);
   if(l.primary){let end=0;for(const[a,b]of covered.get(l.TEI_line_id).sort((a,b)=>a[0]-b[0])){assert.equal(a,end);end=b;}assert.equal(end,codepoints(l.text_exact).length);primary++;characters+=end;}
   else assert(!covered.has(l.TEI_line_id));
  }
 }
 for(const l of read('preliminary.json').lines){assert(!lines.has(l.TEI_line_id));lines.add(l.TEI_line_id);}
 assert.equal(targets.size,558);assert.equal(lines.size,19104);assert.equal(primary,16236);assert.equal(characters,934885);
});
test('all canonical relations, attention and secondary observations preserved',()=>{
 const mm=books.flatMap(b=>b.mappings),aa=books.flatMap(b=>b.annotations);
 assert.deepEqual(Object.fromEntries(['one-to-one','many-to-one','displaced'].map(r=>[r,mm.filter(m=>m.relation===r).length])),{'one-to-one':549,'many-to-one':7,displaced:2});
 assert.equal(aa.length,162);assert.equal(mm.filter(m=>m.editorial_attention).length,4);assert(aa.every(a=>a.primary_coverage===false));
 assert.equal(aa.filter(a=>a.secondary_target).length,1);assert.equal(aa.find(a=>a.secondary_target).secondary_target.xml_id,'latin-deh5-num99');
 assert.equal(read('editorial.json').inherited.ancillary.length,24);assert.equal(read('editorial.json').inherited.historical.case_id,'B001-B009');
});
test('Prologue,I.2.1,I.8.1 and interleavedI.16.3–4 keep exact scope',()=>{
 const d=books[0],x=indexBook(d),prologue=d.mappings.filter(m=>m.canonical.chapter==='0');assert.equal(prologue.length,3);assert(prologue.every(m=>m.fragments.every(f=>x.lines.get(f.line).image_number<=32)));
 const m=d.mappings.find(m=>m.canonical.citation==='I.2.1');assert.equal(m.relation,'many-to-one');assert(new Set(m.fragments.map(f=>x.lines.get(f.line).image_number)).size>1);
 assert(d.mappings.find(m=>m.canonical.citation==='I.8.1').editorial_attention);
 for(const citation of ['I.16.3','I.16.4']){const m=d.mappings.find(m=>m.canonical.citation===citation);assert.equal(m.relation,'displaced');assert(m.fragments.length>1);}
});
test('cross-page spans do not become whole-chapter highlights; ¬ and a͑ survive',()=>{
 const d=books[1],x=indexBook(d),m=d.mappings.find(m=>new Set(m.fragments.map(f=>x.lines.get(f.line).image_number)).size>3);assert(m);
 const selected=new Set(m.fragments.map(f=>f.line));assert(d.lines.some(l=>l.primary&&!selected.has(l.TEI_line_id)));
 assert(books.some(b=>b.lines.some(l=>l.text_exact.includes('a\u0351'))));assert(books.some(b=>b.lines.some(l=>l.text_exact.includes('¬'))));
 assert.equal(books.reduce((n,b)=>n+b.lines.reduce((n,l)=>n+(l.text_exact.match(/¬/g)||[]).length,0),0)+read('preliminary.json').lines.reduce((n,l)=>n+(l.text_exact.match(/¬/g)||[]).length,0),5716);
 assert.equal(visibleLines(d,{mode:'page',page:280}).length,0);assert(d.pages.some(p=>p.image_number===280));
 assert(books[4].lines.some(l=>l.image_number===588));assert(visibleLines(d,{mode:'source'}).length>visibleLines(d).length);
});
test('codepoints differ from UTF16 and graphemes; no normalization or whitespace folding',()=>{
 const text=' a\u0351😀¬  œ\n';assert.equal(utf16Offset(text,4),5);assert.equal(codepoints(text).length,text.length-1);
 const atoms=lineAtoms({text_exact:text},[{start_cp:1,end_cp:4,mapping:'one'}]);assert.equal(atoms.map(a=>a.text).join(''),text);assert.equal(atoms.find(a=>a.mappings.length).text,'a\u0351😀');
 assert.throws(()=>utf16Offset(text,-1));assert.throws(()=>utf16Offset(text,99));
});
test('one-to-many, multiple spans and absence supported without invented segmentation',()=>{
 const line={TEI_line_id:'l',text_exact:'ab a͑😀¬ xy',primary:true};
 const fragments=[{line:'l',start_cp:0,end_cp:2,start_utf16:0,end_utf16:2},{line:'l',start_cp:3,end_cp:7,start_utf16:3,end_utf16:8}];
 const m={id:'multi',relation:'one-to-many',canonical:{xml_id:'latin-deh1-num1'},canonical_targets:[{xml_id:'latin-deh1-num1'},{xml_id:'latin-deh1-num2'}],fragments};
 const absent={id:'missing',relation:'absent',canonical:{xml_id:'latin-deh1-num3'},fragments:[]};
 const d={schema:'millet1556-reader-book/1',lines:[line],divisions:[],mappings:[m,absent],annotations:[]},x=indexBook(d);
 assert.deepEqual(canonicalIds(m),['latin-deh1-num1','latin-deh1-num2']);assert.equal(x.byCanonical.get('latin-deh1-num2')[0],m);assert.equal(x.byCanonical.get('latin-deh1-num3')[0].fragments.length,0);
 assert.equal(lineAtoms(line,x.byLine.get('l')).map(a=>a.text).join(''),line.text_exact);
 m.canonical_targets[0].chapter='1';m.canonical_targets[1].chapter='2';assert.deepEqual([...readingView(d,{mode:'running'},{level:'chapter-level',chapter:'2'},null).included],['multi']);
 const bad=structuredClone(d);bad.mappings[0].fragments[1].end_utf16--;assert.throws(()=>indexBook(bad),/coordinate/);
});
test('stable French deep links preserve existing Latin and parallel parameters',()=>{
 const url='http://localhost:8765/deh/?book=1&chapter=8&unit=1&parallel=deh-1-8-1&bj-source=niese';
 const state={enabled:true,mode:'page',page:'55',chapter:null,canonical:'latin-deh1-num24',alignment:true,folios:false};const u=updateMilletUrl(url,state);
 assert.equal(u.searchParams.get('parallel'),'deh-1-8-1');assert.equal(u.searchParams.get('unit'),'1');assert.deepEqual(locationFromUrl(u),state);
 assert.equal(updateMilletUrl(u,{...state,enabled:false}).searchParams.get('parallel'),'deh-1-8-1');assert(!updateMilletUrl(u,{...state,enabled:false}).searchParams.has('french'));
});
test('loader is book-scoped,cached,and rejects corrupted assets',async()=>{
 const requested=[];const fetcher=async url=>{requested.push(String(url));const name=new URL(url).pathname.split('/').pop();return new Response(fs.readFileSync(folder+name));};
 const loader=createMilletLoader('http://localhost/assets/data/deh-millet1556/',fetcher);await loader.book(2);await loader.book(2);assert.equal(requested.length,2);assert(!requested.some(r=>r.includes('book-01')));
 const bad=createMilletLoader('http://localhost/',async url=>new Response(new URL(url).pathname.endsWith('manifest.json')?fs.readFileSync(folder+'manifest.json'):Buffer.from('{}')));await assert.rejects(bad.book(2),/integrity/);
});

test('flowing reading display joins physical continuations without changing source offsets',()=>{
 assert.equal(flowSeparator('con¬','tinuer'), '');assert.equal(flowSeparator('Par','ce'), ' ');
 assert.equal(flowSeparator('a͑','dit'), ' ');
 const s='a͑😀 con¬  ';const parts=readingParts(s);assert.equal(parts.map(p=>p.text).join(''),s);assert.equal(parts.filter(p=>!p.hidden).map(p=>p.text).join(''),'a͑😀 con');
 for(const b of books)for(const l of b.lines){const parts=readingParts(l.text_exact);assert.equal(parts.map(p=>p.text).join(''),l.text_exact);assert(!parts.filter(p=>!p.hidden).some(p=>p.text.includes('¬')));}
 const ll=[{image_number:1,region_id:'a',source_region_type:'paragraph',text_exact:'con¬'},{image_number:2,region_id:'b',source_region_type:'paragraph',text_exact:'tinuer'}];assert.equal(flowGroups(ll).length,1);
 const labels=folioLabels(books[0]);assert.equal(labels.get(33),'Folio 1 recto');assert.equal(labels.get(34),'Folio 1 verso');assert.equal(labels.get(35),'Folio 2 recto');
 const state=locationFromUrl('https://example.org/deh/?french=millet1556');assert.equal(state.folios,false);state.folios=true;assert.equal(locationFromUrl(updateMilletUrl('https://example.org/deh/',state)).folios,true);
});

test('current unit view presents its recorded French intervals; complete text remains available',()=>{
 for(const b of books)for(const m of b.mappings){const v=readingView(b,{mode:'running'},{level:'section-level'},m.canonical.xml_id);assert.deepEqual([...v.included],[m.id]);assert.deepEqual(v.lines.map(l=>l.TEI_line_id),[...new Set(m.fragments.map(f=>f.line))]);}
 const d=books[0];assert.equal(readingView(d,{mode:'book'},{level:'section-level'},'latin-deh1-num4').included,null);
 const chapter=readingView(d,{mode:'running'},{level:'chapter-level',chapter:'1'},null);assert.equal(chapter.included.size,10);
});
