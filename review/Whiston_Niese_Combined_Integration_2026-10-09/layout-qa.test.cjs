const fs=require('fs'),path=require('path'),http=require('http');
const {chromium}=require('C:/Users/Pollard_R/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root=path.resolve(__dirname,'../..'),site='C:/Users/POLLAR~1/AppData/Local/Temp/LatinJosephus-Whiston-Niese-Combined-disposable-20261009';
const expected=JSON.parse(fs.readFileSync(path.join(__dirname,'CONTENTS_EXPECTATIONS.json'),'utf8')),existing=JSON.parse(fs.readFileSync(path.join(__dirname,'EXISTING_CONTENTS_EXPECTATIONS.json'),'utf8'));
const renderer=fs.readFileSync(path.join(site,'assets/js/renderTei.js'),'utf8');
const report={result:'RUNNING',site,checks:[],interactions:[],existing:[],screenshots:[],pageErrors:[],failedRequests:[]};
const capture=path.join(__dirname,'screenshots');
const save=()=>fs.writeFileSync(path.join(__dirname,process.argv.includes('--before')?'BEFORE_QA.json':'LAYOUT_QA.json'),JSON.stringify(report,null,2));
const server=http.createServer((req,res)=>{const u=new URL(req.url,'http://localhost');let target=path.resolve(site,'.'+decodeURIComponent(u.pathname));if(!target.startsWith(site.replaceAll('/',path.sep)+path.sep)){res.statusCode=403;res.end();return;}if(fs.existsSync(target)&&fs.statSync(target).isDirectory())target=path.join(target,'index.html');if(!fs.existsSync(target)){res.statusCode=404;res.end();return;}res.setHeader('Content-Type',({'.html':'text/html','.xml':'application/xml','.js':'text/javascript','.css':'text/css','.otf':'font/otf','.woff2':'font/woff2','.svg':'image/svg+xml','.png':'image/png'})[path.extname(target)]||'application/octet-stream');res.end(fs.readFileSync(target));});
(async()=>{
 await new Promise(r=>server.listen(0,'127.0.0.1',r));const origin=`http://127.0.0.1:${server.address().port}`;const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});const context=await browser.newContext({viewport:{width:1690,height:1100},deviceScaleFactor:1});
 await context.route('**/assets/js/renderTei.js',route=>route.fulfill({contentType:'text/javascript',body:renderer.replace('  bookTitle.innerText = activeWork.title;','  window.__toc={state:()=>({...state}),reload,assign:p=>Object.assign(state,p)};\n  bookTitle.innerText = activeWork.title;').replaceAll('setState(() => {','window.__tocPending = setState(() => {').replace('  reload().then(() => {','  reload().then(() => {\n    window.__tocReady=true;')}));
 const page=await context.newPage();page.on('pageerror',e=>report.pageErrors.push(String(e)));page.on('requestfailed',r=>report.failedRequests.push({url:r.url(),error:r.failure()?.errorText}));
 async function open(route){await page.goto(origin+route,{waitUntil:'load',timeout:60000});await page.waitForFunction(()=>window.__tocReady,{},{timeout:60000});await page.evaluate(()=>document.fonts.ready);}
 async function settle(){await page.evaluate(()=>window.__tocPending);}
 async function snap(name){await page.evaluate(()=>scrollTo(0,0));await page.screenshot({path:path.join(capture,name)});report.screenshots.push(name);}
 const before=process.argv.includes('--before');report.stage=before?'before':'after';report.entryChecks=0;report.wrappedEntries=0;report.wrappedLineChecks=0;
 for(const width of [1690,1200])for(const theme of ['light','dark'])for(const e of before?expected.filter(x=>[3,12].includes(x.book)):expected){
  await page.setViewportSize({width,height:1100});await open(`/antiquities/?book=${e.book}&view=contents`);await page.evaluate(t=>document.documentElement.dataset.theme=t,theme);await page.waitForTimeout(1200);
  const info=await page.evaluate(({e,before,width})=>{
   const n=document.querySelector('#english .source-contents'),list=n.querySelector('tei-list'),items=[...list.querySelectorAll(':scope > tei-item')],labels=[...list.querySelectorAll(':scope > tei-label')];
   if(items.length!==e.entries||JSON.stringify(labels.map(x=>x.textContent))!==JSON.stringify(e.labels))throw Error('Count/order');
   if(JSON.stringify(items.map(x=>x.querySelector('tei-reg').textContent))!==JSON.stringify(e.displayHeadings))throw Error('Display wording changed');
   if(items.some(x=>x.innerText!==x.querySelector('tei-reg').textContent||getComputedStyle(x.querySelector('tei-orig')).display!=='none'))throw Error('Original displayed twice');
   const notes=n.querySelectorAll('tei-note[subtype=provenance]');if(notes.length!==1||n.querySelector('.source-contents-note')||notes[0].previousElementSibling!==n.querySelector('tei-head'))throw Error('Attribution');
   const children=[...list.children];if(children.length!==2*e.entries||children.some((x,i)=>x.localName!==(i%2?'tei-item':'tei-label')))throw Error('Unexpected pairing');
   const first=x=>{const walk=document.createTreeWalker(x,NodeFilter.SHOW_TEXT);let t;while(t=walk.nextNode()){if(t.textContent.trim()){const r=document.createRange();r.setStart(t,0);r.setEnd(t,1);return r.getBoundingClientRect().toJSON();}}throw Error('Empty');};
   const entries=items.map((item,i)=>{
    const reg=item.querySelector('tei-reg'),a=first(labels[i]),b=first(reg),box=item.getBoundingClientRect(),r=document.createRange();r.selectNodeContents(reg);const rects=[...r.getClientRects()].filter(x=>x.width>.01&&x.height>0),lines=[];
    for(const q of rects){let line=lines.find(x=>Math.abs(x.y-q.y)<1);if(!line){line={y:q.y,left:q.x,right:q.right};lines.push(line);}else{line.left=Math.min(line.left,q.x);line.right=Math.max(line.right,q.right);}}
    lines.sort((x,y)=>x.y-y.y);const delta=Math.abs(a.y-b.y),gap=b.x-labels[i].getBoundingClientRect().right;
    if(!before){
     if(getComputedStyle(list).display!=='grid'||delta>1)throw Error(`Different numeral/heading line ${e.book}.${i+1}: ${delta}`);
     if(gap<4||gap>12)throw Error('Nonmodest/overlapping numeral gap '+gap);
     if(lines.some(x=>Math.abs(x.left-b.x)>1||x.right>box.right+1))throw Error(`Hanging indent/overflow ${e.book}.${i+1}`);
     if(getComputedStyle(item).textAlign!=='left'||!getComputedStyle(item).fontFamily.includes('LJ Coelacanth'))throw Error('Typography');
     if(i&&labels[i].getBoundingClientRect().top<items[i-1].getBoundingClientRect().bottom+2)throw Error('Overlapping rows');
    }
    return {chapter:i+1,numeral:labels[i].textContent,display:reg.textContent,lines:lines.length,numeralHeadingYDelta:delta,gap,hangingLineLefts:lines.map(x=>x.left-b.x)};
   });
   if(n.scrollWidth>n.clientWidth+1||document.documentElement.scrollWidth>innerWidth+1)throw Error('Page/pane overflow');
   const ids=[...document.querySelectorAll('[id]')].map(x=>x.id);if(ids.length!==new Set(ids).size)throw Error('Duplicate DOM IDs');
   const above=[...n.querySelectorAll('tei-div > tei-head,tei-div > tei-p')].map(x=>({text:x.innerText,display:getComputedStyle(x).display,fontFamily:getComputedStyle(x).fontFamily,fontSize:getComputedStyle(x).fontSize,textAlign:getComputedStyle(x).textAlign,top:x.getBoundingClientRect().top}));
   if(above.filter(x=>x.text.startsWith('Book')).length!==1||JSON.stringify(above.filter(x=>x.text.startsWith('Containing')||x.text.startsWith('From')).map(x=>x.text))!==JSON.stringify(e.summaries))throw Error('Separate book/interval material changed');
   if(width===1200&&items[0].clientWidth>350)throw Error('Not a narrow pane');
   return {book:e.book,entries,above,itemWidth:items[0].clientWidth,listDisplay:getComputedStyle(list).display,singleNote:true,duplicateIds:0,overflow:0};
  },{e,before,width});
  report.checks.push({width,theme,...info,result:'PASS'});report.entryChecks+=info.entries.length;report.wrappedEntries+=info.entries.filter(x=>x.lines>1).length;report.wrappedLineChecks+=info.entries.reduce((n,x)=>n+Math.max(0,x.lines-1),0);console.log(report.stage,e.book,width,theme,info.entries.length);save();
  if([3,12].includes(e.book)){
   const stage=before?'BEFORE':'AFTER';await snap(`${stage}_Book-${e.book}_${theme}_${width}.png`);
   await page.locator(`#english tei-item[n="${e.book===3?15:3}"]`).scrollIntoViewIfNeeded();const name=`${stage}_Book-${e.book}_long_${theme}_${width}.png`;await page.screenshot({path:path.join(capture,name)});report.screenshots.push(name);save();
  }
 }
 if(report.pageErrors.length||report.failedRequests.length)throw Error('Browser errors');report.result='PASS';report.books=before?2:20;report.uniqueEntries=before?26:256;report.themes=2;report.widths=[1690,1200];save();await browser.close();server.close();console.log('WHISTON_LAYOUT_PASS',report.stage,report.entryChecks,report.wrappedLineChecks);
})().catch(e=>{report.result='FAIL';report.failure=String(e);save();console.error(e);server.close();process.exit(1)});
