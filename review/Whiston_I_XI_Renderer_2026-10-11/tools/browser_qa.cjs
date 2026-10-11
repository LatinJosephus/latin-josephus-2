/* Exercises real reader controls and live DOM. Hooks expose getters/completion only. */
const fs=require('fs'),path=require('path'),http=require('http'),crypto=require('crypto');
const {chromium}=require('C:/Program Files/WindowsApps/OpenAI.CodexPrimaryRuntime.v26-1007-641-0_26.1007.641.0_x64__3k8sg7r9htsxt/dependencies/node/node_modules/playwright');
const root=path.resolve(__dirname,'../../..'),pack=path.resolve(__dirname,'..');
const runtime='C:/workspace/Whiston-I-XI-Renderer-runtime-20261011',site=path.join(runtime,'site');
const canonical='C:/Users/Pollard_R/Git/LatinJosephus-v2-development';
const oracle=JSON.parse(fs.readFileSync(path.join(pack,'INTERVAL_ORACLE.json')));
const hash=s=>crypto.createHash('sha256').update(s).digest('hex'),norm=s=>s.replace(/\s+/g,' ').trim();
const report={status:'RUNNING',sections:[],structural:[],crossWork:[],navigation:[],unsegmented:[],errors:[],requests:[]};
const save=()=>fs.writeFileSync(path.join(pack,'BROWSER_QA.json'),JSON.stringify(report,null,2)+'\n');
function instrument(s){
 s=s.replace('  bookTitle.innerText = activeWork.title;', '  window.__qa={state:()=>({...state}),traditionalRows,data:()=>fullData};\n  bookTitle.innerText = activeWork.title;');
 s=s.replace('    else parseAnnotations();','    else parseAnnotations();\n    window.__qaRendered={...state}; window.__qaCount=(window.__qaCount||0)+1;');
 return s.replace('  reload().then(() => {','  reload().then(() => { window.__qaReady=true; document.querySelector("#collapse-settings")?.classList.add("show");');
}
function serve(baseline=false){return http.createServer((req,res)=>{
 const pathname=decodeURIComponent(new URL(req.url,'http://localhost').pathname);let rel=pathname.replace(/^\//,'');
 if(rel.split('/').includes('..')){res.writeHead(403);return res.end();}
 let file=path.join(site,rel);
 if(fs.existsSync(file)&&fs.statSync(file).isDirectory())file=path.join(file,'index.html');
 if(rel.startsWith('assets/xml/')||rel.startsWith('assets/js/')||rel==='assets/css/tei.css')file=path.join(baseline?canonical:root,rel);
 if(!baseline&&/^assets\/xml\/(bellum|deh|contra-apionem)\//.test(rel))file=path.join(site,rel);
 if(rel.startsWith('bin/'))file=path.join(root,rel);
 if(!fs.existsSync(file)){res.writeHead(404);return res.end();}
 let bytes=fs.readFileSync(file);if(file.endsWith('renderTei.js'))bytes=Buffer.from(instrument(bytes.toString()));
 const mime={'.js':'text/javascript','.xml':'application/xml','.json':'application/json','.html':'text/html','.css':'text/css','.svg':'image/svg+xml','.png':'image/png','.jpg':'image/jpeg','.otf':'font/otf'};
 res.setHeader('Content-Type',mime[path.extname(file)]||'application/octet-stream');res.end(bytes);
});}
const listen=s=>new Promise(resolve=>s.listen(0,'127.0.0.1',()=>resolve(`http://127.0.0.1:${s.address().port}`)));
async function open(pg,origin,route,query){
 const target=`${origin}/${route}/?${query}`;
 if(!process.env.QA_FORCE_PAGE_LOAD&&pg.url().startsWith(`${origin}/${route}/`)&&await pg.evaluate(()=>!!window.__qaReady)){
  // Exercise the reader's normal history-navigation listener; keep its real
  // loading, selection and rendering functions intact. Direct loads are a
  // separate gate below and can be forced with QA_FORCE_PAGE_LOAD=1.
  const count=await pg.evaluate(()=>window.__qaCount);
  await pg.evaluate(url=>{history.pushState({},'',url);dispatchEvent(new PopStateEvent('popstate'));},target);
  await pg.waitForFunction(count=>window.__qaCount>count,count,{timeout:60000,polling:10});
 }else{
  await pg.goto(target,{waitUntil:'domcontentloaded',timeout:60000});
  await pg.waitForFunction(()=>window.__qaReady,null,{timeout:60000,polling:20});
 }
 for(const lang of ['english','greek','latin'])if(await pg.locator(`#${lang}-pane-select`).isVisible())await pg.locator(`#${lang}-pane-select`).check({force:true});
}
async function select(pg,number){
 const count=await pg.evaluate(()=>window.__qaCount);
 await pg.locator('#niese-selector').selectOption(String(number));
 await pg.waitForFunction(({count,number})=>window.__qaCount>count&&String(window.__qaRendered.nieseNum)===String(number),{count,number},{timeout:60000,polling:10});
}
async function snapshot(pg){return pg.evaluate(()=>{
 const norm=s=>s.replace(/\s+/g,' ').trim();
 const result={state:window.__qa.state(),languages:{}};
 for(const language of ['english','latin','greek']){
  const pane=document.getElementById(language);if(!pane)continue;
  const clone=pane.cloneNode(true);clone.querySelectorAll('[data-original]').forEach(e=>e.remove());
  const allVisible=norm(pane.innerText),html=clone.innerHTML.split(location.origin).join('LOOPBACK_ORIGIN');
  const excluded='h3,tei-num,tei-note,tei-milestone,.niese-exact-note,.niese-correspondence-note,.niese-related-passage,.structural-unavailable';
  clone.querySelectorAll(excluded).forEach(e=>e.remove());
  let hiddenNarrative=[];const walker=document.createTreeWalker(pane,NodeFilter.SHOW_TEXT);
  for(let node;node=walker.nextNode();){
   if(!node.data.trim()||node.parentElement.closest(excluded+', [data-original]'))continue;
   for(let el=node.parentElement;el&&el!==pane.parentElement;el=el.parentElement){
    const cs=getComputedStyle(el);if(cs.display==='none'||cs.visibility==='hidden'||el.hidden){hiddenNarrative.push(node.data);break;}
   }
  }
  const inline=[...clone.querySelectorAll('tei-hi,tei-q,tei-foreign,tei-emph,tei-title,tei-ref,tei-name,tei-seg')].map(e=>({tag:e.localName.replace('tei-',''),text:norm(e.textContent),rend:e.getAttribute('rend')})).filter(e=>e.text);
  const notes=[...pane.querySelectorAll('tei-note[type="whiston-footnote"]')].map(e=>({id:e.id,visible:getComputedStyle(e).display!=='none'&&e.getClientRects().length>0,text:norm(e.innerText),original:norm(e.querySelector('[data-original]')?.textContent||e.textContent)}));
  const ids=[...pane.querySelectorAll('[id]')].map(e=>e.id);
  result.languages[language]={text:norm(clone.textContent),allVisible,html,hiddenNarrative,inline,notes,
   exact:!!pane.querySelector('[data-english-segmentation="exact"]'),context:!!pane.querySelector('.niese-context-note'),
   unavailable:!!pane.querySelector('.structural-unavailable'),citations:[...pane.querySelectorAll('tei-num.niese-generated')].map(e=>e.textContent),
   duplicateIds:ids.filter((x,i)=>ids.indexOf(x)!==i)};
 }
 return result;
});}
function assert(ok,message,detail){if(!ok){if(detail)fs.writeFileSync(path.join(pack,'FAILURE_DETAIL.json'),JSON.stringify(detail,null,2)+'\n');throw Error(message);}}
function compareWitnesses(a,b,label){
 for(const lang of ['latin','greek'])assert(a.languages[lang].html===b.languages[lang].html,`${label} ${lang} presentation changed`,{a:a.languages[lang],b:b.languages[lang]});
}
function checkInterval(actual,expected){
 const s=actual.languages.english;
 assert(s.exact&&!s.context&&!s.unavailable,`${expected.book}.${expected.number} exact mode missing`,actual);
 assert(s.text===expected.text,`${expected.book}.${expected.number} certified interval differs`,{expected,actual:s});
 assert(s.hiddenNarrative.length===0,`${expected.book}.${expected.number} hidden narrative`,s);
 assert(s.citations.length===1&&s.citations[0]===`[${expected.number}]`,'Wrong selected citation',s);
 assert(s.duplicateIds.length===0,'Duplicate English IDs',s);
 for(const note of expected.notes){
  const id=note.attrs['{http://www.w3.org/XML/1998/namespace}id'];const found=s.notes.find(e=>e.id===id);
  assert(found?.visible&&found.original===note.text,`Missing or altered visible note ${id}`,{expected:note,actual:s.notes});
  assert(found.text.includes(note.text),'Displayed note text differs',{expected:note,actual:found});
 }
 assert(s.notes.length===expected.notes.length,'Wrong note ownership',{expected,actual:s});
 const parts=expected.inline.filter(e=>e.tag==='hi');
 assert(norm(s.inline.filter(e=>e.tag==='hi').map(e=>e.text).join(' '))===norm(parts.map(e=>e.text).join(' ')),'Inline emphasis differs',{expected:parts,actual:s.inline});
 return {book:expected.book,number:expected.number,nextPhysical:expected.nextPhysical,passed:true,
  expectedSHA256:expected.sha256,renderedSHA256:hash(s.text),opening:s.text.slice(0,100),closing:s.text.slice(-100),
  allNarrativeVisible:true,notes:s.notes.length,inline:s.inline.length,latinSHA256:hash(actual.languages.latin.html),greekSHA256:hash(actual.languages.greek.html)};
}
async function main(){
 fs.mkdirSync(runtime,{recursive:true});fs.mkdirSync(path.join(pack,'evidence'),{recursive:true});
 report.rendererSHA256=hash(fs.readFileSync(path.join(root,'assets/js/renderTei.js')));
 report.registrySHA256=hash(fs.readFileSync(path.join(root,'assets/xml/antiquities/niese/book-09.json')));
 report.structureSHA256=hash(fs.readFileSync(path.join(root,'assets/xml/antiquities/structure.xml')));
 const candidate=serve(),baseline=serve(true);const [a,b]=await Promise.all([listen(candidate),listen(baseline)]);
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 const ctx=await browser.newContext({viewport:{width:1440,height:1000}});
 const page=await ctx.newPage(),base=await ctx.newPage();
 for(const p of [page,base]){p.on('pageerror',e=>report.errors.push(String(e)));p.on('requestfailed',r=>report.requests.push({url:r.url(),error:r.failure()?.errorText}));}
 try{
  const books=[...new Set(oracle.map(e=>e.book))];
  for(const book of books){
   const rows=oracle.filter(e=>e.book===book).sort((x,y)=>x.number-y.number);
   await Promise.all([open(page,a,'antiquities',`book=${book}&niese=${rows[0].number}`),open(base,b,'antiquities',`book=${book}&niese=${rows[0].number}`)]);
   const menu=await page.locator('#niese-selector').evaluate(e=>[...e.options].filter(e=>e.value).map(e=>Number(e.value)));
   assert(menu.length===rows.length&&rows.every(e=>menu.includes(e.number)),'Incomplete English navigation menu '+book,{menu,rows:rows.map(e=>e.number)});
   for(const expected of rows){
    await Promise.all([select(page,expected.number),select(base,expected.number)]);
    const [actual,prior]=await Promise.all([snapshot(page),snapshot(base)]);
    compareWitnesses(actual,prior,`${book}.${expected.number}`);
    report.sections.push({...checkInterval(actual,expected),GreekLatinPresentationUnchanged:true,URL:new URL(page.url()).search});
    if(report.sections.length%100===0){save();console.log('Displayed sections verified',report.sections.length);}
    if(process.argv.includes('--probe')&&report.sections.length>=35)break;
   }
   save();console.log('Book complete',book,report.sections.length);
   if(process.argv.includes('--probe'))break;
  }
  if(!process.argv.includes('--probe')){
   assert(report.sections.length===3821,'Incomplete exhaustive section QA');
   report.status='SECTIONS-PASS';save();
  }else report.status='PROBE-PASS';
 }catch(e){report.status='FAIL';report.failure=String(e);throw e;}
 finally{save();await browser.close();candidate.close();baseline.close();}
 console.log(report.status);
}
module.exports={root,pack,runtime,site,canonical,oracle,hash,norm,instrument,serve,listen,open,select,snapshot,assert,compareWitnesses,checkInterval,chromium};
if(require.main===module)main().catch(e=>{console.error(e);process.exitCode=1;});
