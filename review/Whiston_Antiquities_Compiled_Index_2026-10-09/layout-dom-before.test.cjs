const fs=require('fs'),path=require('path'),http=require('http');
const {chromium}=require('C:/Users/Pollard_R/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root=path.resolve(__dirname,'../..'),site='C:/Users/Pollard_R/AppData/Local/Temp/LatinJosephus-Whiston-Index-disposable-20261009';
const expected=JSON.parse(fs.readFileSync(path.join(__dirname,'CONTENTS_EXPECTATIONS.json'),'utf8')),existing=JSON.parse(fs.readFileSync(path.join(__dirname,'EXISTING_CONTENTS_EXPECTATIONS.json'),'utf8'));
const renderer=fs.readFileSync(path.join(site,'assets/js/renderTei.js'),'utf8');
const report={result:'RUNNING',site,checks:[],interactions:[],existing:[],screenshots:[],pageErrors:[],failedRequests:[]};
const capture=path.join(__dirname,'layout-correction');
const save=()=>fs.writeFileSync(path.join(__dirname,'layout-correction/DOM_BEFORE_QA.json'),JSON.stringify(report,null,2));
const server=http.createServer((req,res)=>{const u=new URL(req.url,'http://localhost');let target=path.resolve(site,'.'+decodeURIComponent(u.pathname));if(!target.startsWith(site.replaceAll('/',path.sep)+path.sep)){res.statusCode=403;res.end();return;}if(fs.existsSync(target)&&fs.statSync(target).isDirectory())target=path.join(target,'index.html');if(!fs.existsSync(target)){res.statusCode=404;res.end();return;}res.setHeader('Content-Type',({'.html':'text/html','.xml':'application/xml','.js':'text/javascript','.css':'text/css','.otf':'font/otf','.woff2':'font/woff2','.svg':'image/svg+xml','.png':'image/png'})[path.extname(target)]||'application/octet-stream');res.end(fs.readFileSync(target));});
(async()=>{
 await new Promise(r=>server.listen(0,'127.0.0.1',r));const origin=`http://127.0.0.1:${server.address().port}`;const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});const context=await browser.newContext({viewport:{width:1690,height:1100},deviceScaleFactor:1});
 await context.route('**/assets/js/renderTei.js',route=>route.fulfill({contentType:'text/javascript',body:renderer.replace('  bookTitle.innerText = activeWork.title;','  window.__toc={state:()=>({...state}),reload,assign:p=>Object.assign(state,p)};\n  bookTitle.innerText = activeWork.title;').replaceAll('setState(() => {','window.__tocPending = setState(() => {').replace('  reload().then(() => {','  reload().then(() => {\n    window.__tocReady=true;')}));
 const page=await context.newPage();page.on('pageerror',e=>report.pageErrors.push(String(e)));page.on('requestfailed',r=>report.failedRequests.push({url:r.url(),error:r.failure()?.errorText}));
 async function open(route){await page.goto(origin+route,{waitUntil:'load',timeout:60000});await page.waitForFunction(()=>window.__tocReady,{},{timeout:60000});await page.evaluate(()=>document.fonts.ready);}
 async function settle(){await page.evaluate(()=>window.__tocPending);}
 async function snap(name){await page.evaluate(()=>scrollTo(0,0));await page.screenshot({path:path.join(capture,name)});report.screenshots.push(name);}
 await open('/antiquities/?book=12&view=contents');await page.waitForTimeout(900);
 report.probe=await page.locator('#english .source-contents tei-list').evaluate(n=>({tag:n.localName,attributes:[...n.attributes].map(x=>[x.name,x.value]),children:[...n.children].slice(0,4).map(x=>({tag:x.localName,text:x.innerText,display:getComputedStyle(x).display,margin:getComputedStyle(x).margin,lineHeight:getComputedStyle(x).lineHeight,fontFamily:getComputedStyle(x).fontFamily,rect:x.getBoundingClientRect().toJSON()})),display:getComputedStyle(n).display}));
 report.result='PASS';save();await browser.close();server.close();console.log(JSON.stringify(report.probe,null,2));
})().catch(e=>{report.result='FAIL';report.failure=String(e);save();console.error(e);server.close();process.exit(1)});
