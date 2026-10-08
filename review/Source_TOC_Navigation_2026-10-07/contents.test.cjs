const fs = require('fs');
const path = require('path');
const http = require('http');
const cp = require('child_process');
const crypto = require('crypto');
const {chromium} = require('C:/Users/Pollard_R/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root = path.resolve(__dirname, '../..');
const base = '087c0bf651037d83c5156495836510d250bdcf09';
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
 const expected=JSON.parse(fs.readFileSync(path.join(__dirname,'CONTENTS_EXPECTATIONS_2026-10-08.json'),'utf8'));
 const checks=[],interactions=[],themes=[];
 const availability={antiquities:{Latin:'bamberg78',English:'whiston',Greek:'niese'},'bellum-judaicum':{Latin:'cardwell',English:'whiston',Greek:'niese'},deh:{Latin:'ussani',English:'pollard'},'contra-apionem':{Latin:'boysen',English:'whiston',Greek:'niese'}};
 for(const [work,count]of [['antiquities',20],['bellum-judaicum',7],['contra-apionem',2],['deh',5]])for(let book=1;book<=count;book++){
  await open(`/${work}/?book=${book}&view=contents&extra=keep#retained`);
  const slug=work==='bellum-judaicum'?'bellum':work;
  const known=expected.filter(r=>r.work===slug&&Number(r.book)===book);
  const result=await page.evaluate(({known,availability,work})=>{
   const q=window.__qa,state=q.getState(),options=[...document.querySelector('#chapter-selector').options];
   if(state.viewingLevel!==(known.length?'contents-level':'book-level'))throw Error('Book availability/fallback');
   if(known.length&&(!document.querySelector('#annotations').hidden||document.querySelector('#annotations-list').textContent))throw Error('Narrative annotations leak into contents');
   if(known.length&&(options[0].value!=='contents'||options[0].text!=='Table of contents'))throw Error('TOC not first');
   if(!known.length&&options.some(o=>o.value==='contents'))throw Error('Synthetic unverified TOC option');
   const out=[];
   for(const [language,witness]of Object.entries(availability[work])){
    const row=known.find(r=>r.language===language&&r.witness===witness);
    const wrapper=document.querySelector('#'+language.toLowerCase()+' .source-contents');
    if(known.length){
     if(!wrapper)throw Error('Missing pane contents/unavailability state');
     if(!row&&wrapper.textContent!=='No source table of contents is available for this witness.')throw Error('Borrowed source contents');
     if(row){
      const roots=[...wrapper.children].filter(n=>n.localName.startsWith('tei-'));
      if(JSON.stringify(roots.map(n=>n.textContent))!==JSON.stringify(row.texts))throw Error('Source text mismatch '+row.id+' '+JSON.stringify({expected:row.texts,actual:roots.map(n=>n.textContent)}));
      if(JSON.stringify([...wrapper.querySelectorAll('tei-supplied')].map(n=>n.textContent))!==JSON.stringify(row.supplements))throw Error('Supplement mismatch');
      if(wrapper.querySelector('a'))throw Error('Inferred TOC links');
     }
    }
    out.push({work,book:Number(state.bookNum),language,witness,verified:Boolean(row),contentsView:!!known.length,result:'PASS'});
   }
   const ids=[...document.querySelectorAll('[id]')].map(n=>n.id);const duplicates=ids.filter((x,i)=>ids.indexOf(x)!==i);if(known.length&&duplicates.length)throw Error('Duplicate contents DOM IDs '+duplicates);out.forEach(c=>c.preexistingBookDuplicates=duplicates);
   if(!location.href.endsWith('#retained')||new URL(location.href).searchParams.get('extra')!=='keep')throw Error('Lost unrelated state');
   return out;
  },{known,availability,work});checks.push(...result);
  if(result[0].preexistingBookDuplicates.length){await open(`/${work}/?book=${book}&baseline=1`);const d=await page.evaluate(()=>{const ids=[...document.querySelectorAll('[id]')].map(n=>n.id);return ids.filter((x,i)=>ids.indexOf(x)!==i)});if(JSON.stringify(d)!==JSON.stringify(result[0].preexistingBookDuplicates))throw Error('New duplicate IDs in Book fallback');}
  // The alternate Lodge witness has its own contents and never borrows Whiston.
  if(work==='bellum-judaicum'){
   await page.selectOption('#english-source-selector','lodge1602');await page.evaluate(()=>window.__qaPending);
   if(!known.length)throw Error('Lodge eligibility');
   const row=known.find(r=>r.witness==='lodge1602');
   if(await page.locator('#chapter-selector').inputValue()!=='contents')throw Error('Source switch lost contents');
   const texts=await page.locator('#english .source-contents').evaluate(n=>[...n.children].filter(x=>x.localName.startsWith('tei-')).map(x=>x.textContent));
   if(JSON.stringify(texts)!==JSON.stringify(row.texts))throw Error('Lodge source text mismatch '+book);
   checks.push({work,book,language:'English',witness:'lodge1602',verified:true,contentsView:true,textEquality:'PASS',result:'PASS'});
  }
  console.log('contents',work,book,known.length);
 }
 if(checks.length!==104)throw Error('Incomplete 104 source-combination matrix');
 // Real dropdown, reload and browser history for every supported book/witness.
 for(const row of expected){
  const work=row.work==='bellum'?'bellum-judaicum':row.work;
  const route=`/${work}/?book=${row.book}&chapter=1&${row.language.toLowerCase()}=${row.witness}&extra=keep#retained`;
  await open(route);
  const numberedBefore=await page.locator('#chapter-selector option').evaluateAll(ns=>ns.filter(n=>n.value&&n.value!=='contents').map(n=>[n.value,n.text]));
  await page.selectOption('#chapter-selector','contents');await page.evaluate(()=>window.__qaPending);
  let url=new URL(page.url());if(url.searchParams.get('view')!=='contents'||url.searchParams.has('chapter'))throw Error('Contents URL write');
  for(const key of ['subchapter','bamberg','niese','unit'])if(url.searchParams.has(key))throw Error('Conflicting contents URL');
  const before=await page.locator('.source-contents').allTextContents();
  const copied=page.url();await page.reload();await page.waitForFunction(()=>window.__qaReady);
  if(page.url()!==copied||JSON.stringify(await page.locator('.source-contents').allTextContents())!==JSON.stringify(before))throw Error('Copied/reloaded contents');
  const pane=page.locator('#greek-pane-select');if(await pane.isVisible()){await pane.uncheck();await pane.check();if(page.url()!==copied)throw Error('Pane state changed contents');}
  await page.selectOption('#chapter-selector','1');await page.evaluate(()=>window.__qaPending);
  if(new URL(page.url()).searchParams.has('view'))throw Error('Numbered chapter retains contents URL');
  const numberedAfter=await page.locator('#chapter-selector option').evaluateAll(ns=>ns.filter(n=>n.value&&n.value!=='contents').map(n=>[n.value,n.text]));
  if(JSON.stringify(numberedBefore)!==JSON.stringify(numberedAfter))throw Error('Chapter population changed');
  await page.goBack();await page.waitForFunction(()=>window.__qa.getState().viewingLevel==='contents-level');await page.evaluate(()=>window.__qaPending);
  await page.goForward();await page.waitForFunction(()=>window.__qa.getState().viewingLevel==='chapter-level');
  interactions.push({id:row.id,dropdown:'PASS',copy_reload:'PASS',pane:'PASS',numbered_chapters:'PASS',history:'PASS',unrelated_params_fragment:'PASS'});
 }
 await open('/antiquities/?book=2&view=contents');
 await page.selectOption('#book-selector','03');await page.evaluate(()=>window.__qaPending);if(new URL(page.url()).searchParams.get('view')!=='contents')throw Error('Eligible book switch');
 await page.selectOption('#book-selector','06');await page.evaluate(()=>window.__qaPending);if(new URL(page.url()).searchParams.has('view')||await page.locator('.source-contents').count())throw Error('Ineligible book fallback');
 // A keyboard user reaches the same first option through the native selector.
 await open('/antiquities/?book=3&chapter=1');await page.locator('#chapter-selector').focus();await page.keyboard.press('Home');await page.keyboard.press('Enter');await page.evaluate(()=>window.__qaPending);
 if(new URL(page.url()).searchParams.get('view')!=='contents')throw Error('Keyboard contents selection');
 const compiled=fs.readFileSync('C:/Users/Pollard_R/Git/LatinJosephus-v2-development/_site/assets/css/main.css','utf8');
 const branding=fs.readFileSync(path.join(root,'_sass/_branding.scss'),'utf8')+'\n'+fs.readFileSync(path.join(root,'_sass/_reader-ui.scss'),'utf8');
 function luminance(c){return c.match(/[\d.]+/g).slice(0,3).map(Number).map(v=>{v/=255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4}).reduce((s,v,i)=>s+v*[.2126,.7152,.0722][i],0)}
 await page.addStyleTag({content:compiled+'\n'+branding+'\n'+fs.readFileSync(path.join(root,'assets/css/tei.css'),'utf8')});
 for(const theme of ['light','dark']){
  const colors=await page.evaluate(theme=>{
   document.documentElement.dataset.theme=theme;
   const n=document.querySelector('#latin .source-contents'),s=n.querySelector('tei-supplied'),p=n.querySelector('tei-item');
   let surface=n;while(surface.parentElement&&getComputedStyle(surface).backgroundColor==='rgba(0, 0, 0, 0)')surface=surface.parentElement;return {text:getComputedStyle(p).color,suppliedColor:getComputedStyle(s).color,background:getComputedStyle(surface).backgroundColor,italic:getComputedStyle(s).fontStyle,brackets:getComputedStyle(s,'::before').content,note:n.querySelector('tei-note').textContent};
  },theme);
  const a=luminance(colors.text),b=luminance(colors.background),contrast=(Math.max(a,b)+.05)/(Math.min(a,b)+.05);
  if(contrast<4.5||colors.italic!=='italic'||colors.brackets!=='none')throw Error('Theme or supplement distinction '+JSON.stringify(colors));
  await page.locator('#latin').screenshot({path:path.join(__dirname,`CONTENTS_${theme}.png`)});
  themes.push({theme,...colors,contrast:Number(contrast.toFixed(2)),result:'PASS'});
 }
 if(report.errors.length)throw Error(JSON.stringify(report.errors));
 fs.writeFileSync(path.join(__dirname,'CONTENTS_BROWSER_QA_2026-10-08.json'),JSON.stringify({checks,source_combinations:104,eligible_book_sources:expected.length,interactions,book_switch:'PASS',keyboard:'PASS',themes,errors:report.errors,result:'PASS'},null,2));
 await browser.close();server.close();console.log('CONTENTS_QA_PASS',checks.length,interactions.length);
})().catch(e=>{console.error(e);fs.writeFileSync(path.join(__dirname,'CONTENTS_BROWSER_FAILURE.json'),JSON.stringify({error:String(e),report},null,2));server.close();process.exit(1)});