const fs=require('fs'),path=require('path'),http=require('http'),cp=require('child_process'),crypto=require('crypto');
const {chromium}=require('C:/Users/Pollard_R/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root=path.resolve(__dirname,'../..'),site='C:/Users/Pollard_R/AppData/Local/Temp/LatinJosephus-Greek-Capitula-v1.1-disposable-20261008';
const expected=JSON.parse(fs.readFileSync(path.join(__dirname,'CONTENTS_EXPECTATIONS.json'),'utf8'));
const baseline=cp.execFileSync('git',['--no-optional-locks','show','HEAD:assets/xml/source-contents.xml'],{cwd:root});
const renderer=fs.readFileSync(path.join(site,'assets/js/renderTei.js'),'utf8');
const report={result:'RUNNING',site,build:'Jekyll 4.4.1; responsive-image plugin omitted only from disposable build (missing rmagick); source config unchanged',checks:[],themes:[],interactions:[],screenshots:[],pageErrors:[],failedRequests:[]};
const server=http.createServer((req,res)=>{
 const u=new URL(req.url,'http://localhost');let target=path.resolve(site,'.'+decodeURIComponent(u.pathname));
 if(!target.startsWith(site.replaceAll('/',path.sep)+path.sep)){res.statusCode=403;res.end();return;}
 if(fs.existsSync(target)&&fs.statSync(target).isDirectory())target=path.join(target,'index.html');
 if(!fs.existsSync(target)){res.statusCode=404;res.end();return;}
 const ext=path.extname(target);res.setHeader('Content-Type',({'.html':'text/html','.xml':'application/xml','.js':'text/javascript','.css':'text/css','.otf':'font/otf','.woff2':'font/woff2','.png':'image/png','.svg':'image/svg+xml'})[ext]||'application/octet-stream');
 res.end(fs.readFileSync(target));
});
const save=()=>fs.writeFileSync(path.join(__dirname,'BUILT_SITE_BROWSER_QA.json'),JSON.stringify(report,null,2));
(async()=>{
 await new Promise(r=>server.listen(0,'127.0.0.1',r));const origin=`http://127.0.0.1:${server.address().port}`;
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 const context=await browser.newContext({viewport:{width:1690,height:1100},deviceScaleFactor:1});
 // Memory-only observation hooks; no production renderer changes.
 await context.route('**/assets/js/renderTei.js',route=>route.fulfill({contentType:'text/javascript',body:renderer.replace('  bookTitle.innerText = activeWork.title;','  window.__toc={state:()=>({...state}),reload,assign:p=>Object.assign(state,p)};\n  bookTitle.innerText = activeWork.title;').replaceAll('setState(() => {','window.__tocPending = setState(() => {').replace('  reload().then(() => {','  reload().then(() => {\n    window.__tocReady=true;')}));
 const page=await context.newPage();page.on('pageerror',e=>report.pageErrors.push(String(e)));page.on('requestfailed',r=>report.failedRequests.push({url:r.url(),error:r.failure()?.errorText}));
 async function open(route){await page.goto(origin+route,{waitUntil:'load',timeout:60000});await page.waitForFunction(()=>window.__tocReady,{},{timeout:60000});await page.evaluate(()=>document.fonts.ready);}
 async function settled(){await page.evaluate(()=>window.__tocPending);}
 async function snap(name){await page.evaluate(()=>window.scrollTo(0,0));await page.screenshot({path:path.join(__dirname,name)});report.screenshots.push(name);}
 const targets=[1,2,3,4,6,7,8,9,10];
 // Before screenshots: identical disposable site and renderer, base-commit registry only.
 await context.route('**/assets/xml/source-contents.xml',route=>route.fulfill({contentType:'application/xml',body:baseline}));
 for(const theme of ['light','dark'])for(const book of [1,2,7,9,10]){await open(`/antiquities/?book=${book}&view=contents`);await page.evaluate(t=>document.documentElement.dataset.theme=t,theme);await snap(`BEFORE_antiquities-${book}_${theme}.png`);}
 await context.unroute('**/assets/xml/source-contents.xml');
 for(const theme of ['light','dark'])for(const book of targets){
  await open(`/antiquities/?book=${book}&view=contents&extra=keep#retained`);await page.evaluate(t=>document.documentElement.dataset.theme=t,theme);
  const e=expected.find(r=>r.work==='antiquities'&&r.book===book&&r.language==='Greek');
  const data=await page.evaluate(e=>{
   const q=window.__toc.state();if(q.viewingLevel!=='contents-level')throw Error('Not contents mode');
   const options=[...document.querySelector('#chapter-selector').options];if(options[0].value!=='contents'||options[0].text!=='Table of contents')throw Error('TOC first');
   const n=document.querySelector('#greek .source-contents'),roots=[...n.children].filter(x=>x.localName.startsWith('tei-'));
   if(JSON.stringify(roots.map(n=>n.textContent))!==JSON.stringify(e.texts))throw Error('Exact source transcription mismatch '+e.book);
   const items=[...n.querySelectorAll('tei-list[type="capitula"] > tei-item')];
   if(JSON.stringify(items.map(i=>({label:i.querySelector('tei-label').textContent,text:i.textContent,n:i.getAttribute('n')})))!==JSON.stringify(e.entries))throw Error('Entry/label mismatch');
   if(n.querySelector('a'))throw Error('Speculative clickable target');
   const ids=[...document.querySelectorAll('[id]')].map(x=>x.id);if(new Set(ids).size!==ids.length)throw Error('Duplicate DOM IDs');
   const heading=n.querySelector('tei-head'),entry=items[0],label=entry.querySelector('tei-label');
   const style=el=>({family:getComputedStyle(el).fontFamily,size:getComputedStyle(el).fontSize,color:getComputedStyle(el).color});
   let surface=n;while(surface.parentElement&&getComputedStyle(surface).backgroundColor==='rgba(0, 0, 0, 0)')surface=surface.parentElement;
   if(n.scrollWidth>n.clientWidth+1||document.documentElement.scrollWidth>innerWidth+1)throw Error('Overflow');
   if(!document.fonts.check('18px "LJ Coelacanth"'))throw Error('Reading font unavailable');
   const latin=document.querySelector('#latin .source-contents'),english=document.querySelector('#english .source-contents');
   if(english.textContent!=='No source table of contents is available for this witness.')throw Error('Borrowed Whiston TOC');
   const latent=latin.textContent==='No source table of contents is available for this witness.'?'unavailable':'own source contents';
   if((e.book>=2&&e.book<=4)!==(latent==='own source contents'))throw Error('Latin availability changed');
   if(e.book===1&&n.querySelector('tei-p[type="general-proem"]'))throw Error('Narrative proem imported');
   return {entries:items.length,headings:[...n.querySelectorAll('tei-head')].map(x=>x.textContent),trailer:[...n.querySelectorAll('tei-trailer')].map(x=>x.textContent),heading:style(heading),entry:style(entry),label:style(label),background:getComputedStyle(surface).backgroundColor,latin:latent,english:'unavailable',overflow:false,duplicateIds:0};
  },e);
  const lum=c=>c.match(/[\d.]+/g).slice(0,3).map(Number).map(v=>{v/=255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4}).reduce((a,v,i)=>a+v*[.2126,.7152,.0722][i],0);
  const a=lum(data.entry.color),b=lum(data.background),contrast=(Math.max(a,b)+.05)/(Math.min(a,b)+.05);if(contrast<4.5)throw Error('Contrast '+book+' '+theme+' '+contrast);
  report.themes.push({book,theme,...data,contrast:Number(contrast.toFixed(2)),result:'PASS'});
  if([1,2,7,9,10].includes(book))await snap(`AFTER_antiquities-${book}_${theme}.png`);
  // Scroll to final entry: full list remains present, wraps naturally, no clipped content.
  await page.locator('#greek tei-item').last().scrollIntoViewIfNeeded();if(book===9||book===10)await page.screenshot({path:path.join(__dirname,`AFTER_antiquities-${book}_${theme}_last-entry.png`)});
  if(theme==='light'){
   const copied=page.url(),before=await page.locator('#greek .source-contents').textContent();await page.reload();await page.waitForFunction(()=>window.__tocReady);
   if(page.url()!==copied||await page.locator('#greek .source-contents').textContent()!==before)throw Error('URL reload');
   await page.evaluate(()=>document.querySelector('#collapse-settings').classList.add('show')); for(const pane of ['greek','english']){await page.uncheck(`#${pane}-pane-select`,{force:true});await page.check(`#${pane}-pane-select`,{force:true});if(page.url()!==copied)throw Error('Pane switching lost identity');}
   await page.evaluate(()=>document.querySelector('#collapse-settings').classList.add('show'));
   await page.selectOption('#chapter-selector','1');await settled();if(new URL(page.url()).searchParams.has('view'))throw Error('TOC to Chapter');
   await page.selectOption('#chapter-selector','contents');await settled();if(new URL(page.url()).searchParams.get('view')!=='contents')throw Error('Chapter to TOC');
   await page.goBack();await page.waitForFunction(()=>window.__toc.state().viewingLevel==='chapter-level');await page.goForward();await page.waitForFunction(()=>window.__toc.state().viewingLevel==='contents-level');
   const url=new URL(page.url());for(const key of ['chapter','subchapter','bamberg','niese','unit'])if(url.searchParams.has(key))throw Error('Stale structural parameter');if(url.searchParams.get('extra')!=='keep'||url.hash!=='#retained')throw Error('Lost unrelated state');
   report.interactions.push({book,copy_reload:'PASS',panes:'PASS',chapter_to_contents:'PASS',contents_to_chapter:'PASS',history:'PASS',clean_url:'PASS'});
  }
  report.checks.push({book,theme,source:'niese',result:'PASS'});save();console.log('built-site Greek contents',book,theme,data.entries);
 }
 // All 30 pre-existing source records, including Greek V and XI-XX, remain exact in the reader.
 for(const e of expected.filter(r=>!targets.includes(Number(r.book))||r.work!=='antiquities'||r.language!=='Greek')){
  const work=e.work==='bellum'?'bellum-judaicum':e.work;await open(`/${work}/?book=${e.book}&view=contents&${e.language.toLowerCase()}=${e.witness}`);
  const data=await page.locator(`#${e.language.toLowerCase()} .source-contents`).evaluate(n=>({texts:[...n.children].filter(x=>x.localName.startsWith('tei-')).map(x=>x.textContent),supplements:[...n.querySelectorAll('tei-supplied')].map(x=>x.textContent)}));
  if(JSON.stringify(data.texts)!==JSON.stringify(e.texts)||JSON.stringify(data.supplements)!==JSON.stringify(e.supplements))throw Error('Existing TOC regression '+e.id);
  report.checks.push({id:e.id,existing_contents_exact:'PASS'});console.log('existing',e.id);
 }
 await open('/antiquities/?book=1&view=contents');await page.evaluate(()=>document.querySelector('#collapse-settings').classList.add('show'));
 for(let b=2;b<=20;b++){await page.selectOption('#book-selector',String(b).padStart(2,'0'));await settled();if(new URL(page.url()).searchParams.get('view')!=='contents')throw Error('Book switching lost TOC '+b);}
 report.book_switching_20_books='PASS';
 await open('/antiquities/?book=9&chapter=1');await page.evaluate(()=>document.querySelector('#collapse-settings').classList.add('show'));await page.locator('#chapter-selector').focus();await page.keyboard.press('Home');await page.keyboard.press('Enter');await settled();if(new URL(page.url()).searchParams.get('view')!=='contents')throw Error('Keyboard');report.keyboard='PASS';
 for(const book of [8,9,10]){await open(`/antiquities/?book=${book}&view=contents`);if(!await page.locator('#niese-level').isDisabled())throw Error('Niese inadvertently enabled '+book);}report.niese_VIII_X_disabled='PASS';
 if(report.pageErrors.length)throw Error(JSON.stringify(report.pageErrors));report.result='PASS';report.new_books=9;report.new_entries=109;report.theme_displays=18;report.existing_records=30;save();
 await browser.close();server.close();console.log('BUILT_SITE_TOC_QA_PASS');
})().catch(e=>{report.result='FAIL';report.failure=String(e);save();console.error(e);server.close();process.exit(1)});
