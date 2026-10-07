const fs = require('fs');
const path = require('path');
const http = require('http');
const cp = require('child_process');
const crypto = require('crypto');
const {chromium} = require('C:/Users/Pollard_R/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root = path.resolve(__dirname, '../..');
const base = 'b8d4db2938e3a61a7f75ea8fcbb06f22fc78f02d';
const head = cp.execFileSync('git',['--no-optional-locks','show',`${base}:assets/js/renderTei.js`], {cwd:root, encoding:'utf8'});
const updated = fs.readFileSync(path.join(root,'assets/js/renderTei.js'),'utf8');
const include = fs.readFileSync(path.join(root,'_includes/display-settings.html'),'utf8');
const annotations = fs.readFileSync(path.join(root,'_includes/annotations-bar.html'),'utf8');
const report = {traditional:{}, niese:{}, crossWork:[], ui:[], errors:[]};
function cleanHTML(node){if(!node)return null;node=node.cloneNode(true);node.querySelectorAll('tei-anchor[type="bamberg-boundary"]').forEach(a=>a.remove());return node.outerHTML;}
function instrument(source) {
 const extra = source.includes('const loadTraditionalRegistry') ? ',traditionalRegistry:()=>traditionalRegistry, alignmentRegistry:()=>alignmentRangeRegistry, traditionalRangeView,traditionalPoint,traditionalRows' : '';
 const supplemental = (source.includes('const traditionalRangePoint') ? ',traditionalRangePoint' : '') + (source.includes('let bambergRegistry') ? ',bambergRows,bambergSelection,bambergRegistry:()=>bambergRegistry,boundaryRegistry:()=>boundaryRegistry' : '');
 source = source.replace('  bookTitle.innerText = activeWork.title;', `  ${cleanHTML.toString()}
  window.__qa = {cleanHTML, getState:()=>({...state}), getData:()=>fullData, view:()=>viewData, reload, setState, setChapterSelectOptions, setSectionSelectOptions, setNieseSelectOptions, currentIdBase, applyNavigationFromUrl, syncUrlFromState, selectView${extra}${supplemental}, assign:patch=>Object.assign(state,patch)};\n  bookTitle.innerText = activeWork.title;`);
 source = source.replaceAll('setState(() => {', 'window.__qaPending = setState(() => {');
 return source.replace('  reload().then(() => {','  reload().then(() => {\n    window.__qaReady = true;');
}
const server=http.createServer((req,res)=>{
 const url=new URL(req.url,'http://localhost');
 let file;
 if(['/antiquities/','/deh/','/bellum-judaicum/','/contra-apionem/'].includes(url.pathname)) {
  const isAnt=url.pathname==='/antiquities/';
  const ui=include.replace(/{% if page.permalink == "\/antiquities\/" %}([\s\S]*?){% endif %}/g,(_,body)=>{const [a,b='']=body.split('{% else %}');return isAnt?a:b;});
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
 const expected=[18,3,11,5,13,0,0,0,0,0,0,1,21,27,13,20,19,19,8,20];
 const ranges=[],urls=[],coverage=[],pairChecks=[];
 for(let book=1;book<=20;book++){
  await open(`/antiquities/?book=${book}`);
  const checked=await page.evaluate(async expected=>{
   const q=window.__qa,rows=q.bambergRows(),full=q.getData(),all=q.boundaryRegistry();
   if(rows.length!==expected)throw Error('Bamberg per-book count');
   const selector=document.querySelector('#bamberg-selector'),radio=document.querySelector('#bamberg-level');
   if(selector.options.length!==expected||radio.disabled!==(expected===0)||selector.disabled!==(expected===0))throw Error('Bamberg availability');
   const ids=rows.map(r=>r.id);if(new Set(ids).size!==ids.length)throw Error('Duplicate source identity');
   const omit=new Set(['tei-num','tei-milestone','tei-pb','tei-lb','tei-note','tei-anchor']);
   const project=n=>n.nodeType===3?n.data:omit.has(n.localName)?'':[...n.childNodes].map(project).join('');
   const norm=s=>s.replace(/\s+/g,' ').trim(),out=[];
   function position(data,point){let count=0,result=null;function walk(n){if(n===point.node){result=count;return;}if(n.nodeType===3){count+=n.data.length;return;}if(omit.has(n.localName))return;for(const c of n.childNodes){walk(c);if(result!==null)return;}}walk(data.querySelector('tei-body'));if(result===null)throw Error('Unlocatable endpoint');return result;}
   for(const [i,row]of rows.entries()){
    if(Number(row['source-order'])!==i+1||row.end!==(rows[i+1]?.id||'BOOK_END'))throw Error('Source order/end association');
    for(const lang of ['Latin','Greek','English']){
     const data=full[lang],loc=row[lang],next=all.find(r=>r.id===row.end),view=q.traditionalRangeView(lang,data,row);
     if(loc.available!=='true'||view.classList.contains('structural-unavailable'))throw Error('Unavailable or reversed range '+row.id+' '+lang);
     const body=project(data.querySelector('tei-body')),start=q.traditionalRangePoint(data,loc),end=next?q.traditionalRangePoint(data,next[lang]):null;
     const a=position(data,start),b=end?position(data,end):body.length,t=position(data,q.traditionalPoint(data,loc));
     const actual=project(view),reference=body.slice(a,b);
     if(a>=b||actual!==reference||!norm(actual.slice(t-a)).startsWith(norm(loc.anchor)))throw Error('Wrong Bamberg membership or incipit '+row.id+' '+lang);
     const domIDs=[...view.querySelectorAll('[id]')].map(n=>n.id);if(new Set(domIDs).size!==domIDs.length)throw Error('Duplicate rendered IDs');
     // Exact exclusive endpoint must belong to the next selection, not this one.
     if(end){const r=document.createRange();r.selectNode(end.node);const frag=r.cloneContents(),first=frag.firstElementChild;if(first?.id&&view.querySelector(`[id="${first.id}"]`))throw Error('Next prefix leaked '+row.id+' '+lang);}
     out.push({id:row.id,book:row.book,language:lang,start:loc.target,end:next?.[lang].target||'BOOK_END',startProjection:a,endProjection:b,firstNarrative:norm(actual.slice(t-a)).slice(0,120),textLength:actual.length,whole_membership:'PASS',exclusive_endpoint:'PASS',nonempty:'PASS',unique_DOM_ids:'PASS',result:'PASS'});
    }
   }
   return {ranges:out,coverage:{book:q.getState().bookNum,options:rows.length,radioDisabled:radio.disabled,selectorDisabled:selector.disabled,identities:ids,result:'PASS'}};
  },expected[book-1]);ranges.push(...checked.ranges);coverage.push(checked.coverage);
  // Exercise real dropdown listeners, next/previous buttons and URL parsing for every source ID.
  if(expected[book-1]){
   await page.check('#bamberg-level');await page.waitForFunction(()=>new URL(location.href).searchParams.has('bamberg'));
   const checks=await page.evaluate(async()=>{
    const q=window.__qa,rows=q.bambergRows(),out=[];
    const menu=document.querySelector('#bamberg-selector');
    for(const [i,row]of rows.entries()){
     menu.value=row.id;menu.dispatchEvent(new Event('change',{bubbles:true}));await window.__qaPending;
     const state=q.getState(),url=new URL(location.href);
     if(state.bambergId!==row.id||state.viewingLevel!=='bamberg-level'||url.searchParams.get('bamberg')!==String(Number(row.id.split('-row')[1])))throw Error('Bamberg URL identity');
     for(const key of ['chapter','subchapter','unit','niese'])if(url.searchParams.has(key))throw Error('Stale competing URL');
     if([...document.querySelectorAll('.structural-unavailable')].length)throw Error('Unavailable current range');
     if(document.querySelector('#bamberg-previous').disabled!==(i===0)||document.querySelector('#bamberg-next').disabled!==(i===rows.length-1))throw Error('Prev/next limits');
     // Manual URL parser round-trip, including unrelated state and fragment.
     history.replaceState({},'',`?book=${Number(state.bookNum)}&bamberg=${Number(row.id.split('-row')[1])}&extra=keep#preserved`);q.applyNavigationFromUrl();await q.reload();q.syncUrlFromState('replace');
     if(q.getState().bambergId!==row.id||!location.href.endsWith('#preserved')||new URL(location.href).searchParams.get('extra')!=='keep')throw Error('Round-trip changed identity or unrelated state');
     if(i+1<rows.length){document.querySelector('#bamberg-next').click();await window.__qaPending;if(q.getState().bambergId!==rows[i+1].id)throw Error('Next violates source order');document.querySelector('#bamberg-previous').click();await window.__qaPending;if(q.getState().bambergId!==row.id)throw Error('Previous violates source order');}
     const pane=document.querySelector('#greek-pane-select');for(let toggle=0;toggle<2;toggle++){pane.checked=!pane.checked;pane.dispatchEvent(new Event('change',{bubbles:true}));if(q.getState().bambergId!==row.id)throw Error('Pane toggle changes identity');}
     const ids=[...document.querySelectorAll('[id]')].map(n=>n.id);if(new Set(ids).size!==ids.length)throw Error('Duplicate page DOM IDs');
     out.push({id:row.id,selector:'PASS',URL_round_trip:'PASS',previous_next:'PASS',pane_switch:'PASS',DOM_ids:'PASS',result:'PASS'});
    }return out;
   });urls.push(...checks);
  }
  console.log('Bamberg',book,checked.ranges.length,'language ranges');
 }
 if(ranges.length!==594||urls.length!==198)throw Error('Global Bamberg QA totals');
 const pairIDs=[['LOEB-04-Chapter-5-0','B78-table1-row043'],['LOEB-13-Chapter-8-0','B78-table1-row079'],['LOEB-17-Chapter-6-0','B78-table1-row162'],['LOEB-17-Chapter-11-0','B78-table1-row171'],['LOEB-18-Chapter-8-0','B78-table1-row190'],['LOEB-19-Chapter-6-0','B78-table1-row198']];
 for(const [trad,bam]of pairIDs){const book=Number(trad.split('-')[1]);await open(`/antiquities/?book=${book}`);
  pairChecks.push(...await page.evaluate(({trad,bam})=>{
   const q=window.__qa,a=q.traditionalRegistry().find(r=>r.id===trad),b=q.bambergRegistry().find(r=>r.id===bam),checks=[];
   if(a['canonical-niese']!==b['canonical-niese'])throw Error('Pair Niese metadata mismatch');
   for(const lang of ['Latin','Greek','English']){const data=q.getData()[lang],x=q.traditionalPoint(data,a[lang]),y=q.traditionalPoint(data,b[lang]);if(x.node===y.node)throw Error('Collapsed same Niese physical positions');
    const views=[a,b].map(r=>q.traditionalRangeView(lang,data,r));if(views.some(v=>v.classList.contains('structural-unavailable')))throw Error('Pair not selectable');checks.push({traditional:trad,bamberg:bam,language:lang,niese:b['canonical-niese'],traditionalTarget:a[lang].target,bambergTarget:b[lang].target,bambergLabel:b['manuscript-label-as-recorded'],distinct_physical_points:'PASS',independent_selection:'PASS',result:'PASS'});
   }return checks;
  },{trad,bam}));
 }
 // Negative evidence is unavailable through ordinary interaction, not synthetic empty selections.
 for(let book=6;book<=11;book++){
  await open('/antiquities/?book=5&bamberg=B78-table1-row050');await page.selectOption('#book-selector',String(book).padStart(2,'0'));await page.evaluate(()=>window.__qaPending);
  await page.waitForFunction(b=>window.__qa.getState().bookNum===b&&window.__qa.getState().viewingLevel==='book-level',String(book).padStart(2,'0'));
  if(!await page.locator('#bamberg-level').isDisabled()||new URL(page.url()).searchParams.has('bamberg')||await page.locator('.structural-unavailable').count())throw Error('Negative evidence ordinary fallback');
  await page.selectOption('#book-selector','01');await page.evaluate(()=>window.__qaPending);await page.waitForFunction(()=>window.__qa.getState().bookNum==='01'&&!document.querySelector('#bamberg-level').disabled);
 }
 // Malformed and cross-book IDs remain explicit and never select nearby text.
 const invalid=[];for(const url of ['?book=13&bamberg=III','?book=6&bamberg=B78-table1-row005','?book=12&bamberg=','?book=1&bamberg=B78-table1-row079']){
  await open('/antiquities/'+url);if(await page.locator('.structural-unavailable').count()!==3)throw Error('Invalid Bamberg URL substituted text');invalid.push({url,result:'PASS'});
 }
 await open('/antiquities/?book=13&bamberg=B78-table1-row069&extra=keep#retained');
 // Choose actual duplicate-label records by registry data, not label arithmetic.
 const duplicate=await page.evaluate(()=>window.__qa.bambergRows().filter(r=>r['manuscript-label-as-recorded']==='III').map(r=>({id:r.id,label:r.display})));
 if(duplicate.length!==2||duplicate[0].label===duplicate[1].label)throw Error('Duplicate III labels not disambiguated');
 await page.selectOption('#bamberg-selector',duplicate[0].id);await page.waitForFunction(id=>new URL(location.href).searchParams.get('bamberg')===String(Number(id.split('-row')[1])),duplicate[0].id);
 await page.selectOption('#bamberg-selector',duplicate[1].id);await page.waitForFunction(id=>new URL(location.href).searchParams.get('bamberg')===String(Number(id.split('-row')[1])),duplicate[1].id);
 await page.reload();await page.waitForFunction(()=>window.__qaReady);if(await page.evaluate(()=>window.__qa.getState().bambergId)!==duplicate[1].id)throw Error('Duplicate reload identity');
 await page.goBack();await page.waitForFunction(id=>window.__qa.getState().bambergId===id,duplicate[0].id);await page.goForward();await page.waitForFunction(id=>window.__qa.getState().bambergId===id,duplicate[1].id);
 await page.locator('#bamberg-selector').focus();await page.keyboard.press('ArrowDown');await page.keyboard.press('Enter');await page.waitForTimeout(300);
 await page.evaluate(()=>window.__qaPending);const keyboard=await page.evaluate(()=>({selected:document.querySelector('#bamberg-selector').value,state:window.__qa.getState().bambergId,url:new URL(location.href).searchParams.get('bamberg')}));
 if(keyboard.selected!==keyboard.state||String(Number(keyboard.selected.split('-row')[1]))!==keyboard.url||keyboard.selected===duplicate[1].id)throw Error('Keyboard selection/state');
 if(report.errors.length)throw Error(JSON.stringify(report.errors));
 fs.writeFileSync(path.join(__dirname,'BAMBERG_RANGE_QA.json'),JSON.stringify({ranges,count:ranges.length,result:'PASS'},null,2));
 fs.writeFileSync(path.join(__dirname,'BAMBERG_URL_QA.json'),JSON.stringify({checks:urls,count:urls.length,negative_evidence_books:[6,7,8,9,10,11],invalid,duplicates:duplicate,history:'PASS',reload:'PASS',keyboard,result:'PASS'},null,2));
 fs.writeFileSync(path.join(__dirname,'SAME_NIESE_DIFFERENT_POSITION_QA.json'),JSON.stringify({checks:pairChecks,pairs:6,language_checks:18,result:'PASS'},null,2));
 fs.writeFileSync(path.join(__dirname,'BAMBERG_BROWSER_QA.json'),JSON.stringify({coverage,division_identities:198,language_displays:594,errors:report.errors,result:'PASS'},null,2));
 await browser.close();server.close();console.log('ALL_BAMBERG_BROWSER_QA_PASS');
})().catch(e=>{console.error(e);fs.writeFileSync(path.join(__dirname,'BAMBERG_BROWSER_FAILURE.json'),JSON.stringify({error:String(e)},null,2));server.close();process.exit(1);});
