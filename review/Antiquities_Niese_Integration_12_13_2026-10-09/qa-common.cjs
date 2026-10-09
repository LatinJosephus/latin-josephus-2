const fs=require('fs'),path=require('path'),http=require('http'),crypto=require('crypto');
const {chromium}=require('C:/Users/Pollard_R/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const packet=__dirname,root=path.resolve(packet,'../..'),build='C:/workspace/Antiquities-Niese-12-13-integration-runtime-20261009';
const expected=JSON.parse(fs.readFileSync(path.join(root,'review/Antiquities_Niese_BookIX_2026-10-09/EXPECTED_INTERVALS.json'),'utf8'));
const digest=x=>crypto.createHash('sha256').update(JSON.stringify(x)).digest('hex');
function instrument(source){
 source=source.replace('  bookTitle.innerText = activeWork.title;',`  window.__qa={getState:()=>({...state}),getData:()=>fullData,view:()=>viewData,reload,setState,selectView,selectCanonicalView,currentIdBase,canonicalNieseStartEntries,antiquitiesNieseStartEntries,traditionalRangeView,traditionalRows,bambergRows,bambergSelection,traditionalRegistry:()=>traditionalRegistry,alignmentRegistry:()=>alignmentRangeRegistry,bambergRegistry:()=>bambergRegistry,assign:patch=>Object.assign(state,patch)};
  bookTitle.innerText = activeWork.title;`);
 source=source.replaceAll('setState(() => {','window.__qaPending = setState(() => {');
 source=source.replace('    syncNavigationControls();','    syncNavigationControls(); window.__qaRenderedState={...state};');
 return source.replace('  reload().then(() => {','  reload().then(() => { window.__qaReady=true; document.querySelector("#collapse-settings")?.classList.add("show");');
}
function serve(site,qa=true){return http.createServer((req,res)=>{
 const u=new URL(req.url,'http://localhost');let f=path.resolve(site,'.'+decodeURIComponent(u.pathname));
 if(!f.startsWith(path.resolve(site)+path.sep)){res.statusCode=403;return res.end();}
 if(fs.existsSync(f)&&fs.statSync(f).isDirectory())f=path.join(f,'index.html');
 if(!fs.existsSync(f)){res.statusCode=404;return res.end();}
 let raw=fs.readFileSync(f);if(qa&&f.endsWith('renderTei.js'))raw=Buffer.from(instrument(raw.toString()));
 res.setHeader('Content-Type',f.endsWith('.svg')?'image/svg+xml':f.endsWith('.png')?'image/png':f.endsWith('.jpg')?'image/jpeg':f.endsWith('.xml')?'application/xml':f.endsWith('.json')?'application/json':f.endsWith('.js')?'text/javascript':f.endsWith('.css')?'text/css':f.endsWith('.html')?'text/html':'application/octet-stream');res.end(raw);
});}
const normalize=s=>String(s||'').replace(/\s+/g,' ').trim();
function narrative(node){
 if(!node)return null;const c=node.cloneNode(true);
 c.querySelectorAll('tei-num,tei-milestone,tei-note,tei-app,tei-rdg,.niese-context-note,.niese-correspondence-note,.structural-unavailable').forEach(x=>x.remove());
 return [...(c.matches?.('tei-p')?[c]:[]),...c.querySelectorAll('tei-p')].filter(p=>!p.closest('tei-div2[n="0"]')).map(p=>p.id==='latin-book09-num288'?p.textContent.replace(/explicit liber nonus$/,''):p.textContent).join('').replace(/\s+/g,' ').trim();
}
function canonicalHTML(node,book,language){
 if(!node)return null;const c=node.cloneNode(true);
 if([8,9,10].includes(Number(book))){c.querySelectorAll('tei-milestone[unit="niese"],.niese-correspondence-note').forEach(n=>n.remove());if(language==='Greek')c.querySelectorAll('tei-num').forEach(n=>n.remove());}
 return c.outerHTML;
}
module.exports={fs,path,http,crypto,chromium,packet,root,build,expected,digest,instrument,serve,normalize,narrative,canonicalHTML};
