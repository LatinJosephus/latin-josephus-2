const fs = require('fs');
const path = require('path');
const http = require('http');
const cp = require('child_process');
const crypto = require('crypto');
const {chromium} = require('C:/Users/Pollard_R/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root = path.resolve(__dirname, '../..');
const base = 'ad3158b7a86dea6997510b3de17f2e510c23367c';
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
  window.__qa = {cleanHTML, getState:()=>({...state}), getData:()=>fullData, view:()=>viewData, reload, setState, setChapterSelectOptions, setSectionSelectOptions, setNieseSelectOptions, currentIdBase, applyNavigationFromUrl, syncUrlFromState, selectView, canonicalNieseStartEntries${extra}${supplemental}, assign:patch=>Object.assign(state,patch)};\n  bookTitle.innerText = activeWork.title;`);
 source = source.replaceAll('setState(() => {', 'window.__qaPending = setState(() => {');
 return source.replace('  reload().then(() => {','  reload().then(() => {\n    document.querySelector("#collapse-settings")?.classList.add("show"); window.__qaReady = true;');
}
const buildRoot='C:/workspace/Antiquities-Niese-09-runtime-20261009/build/site';
const server=http.createServer((req,res)=>{
 const url=new URL(req.url,'http://localhost');
 if(url.pathname==='/__renderer.js'){
  res.setHeader('Content-Type','text/javascript');res.end(instrument(url.searchParams.has('baseline')?head:updated));return;
 }
 let target=path.resolve(buildRoot,'.'+decodeURIComponent(url.pathname));
 if(!target.startsWith(path.resolve(buildRoot)+path.sep)){res.statusCode=403;res.end();return;}
 if(fs.existsSync(target)&&fs.statSync(target).isDirectory())target=path.join(target,'index.html');
 if(!fs.existsSync(target)){res.statusCode=404;res.end();return;}
 if(target.endsWith('.html')){
  let html=fs.readFileSync(target,'utf8');
  html=html.replace(/src="[^"]*renderTei\.js[^"]*"/g,`src="/__renderer.js${url.searchParams.has('baseline')?'?baseline=1':''}"`);
  res.setHeader('Content-Type','text/html');res.end(html);return;
 }
 res.setHeader('Content-Type',target.endsWith('.xml')?'application/xml':target.endsWith('.js')?'text/javascript':target.endsWith('.css')?'text/css':'application/octet-stream');
 res.end(fs.readFileSync(target));
});
(async()=>{
 await new Promise(r=>server.listen(0,'127.0.0.1',r));
 const origin=`http://127.0.0.1:${server.address().port}`;
 const context=await chromium.launchPersistentContext('C:/workspace/Antiquities-Niese-09-runtime-20261009/profile-bellum',{headless:true, executablePath:"C:/Program Files/Google/Chrome/Application/chrome.exe"});
 const page=await context.newPage();
 page.on('pageerror',e=>(report.errors.push(String(e)),console.error('PAGEERROR',String(e))));
 async function open(route){await page.goto(origin+route,{waitUntil:"domcontentloaded"});await page.waitForFunction(()=>window.__qaReady,{},{timeout:60000});}
 {
  const checks=[];
  for(let book=1;book<=7;book++)for(const source of ['whiston','lodge1602']){
   const snapshots=[];
   for(const baseline of [true,false]){
    await open(`/bellum-judaicum/?book=${book}&english=${source}${baseline?'&baseline=1':''}`);
    snapshots.push(await page.evaluate(()=>{
     const q=window.__qa,full=q.getData(),samples=[];
     const capture=(key)=>samples.push([key,...Object.entries(full).map(([l,d])=>q.cleanHTML(q.selectView(l,d,q.currentIdBase())))]);
     capture('initial');
     // Capture whole-book citation identities before exercising chapter menus.
     // Each projection uses the full, un-clipped source.
     const niese=q.canonicalNieseStartEntries().map(e=>String(e.number));
     for(const n of niese){q.assign({viewingLevel:'niese-level',nieseNum:n,chapterNum:null,sectionNum:null});capture('niese:'+n);}
     const chapters=[...document.querySelector('#chapter-selector').options].filter(o=>o.value && o.value!=="contents").map(o=>o.value);
     for(const chapter of chapters){q.assign({viewingLevel:'chapter-level',chapterNum:chapter,sectionNum:null,nieseNum:null});capture('chapter:'+chapter);q.assign({viewingLevel:'section-level'});q.setSectionSelectOptions();for(const u of [...document.querySelector('#section-selector').options].filter(o=>o.value && o.value!=="contents").map(o=>o.value)){q.assign({sectionNum:u});capture('unit:'+chapter+':'+u);}}
     return {source:q.getState().sources.English,niese:niese.length,unique_Niese_identities:new Set(niese).size,chapters:chapters.length,samples};
    }));
   }
   if(JSON.stringify(snapshots[0])!==JSON.stringify(snapshots[1]))throw Error('Protected source regression '+book+' '+source);
   checks.push({work:'bellum-judaicum',book,source,chapters:snapshots[1].chapters,niese:snapshots[1].niese,unique_Niese_identities:snapshots[1].unique_Niese_identities,ranges:snapshots[1].samples.length,result:'PASS'});console.log('protected-source',book,source,'Niese',snapshots[1].niese,'ranges',snapshots[1].samples.length);
  }
  fs.writeFileSync(path.join(__dirname,'PROTECTED_SOURCE_GATE_QA.json'),JSON.stringify({checks,origin,result:'PASS'},null,2));await context.close();server.close();return;
 }
})().catch(e=>{console.error(e);fs.writeFileSync(path.join(__dirname,'BELLUM_SOURCE_FAILURE.json'),JSON.stringify({error:String(e),report},null,2));server.close();process.exit(1);});
