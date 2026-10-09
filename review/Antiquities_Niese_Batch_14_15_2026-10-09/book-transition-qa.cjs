const fs=require('fs'),path=require('path'),http=require('http'),crypto=require('crypto');
const {chromium}=require('C:/Users/Pollard_R/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root=path.resolve(__dirname,'../..'),runtime='C:/workspace/Antiquities-Niese-14-15-runtime-20261009',site=path.join(runtime,'build5/site');
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
const instrument=s=>s.replace('  bookTitle.innerText = activeWork.title;','  window.__qa={getState:()=>({...state})};\n  bookTitle.innerText = activeWork.title;').replace('    syncNavigationControls();','    syncNavigationControls();window.__qaRenderedState={...state};').replace('  reload().then(() => {','  reload().then(() => {window.__qaReady=true;document.querySelector("#collapse-settings")?.classList.add("show");');
async function main(){
 const result={status:'PENDING',local_build:site,registry_injected:false,transitions:[],errors:[]};
 const server=http.createServer((req,res)=>{let f=path.resolve(site,'.'+decodeURIComponent(new URL(req.url,'http://localhost').pathname));if(!f.startsWith(path.resolve(site)+path.sep)){res.statusCode=403;return res.end();}if(fs.existsSync(f)&&fs.statSync(f).isDirectory())f=path.join(f,'index.html');if(!fs.existsSync(f)){res.statusCode=404;return res.end();}let raw=fs.readFileSync(f);if(f.endsWith('renderTei.js'))raw=Buffer.from(instrument(raw.toString()));res.setHeader('Content-Type',f.endsWith('.xml')?'application/xml':f.endsWith('.json')?'application/json':f.endsWith('.js')?'text/javascript':f.endsWith('.html')?'text/html':f.endsWith('.css')?'text/css':f.endsWith('.svg')?'image/svg+xml':'application/octet-stream');res.end(raw);});
 await new Promise((resolve,reject)=>{server.once('error',reject);server.listen(8914,'127.0.0.1',resolve);});
 const browser=await chromium.launchPersistentContext(path.join(runtime,'browser-transition-build5'),{headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'}),page=await browser.newPage();
 page.on('pageerror',e=>result.errors.push(String(e)));page.on('console',m=>{if(m.type()==='error')result.errors.push(m.text());});page.on('requestfailed',r=>result.errors.push(r.url()));
 try{
  await page.goto('http://127.0.0.1:8914/antiquities/?book=14&niese=491');await page.waitForFunction(()=>window.__qaReady);for(const l of ['greek','english'])await page.check(`#${l}-pane-select`);
  for(const b of [15,14]){
   await page.selectOption('#book-selector',String(b));await page.waitForFunction(b=>window.__qaRenderedState?.bookNum===String(b)&&window.__qaRenderedState.viewingLevel==='book-level',b);
   const cleared=await page.evaluate(()=>window.__qa.getState().nieseNum);if(cleared!==null)throw Error('Stale Niese selection after book switch');
   await page.check('#level-select input[value="niese-level"]');await page.waitForFunction(b=>window.__qaRenderedState?.bookNum===String(b)&&window.__qaRenderedState.nieseNum==='1'&&document.querySelector('#latin [type="niese-section"][n="1"]')&&document.querySelector('#greek [type="niese-section"][n="1"]'),b);
   const v=await page.evaluate(()=>({menu:[...document.querySelector('#niese-selector').options].filter(o=>o.value).map(o=>Number(o.value)),Greek:document.querySelector('#greek').textContent,Latin:document.querySelector('#latin').textContent,url:location.href}));
   if(v.menu.length!==(b===14?491:425)||v.menu[0]!==1||!v.url.includes('niese=1'))throw Error('Book reset menu');
   const roman=b===14?'XIV':'XV',opening=JSON.parse(fs.readFileSync(path.join(root,`review/Antiquities_Niese_Book${roman}_2026-10-09/EXPECTED_REVIEWED_INTERVALS.json`))).find(e=>e.number===1).text.replace(/\s+/g,' ').trim();
   if(!v.Latin.replace(/\s+/g,' ').includes(opening))throw Error('Wrong book opening '+JSON.stringify({book:b,Latin:v.Latin,expected:opening}));
   result.transitions.push({toBook:b,old_identity_cleared:true,opening_reset_to:1,selectable:v.menu.length,url:v.url,result:'PASS'});
  }
  if(result.errors.length)throw Error('Browser errors');result.renderer_sha256=sha(fs.readFileSync(path.join(site,'assets/js/renderTei.js')));result.status='PASS';
 }catch(e){result.status='FAIL';result.failure=String(e);throw e;}finally{fs.writeFileSync(path.join(__dirname,'BOOK_XIV_XV_TRANSITION_READER_QA.json'),JSON.stringify(result,null,2)+'\n');console.log('XIV/XV book transition',result.status);await browser.close();await new Promise(r=>server.close(r));}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
