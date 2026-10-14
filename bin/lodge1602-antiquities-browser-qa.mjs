#!/usr/bin/env node
// Actual built-reader acceptance; expected Lodge intervals are independently
// traversed from the immutable scholarly master, never renderer output.
// --root <checkout> --site <built-site> --output <external-results-directory>
// --mode baseline captures protected views; integrated compares --baseline <json>.
// Optional --base-url, --port, --browser-executable and --playwright-module.
import fs from 'node:fs'; import path from 'node:path'; import http from 'node:http'; import crypto from 'node:crypto'; import assert from 'node:assert/strict'; import {createRequire} from 'node:module';
const args=process.argv.slice(2), opt=(k,d)=>args.includes(k)?args[args.indexOf(k)+1]:d;
const root=path.resolve(opt('--root','.')),site=path.resolve(opt('--site','_site')),out=path.resolve(opt('--output','qa-output')),mode=opt('--mode','integrated');assert(args.includes('--output'),'Pass an explicit external --output directory');assert(out!==root&&!out.startsWith(root+path.sep),'QA results must remain outside the source checkout');fs.mkdirSync(out,{recursive:true});
const require=createRequire(import.meta.url),pw=require(opt('--playwright-module','playwright'));
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
assert.equal(sha(fs.readFileSync(path.join(root,'_docs/lodge1602-antiquities-source/book-02-frozen.xml'))),'ba43e5c5937a1c8a82a0575886d9747121600b30a6430e50f90fcf1c16772e8b');assert.equal(sha(fs.readFileSync(path.join(root,'_docs/lodge1602-antiquities-source/book-02-final.tsv'))),'a5b667891b6c5ae35b44b9c7b3923bcc5f886c7ae217493f4a4b0e5af2418863'); const save=(n,d)=>fs.writeFileSync(path.join(out,n),JSON.stringify(d,null,2)+'\n');
const errors=[],network=[];let server; const supplied=opt('--base-url',null);
if(!supplied){server=http.createServer((req,res)=>{const pathname=decodeURIComponent(new URL(req.url,'http://localhost').pathname);let file=path.resolve(site,'.'+pathname);if(!file.startsWith(site+path.sep)&&file!==site){res.writeHead(403).end();return;}if(pathname.startsWith('/__qa/'))file=path.join(root,'_docs/lodge1602-antiquities-source',pathname.slice(6));if(pathname==='/assets/js/renderTei.js'&&opt('--renderer-override',null))file=path.resolve(opt('--renderer-override'));if(pathname==='/assets/css/tei.css'&&opt('--stylesheet-override',null))file=path.resolve(opt('--stylesheet-override'));if(fs.existsSync(file)&&fs.statSync(file).isDirectory())file=path.join(file,'index.html');if(!fs.existsSync(file)){res.writeHead(404).end();return;}res.setHeader('Content-Type',({'.html':'text/html','.js':'text/javascript','.css':'text/css','.xml':'application/xml','.json':'application/json','.tsv':'text/plain'})[path.extname(file)]||'application/octet-stream');res.end(fs.readFileSync(file));});await new Promise(r=>server.listen(Number(opt('--port',0)),'127.0.0.1',r));}
const base=supplied||`http://127.0.0.1:${server.address().port}`;
const browser=await pw.chromium.launch({headless:true,...(opt('--browser-executable',null)?{executablePath:opt('--browser-executable')}:{} )});const context=await browser.newContext({viewport:{width:1440,height:1000}});const page=await context.newPage();
page.setDefaultTimeout(60000);page.setDefaultNavigationTimeout(60000);
page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.status()>=400)network.push({url:r.url(),status:r.status()});});page.on('requestfailed',r=>network.push({url:r.url(),error:r.failure()?.errorText}));
async function init(){await page.evaluate(()=>{
 document.querySelector("#collapse-settings")?.classList.add("show");
 window.qa={};qa.pause=()=>new Promise(r=>setTimeout(r,0));qa.ready=async p=>{const until=Date.now()+60000;while(!p()){if(Date.now()>until)throw Error('Reader timeout '+location.href);await new Promise(r=>setTimeout(r,10));}await qa.pause();};
 qa.change=async(selector,value)=>{const el=document.querySelector(selector);if(!el)throw Error('Missing '+selector);let changed=false;const ob=new MutationObserver(()=>{changed=true;ob.disconnect();});ob.observe(document.querySelector('#english'),{childList:true});if(el.type==='radio')el.checked=true;else {const o=[...el.options].find(o=>o.value===String(value)||Number(o.value)===Number(value));if(!o)throw Error('Missing value '+selector+' '+value);el.value=o.value;}el.dispatchEvent(new Event('change',{bubbles:true}));await qa.ready(()=>changed);};
 qa.click=async selector=>{let changed=false;const ob=new MutationObserver(()=>{changed=true;ob.disconnect();});ob.observe(document.querySelector("#english"),{childList:true});document.querySelector(selector).click();await qa.ready(()=>changed);};
 qa.source=(n)=>{if(n.nodeType===3)return n.data;if(n.nodeType!==1&&n.nodeType!==11)return '';if(n.nodeType===1){if(n.matches('[data-original],tei-milestone,tei-num.niese-generated,.niese-context-note,.niese-correspondence-note,.lodge-source-controls,.lodge-source-context'))return '';if(n.matches('tei-note')){const o=n.querySelector('[data-original]');if(o)return o.textContent;}}return [...n.childNodes].map(qa.source).join('');};
 qa.pane=()=>[...document.querySelector('#english').children].filter(n=>n.tagName!=='H3').map(qa.source).join('');
 qa.snapshot=()=>Object.fromEntries(['english','greek','latin'].map(k=>[k,{text:[...document.querySelector('#'+k).children].filter(n=>n.tagName!=='H3').map(qa.source).join(''),ids:[...document.querySelector('#'+k).querySelectorAll('[id]')].map(n=>n.id)}]));
 });}
async function go(url){await page.goto(base+url,{waitUntil:'domcontentloaded'});await page.waitForFunction(()=>document.querySelector('#english tei-p')||document.querySelector('#english .niese-correspondence-note')||document.querySelector('#english .structural-unavailable')||document.querySelector('#unsupported-niese-notice'),{timeout:60000});await init();}
async function installOracle(name,hi){
 return await page.evaluate(async ({raw,name,hi})=>{
  const d=new DOMParser().parseFromString(raw,'application/xml');if(d.querySelector('parsererror'))throw Error('Frozen XML invalid');
  const metadata=await (await fetch('/assets/data/lodge1602-antiquities/'+name+'.json')).json();
  const letters=['12','13','14','19','20'].includes(metadata.book_key);
  const excluded=new Set(['note','head','argument','trailer','byline','opener','closer','signed','label']);
  qa.literal=n=>{const walk=(node,inP=false,excludedHere=false,inChapter=false,inLetter=false)=>{if(node.nodeType===3)return inP&&!excludedHere?node.data:'';if(node.nodeType!==1&&node.nodeType!==11)return '';const name=(node.localName||'').replace(/^tei-/,'');if(node.nodeType===1&&(!node.localName.startsWith('tei-')||node.matches('tei-num.niese-generated,tei-milestone'))){if(node.matches('.lodge-source-context,.lodge-source-controls,.niese-context-note,.niese-correspondence-note'))return '';if(node.matches('tei-num.niese-generated,tei-milestone'))return '';}
   const letter=inLetter||name.toLowerCase()==='floatingtext';const chapter=inChapter||(name==='div'&&node.getAttribute('type')==='chapter');return [...node.childNodes].map(c=>walk(c,inP||name==='p'||(name==='item'&&chapter)||(letters&&name==='opener'&&letter),excludedHere||(excluded.has(name)&&!(letters&&letter&&['opener','signed'].includes(name))),chapter,letter)).join('');};return walk(n);};
  let n=0;const sections=Array.from({length:hi+1},(_,i)=>({n:i,text:'',notes:[],gaps:[],pbs:[],native:[]}));
  const attrs=node=>[...node.attributes].filter(a=>!['xml:id','id','data-processed','data-origname','data-empty','data-xmlns','class','title'].includes(a.name)).map(a=>[a.name,a.value]).sort((a,b)=>a[0].localeCompare(b[0]));qa.attrs=attrs;
  const walk=(node,inP=false,skip=false,inChapter=false,inLetter=false)=>{if(node.nodeType===3){if(inP&&!skip)sections[n].text+=node.data;return;}if(node.nodeType!==1)return;const name=node.localName;
   if(name==='milestone'&&node.getAttribute('unit')==='niese'){n=Number(node.getAttribute('n'));return;}
   const entry={attrs:attrs(node),text:node.textContent};if(name==='note')sections[n].notes.push(entry);if(name==='gap')sections[n].gaps.push(entry);if(name==='pb')sections[n].pbs.push(entry);if(name==='milestone')sections[n].native.push(entry);
   const letter=inLetter||name.toLowerCase()==='floatingtext';const chapter=inChapter||(name==='div'&&node.getAttribute('type')==='chapter');for(const c of node.childNodes)walk(c,inP||name==='p'||(name==='item'&&chapter)||(letters&&name==='opener'&&letter),skip||(excluded.has(name)&&!(letters&&letter&&['opener','signed'].includes(name))),chapter,letter);};walk(d.documentElement);
  qa.expected=sections;qa.metadata=metadata;
  qa.actual=()=>{const view=document.querySelector('#english tei-div2[type="niese-section"]');if(!view)throw Error('No exact Lodge section');
   const rows=tag=>[...view.querySelectorAll('tei-'+tag)].filter(n=>!n.closest('.lodge-source-context')&&(tag!=='milestone'||n.getAttribute('unit')!=='niese')).map(n=>({attrs:attrs(n),text:n.textContent}));return {text:qa.literal(view),notes:rows('note'),gaps:rows('gap'),pbs:rows('pb'),native:rows('milestone')};};
  return {sections,fullText:sections.map(s=>s.text).join(''),counts:{notes:sections.flatMap(s=>s.notes).length,gaps:sections.flatMap(s=>s.gaps).length,pbs:sections.flatMap(s=>s.pbs).length,native:sections.flatMap(s=>s.native).length},sourceHash:metadata.authorities.frozen_XML};
 },{raw:fs.readFileSync(path.join(root,'_docs/lodge1602-antiquities-source/'+name+'-frozen.xml'),'utf8'),name,hi});
}
const cases=[];for(let b=1;b<=20;b++){const start=b===1?27:1;cases.push(`/antiquities/?book=${b}&niese=${start}`);}cases.push('/antiquities/?book=preface&niese=1','/antiquities/?book=preface&niese=26','/antiquities/?book=1&niese=346','/antiquities/?book=7&niese=69','/antiquities/?book=7&niese=99','/antiquities/?book=9&niese=51','/antiquities/?book=11&niese=200','/antiquities/?book=16&niese=200','/antiquities/?book=2&chapter=1','/antiquities/?book=2&chapter=13&subchapter=3','/bellum-judaicum/?book=1&niese=24','/bellum-judaicum/?book=1&niese=24&english=lodge1602','/bellum-judaicum/?book=1&niese=24&english=lodge1602&lodgeNotes=0','/bellum-judaicum/?book=3&chapter=1','/deh/?book=1','/contra-apionem/?book=2&num=51');
const baselineFile=opt('--baseline',path.join(out,'BASELINE_BROWSER.json'));
async function verifyBatchUnits(){
 const focusOnly=args.includes('--focused-only');
 const units=[['preface','preface',1,26,'0e7ee1b3abb66081d9cfbf5347dc7d1ba7d116f2f26cdf344437184cd5644b57'],['book-01','1',27,346,'b2270f7e701530aa5b738ff86eb8f894189123dee8b3dab72dd2241c9a3eeae2'],['book-03','3',1,322,'bf8a13a752ea057f337ea92638db4878c4421d4d7a4393ef607a1d606d5270f6'],['book-04','4',1,331,'afffc6760f3b5a317026f394c5a274800cd9e506152e689b4891e6ab0176e290'],['book-05','5',1,362,'79ef658653d650151af89ba6e5da6b5ae62e087ecd80caced91412be18a047bc']];
 const newUnits=[["book-06", "6", 1, 378, "1255d9352136dbad2c78858f34ce1e7cc39de12d6c2511bf0015230bf700c680"], ["book-07", "7", 1, 394, "b6cba578e64982baf686ef6ef652694dbf76a910eeda14ff61b89d102fcf20cf"], ["book-08", "8", 1, 420, "2c5dc5d7f2a6e23d00ddd0309457b7db3535203b6dbf0b1eebba5aae26f49296"], ["book-09", "9", 1, 291, "441e70e48159a9cd678a62ff3992d8ca919995c5091c210106b7ea73bee292c9"], ["book-10", "10", 1, 281, "d3909b05d3406f557a3f16d1b8230317bee07a3e80478c4fc03793a6c541fdc0"]];
 const latestUnits=[["book-11", "11", 1, 347, "cd4e3138187245df36c7ca52eb72827e43dae71975ff7e39da77fcf5cd8d6af1"], ["book-12", "12", 1, 434, "493e1c66530c96d3b50564e7dad009faba3fed1b4fdea42c564e48c44c20fa46"], ["book-13", "13", 1, 433, "51885a8399dea421068143f0f99a7ea54b2876f6d377b51f68ad23a1d2b6d60a"], ["book-14", "14", 1, 491, "bad2ffde21417f681e5467ba2248294c9438d71229cff8f9389a4ae9e8611876"], ["book-15", "15", 1, 425, "8a1a5320697edc28b7534f00f4cc2ef9614be73d1ca2c03e881c9b4239f3690a"]];
 const finalBatch=args.includes('--xvi-xx');
 const finalUnits=[["book-16", "16", 1, 404, "6ebfe8f08fbbcc39e25d575e5c1c246a26cdfd66ac527f5228ef9a2adb1af78f"], ["book-17", "17", 1, 355, "9f20526cd53e206f01e7ad23eb8bae99f41305c25afe541fa627120330e790c0"], ["book-18", "18", 1, 379, "44c4895c813af778a9bd047c0f24682a6ec0206f9ad175f2db26b8c51a375d53"], ["book-19", "19", 1, 366, "22c2db87df6e41611d2a390d520f1f80555df4d7d99ff0dc090796a36d928019"], ["book-20", "20", 1, 268, "6c65c8484959c2932dafc9b968d10d10b6c74e15f6b9bfda208410f6e5f5ad81"]];
 const latest=args.includes('--xi-xv');
 const selectedUnits=finalBatch?finalUnits:latest?latestUnits:args.includes('--vi-x')?newUnits:units;
 const previous=args.includes('--resume-batch')?JSON.parse(fs.readFileSync(path.join(out,'LODGE_BATCH_BROWSER_QA.json'))):null;
 const results=previous?.units??[],focused=previous?.focused??[];let total=results.reduce((sum,r)=>sum+r.identities,0);
 for(const [name,key,lo,hi,hash] of selectedUnits){
  if(results.some(r=>r.unit===name&&r.master_sha256===hash&&r.status==='PASS'))continue;
  assert.equal(sha(fs.readFileSync(path.join(root,'_docs/lodge1602-antiquities-source/'+name+'-frozen.xml'))),hash,'Independent pinned frozen master '+name);
  await go(`/antiquities/?book=${key}&niese=${lo}&english=lodge1602`);const oracle=await installOracle(name,hi);
  const important=finalBatch?({"16": [1, 182, 404], "17": [1, 25, 119, 355], "18": [1, 379], "19": [1, 14, 73, 355, 366], "20": [1, 42, 268]}[key]):latest?({"11": [1, 63, 65, 124, 347], "12": [1, 126, 434], "13": [1, 290, 333, 433], "14": [1, 217, 218, 219, 220, 221, 222, 223, 224, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 308, 374, 388, 429, 491], "15": [1, 290, 425]}[key]):args.includes('--vi-x')?({'6':[1,61,378],'7':[1,69,70,80,99,394],'8':[1,170,420],'9':[1,51,75,80,109,291],'10':[1,61,237,238,239,281]}[key]):key==='1'?[27,65,79,159,166,206,346]:key==='3'?[1,82,322]:key==='4'?[1,61,312,331]:[lo,hi];
  const checkpointFile=path.join(out,name+'-INTERVAL_CHECKPOINT.json');
  const priorRows=args.includes('--resume-batch')&&fs.existsSync(checkpointFile)?JSON.parse(fs.readFileSync(checkpointFile)).rows:[];
  for(const r of priorRows)assert.equal(r.text,oracle.sections[r.n].text,'Resumed independently frozen interval '+name+'.'+r.n);
  await page.exposeFunction('lodgeCheckpoint'+key,rows=>{fs.writeFileSync(checkpointFile,JSON.stringify({master_sha256:hash,status:'INTERVAL_CHECKPOINT',unit:name,rows},null,2)+'\n');console.log('Checkpoint '+name+' '+rows.length);});
  const rows=await page.evaluate(async({lo,hi,selected,priorRows,key})=>{const rows=[...priorRows];for(const n of selected){
   if(rows.some(r=>r.n===n))continue;
   if(n>lo)await qa.change('#niese-selector',n);const actual=qa.actual(),expected=qa.expected[n];
   if(actual.text!==expected.text)throw Error('Independent frozen text/exclusive endpoint '+n+' '+JSON.stringify({actual:actual.text.slice(0,120),expected:expected.text.slice(0,120)}));
   for(const k of ['notes','gaps','pbs','native'])if(JSON.stringify(actual[k])!==JSON.stringify(expected[k]))throw Error('Independent frozen source features '+k+' '+n);
   const view=document.querySelector('#english tei-div2[type="niese-section"]'),ids=[...document.querySelectorAll('#english [id]')].map(e=>e.id);
   if(new Set(ids).size!==ids.length)throw Error('Duplicate source ID '+n);
   if(Number(view.dataset.nieseStart)!==n||Number(view.dataset.nieseEndExclusive)!==n+1||Number(document.querySelector('#niese-selector').value)!==n||Number(new URL(location.href).searchParams.get('niese'))!==n)throw Error('Selected exact interval and URL '+n);
   if(document.querySelector('#english-source-selector').value!=='lodge1602'||document.querySelector('#niese-previous').disabled!==(n===lo)||document.querySelector('#niese-next').disabled!==(n===hi))throw Error('Source and endpoint controls '+n);
   const notice=document.querySelector('#english .niese-correspondence-note');
   if(qa.metadata.book_key==='10'&&n===238){if(!notice||notice.textContent!=='No separate corresponding passage in Lodge (1602)'||actual.text!==''||document.querySelector('#english tei-p'))throw Error('Approved X.238 empty view');}
   else if(qa.metadata.book_key==='14'&&((n>=218&&n<=223)||(n>=229&&n<=264))){if(!notice||notice.textContent!=='No separate corresponding passage in Lodge (1602); documentary collection abbreviated.'||actual.text!==''||document.querySelector('#english tei-p')||document.querySelector('#english tei-gap'))throw Error('Approved Book XIV empty view '+n);}
   else if(notice||document.querySelector('#english .tei-omission-notice'))throw Error('Other witness omission leaked into Lodge '+n);
   rows.push({n,text:actual.text,notes:actual.notes.length,gaps:actual.gaps.length,pbs:actual.pbs.length,native:actual.native.length});
   if(rows.length%75===0)await window['lodgeCheckpoint'+key](rows);
  }await window['lodgeCheckpoint'+key](rows);return rows;},{lo,hi,priorRows,key,selected:focusOnly?important:Array.from({length:hi-lo+1},(_,i)=>lo+i)});
  console.log('Exact interval content checks complete '+name+' '+rows.length);
  const checks=rows.map(r=>({identity:(key==='preface'?'I':key)+'.'+r.n,status:'PASS',characters:r.text.length,expected_sha256:sha(oracle.sections[r.n].text),actual_sha256:sha(r.text),incipit:r.text.slice(0,130),tail:r.text.slice(-130),notes:r.notes,gaps:r.gaps,page_breaks:r.pbs,native_milestones:r.native}));
  await page.evaluate(()=>qa.change('#book-level'));const book=await page.evaluate(()=>{const node=document.querySelector('#english tei-div1');return {literal:qa.literal(node),chapters:[...document.querySelector('#lodge-native-chapter').options].filter(o=>o.value).map(o=>({id:o.value,present:!!document.getElementById(o.value)})),paragraphs:node.querySelectorAll('tei-p').length,notes:node.querySelectorAll('tei-note').length,gaps:node.querySelectorAll('tei-gap').length,pbs:node.querySelectorAll('tei-pb').length,native:node.querySelectorAll('tei-milestone:not([unit="niese"])').length,contents:node.querySelector('tei-list')?.textContent??null,counts:qa.metadata.source_counts};});
  assert.equal(book.literal,oracle.fullText,'Complete source-native book text '+name);assert.equal(book.literal.length,book.counts.literal_character_data_units);assert.equal(book.paragraphs,book.counts.TCP_paragraphs);assert.equal(book.notes,book.counts.marginal_notes);assert.equal(book.gaps,book.counts.TCP_gaps);assert.equal(book.pbs,book.counts.page_breaks);assert.equal(book.native,book.counts.native_TCP_milestones);assert.equal(book.chapters.length,book.counts.printed_chapters);assert(book.chapters.every(c=>c.present));
  for(const chapter of book.chapters){await page.selectOption('#lodge-native-chapter',chapter.id);assert.equal(await page.locator('#lodge-native-chapter').inputValue(),chapter.id);}
  if(book.contents!==null){await page.evaluate(()=>qa.change('#chapter-selector','contents'));assert.equal(await page.locator('#english .source-contents tei-list').textContent(),book.contents,'Original source contents '+name);}
  for(const n of important){console.log('Focused '+key+'.'+n);await go(`/antiquities/?book=${key}&niese=${n}&english=lodge1602&keep=batch-proof`);await installOracle(name,hi);assert.equal(await page.evaluate(()=>qa.actual().text),oracle.sections[n].text);const before=await page.evaluate(()=>qa.snapshot());
   for(const lang of ['greek','latin'])assert(before[lang].text.length>0,'Comparison pane text or source-qualified notice '+lang);
   await page.evaluate(()=>qa.change('#english-source-selector','whiston'));assert.equal(Number(await page.locator('#niese-selector').inputValue()),n);const after=await page.evaluate(()=>qa.snapshot());for(const lang of ['greek','latin'])assert.deepEqual(after[lang],before[lang],'Comparison pane citation and source retained');
   await page.evaluate(()=>qa.change('#english-source-selector','lodge1602'));assert.equal(await page.evaluate(()=>qa.actual().text),oracle.sections[n].text);assert.equal(new URL(page.url()).searchParams.get('keep'),'batch-proof');
   if(n<hi){await page.evaluate(()=>qa.click('#niese-next'));assert.equal(await page.evaluate(()=>qa.actual().text),oracle.sections[n+1].text);await page.goBack();await page.waitForFunction(n=>Number(document.querySelector('#niese-selector').value)===n,n);await page.goForward();await page.waitForFunction(n=>Number(document.querySelector('#niese-selector').value)===n+1,n);}
   await page.reload({waitUntil:'domcontentloaded'});await page.waitForFunction(()=>document.querySelector('#english tei-div2[type="niese-section"]'));await init();await installOracle(name,hi);const current=Number(new URL(page.url()).searchParams.get('niese'));assert.equal(await page.evaluate(()=>qa.actual().text),oracle.sections[current].text);
   await page.locator('#lodge-notes-visible').uncheck();assert.equal(await page.locator('#english tei-note:visible').count(),0);await page.locator('#lodge-notes-visible').check();focused.push({book:key,n,status:'PASS',checks:['direct_URL','approved_interval','source_switch','Greek_Latin_citation','previous_next','history','refresh','note_toggle']});
  }
  total+=checks.length;results.push({unit:name,identities:checks.length,status:'PASS',master_sha256:hash,literal_characters:book.literal.length,literal_sha256:sha(book.literal),source_counts:book.counts,native_chapters:book.chapters,sections:checks});save('LODGE_BATCH_BROWSER_QA.json',{status:'RUNNING',completed:total,units:results,focused});console.log('Lodge '+name+' '+checks.length+' exact intervals PASS');
 }
 await go('/antiquities/?book=preface&niese=26&english=lodge1602');await page.evaluate(()=>qa.change('#book-selector','1'));assert.equal(await page.locator('#english-source-selector').inputValue(),'lodge1602');assert.equal(new URL(page.url()).searchParams.get('book'),'1');
 // Existing book navigation opens Book view and clears the previous citation.
 // Niese view must then open at the new unit's first certified identity.
 await page.evaluate(()=>qa.change('#niese-level'));assert.equal(Number(await page.locator('#niese-selector').inputValue()),27);await installOracle('book-01',346);assert.equal(await page.evaluate(()=>qa.actual().text),await page.evaluate(()=>qa.expected[27].text));
 await page.evaluate(()=>qa.change('#book-selector','preface'));assert.equal(await page.locator('#english-source-selector').inputValue(),'lodge1602');await page.evaluate(()=>qa.change('#niese-level'));assert.equal(Number(await page.locator('#niese-selector').inputValue()),1);await installOracle('preface',26);assert.equal(await page.evaluate(()=>qa.actual().text),await page.evaluate(()=>qa.expected[1].text));focused.push({transition:'Proem I.26 → Book I view → I.27 → Proem view → I.1',status:'PASS',existing_book_navigation_preserved:true});
 if(args.includes('--vi-x')) {
  await go('/antiquities/?book=10&niese=238&english=lodge1602&lodgeNotes=0');await installOracle('book-10',281);
  assert.equal(await page.locator('#english .niese-correspondence-note').textContent(),'No separate corresponding passage in Lodge (1602)');
  assert.equal(await page.locator('#english tei-p').count(),0);assert.equal(await page.locator('#english tei-gap').count(),0);
  await page.evaluate(()=>qa.click('#niese-previous'));assert.equal(await page.evaluate(()=>qa.actual().text),await page.evaluate(()=>qa.expected[237].text));
  await page.evaluate(()=>qa.click('#niese-next'));assert.equal(await page.evaluate(()=>qa.actual().text),'');
  await page.evaluate(()=>qa.click('#niese-next'));assert.equal(await page.evaluate(()=>qa.actual().text),await page.evaluate(()=>qa.expected[239].text));
  assert.match(await page.evaluate(()=>qa.actual().text),/^Whereupon the\s+king called him vnto his presence,/);
  assert.equal(await page.locator('#english tei-note:visible').count(),0);assert.equal(new URL(page.url()).searchParams.get('lodgeNotes'),'0');
  await page.evaluate(()=>qa.change('#book-level'));const whole=await page.evaluate(()=>{const b=document.querySelector('#english tei-div1');return {text:qa.literal(b),empty:[...b.querySelectorAll('tei-p')].filter(p=>!p.textContent.trim()).length};});
  assert.equal(whole.empty,0);assert.equal(whole.text.split('Whereupon the  king called him vnto his presence,').length,2);
  await go('/antiquities/?book=10&niese=239&english=lodge1602');await installOracle('book-10',281);await page.evaluate(()=>qa.change('#chapter-level'));
  assert.equal((await page.evaluate(()=>qa.literal(document.querySelector('#english')))).split('Whereupon the  king called him vnto his presence,').length,2);
  await go('/antiquities/?book=10&niese=238&english=lodge1602');if(await page.evaluate(()=>document.documentElement.dataset.theme)!=='dark')await page.locator('#light-toggle').click();await page.waitForFunction(()=>document.documentElement.dataset.theme==='dark');
  await page.waitForTimeout(600);assert(await page.locator('#english .niese-correspondence-note').isVisible());assert.equal(await page.locator('#english .niese-correspondence-note').evaluate(e=>e.style.color),'var(--lj-brand-ink)');await page.screenshot({path:path.join(out,'Lodge-X-238-dark.png')});
  await page.locator('#light-toggle').click();await page.waitForFunction(()=>document.documentElement.dataset.theme==='light');await page.waitForTimeout(600);assert(await page.locator('#english .niese-correspondence-note').isVisible());assert.equal(await page.locator('#english .niese-correspondence-note').evaluate(e=>e.style.color),'var(--lj-brand-ink)');await page.screenshot({path:path.join(out,'Lodge-X-238-light.png')});
  focused.push({book:'10',n:238,status:'PASS',checks:['explicit_Lodge_notice','no_TCP_gap','no_borrowed_words','previous_237_empty_238_next_239','hidden_notes_URL','book_chapter_no_empty_paragraph_or_duplicate_239','light_dark_visibility']});
 }
 if(latest) {
  await go('/antiquities/?book=14&niese=218&english=lodge1602&lodgeNotes=0');await installOracle('book-14',491);
  const covers=await page.evaluate(()=>qa.metadata.project_navigation_covers.filter(c=>c.scheme==='subchapter'&&c.start_niese>=217&&c.start_niese<=265));
  for(const cover of covers) {
   const match=cover.project_boundary_id.match(/Subchapter-(\d+)-(\d+)$/);assert(match);
   await go(`/antiquities/?book=14&chapter=${match[1]}&subchapter=${match[2]}&english=lodge1602&lodgeNotes=0`);await installOracle('book-14',491);
   const actual=await page.evaluate(({lo,hi})=>({text:qa.literal(document.querySelector('#english')),expected:qa.expected.slice(lo,hi).map(x=>x.text).join(''),notices:document.querySelectorAll('#english .niese-correspondence-note').length,empty:[...document.querySelectorAll('#english tei-p')].filter(p=>!p.textContent.trim()).length}),{lo:cover.start_niese,hi:cover.end_niese_exclusive});
   assert.equal(actual.text,actual.expected);assert.equal(actual.empty,0);assert.equal(actual.notices,actual.expected.length===0?1:0);
   focused.push({context:cover.project_boundary_id,first:cover.start_niese,exclusiveEnd:cover.end_niese_exclusive,status:'PASS',grouped_absence_notice:actual.notices,no_empty_paragraphs:true});
  }
  await go('/antiquities/?book=14&niese=218&english=lodge1602');await installOracle('book-14',491);
  for(const theme of ['dark','light']) {if(await page.evaluate(()=>document.documentElement.dataset.theme)!==theme)await page.locator('#light-toggle').click();await page.waitForFunction(t=>document.documentElement.dataset.theme===t,theme);assert(await page.locator('#english .niese-correspondence-note').isVisible());await page.screenshot({path:path.join(out,'Lodge-XIV-218-'+theme+'.png')});}
  await page.evaluate(()=>qa.change('#book-level'));await installOracle('book-14',491);
  const whole=await page.evaluate(()=>({text:qa.literal(document.querySelector('#english tei-div1')),expected:qa.expected.map(x=>x.text).join(''),notices:document.querySelectorAll('#english .niese-correspondence-note').length,empty:[...document.querySelectorAll('#english tei-p')].filter(p=>!p.textContent.trim()).length}));
  assert.equal(whole.text,whole.expected);assert.equal(whole.notices,0);assert.equal(whole.empty,0);
  focused.push({book:'14',status:'PASS',checks:['full_native_narrative_once','zero_repetitive_notices','no_empty_paragraphs','light_dark_visibility']});
 }
 if(finalBatch){
  for(const [previous,next,endpoint] of [['15','16',425],['19','20',366]]){
   await go('/antiquities/?book='+previous+'&niese='+endpoint+'&english=lodge1602');
   await page.evaluate(b=>qa.change('#book-selector',b),next);assert.equal(await page.locator('#english-source-selector').inputValue(),'lodge1602');
   await page.evaluate(()=>qa.change('#niese-level'));await installOracle('book-'+next,next==='16'?404:268);assert.equal(Number(await page.locator('#niese-selector').inputValue()),1);assert.equal(await page.evaluate(()=>qa.actual().text),await page.evaluate(()=>qa.expected[1].text));focused.push({transition:previous+' → '+next,status:'PASS'});
  }
  await go('/antiquities/?book=20&niese=268&english=lodge1602&lodgeNotes=0');await installOracle('book-20',268);assert.equal(await page.evaluate(()=>qa.actual().text),await page.evaluate(()=>qa.expected[268].text));assert(await page.locator('#niese-next').isDisabled());assert.equal(await page.locator('#english tei-note:visible').count(),0);
  for(const theme of ['dark','light']){if(await page.evaluate(()=>document.documentElement.dataset.theme)!==theme)await page.locator('#light-toggle').click();await page.waitForFunction(t=>document.documentElement.dataset.theme===t,theme);assert(await page.locator('#english tei-div2[type="niese-section"]').isVisible());await page.screenshot({path:path.join(out,'Lodge-XX-268-'+theme+'.png')});}
  focused.push({book:'20',n:268,status:'PASS',checks:['exact_final_endpoint','no_next_work_text','lodgeNotes=0','light_dark']});
 }
 assert.equal(total,finalBatch?(focusOnly?17:1772):latest?(focusOnly?67:2130):args.includes('--vi-x')?(focusOnly?24:1764):(focusOnly?18:1361));assert.equal(errors.length,0,'No reader JavaScript exceptions');assert.equal(network.length,0,'No failed reader requests');save('LODGE_BATCH_BROWSER_QA.json',{status:'PASS',scope:focusOnly?'FOCUSED_PUBLICATION_SMOKE':(finalBatch?'ALL_1772_EXACT_INTERVALS':latest?'ALL_2130_EXACT_INTERVALS':args.includes('--vi-x')?'ALL_1764_EXACT_INTERVALS':'ALL_1361_EXACT_INTERVALS'),completed:total,oracle:'Independent physical traversal of all five pinned frozen masters; actual built-reader selector events and exact text, endpoints and native source features',units:results});save('LODGE_BATCH_FOCUSED_INTERACTION_QA.json',{status:'PASS',cases:focused});
}
try{
 if(args.includes('--theme-only')) {
  await go('/antiquities/?book=10&niese=238&english=lodge1602');
  const before=await page.evaluate(()=>document.documentElement.dataset.theme);
  await page.locator('#light-toggle').click();await page.waitForFunction(t=>document.documentElement.dataset.theme!==t,before);
  assert(await page.locator('#english .niese-correspondence-note').isVisible());
  await page.locator('#light-toggle').click();await page.waitForFunction(t=>document.documentElement.dataset.theme===t,before);
  assert(await page.locator('#english .niese-correspondence-note').isVisible());
  assert.equal(errors.length,0);assert.equal(network.length,0);save('THEME_CONTROL_QA.json',{status:'PASS',actual_theme_button:true,source_specific_notice_visible_in_both_themes:true});
 }
 else if(args.includes('--batch-only'))await verifyBatchUnits();
 else {
 const existing=mode==='baseline'?null:JSON.parse(fs.readFileSync(baselineFile));const regression=[];
 for(const url of cases){await go(url);const d=await page.evaluate(()=>qa.snapshot());const row={url,digest:sha(JSON.stringify(d)),texts:Object.fromEntries(Object.entries(d).map(([k,v])=>[k,{sha256:sha(v.text),characters:v.text.length}]))};if(existing)assert.equal(row.digest,existing.regression.find(r=>r.url===url).digest,'Protected reader '+url);regression.push(row);console.log('Regression '+url);}
 await go('/antiquities/?book=2&niese=1');const whiston=await page.evaluate(async()=>{const rows=[];for(let n=1;n<=349;n++){if(n>1)await qa.change('#niese-selector',n);rows.push({n,text:qa.pane(),protected:qa.snapshot()});}return rows;});const whistonDigests=whiston.map(r=>({n:r.n,sha256:sha(r.text),characters:r.text.length}));const comparisonDigests=whiston.map(r=>({n:r.n,Greek:sha(JSON.stringify(r.protected.greek)),Latin:sha(JSON.stringify(r.protected.latin))}));if(existing?.comparisonDigests)assert.deepEqual(comparisonDigests,existing.comparisonDigests,'All349 Greek/Latin source payloads unchanged');if(existing)assert.deepEqual(whistonDigests,existing.whiston,'All349 Whiston intervals unchanged');
 if(mode==='baseline'){save('BASELINE_BROWSER.json',{status:'PASS',base,regression,whiston:whistonDigests,comparisonDigests,console:errors,network});}
 else {save('CROSS_WORK_REGRESSION_QA.json',{status:'PASS',regression,whiston:whistonDigests,comparisonDigests});
 await go('/antiquities/?book=2&niese=1&english=lodge1602');
 const oracle=await installOracle('book-02',349);
 assert.equal(oracle.fullText.length,132602,'Frozen literal convention');assert.equal(sha(oracle.fullText),'ed69d4be091b81492a4c326696f1bf06dc70a7747ac6a036350e0f29b72d20ad');
 const lodge=[];
 for(let n=1;n<=349;n++){
  if(n>1)await page.evaluate(n=>qa.change('#niese-selector',n),n);
  const actual=await page.evaluate(()=>qa.actual());const paneIds=await page.locator('#english [id]').evaluateAll(nodes=>nodes.map(n=>n.id));assert.equal(new Set(paneIds).size,paneIds.length,'No duplicate Lodge IDs II.'+n);const expected=oracle.sections[n];assert.equal(actual.text,expected.text,'Exact frozen source II.'+n);for(const k of ['notes','gaps','pbs','native'])assert.deepEqual(actual[k],expected[k],k+' source loci II.'+n);
  const controls=await page.evaluate(()=>({selected:document.querySelector('#niese-selector').value,url:new URL(location.href).searchParams.get('niese'),source:document.querySelector('#english-source-selector').value,options:[...document.querySelector('#niese-selector').options].filter(o=>o.value).length,prev:document.querySelector('#niese-previous').disabled,next:document.querySelector('#niese-next').disabled}));
  assert.equal(Number(controls.selected),n);assert.equal(Number(controls.url),n);assert.equal(controls.source,'lodge1602');assert.equal(controls.options,349);assert.equal(controls.prev,n===1);assert.equal(controls.next,n===349);
  await page.evaluate(n=>{for(const lang of ['greek','latin']){const box=document.querySelector('#'+lang+'-pane-select');if(!box)throw Error('Missing language visibility control');box.click();if(Number(document.querySelector('#niese-selector').value)!==n)throw Error('Language changes Niese identity');box.click();} },n);
  // Actual controls navigate to both adjacent sections; assertions include content.
  if(n<349){await page.evaluate(()=>qa.click('#niese-next'));const next=await page.evaluate(()=>qa.actual().text);assert.equal(next,oracle.sections[n+1].text,'Next II.'+n);await page.evaluate(n=>qa.change('#niese-selector',n),n);}
  if(n>1){await page.evaluate(()=>qa.click('#niese-previous'));assert.equal(await page.evaluate(()=>qa.actual().text),oracle.sections[n-1].text,'Previous II.'+n);await page.evaluate(n=>qa.change('#niese-selector',n),n);}
  await page.evaluate(()=>qa.change('#english-source-selector','whiston'));assert.equal(Number(await page.locator('#niese-selector').inputValue()),n);assert.equal(sha(await page.evaluate(()=>qa.pane())),existing.whiston[n-1].sha256,'Whiston switch II.'+n);
  await page.evaluate(()=>qa.change('#english-source-selector','lodge1602'));assert.equal(Number(await page.locator('#niese-selector').inputValue()),n);assert.equal(await page.evaluate(()=>qa.actual().text),expected.text,'Lodge return II.'+n);
  lodge.push({identity:'2.'+n,status:'PASS',characters:actual.text.length,expected_sha256:sha(expected.text),actual_sha256:sha(actual.text),incipit:actual.text.slice(0,130),tail:actual.text.slice(-130),notes:actual.notes.length,gaps:actual.gaps.length,page_breaks:actual.pbs.length,native_milestones:actual.native.length,adjacent_navigation:'PASS',source_switch:'PASS'});
  if(n%30===0){save('LODGE_349_BROWSER_QA.json',{status:'RUNNING',completed:n,sections:lodge});console.log('Lodge II.'+n);}
 }
 save('LODGE_349_BROWSER_QA.json',{status:'PASS',identities:349,oracle:'Independently traversed immutable frozen scholarly XML, excluding original paratext under the certified literal convention',sections:lodge});
 const representatives=[1,6,12,38,66,73,75,79,80,95,104,107,118,140,142,152,159,209,284,326,337,349];save('LODGE_REPRESENTATIVE_BROWSER_QA.json',{status:'PASS',cases:lodge.filter(r=>representatives.includes(Number(r.identity.split('.')[1])))});
 await page.evaluate(()=>qa.change('#book-level'));const book=await page.evaluate(()=>{const node=document.querySelector('#english tei-div1');return {literal:qa.literal(node),notes:[...node.querySelectorAll('tei-note')].map(n=>({id:n.id,text:n.textContent,visible:getComputedStyle(n).display!=='none'})),gaps:node.querySelectorAll('tei-gap').length,pbs:node.querySelectorAll('tei-pb').length,native:node.querySelectorAll('tei-milestone:not([unit="niese"])').length,chapters:[...document.querySelector('#lodge-native-chapter').options].filter(o=>o.value).map(o=>({id:o.value,present:!!document.getElementById(o.value)})),contents:node.querySelector('tei-list').textContent,paragraphs:node.querySelectorAll('tei-p').length};});
 assert.equal(book.literal,oracle.fullText);assert.equal(book.notes.length,151);assert(book.notes.every(n=>n.visible));assert.equal(book.gaps,132);assert.equal(book.pbs,25);assert.equal(book.native,149);assert.equal(book.paragraphs,33);assert.equal(book.chapters.length,7);assert(book.chapters.every(c=>c.present));
 for(const c of book.chapters)await page.selectOption('#lodge-native-chapter',c.id);
 await page.screenshot({path:path.join(out,'Lodge-Book-II.png'),fullPage:false});
 save('NATIVE_CHAPTER_AND_CONTENTS_QA.json',{status:'PASS',literal_characters:book.literal.length,literal_sha256:sha(book.literal),chapters:book.chapters,paragraphs:book.paragraphs,contents_sha256:sha(book.contents)});
 save('TCP_GAPS_AND_PB_QA.json',{status:'PASS',gaps:book.gaps,page_breaks:book.pbs,native_milestones:book.native,exact_interval_source_tokens:'PASS'});
 save('MARGINAL_NOTES_QA.json',{status:'PASS',book_notes:book.notes.length,interval_notes:lodge.reduce((n,r)=>n+r.notes,0),pre_first_identity_note:book.notes[0],notes:book.notes});
 await page.evaluate(()=>qa.change('#chapter-selector','contents'));assert.equal(await page.locator('#english .source-contents tei-list').textContent(),book.contents,'Original Lodge contents');
 await page.evaluate(()=>qa.change('#niese-level'));await page.evaluate(()=>qa.change('#niese-selector',284));assert.equal(await page.locator('#english .niese-correspondence-note,.structural-unavailable,.tei-omission-notice').count(),0,'No witness qualification leakage');
 await page.screenshot({path:path.join(out,'Lodge-II-284.png')});

 const stateChecks=[];
 const hide=async()=>{await page.locator('#lodge-notes-visible').uncheck();await page.waitForFunction(()=>new URL(location.href).searchParams.get('lodgeNotes')==='0');assert.equal(await page.locator('#english tei-note:visible').count(),0);};
 await hide();await page.evaluate(()=>qa.change('#niese-selector',6));assert.equal(await page.locator('#english tei-note:visible').count(),0);assert.equal(new URL(page.url()).searchParams.get('lodgeNotes'),'0');
 await page.evaluate(()=>qa.change('#english-source-selector','whiston'));assert.equal(await page.locator('#english.lodge-notes-hidden').count(),0);await page.evaluate(()=>qa.change('#english-source-selector','lodge1602'));assert.equal(await page.locator('#english tei-note:visible').count(),0);
 await page.evaluate(()=>qa.click('#niese-next'));assert.equal(new URL(page.url()).searchParams.get('lodgeNotes'),'0');await page.goBack();await page.waitForFunction(()=>document.querySelector('#niese-selector').value==='6');await page.goForward();await page.waitForFunction(()=>document.querySelector('#niese-selector').value==='7');assert.equal(await page.locator('#english tei-note:visible').count(),0);
 await page.reload({waitUntil:'domcontentloaded'});await page.waitForFunction(()=>document.querySelector('#english tei-div2[type="niese-section"][n="7"]'));assert.equal(await page.locator('#english tei-note:visible').count(),0);await init();
 await page.locator('#lodge-notes-visible').check();await page.waitForFunction(()=>!new URL(location.href).searchParams.has('lodgeNotes'));stateChecks.push('notes hidden/visible preference through identity/source/previous-next/back-forward/refresh');
 await page.evaluate(()=>qa.change('#chapter-level'));assert.equal(await page.locator('#english [data-english-segmentation="containing-context"]').count(),1);assert.match(await page.locator('#english .niese-context-note').textContent(),/printed chapters are independent/);
 await page.evaluate(()=>qa.change('#subchapter-level'));assert.equal(await page.locator('#english [data-english-segmentation="containing-context"]').count(),1);await page.evaluate(()=>qa.change('#section-level'));assert.equal(await page.locator('#english [data-english-segmentation="containing-context"]').count(),1);await page.evaluate(()=>qa.change('#bamberg-level'));assert.equal(await page.locator('#english [data-english-segmentation="containing-context"]').count(),1);stateChecks.push('Chapter/Subchapter/Alignment/Bamberg use explicitly labelled Lodge containing Niese context');
 for(const url of ['/antiquities/?book=2&niese=1&english=lodge1602&keep=proof','/antiquities/?book=2&niese=349&english=lodge1602&lodgeNotes=0']){await go(url);const n=Number(new URL(page.url()).searchParams.get('niese'));assert.equal(Number(await page.locator('#english tei-div2[type="niese-section"]').getAttribute('n')),n);if(n===1){assert.equal(await page.locator('#english .lodge-source-context tei-note').count(),1);assert.equal(await page.locator('#english tei-div2[type="niese-section"] > .lodge-source-context').count(),1);await page.evaluate(()=>qa.change('#english-source-selector','whiston'));await page.evaluate(()=>qa.change('#english-source-selector','lodge1602'));assert.equal(new URL(page.url()).searchParams.get('keep'),'proof');}else assert.equal(await page.locator('#english tei-note:visible').count(),0);}
 stateChecks.push('direct endpoints, independent pre-II.1 note context, unrelated query parameter retained');
 for(const b of ['preface',...Array.from({length:20},(_,i)=>String(i+1))]){await go('/antiquities/?book='+b+'&english=lodge1602');assert.equal(await page.locator('#english-source-selector option[value="lodge1602"]').count(),1);assert.equal(await page.locator('#english-source-selector').inputValue(),'lodge1602');}stateChecks.push('Complete Lodge Proem and Books I–XX source availability');
 for(const n of ['0','350','not-a-number']){await go('/antiquities/?book=2&english=lodge1602&niese='+n);assert.equal(await page.locator('#unsupported-niese-notice').count(),1);assert.equal(await page.locator('#english tei-p').count(),0);}stateChecks.push('invalid Lodge Niese requests show no substituted text, no II.350');
 save('SOURCE_SWITCH_AND_URL_QA.json',{status:'PASS',all349_source_switch_checks:'PASS',checks:stateChecks});
 save('BROWSER_SUMMARY.json',{status:'PASS',identities:349,section_assertions:['literal_text','exclusive_end','notes','gaps','page_breaks','source_milestones','previous','next','source_switch'],representative_cases:representatives.length,protected_views:regression.length,protected_whiston_intervals:349});
 if(args.includes('--batch'))await verifyBatchUnits();

 }
 }
}catch(e){save('RUN_FAILURE.json',{status:'FAIL',message:e.stack,errors,network});throw e;}finally{save('CONSOLE_AND_NETWORK_QA.json',{errors,network});await browser.close();if(server)await new Promise(r=>server.close(r));}
