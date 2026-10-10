const fs=require('fs'),path=require('path'),http=require('http'),crypto=require('crypto');
const {chromium}=require('C:/Program Files/WindowsApps/OpenAI.CodexPrimaryRuntime.v26-1007-641-0_26.1007.641.0_x64__3k8sg7r9htsxt/dependencies/node/node_modules/playwright');
const packet=__dirname,root=path.resolve(packet,'../..'),runtime='C:/workspace/Antiquities-Niese-20-integration-runtime-20261010';
const candidate=path.join(runtime,'final-site'),baseline=path.join(runtime,'baseline-site');
const sha=x=>crypto.createHash('sha256').update(typeof x==='string'||Buffer.isBuffer(x)?x:JSON.stringify(x)).digest('hex');
function instrument(s){
 const key='  bookTitle.innerText = activeWork.title;';if(!s.includes(key))throw Error('Instrumentation point absent');
 s=s.replace(key,`  window.__qa={getState:()=>({...state}),getData:()=>fullData,view:()=>viewData,assign:p=>Object.assign(state,p),reload,setState,selectView,selectCanonicalView,currentIdBase,canonicalNieseStartEntries,antiquitiesNieseStartEntries,traditionalRangeView,traditionalPoint,antiquitiesNieseFragmentView,identityRegistry:nieseIdentityRegistry,traditionalRows,bambergRows,milestoneChapterView,setSectionSelectOptions,alignedParagraphsForCanonicalId,traditionalRegistry:()=>traditionalRegistry,alignmentRegistry:()=>alignmentRangeRegistry,bambergRegistry:()=>bambergRegistry};\n${key}`);
 s=s.replaceAll('setState(() => {','window.__qaPending = setState(() => {');
 s=s.replace('    syncNavigationControls();','    syncNavigationControls(); window.__qaRenderedState={...state};');
 return s.replace('  reload().then(() => {','  reload().then(() => { window.__qaReady=true; document.querySelector("#collapse-settings")?.classList.add("show");');
}
function serve(site,qa=true){return http.createServer((req,res)=>{
 const url=new URL(req.url,'http://localhost');let file=path.resolve(site,'.'+decodeURIComponent(url.pathname));
 if(!file.startsWith(path.resolve(site)+path.sep)){res.statusCode=403;return res.end();}
 if(fs.existsSync(file)&&fs.statSync(file).isDirectory())file=path.join(file,'index.html');
 if(!fs.existsSync(file)){res.statusCode=404;return res.end();}
 let raw=fs.readFileSync(file);if(qa&&file.endsWith('renderTei.js'))raw=Buffer.from(instrument(raw.toString()));
 const mime={'.xml':'application/xml','.json':'application/json','.js':'text/javascript','.css':'text/css','.html':'text/html','.svg':'image/svg+xml','.png':'image/png','.jpg':'image/jpeg'};
 res.setHeader('Content-Type',mime[path.extname(file)]||'application/octet-stream');res.end(raw);
});}
async function listen(server,port=0){
 await new Promise((resolve,reject)=>{server.once('error',reject);server.listen(port,'127.0.0.1',resolve);});
 return `http://127.0.0.1:${server.address().port}`;
}
function normalize(value){return String(value||'').replace(/\s+/g,' ').trim();}
function narrative(node){
 if(!node)return null;const copy=node.cloneNode(true);
 copy.querySelectorAll('tei-num,tei-milestone,tei-note,tei-app,tei-rdg,.niese-context-note,.niese-correspondence-note,.structural-unavailable').forEach(x=>x.remove());
 return [...(copy.matches?.('tei-p')?[copy]:[]),...copy.querySelectorAll('tei-p')]
  .filter(p=>!p.closest('tei-div2[n="0"]')).map(p=>p.textContent).join('').replace(/\s+/g,' ').trim();
}
function cleanContaining(node,book,language){
 if(!node)return null;const copy=node.cloneNode(true);
 copy.querySelectorAll('tei-milestone[unit^="niese"],.niese-correspondence-note,.niese-context-note').forEach(x=>x.remove());
 if([16,17].includes(Number(book))&&language==='Greek')copy.querySelectorAll('tei-num').forEach(x=>x.remove());
 return copy.outerHTML.replaceAll(location.origin,'LOCAL_ORIGIN');
}
async function open(page,origin,query,work='antiquities',qa=true){
 await page.goto(`${origin}/${work}/?${query}`,{waitUntil:'domcontentloaded'});
 if(qa)await page.waitForFunction(()=>window.__qaReady,{},{timeout:60000});
 else await page.waitForFunction(()=>document.querySelector('#book-selector')?.options.length>1&&document.querySelector('#latin tei-p,#latin .structural-unavailable'),{},{timeout:60000});
}
async function change(page,selector,value){await page.selectOption(selector,String(value));await page.evaluate(()=>window.__qaPending);}
async function capture(page){return page.evaluate(code=>{
 const text=eval('('+code+')');const languages={};
 for(const lang of ['Latin','Greek','English']){
  const el=document.querySelector('#'+lang.toLowerCase());
  languages[lang]={text:text(el),unavailable:!!el.querySelector('.structural-unavailable'),
   context:!!el.querySelector('.niese-context-note'),note:el.querySelector('.niese-correspondence-note')?.textContent||null,
   fragments:el.querySelectorAll('tei-div[type="physical-fragment"]').length};
 }
 const ids=[...document.querySelectorAll('[id]')].map(n=>n.id);
 return {languages,duplicateIDs:ids.filter((id,i)=>ids.indexOf(id)!==i),url:location.href,
  nieseValue:document.querySelector('#niese-selector')?.value,
  previousDisabled:document.querySelector('#niese-previous')?.disabled,nextDisabled:document.querySelector('#niese-next')?.disabled};
},narrative.toString());}
function builtHashes(){
 const files=['assets/js/renderTei.js','assets/xml/antiquities/structure.xml','assets/css/tei.css',
  ...[16,17].flatMap(b=>['Latin','Greek','English'].map(l=>`assets/xml/antiquities/${l}/book-${b}.xml`)),
  ...[16,17].map(b=>`assets/xml/antiquities/niese/book-${b}.json`)];
 return files.map(file=>{const hash=sha(fs.readFileSync(path.join(candidate,file)));if(hash!==sha(fs.readFileSync(path.join(root,file))))throw Error('Candidate build drift '+file);return {file,sha256:hash};});
}
module.exports={fs,path,http,crypto,chromium,packet,root,runtime,candidate,baseline,sha,instrument,serve,listen,normalize,narrative,cleanContaining,open,change,capture,builtHashes};
