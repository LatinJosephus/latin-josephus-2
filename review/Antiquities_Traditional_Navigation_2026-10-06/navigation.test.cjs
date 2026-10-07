const fs = require('fs');
const path = require('path');
const http = require('http');
const cp = require('child_process');
const crypto = require('crypto');
const {chromium} = require('C:/Users/Pollard_R/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root = path.resolve(__dirname, '../..');
const base = 'f7d9142cad998e8a005adea1a22532b9a78592db';
const head = cp.execFileSync('git',['--no-optional-locks','show',`${base}:assets/js/renderTei.js`], {cwd:root, encoding:'utf8'});
const updated = fs.readFileSync(path.join(root,'assets/js/renderTei.js'),'utf8');
const include = fs.readFileSync(path.join(root,'_includes/display-settings.html'),'utf8');
const annotations = fs.readFileSync(path.join(root,'_includes/annotations-bar.html'),'utf8');
const report = {traditional:{}, niese:{}, crossWork:[], ui:[], errors:[]};
function instrument(source) {
 const extra = source.includes('const loadTraditionalRegistry') ? ',traditionalRegistry:()=>traditionalRegistry, alignmentRegistry:()=>alignmentRangeRegistry, traditionalRangeView,traditionalPoint,traditionalRows' : '';
 source = source.replace('  bookTitle.innerText = activeWork.title;', `  window.__qa = {getState:()=>({...state}), getData:()=>fullData, view:()=>viewData, reload, setState, setChapterSelectOptions, setSectionSelectOptions, setNieseSelectOptions, currentIdBase, applyNavigationFromUrl, syncUrlFromState, selectView${extra}, assign:patch=>Object.assign(state,patch)};\n  bookTitle.innerText = activeWork.title;`);
 return source.replace('  reload().then(() => {','  reload().then(() => {\n    window.__qaReady = true;');
}
const server=http.createServer((req,res)=>{
 const url=new URL(req.url,'http://localhost');
 let file;
 if(['/antiquities/','/deh/','/bellum-judaicum/','/contra-apionem/'].includes(url.pathname)) {
  const isAnt=url.pathname==='/antiquities/';
  const ui=include.replace(/{% if page.permalink == "\/antiquities\/" %}([\s\S]*?){% else %}([\s\S]*?){% endif %}/g,(_,a,b)=>isAnt?a:b);
  file=`<!doctype html><html><head><meta charset="utf-8"><style>.hidden,[hidden]{display:none!important}</style><link rel="stylesheet" href="/assets/css/tei.css"></head><body>${ui}<div id="pane-container">${['Latin','English','Greek','French','Italian'].map(l=>`<div id="${l.toLowerCase()}" class="pane"><h3>${l}</h3></div>`).join('')}</div>${annotations}<script>HTMLCollection.prototype.forEach=Array.prototype.forEach;</script><script src="/assets/js/CETEI.js"></script><script src="/__renderer.js${url.searchParams.get('baseline')==='1'?'?baseline=1':''}"></script></body></html>`;
  res.setHeader('Content-Type','text/html');res.end(file);return;
 }
 if(url.pathname==='/__renderer.js') {res.setHeader('Content-Type','text/javascript');res.end(instrument(url.searchParams.has('baseline')?head:updated));return;}
 const target=path.resolve(root,'.'+url.pathname);
 if(!target.startsWith(root+path.sep)||!fs.existsSync(target)){res.statusCode=404;res.end();return;}
 res.setHeader('Content-Type',target.endsWith('.xml')?'application/xml':target.endsWith('.js')?'text/javascript':'text/css');res.end(fs.readFileSync(target));
});
(async()=>{
 await new Promise(r=>server.listen(0,'127.0.0.1',r));
 const origin=`http://127.0.0.1:${server.address().port}`;
 const browser=await chromium.launch({headless:true, executablePath:"C:/Program Files/Google/Chrome/Application/chrome.exe"});
 const context=await browser.newContext(); const page=await context.newPage();
 page.on('pageerror',e=>(report.errors.push(String(e)),console.error('PAGEERROR',String(e))));
 async function open(route){await page.goto(origin+route);await page.waitForFunction(()=>window.__qaReady,{},{timeout:60000});}
 if(process.argv.includes('--protected-source-gate')){
  const checks=[];
  for(let book=1;book<=7;book++)for(const source of ['whiston','lodge1602']){
   const snapshots=[];
   for(const baseline of [true,false]){
    await open(`/bellum-judaicum/?book=${book}&chapter=1&english=${source}${baseline?'&baseline=1':''}`);
    snapshots.push(await page.evaluate(()=>{
     const q=window.__qa,full=q.getData(),samples=[];
     const capture=(key)=>samples.push([key,...Object.entries(full).map(([l,d])=>q.selectView(l,d,q.currentIdBase())?.outerHTML)]);
     capture('initial');
     const chapters=[...document.querySelector('#chapter-selector').options].filter(o=>o.value).map(o=>o.value);
     for(const chapter of chapters){q.assign({viewingLevel:'chapter-level',chapterNum:chapter,sectionNum:null,nieseNum:null});capture('chapter:'+chapter);q.assign({viewingLevel:'section-level'});q.setSectionSelectOptions();for(const u of [...document.querySelector('#section-selector').options].filter(o=>o.value).map(o=>o.value)){q.assign({sectionNum:u});capture('unit:'+chapter+':'+u);}}
     q.setNieseSelectOptions();const niese=[...document.querySelector('#niese-selector').options].filter(o=>o.value).map(o=>o.value);
     for(const n of niese){q.assign({viewingLevel:'niese-level',nieseNum:n,chapterNum:null,sectionNum:null});capture('niese:'+n);}
     return {source:q.getState().sources.English,niese:niese.length,chapters:chapters.length,samples};
    }));
   }
   if(JSON.stringify(snapshots[0])!==JSON.stringify(snapshots[1]))throw Error('Protected source regression '+book+' '+source);
   checks.push({work:'bellum-judaicum',book,source,chapters:snapshots[1].chapters,niese:snapshots[1].niese,ranges:snapshots[1].samples.length,result:'PASS'});console.log('protected-source',book,source,snapshots[1].samples.length);
  }
  fs.writeFileSync(path.join(__dirname,'PROTECTED_SOURCE_GATE_QA.json'),JSON.stringify({checks,result:'PASS'},null,2));await browser.close();server.close();return;
 }
 if(process.argv.includes('--rendered-gate')){
  const cases=[[1,'preface',2],[2,13,4],[4,8,32],[5,3,2],[6,3,2],[6,12,8],[6,13,1],[7,1,1],[8,10,3],[11,8,null],[11,8,2],[11,8,3],[11,8,4],[11,8,5],[11,8,6],[14,10,19],[15,3,5],[16,8,2]];
  const checks=[];
  for(const [book,chapter,subchapter]of cases){
   const route=chapter==='preface'?`/antiquities/?book=preface&subchapter=${subchapter}`:`/antiquities/?book=${book}&chapter=${chapter}${subchapter?`&subchapter=${subchapter}`:''}`;
   await open(route);
   const result=await page.evaluate(()=>{
    const ids=[...document.querySelectorAll('[id]')].map(n=>n.id),dups=ids.filter((id,i)=>ids.indexOf(id)!==i);
    const labels=[...document.querySelectorAll('#book-select label,#level-select label')].map(n=>n.textContent.trim());
    if(dups.length)throw Error('Duplicate rendered IDs '+dups.join(','));
    if(labels.some(l=>/sub-chapter/i.test(l))||!labels.includes('Alignment unit')||!labels.includes('Subchapter'))throw Error('Incorrect Antiquities labels '+JSON.stringify(labels));
    const state=window.__qa.getState();return {state,renderedIDs:ids.length,disclosures:document.querySelectorAll('[data-structural-notice]').length,result:'PASS'};
   });
   const url=page.url();await page.uncheck('#english-pane-select');await page.uncheck('#greek-pane-select');await page.check('#english-pane-select');await page.check('#greek-pane-select');
   if(page.url()!==url)throw Error('Pane switch changed structural URL');
   checks.push({book,chapter,subchapter,...result});
  }
  const phaseCoverage=await page.evaluate(()=>({XI_Niese_control_disabled:document.querySelector('#niese-level').disabled}));
  await open('/antiquities/?book=11&chapter=8&subchapter=4&extra=keep#anchor');
  await page.locator('#latin [data-structural-notice] summary').click();
  await page.locator('#latin [data-structural-notice] a').click();await page.waitForFunction(()=>window.__qaReady&&window.__qa.getState().viewingLevel==='book-level');
  if(new URL(page.url()).searchParams.get('extra')!=='keep'||!page.url().endsWith('#anchor'))throw Error('Witness link loses unrelated URL state');
  const record={checks,duplicate_rendered_DOM_IDs:'NONE',source_language_toggles:'PASS',Antiquities_labels:'PASS',witness_order_link:'PASS',public_XI_XX_Niese_expansion:false};
  fs.writeFileSync(path.join(__dirname,'RENDERED_GATE_QA.json'),JSON.stringify(record,null,2));await browser.close();server.close();console.log('RENDERED_GATE_PASS',checks.length);return;
 }
 if(process.argv.includes('--multispan-gate')){
  await open('/antiquities/?book=11');
  const result=await page.evaluate(()=>{
   const q=window.__qa;
   const omit=new Set(['tei-num','tei-milestone','tei-pb','tei-lb','tei-note','tei-anchor']);
   const project=n=>n.nodeType===3?n.data:omit.has(n.localName)||n.hasAttribute?.('data-structural-notice')?'':[...n.childNodes].map(project).join('');
   const norm=s=>s.replace(/\s+/g,' ').trim();
   const checks=[],fragments={};
   for(const language of ['Greek','Latin','English']){
    const full=q.getData()[language],body=full.querySelector('tei-body'),all=project(body);
    function position(point){let count=0,result=null;function walk(n){if(n===point.node){result=count;return;}if(n.nodeType===3){count+=n.data.length;return;}if(omit.has(n.localName))return;for(const c of n.childNodes){walk(c);if(result!==null)return;}}walk(body);return result;}
    for(const id of ['LOEB-11-Chapter-8-0',...Array.from({length:5},(_,i)=>`LOEB-11-Subchapter-8-${i+2}`)]){
     const row=q.traditionalRegistry().find(r=>r.id===id),view=q.traditionalRangeView(language,full,row);
     const intervals=row[language].spans.map(s=>[position(q.traditionalPoint(full,s.start)),s.end.kind==='book-end'?all.length:position(q.traditionalPoint(full,s.end))]);
     for(let i=0;i<intervals.length;i++)for(let j=0;j<i;j++)if(Math.max(intervals[i][0],intervals[j][0])<Math.min(intervals[i][1],intervals[j][1]))throw Error('Duplicate physical membership '+id+' '+language);
     const expected=intervals.map(([a,b])=>all.slice(a,b)).join(''),actual=project(view);
     if(actual!==expected){let at=0;while(at<actual.length&&actual[at]===expected[at])at++;throw Error(JSON.stringify({id,language,intervals,firstDifference:at,actualLength:actual.length,expectedLength:expected.length,actual:actual.slice(at-80,at+250),expected:expected.slice(at-80,at+250)}));}
     const ids=[...view.querySelectorAll('[id]')].map(n=>n.id);if(new Set(ids).size!==ids.length)throw Error('Duplicate rendered ID '+id);
     if(!norm(actual).startsWith(norm(row[language].anchor)))throw Error('Wrong first content '+id+' '+language);
     if(intervals.length>1&&!view.querySelector('[data-structural-notice] a'))throw Error('No disclosure/witness link '+id);
     if(id.endsWith('Subchapter-8-2')&&language==='Latin')for(const label of ['[BJ 4.105a]','[BJ 4.105b]'])if(!view.textContent.includes(label))throw Error('Interpolation lost '+label);
     if(id.endsWith('Subchapter-8-4')&&language==='Latin'){
      const nums=[...view.querySelectorAll('tei-num')].map(n=>n.textContent);
      if(!nums.includes('[326a]')||!nums.includes('[VIII.iv.326b]')||nums.includes('[342b]')||nums.includes('[329]'))throw Error('Wrong XI.viii.4 membership');
     }
     checks.push({id,language,spans:intervals.length,ordered_physical_intervals:intervals,incipit:norm(actual).slice(0,110),result:'PASS'});
     fragments[id+'|'+language]={intervals,projection:actual};
    }
    const chapter=fragments['LOEB-11-Chapter-8-0|'+language];
    const subs=['LOEB-11-Subchapter-8-1',...Array.from({length:5},(_,i)=>`LOEB-11-Subchapter-8-${i+2}`)].map(id=>project(q.traditionalRangeView(language,full,q.traditionalRegistry().find(r=>r.id===id)))).join('');
    if(norm(chapter.projection)!==norm(subs))throw Error('Chapter/Subchapter coverage partition '+language);
   }
   // The identical generic resolver supports a citation selection with split witness text.
   const full=q.getData().Latin;
   const loc=(p,edge)=>({available:'true',target:`latin-book11-num${p}`,kind:edge?'element-edge':'paragraph',...(edge?{edge}: {})});
   const citationChecks=[];
   for(const [n,spans]of [[326,[{start:loc(321,'num[6]'),end:loc(321,'num[7]')},{start:loc(326),end:loc(326,'num[2]')}]], [342,[{start:loc(340,'num[3]'),end:loc(312)},{start:loc(321,'num[7]'),end:loc(343)}]]]){
    const view=q.traditionalRangeView('Latin',full,{id:`qa-citation-${n}`,scheme:'niese',Latin:{spans}});
    if(view.querySelectorAll('[type="physical-fragment"]').length!==2||!project(view).trim())throw Error('Generic Niese multi-span model '+n);
    citationChecks.push({niese:n,language:'Latin',spans:2,result:'PASS',public_navigation_expansion:false});
   }
   return {checks,citationChecks,canonical_membership_no_duplication:'PASS',interpolations_retained:'PASS',disclosure_and_witness_link:'PASS'};
  });
  const witness=[];
  for(const baseline of [true,false]){
   await open(`/antiquities/?book=11${baseline?'&baseline=1':''}`);
   witness.push(await page.evaluate(()=>{
    const q=window.__qa;const full=q.getData();
    const book=Object.fromEntries(Object.entries(full).map(([l,d])=>[l,[...d.querySelectorAll('tei-p[id]')].map(p=>[p.id,p.getAttribute('sameAs'),p.outerHTML])]));
    const units={};for(const u of ['304','306','326','329','340','312','313','321','343','346']){q.assign({viewingLevel:'section-level',sectionNum:u});units[u]=Object.fromEntries(Object.entries(full).map(([l,d])=>{const view=q.selectView(l,d,q.currentIdBase());return [l,[...view.querySelectorAll('tei-p')].concat(view.localName==='tei-p'?[view]:[]).map(p=>p.outerHTML)];}));}
    return {book,units};
   }));
  }
  if(JSON.stringify(witness[0])!==JSON.stringify(witness[1]))throw Error('Book/Alignment-unit witness-order regression');
  result.book_and_alignment_views_vs_base='PASS';result.no_corpus_changes='Verified by independent SHA-256 integrity QA';
  fs.writeFileSync(path.join(__dirname,'XI_MULTISPAN_GATE_QA.json'),JSON.stringify(result,null,2));await browser.close();server.close();console.log('MULTISPAN_GATE_PASS',JSON.stringify(result));return;
 }
 if(process.argv.includes('--projection-diagnosis')){
  await open('/antiquities/?book=11');
  const result=await page.evaluate(()=>{
   const q=window.__qa,full=q.getData().Latin;
   const omit=new Set(['tei-num','tei-milestone','tei-pb','tei-lb','tei-note','tei-anchor']);
   const project=n=>n.nodeType===3?n.data:omit.has(n.localName)?'':[...n.childNodes].map(project).join('');
   return ['LOEB-11-Chapter-8-0','LOEB-11-Subchapter-8-6'].map(id=>{
    const row=q.traditionalRegistry().find(r=>r.id===id),start=q.traditionalPoint(full,row.Latin);
    const range=document.createRange();if(start.kind==='paragraph')range.setStart(start.node,0);else range.setStartBefore(start.node);const body=start.node.closest('tei-body');range.setEnd(body,body.childNodes.length);
    let count=0,pos=null;function walk(n){if(n===start.node){pos=count;return;}if(n.nodeType===3){count+=n.data.length;return;}if(omit.has(n.localName))return;for(const c of n.childNodes){walk(c);if(pos!==null)return;}}walk(body);const actual=project(q.traditionalRangeView('Latin',full,row)),expected=project(body).slice(pos);
    let at=0;while(at<actual.length&&actual[at]===expected[at])at++;
    return {id,locator:row.Latin,actual_length:actual.length,expected_length:expected.length,first_difference:at,actual_context:actual.slice(at-80,at+250),expected_context:expected.slice(at-80,at+250),expected_tail:expected.slice(-300),actual_tail:actual.slice(-300)};
   });
  });
  console.log(JSON.stringify(result,null,2));fs.writeFileSync(path.join(__dirname,'XI_LATIN_PROJECTION_DIAGNOSIS.json'),JSON.stringify(result,null,2));await browser.close();server.close();return;
 }
 if(process.argv.includes('--alignment-gate')){
  const units=['259','262','271','272','275'];const checks=[];
  const expected={
   '259':{Latin:'Haec dicens sacerdos',English:'When the high priest had spoken',Greek:'Ταῦτα'},
   '262':{Latin:'porro saul rex',English:'Now this king Saul',Greek:'Σαοῦλος δὲ'},
   '271':{Latin:'Abiathar itaque',English:'But Abiathar',Greek:'Ὁ δ᾽ Ἀβιάθαρος'},
   '272':{Latin:'Eo siquidem tempore',English:'About this time',Greek:'Κατὰ δὲ'},
   '275':{Latin:'Dauid autem',English:'Then David removed',Greek:'Δαυίδης δὲ'}
  };
  for(const unit of units){
   await open(`/antiquities/?book=6&unit=${unit}`);
   const result=await page.evaluate(()=>{
    const q=window.__qa;
    const omit=new Set(['tei-num','tei-milestone','tei-pb','tei-lb','tei-note','tei-anchor']);
    const projection=node=>{if(node.nodeType===3)return node.data;if(omit.has(node.localName)||node.hasAttribute?.('data-structural-notice'))return '';return [...node.childNodes].map(projection).join('');};
    return {state:q.getState(),panes:Object.fromEntries(Object.entries(q.view()).map(([l,v])=>[l,projection(v).replace(/\s+/g,' ').trim()]))};
   });
   for(const language of ['Latin','English','Greek'])if(!result.panes[language].startsWith(expected[unit][language]))throw Error(JSON.stringify({unit,language,expected:expected[unit][language],result}));
   const url=page.url();await page.uncheck('#greek-pane-select');await page.uncheck('#english-pane-select');await page.check('#greek-pane-select');await page.check('#english-pane-select');
   if(page.url()!==url||await page.evaluate(()=>window.__qa.getState().sectionNum)!==unit)throw Error('Pane-switch identity regression '+unit);
   checks.push({unit,panes:Object.fromEntries(Object.entries(result.panes).map(([l,t])=>[l,t.slice(0,160)])),pane_switch:'PASS',result:'PASS'});
  }
  const coverage=await page.evaluate(()=>{
   const q=window.__qa,full=q.getData().Greek;
   const omit=new Set(['tei-num','tei-milestone','tei-pb','tei-lb','tei-note','tei-anchor']);
   const projection=node=>{if(node.nodeType===3)return node.data;if(omit.has(node.localName)||node.hasAttribute?.('data-structural-notice'))return '';return [...node.childNodes].map(projection).join('');};
   let joined='';for(const u of ['262','271','272']){q.assign({sectionNum:u});joined+=projection(q.selectView('Greek',full,q.currentIdBase()));}
   const start=full.querySelector('[id="greek-book06-num262"]'),end=full.querySelector('[id="greek-book06-num275"]');
   const range=document.createRange();range.setStart(start,0);range.setEnd(end,0);
   const norm=t=>t.replace(/\s+/g,' ').trim();
   return {three_bindings:q.alignmentRegistry().length,partition:norm(joined)===norm(projection(range.cloneContents()))?'PASS':'FAIL'};
  });
  if(coverage.partition!=='PASS'||coverage.three_bindings!==3)throw Error(JSON.stringify(coverage));
  const niese=[];
  for(const n of [269,271]){
   const snapshots=[];
   for(const baseline of [true,false]){
    await open(`/antiquities/?book=6&niese=${n}${baseline?'&baseline=1':''}`);
    snapshots.push(await page.evaluate(()=>Object.fromEntries(Object.entries(window.__qa.view()).map(([l,v])=>{v=v.cloneNode(true);v.querySelectorAll('tei-anchor[type="traditional-boundary"]').forEach(a=>a.remove());return [l,v.outerHTML];}))));
   }
   if(JSON.stringify(snapshots[0])!==JSON.stringify(snapshots[1]))throw Error('Niese focused regression '+n);
   niese.push({niese:n,language_comparisons:3,result:'PASS'});
  }
  const record={units:checks,neighboring_units:['259','275'],alignment_partition:coverage,niese,XML_ID_sameAs_text_topology:'Verified separately by byte integrity script',generic_data_bindings:true};
  fs.writeFileSync(path.join(__dirname,'VI_ALIGNMENT_GATE_QA.json'),JSON.stringify(record,null,2));
  await browser.close();server.close();console.log('ALIGNMENT_GATE_PASS',JSON.stringify(record));return;
 }
 if(process.argv.includes('--locator-gate')){
  await open('/antiquities/?book=6&chapter=12&subchapter=8');
  const alignmentRepairApplied=await page.evaluate(()=>window.__qa.alignmentRegistry().length===3);
  const result=await page.evaluate(()=>{
   const q=window.__qa;const row=q.traditionalRegistry().find(r=>r.id==='LOEB-06-Subchapter-12-8');
   const end=q.traditionalRegistry().find(r=>r.id===row.end);
   const omit=new Set(['tei-num','tei-milestone','tei-pb','tei-lb','tei-note','tei-anchor']);
   const projection=node=>{if(node.nodeType===3)return node.data;if(omit.has(node.localName)||node.hasAttribute?.('data-structural-notice'))return '';return [...node.childNodes].map(projection).join('');};
   const checks=[];
   for(const language of ['Latin','English']){
    const data=q.getData()[language],view=q.traditionalRangeView(language,data,row);
    const start=q.traditionalPoint(data,row[language]),ep=q.traditionalPoint(data,end[language]);
    const range=document.createRange();range.setStartBefore(start.node);range.setEndBefore(ep.node);
    const ordered=start.node.compareDocumentPosition(ep.node)&Node.DOCUMENT_POSITION_FOLLOWING;
    const actual=projection(view).replace(/\s+/g,' ').trim();
    const expected=row[language].anchor.replace(/\s+/g,' ').trim();
    checks.push({language,start:row[language],end:end[language],ordered:Boolean(ordered),incipit:actual.slice(0,160),result:Boolean(ordered)&&actual.startsWith(expected)&&projection(view)===projection(range.cloneContents())?'PASS':'FAIL'});
   }
   return checks;
  });
  if(result.some(r=>r.result!=='PASS'))throw Error(JSON.stringify(result));
  const originalNiese=[];
  for(const n of [269,271]){
   await open(`/antiquities/?book=6&niese=${n}&baseline=1`);
   originalNiese.push(await page.evaluate(n=>{
    const q=window.__qa;
    const omit=new Set(['tei-num','tei-milestone','tei-pb','tei-lb','tei-note','tei-anchor']);
    const projection=node=>{if(node.nodeType===3)return node.data;if(omit.has(node.localName)||node.hasAttribute?.('data-structural-notice'))return '';return [...node.childNodes].map(projection).join('');};
    const latin=q.selectView('Latin',q.getData().Latin,q.currentIdBase());
    const english=q.selectView('English',q.getData().English,q.currentIdBase());
    english.querySelectorAll('.niese-context-note').forEach(e=>e.remove());
    const greek=q.selectView('Greek',q.getData().Greek,q.currentIdBase());
    return {niese:n,Latin:projection(latin).replace(/\s+/g,' ').trim().slice(0,140),English:projection(english).replace(/\s+/g,' ').trim().slice(0,140),Greek:projection(greek).replace(/\s+/g,' ').trim().slice(0,140)};
   },n));
  }
  if(!originalNiese[0].Latin.startsWith('Abiathar itaque')||!originalNiese[1].Latin.startsWith('Eo siquidem tempore')||!originalNiese[0].English.startsWith('But Abiathar')||!originalNiese[1].English.startsWith('About this time')||!originalNiese[0].Greek.startsWith('Ὁ δ᾽ Ἀβιάθαρος')||!originalNiese[1].Greek.startsWith('Κατὰ δὲ'))throw Error(JSON.stringify(originalNiese));
  fs.writeFileSync(path.join(__dirname,'VI_LOCATOR_GATE_QA.json'),JSON.stringify({targeted_ranges:result,range_passes:2,base_niese_behavior:originalNiese,base_niese_pane_checks:6,alignment_repair_applied:alignmentRepairApplied},null,2));
  await browser.close();server.close();console.log('LOCATOR_GATE_2_OF_2_PASS',JSON.stringify(originalNiese));return;
 }
 await open('/antiquities/?book=1&chapter=1');
 let totals={rows:0, executable:0, unavailable:0, byLanguage:{}, menusChapters:0, menusSubchapters:0, physical:0};
 for(const book of ['preface',...Array.from({length:20},(_,i)=>String(i+1).padStart(2,'0'))]){
  const result=await page.evaluate(async book=>{
   const q=window.__qa;q.assign({bookNum:book,chapterNum:null,subchapterNum:null,sectionNum:null,nieseNum:null,viewingLevel:'book-level'});await q.reload();
   const data=q.getData(),rows=q.traditionalRows('chapter').concat(q.traditionalRows('subchapter'));
   const norm=s=>s.replace(/\s+/g,' ').trim();
   const omit=new Set(['tei-num','tei-milestone','tei-pb','tei-lb','tei-note','tei-anchor']);
   const projection=node=>{if(node.nodeType===3)return node.data;if(omit.has(node.localName)||node.hasAttribute?.('data-structural-notice'))return '';return [...node.childNodes].map(projection).join('');};
   const results={rows:rows.length,executable:0,unavailable:0,byLanguage:{},menusChapters:document.querySelector('#chapter-selector').options.length-1,menusSubchapters:0, failures:[]};
   for(const chapter of (book==='preface'?['']:q.traditionalRows('chapter').map(r=>r.chapter))){q.assign({chapterNum:chapter,viewingLevel:'subchapter-level'});await q.reload();results.menusSubchapters+=document.querySelector('#subchapter-selector').options.length-1;}
   // Refresh full sources after rendering; ranges never operate on already-clipped panes.
   q.assign({viewingLevel:'book-level',chapterNum:null});await q.reload();
   for(const row of rows)for(const language of ['Greek','Latin','English']){
    const full=q.getData()[language];const end=row.end==='BOOK_END'?null:q.traditionalRegistry().find(r=>r.id===row.end);
    const spans=row[language].spans||[{start:row[language],end:end?.[language]||{kind:'book-end'}}];
    const executable=spans.every(s=>s.start.available==='true'&&(s.end.kind==='book-end'||s.end.available==='true'));
    const view=q.traditionalRangeView(language,full,row);
    if(!executable){results.unavailable++;if(!view.classList.contains('structural-unavailable'))results.failures.push([row.id,language,'missing availability']);continue;}
    results.executable++;results.byLanguage[language]=(results.byLanguage[language]||0)+1;
    const observed=projection(view);
    if(!norm(observed).startsWith(norm(row[language].anchor)))results.failures.push([row.id,language,'incipit',norm(observed).slice(0,160),row[language].anchor]);
    const ids=[...view.querySelectorAll('[id]')].map(n=>n.id);if(new Set(ids).size!==ids.length)results.failures.push([row.id,language,'duplicate ID']);
    // Independent projected-text interval verifies both endpoints, not merely a nearby numeral.
    function position(point){let count=0,result=null;function walk(node){if(node===point.node){result=count;return;}if(node.nodeType===3){count+=node.data.length;return;}if(omit.has(node.localName))return;for(const child of node.childNodes){walk(child);if(result!==null)return;}}walk(full.querySelector('tei-body'));return result;}
    const all=projection(full.querySelector('tei-body'));
    const intervals=spans.map(s=>[position(q.traditionalPoint(full,s.start)),s.end.kind==='book-end'?all.length:position(q.traditionalPoint(full,s.end))]);
    const expected=intervals.map(([a,b])=>all.slice(a,b)).join('');
    for(let i=0;i<intervals.length;i++)for(let j=0;j<i;j++)if(Math.max(intervals[i][0],intervals[j][0])<Math.min(intervals[i][1],intervals[j][1]))results.failures.push([row.id,language,'duplicated span membership']);
    if(observed!==expected)results.failures.push([row.id,language,'range projection mismatch',observed.slice(0,100),expected.slice(0,100),{actualLength:observed.length,expectedLength:expected.length,firstDifference:[...observed].findIndex((c,i)=>c!==expected[i]),actualTail:observed.slice(-250),expectedTail:expected.slice(-250)}]);
   }
   return results;
  },book);
  if(result.failures.length)throw new Error(JSON.stringify({book,...result}));
  totals.rows+=result.rows;totals.executable+=result.executable;totals.unavailable+=result.unavailable;totals.menusChapters+=result.menusChapters;totals.menusSubchapters+=result.menusSubchapters;
  for(const [l,c]of Object.entries(result.byLanguage))totals.byLanguage[l]=(totals.byLanguage[l]||0)+c;
  console.log('traditional',book,result.executable,result.unavailable);fs.writeFileSync(path.join(__dirname,'BROWSER_PROGRESS.json'),JSON.stringify({lastBook:book,totals},null,2));
 }
 totals.physical=await page.evaluate(()=>new Set(window.__qa.traditionalRegistry().map(r=>r['physical-point'])).size);
 if(totals.rows!==1689||totals.menusChapters!==257||totals.menusSubchapters!==1432||totals.physical!==1441)throw Error(JSON.stringify(totals));
 report.traditional=totals;
 // All currently supported Niese selections compared to the original renderer, by text and IDs.
 for(let book=1;book<=7;book++){
  const snapshots=[];
  for(const baseline of [true,false]){
   await open(`/antiquities/?book=${book}&niese=${book===1?27:1}${baseline?'&baseline=1':''}`);
   snapshots.push(await page.evaluate(async()=>{
    const q=window.__qa;const data=q.getData();const options=[...document.querySelector('#niese-selector').options].filter(o=>o.value).map(o=>o.value);const entries=[];
    for(const n of options){q.assign({viewingLevel:'niese-level',nieseNum:n,chapterNum:null,sectionNum:null});entries.push([n,...['Greek','Latin','English'].map(l=>{
     const v=q.selectView(l,data[l],q.currentIdBase());if(!v)return null;v.querySelectorAll('tei-anchor[type="traditional-boundary"]').forEach(a=>a.remove());return v.outerHTML;
    })]);}
    return entries;
   }));
  }
  if(JSON.stringify(snapshots[0])!==JSON.stringify(snapshots[1]))throw Error('Niese regression Book '+book);
  report.niese[book]={selections:snapshots[1].length,language_comparisons:snapshots[1].length*3,result:'PASS'};console.log('niese',book,snapshots[1].length);
 }
 // Differential checks exercise every supported book and all menu-defined ranges in other works.
 for(const [work,count]of [['deh',5],['bellum-judaicum',7],['contra-apionem',2]])for(let book=1;book<=count;book++){
  const snapshots=[];
  for(const baseline of [true,false]){
   await open(`/${work}/?book=${book}&chapter=1${baseline?'&baseline=1':''}`);
   snapshots.push(await page.evaluate(async()=>{
    const q=window.__qa;const chapters=[...document.querySelector('#chapter-selector').options].filter(o=>o.value).map(o=>[o.value,o.text]);const samples=[];
    for(const [ch]of chapters){q.assign({viewingLevel:'chapter-level',chapterNum:ch,sectionNum:null});q.setSectionSelectOptions();samples.push([ch,...Object.entries(q.getData()).map(([l,d])=>q.selectView(l,d,q.currentIdBase())?.outerHTML)]);
     q.assign({viewingLevel:'section-level'});q.setSectionSelectOptions();const units=[...document.querySelector('#section-selector').options].filter(o=>o.value).map(o=>[o.value,o.text]);
     for(const [u]of units){q.assign({sectionNum:u});samples.push([ch,u,...Object.entries(q.getData()).map(([l,d])=>q.selectView(l,d,q.currentIdBase())?.outerHTML)]);}
    }
    return {chapters,samples,sectionLabel:document.querySelector('label[for="section-level"]').textContent};
   }));
  }
  if(JSON.stringify(snapshots[0])!==JSON.stringify(snapshots[1]))throw Error(`Cross-work regression ${work} ${book}`);
  report.crossWork.push({work,book,chapters:snapshots[1].chapters.length,ranges:snapshots[1].samples.length,result:'PASS'});console.log('cross-work',work,book,snapshots[1].samples.length);
 }
 // Exercise actual event listeners, URL normalization, reload and history.
 await open('/antiquities/?book=5&chapter=3&subchapter=2&extra=keep#retained');
 async function assertState(expected){const actual=await page.evaluate(()=>window.__qa.getState());for(const[k,v]of Object.entries(expected))if(actual[k]!==v)throw Error(JSON.stringify({expected,actual}));}
 await assertState({chapterNum:'3',subchapterNum:'2',viewingLevel:'subchapter-level'});
 await page.reload();await page.waitForFunction(()=>window.__qaReady);await assertState({subchapterNum:'2'});
 await page.check('#niese-level');await page.waitForFunction(()=>window.__qa.getState().viewingLevel==='niese-level'&&new URL(location.href).searchParams.has('niese'));
 const firstNiese=await page.evaluate(()=>window.__qa.getState().nieseNum);
 await page.selectOption('#niese-selector','179');await page.waitForFunction(()=>new URL(location.href).searchParams.get('niese')==='179');
 if(new URL(page.url()).searchParams.has('chapter')||!page.url().endsWith('#retained'))throw Error('Stale URL/fragment');
 await page.goBack();await page.waitForFunction(n=>window.__qa.getState().nieseNum===n,firstNiese);
 await page.goBack();await page.waitForFunction(()=>window.__qa.getState().subchapterNum==='2');
 await page.goForward();await page.waitForFunction(()=>window.__qa.getState().viewingLevel==='niese-level');
 await page.check('#section-level');await page.selectOption('#section-selector','179');await page.waitForFunction(()=>new URL(location.href).searchParams.get('unit')==='179');
 await page.check('#greek-pane-select',{force:true});await assertState({sectionNum:'179'});
 await open('/antiquities/?book=4&unit=276b');await assertState({sectionNum:'276b'});
 if(!await page.locator('#latin [id="latin-book04-num276b"]').count())throw Error('Non-simple unit ID');
 await open('/antiquities/?book=preface&subchapter=2');await assertState({bookNum:'preface',subchapterNum:'2'});
 if(await page.locator('#chapter-selector option[value="0"]').count())throw Error('Invented Chapter zero');
 await open('/antiquities/?book=9&chapter=5');if(await page.locator('.structural-unavailable').count()!==3)throw Error('Missing IX chapter');
 await page.selectOption('#book-selector','07');await page.waitForFunction(()=>window.__qa.getState().bookNum==='07');await page.check('#chapter-level');await page.waitForFunction(()=>window.__qa.getState().chapterNum==='1');
 if(await page.locator('#latin [id="latin-book07-num"]').count()!==1)throw Error('VII stable ID not resolved');
 report.ui.push('Chapter/Subchapter reload','Subchapter to Niese','Back/forward','Alignment unit','Language pane toggle','Book switching','Proem','num276b','Book IX unavailable','Book VII opening','Unrelated parameters and fragment');
 if(report.errors.length)throw Error(JSON.stringify(report.errors));
 fs.writeFileSync(path.join(__dirname,'BROWSER_QA.json'),JSON.stringify(report,null,2));
 await browser.close();server.close();console.log('ALL_BROWSER_QA_PASS',JSON.stringify(report.traditional));
})().catch(e=>{console.error(e);fs.writeFileSync(path.join(__dirname,'BROWSER_FAILURE.json'),JSON.stringify({error:String(e),report},null,2));server.close();process.exit(1);});
