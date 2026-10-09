const fs = require('fs');
const path = require('path');
const http = require('http');
const cp = require('child_process');
const crypto = require('crypto');
const {chromium} = require('C:/Users/Pollard_R/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root = path.resolve(__dirname, '../..');
const base = 'f393fa1223b38d9ca114e583fcc57d5e34425815';
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
 return source.replace('  reload().then(() => {','  reload().then(() => {\n    document.querySelector("#collapse-settings")?.classList.add("show"); window.__qaReady = true;');
}
const buildRoot='C:/workspace/Antiquities-Niese-Batch-08-10/local-build-current/site';
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
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 const page=await browser.newPage();const errors=[];page.on('pageerror',e=>errors.push(String(e)));
 const checks=[];
 for(const book of [8,9,10]){
  await page.goto(`${origin}/antiquities/?book=${book}&niese=1`);
  await page.waitForFunction(()=>window.__qaReady);
  const inspect=()=>page.evaluate(()=>({state:window.__qa.getState(),disabled:document.querySelector('#niese-level').disabled,visible:document.querySelector('#niese-level').getBoundingClientRect().height>0,ids:[...document.querySelectorAll('#Greek [id],#Latin [id],#English [id],#greek [id],#latin [id],#english [id]')].map(n=>n.id),UI_duplicate_annotations:[...document.querySelectorAll('#annotations')].map(n=>n.outerHTML.slice(0,150))}));
  let x=await inspect();if(!x.disabled||x.state.nieseNum!==null||x.state.viewingLevel==='niese-level')throw Error('Unsupported Niese mode enabled '+book);
  if(new Set(x.ids).size!==x.ids.length)throw Error('Duplicate DOM ids in fallback '+book+' '+JSON.stringify(x.ids.filter((id,i)=>x.ids.indexOf(id)!==i)));
  await page.reload();await page.waitForFunction(()=>window.__qaReady);x=await inspect();if(!x.disabled||x.state.nieseNum!==null)throw Error('Unsupported reload '+book);
  checks.push({book,existing_UI_duplicate_annotations:x.UI_duplicate_annotations,deep_link_fallback:'PASS',reload:'PASS',no_duplicate_text_pane_DOM_ids:'PASS',niese_enabled:false});
 }
 await page.goto(`${origin}/antiquities/?book=7&niese=100`);await page.waitForFunction(()=>window.__qaReady);
 if(await page.locator('#niese-level').isDisabled())throw Error('Certified VII disabled');
 const active=await page.evaluate(()=>window.__qa.getState());if(String(active.nieseNum)!=='100')throw Error('Certified VII identity');
 await page.selectOption('#book-selector','9');await page.evaluate(()=>window.__qaPending);
 if(!await page.locator('#niese-level').isDisabled())throw Error('IX enabled after switching');
 await page.selectOption('#book-selector','7');await page.evaluate(()=>window.__qaPending);
 if(await page.locator('#niese-level').isDisabled())throw Error('VII not restored');
 await page.check('#niese-level',{force:true});await page.evaluate(()=>window.__qaPending);
 await page.selectOption('#niese-selector','100');await page.evaluate(()=>window.__qaPending);
 if(await page.evaluate(()=>String(window.__qa.getState().nieseNum))!=='100')throw Error('VII selection restoration');
 for(const theme of ['light','dark']){await page.evaluate(t=>document.documentElement.dataset.theme=t,theme);if(await page.locator('#niese-selector').isDisabled())throw Error('Theme Niese control');}
 if(errors.length)throw Error(JSON.stringify(errors));
 fs.writeFileSync(path.join(__dirname,'AVAILABILITY_CURRENT_BASELINE_QA.json'),JSON.stringify({checks,switch_VII_IX_VII:'PASS',light_dark:'PASS',new_book_exact_Niese_QA:'NOT_RUN: neither book certified or enabled',result:'PASS'},null,2));
 await browser.close();server.close();console.log('AVAILABILITY_PASS');
})().catch(e=>{console.error(e);server.close();process.exit(1)});
