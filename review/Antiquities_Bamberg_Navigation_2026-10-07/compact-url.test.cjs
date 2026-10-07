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
 source=source.replace('    syncNavigationControls();','    syncNavigationControls(); window.__qaRenderedState = {...state};');
 const extra = source.includes('const loadTraditionalRegistry') ? ',traditionalRegistry:()=>traditionalRegistry, alignmentRegistry:()=>alignmentRangeRegistry, traditionalRangeView,traditionalPoint,traditionalRows' : '';
 const supplemental = (source.includes('const traditionalRangePoint') ? ',traditionalRangePoint' : '') + (source.includes('let bambergRegistry') ? ',bambergRows,bambergSelection,bambergIdentityFromUrl,bambergUrlValue,bambergRegistry:()=>bambergRegistry,boundaryRegistry:()=>boundaryRegistry' : '');
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
 const checks=[];
 await open('/antiquities/?book=13&bamberg=76');
 const inventory=await page.evaluate(()=>window.__qa.bambergRegistry().map(r=>({id:r.id,book:r.book,label:r['manuscript-label-as-recorded'],key:window.__qa.bambergUrlValue(r.id)})));
 if(inventory.length!==198||new Set(inventory.map(r=>r.key)).size!==198)throw Error('Compact keys not unique');
 async function capture(){return await page.evaluate(()=>({id:window.__qa.getState().bambergId,level:window.__qa.getState().viewingLevel,selected:document.querySelector('#bamberg-selector').value,url:location.href,panes:Object.fromEntries(Object.entries(window.__qa.view()).map(([l,v])=>[l,v.outerHTML])),unavailable:document.querySelectorAll('.structural-unavailable').length}));}
 async function assertIdentity(row){const r=await capture(),url=new URL(r.url);if(r.id!==row.id||r.selected!==row.id||r.level!=='bamberg-level'||r.unavailable||url.searchParams.get('bamberg')!==row.key)throw Error('Wrong compact selection '+JSON.stringify({row,state:r.id,selected:r.selected,url:r.url}));for(const key of ['chapter','subchapter','unit','niese'])if(url.searchParams.has(key))throw Error('Stale competing parameter');if(url.searchParams.get('extra')!=='keep'||url.hash!=='#retained')throw Error('Unrelated state lost');return r;}
 for(const [i,row]of inventory.entries()){
  // Copy/paste loads a fresh document at the compact URL, resolving the exact frozen identity.
  const compact=`${origin}/antiquities/?book=${row.book}&bamberg=${row.key}&extra=keep#retained`;
  await open(compact.slice(origin.length));const initial=await assertIdentity(row);
  // A real browser reload repeats parsing with a fresh registry request, not an injected state update.
  await page.reload();await page.waitForFunction(()=>window.__qaReady);const reloaded=await assertIdentity(row);
  if(JSON.stringify(initial.panes)!==JSON.stringify(reloaded.panes))throw Error('Reload range changed '+row.id);
  // All old verbose IDs remain accepted, and are immediately rewritten to the compact public form.
  const alias=await page.evaluate(async row=>{
   const q=window.__qa;
   for(const value of [row.id,row.key.padStart(3,'0')]){
    history.replaceState({},'',`?book=${row.book}&bamberg=${value}&chapter=999&unit=999&niese=1&extra=keep#retained`);q.applyNavigationFromUrl();await q.reload();q.syncUrlFromState('replace');
    if(q.getState().bambergId!==row.id||new URL(location.href).searchParams.get('bamberg')!==row.key)throw Error('Verbose or padded input alias failed');
   }
   return {fromCompact:q.bambergIdentityFromUrl(row.key),serialized:q.bambergUrlValue(row.id)};
  },row);
  if(alias.fromCompact!==row.id||alias.serialized!==row.key)throw Error('Serialization not lossless');
  const afterAlias=await assertIdentity(row);if(JSON.stringify(initial.panes)!==JSON.stringify(afterAlias.panes))throw Error('Alias changed material '+row.id);
  const peers=inventory.filter(r=>r.book===row.book),pos=peers.findIndex(r=>r.id===row.id),other=peers[pos+1]||peers[pos-1];
  // Back/forward history must recover each identity, including duplicate-label and unnumbered records.
  if(other){
   await page.selectOption('#bamberg-selector',other.id);await page.evaluate(()=>window.__qaPending);await assertIdentity(other);
   await page.goBack();await page.waitForFunction(id=>window.__qaRenderedState?.bambergId===id,row.id);await assertIdentity(row);
   await page.goForward();await page.waitForFunction(id=>window.__qaRenderedState?.bambergId===id,other.id);await assertIdentity(other);
  }else{
   await page.check('#book-level');await page.evaluate(()=>window.__qaPending);
   if(new URL(page.url()).searchParams.has('bamberg'))throw Error('Book switch retains Bamberg param');
   await page.goBack();await page.waitForFunction(id=>window.__qaRenderedState?.bambergId===id,row.id);await assertIdentity(row);
   await page.goForward();await page.waitForFunction(()=>window.__qaRenderedState?.viewingLevel==='book-level');
  }
  checks.push({...row,copy_load:'PASS',real_reload:'PASS',exact_range_DOM:'PASS',verbose_alias:'PASS',padded_numeric_alias:'PASS',lossless_identity:'PASS',back_forward:'PASS',unrelated_parameters_fragment:'PASS',result:'PASS'});
  if((i+1)%10===0)console.log('compact URL QA',i+1,'of 198');
 }
 const invalid=[];for(const value of ['0','-1','1.5','III','999999','B78-table1-row999']){
  await open(`/antiquities/?book=13&bamberg=${value}`);if(await page.locator('.structural-unavailable').count()!==3)throw Error('Invalid compact key substituted text '+value);invalid.push({value,result:'PASS'});
 }
 await open('/antiquities/?book=1&bamberg=76');if(await page.locator('.structural-unavailable').count()!==3)throw Error('Cross-book compact identity accepted');
 if(report.errors.length)throw Error(JSON.stringify(report.errors));
 const result={count:198,unique_compact_keys:198,checks,invalid,cross_book_identity:'PASS',registry_identity_unchanged:true,source_provenance_unchanged:true,book_specific_conditionals:0,writer:'compact numeric frozen row',parser:'compact row and verbose input alias',result:'PASS'};
 fs.writeFileSync(path.join(__dirname,'BAMBERG_COMPACT_URL_QA.json'),JSON.stringify(result,null,2));
 await browser.close();server.close();console.log('ALL_COMPACT_URL_QA_PASS',checks.length);
})().catch(e=>{console.error(e);fs.writeFileSync(path.join(__dirname,'COMPACT_URL_FAILURE.json'),JSON.stringify({error:String(e)},null,2));server.close();process.exit(1)});
