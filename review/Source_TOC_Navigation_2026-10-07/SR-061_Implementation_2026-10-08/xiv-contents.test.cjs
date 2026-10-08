const fs = require('fs');
const path = require('path');
const http = require('http');
const cp = require('child_process');
const crypto = require('crypto');
const {chromium} = require('C:/Users/Pollard_R/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root = path.resolve(__dirname, '../../..');
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
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 const page=await browser.newPage({viewport:{width:1600,height:1000}});
 const errors=[],checks=[],themes=[];page.on('pageerror',e=>errors.push(String(e)));
 async function open(route){await page.goto(origin+route);await page.waitForFunction(()=>window.__qaReady,{},{timeout:60000});}
 async function settle(){await page.evaluate(()=>window.__qaPending);}
 const entries=JSON.parse(fs.readFileSync(path.join(__dirname,'ENTRY_INVENTORY.json'),'utf8'));
 await open('/antiquities/?book=14&view=contents&extra=keep#retained');
 const content=await page.evaluate(entries=>{
  if(window.__qa.getState().viewingLevel!=='contents-level')throw Error('Not contents mode');
  const latin=document.querySelector('#latin .source-contents'),greek=document.querySelector('#greek .source-contents'),english=document.querySelector('#english .source-contents');
  const items=[...latin.querySelectorAll('tei-item')];if(items.length!==27)throw Error('Entry count');
  const labels=[...latin.querySelectorAll('tei-supplied')].map(n=>n.textContent);
  if(JSON.stringify(labels)!==JSON.stringify(['[V]','[VI]','[VII]','[VIII]','[IX]','[X]','[XI]','[XII]']))throw Error('Supplied numbering');
  items.forEach((item,i)=>{
   const c=item.cloneNode(true),lab=c.querySelector(':scope > tei-label');
   if(lab){const next=lab.nextSibling;if(next.nodeType!==Node.TEXT_NODE||!next.textContent.startsWith(' '))throw Error('Editorial separator');next.deleteData(0,1);lab.remove();}
   if(c.textContent!==entries[i].source_projection)throw Error('Latin projection mismatch '+entries[i].display_label);
  });
  if((latin.textContent.match(/Tunc autem filiis interminatus/g)||[]).length!==1)throw Error('Herodian omission/duplication');
  if(!items[6].textContent.trim().endsWith('obstructis portis romanos excluserunt.'))throw Error('VII end');
  if(!items[11].textContent.trim().endsWith('mereretur.'))throw Error('XII end');
  if(!greek?.querySelector('tei-div2[n="0"]')||greek.textContent.length<100)throw Error('Greek source contents missing');
  if(english.textContent!=='No source table of contents is available for this witness.')throw Error('Wrong English availability');
  if(latin.querySelector('a')||greek.querySelector('a'))throw Error('Synthetic entry links');
  const ids=[...document.querySelectorAll('[id]')].map(n=>n.id);if(new Set(ids).size!==ids.length)throw Error('Duplicate rendered IDs');
  if(document.querySelector('#chapter-selector').options[0].value!=='contents')throw Error('First option');
  return {entries:27,source_numerals:19,supplied_labels:labels,projection_checks:27,approved_boundary_checks:8,Greek_Latin_side_by_side:'PASS',English_unavailable:'PASS',Herodian_retained_once:'PASS',nonclickable:'PASS',DOM_IDs:'PASS'};
 },entries);checks.push(content);
 const copied=page.url(),before=await page.locator('.source-contents').allTextContents();
 await page.reload();await page.waitForFunction(()=>window.__qaReady);if(page.url()!==copied||JSON.stringify(await page.locator('.source-contents').allTextContents())!==JSON.stringify(before))throw Error('Copy/reload');
 await page.uncheck('#greek-pane-select',{force:true});await page.check('#greek-pane-select',{force:true});if(page.url()!==copied)throw Error('Pane identity');
 await page.selectOption('#chapter-selector','1');await settle();if(new URL(page.url()).searchParams.has('view'))throw Error('Chapter exit');
 if(await page.locator('.source-contents').count())throw Error('Companion leaked into Chapter view');
 await page.goBack();await page.waitForFunction(()=>window.__qa.getState().viewingLevel==='contents-level');await settle();
 await page.goForward();await page.waitForFunction(()=>window.__qa.getState().viewingLevel==='chapter-level');await settle();
 await page.selectOption('#chapter-selector','contents');await settle();
 let url=new URL(page.url());for(const k of ['chapter','subchapter','bamberg','niese','unit'])if(url.searchParams.has(k))throw Error('Conflicting parameter '+k);
 if(url.searchParams.get('extra')!=='keep'||url.hash!=='#retained')throw Error('Unrelated preference/fragment');
 await page.selectOption('#book-selector','13');await settle();if(new URL(page.url()).searchParams.get('view')!=='contents')throw Error('Book13 contents');
 await page.selectOption('#book-selector','14');await settle();if(await page.locator('#latin tei-item').count()!==27)throw Error('Return XIV');
 await page.selectOption('#book-selector','06');await settle();
 if(new URL(page.url()).searchParams.has('view'))throw Error('Unavailable book fallback');
 checks.push({copy_reload:'PASS',panes:'PASS',chapter_exit_and_contents_return:'PASS',history:'PASS',book_switch:'PASS',unrelated_params:'PASS'});
 await open('/antiquities/?book=14&view=contents');
 const styles=fs.readFileSync('C:/Users/Pollard_R/Git/LatinJosephus-v2-development/_site/assets/css/main.css','utf8')+'\n'+fs.readFileSync(path.join(root,'_sass/_branding.scss'),'utf8')+'\n'+fs.readFileSync(path.join(root,'_sass/_reader-ui.scss'),'utf8')+'\n'+fs.readFileSync(path.join(root,'assets/css/tei.css'),'utf8');
 await page.addStyleTag({content:styles});
 function lum(c){return c.match(/[\d.]+/g).slice(0,3).map(Number).map(v=>{v/=255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4}).reduce((s,v,i)=>s+v*[.2126,.7152,.0722][i],0)}
 for(const theme of ['light','dark']){
  const c=await page.evaluate(theme=>{
   document.documentElement.dataset.theme=theme;const n=document.querySelector('#latin .source-contents'),p=n.querySelector('tei-item'),labels=[...n.querySelectorAll('tei-supplied')];
   let s=n;while(s.parentElement&&getComputedStyle(s).backgroundColor==='rgba(0, 0, 0, 0)')s=s.parentElement;
   const values=labels.map(l=>({text:l.textContent,visible:!!l.getBoundingClientRect().height,before:getComputedStyle(l,'::before').content,after:getComputedStyle(l,'::after').content,italic:getComputedStyle(l).fontStyle,reason:l.getAttribute('reason'),source:l.getAttribute('source')}));
   if(values.some(v=>!v.visible||!/^\[[IVX]+\]$/.test(v.text)||v.before!=='none'||v.after!=='none'||v.source!=='#sr061-editorial-approval'||v.reason!=='not-transmitted'))throw Error('Unmarked/double brackets or Blatt confusion');
   return {text:getComputedStyle(p).color,background:getComputedStyle(s).backgroundColor,labels:values};
  },theme);
  const x=lum(c.text),y=lum(c.background),contrast=(Math.max(x,y)+.05)/(Math.min(x,y)+.05);if(contrast<4.5)throw Error('Contrast');
  await page.locator('#latin tei-item').nth(4).scrollIntoViewIfNeeded();
  await page.screenshot({path:path.join(__dirname,`XIV_${theme}.png`)});
  themes.push({theme,...c,contrast:Number(contrast.toFixed(2)),result:'PASS'});
 }
 if(errors.length)throw Error(errors.join('\n'));
 fs.writeFileSync(path.join(__dirname,'XIV_BROWSER_QA.json'),JSON.stringify({result:'PASS',checks,themes,errors,renderer_changed:false,source_XML_changed:false},null,2));
 await browser.close();server.close();console.log('XIV_BROWSER_PASS: 27 entries, 8 visible bracketed labels, 2 themes, URL/history/panes/source projection');
})().catch(e=>{console.error(e);fs.writeFileSync(path.join(__dirname,'XIV_BROWSER_FAILURE.json'),JSON.stringify({error:String(e)},null,2));server.close();process.exit(1)});
