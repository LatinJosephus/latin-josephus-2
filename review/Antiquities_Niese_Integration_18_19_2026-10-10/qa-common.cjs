const fs=require('fs'),path=require('path'),http=require('http'),crypto=require('crypto');
const {chromium}=require('C:/Program Files/WindowsApps/OpenAI.CodexPrimaryRuntime.v26-1007-641-0_26.1007.641.0_x64__3k8sg7r9htsxt/dependencies/node/node_modules/playwright');
const runtime='C:/workspace/Antiquities-Niese-18-19-integration-runtime-20261010',root=path.resolve(__dirname,'../..');
const authority=path.join(root,'review/Antiquities_Niese_BookXI_2026-10-09');
const authorityNames=new Set(['EXPECTED_SELECTIONS.json','AUTHORIZED_ADDITIONS.json','TRADITIONAL_EXPECTATIONS.json']);
const load=p=>JSON.parse(fs.readFileSync(!fs.existsSync(p)&&authorityNames.has(path.basename(p))?path.join(authority,path.basename(p)):p,'utf8')),save=(p,x)=>fs.writeFileSync(p,JSON.stringify(x,null,2)+'\n');
const norm=s=>String(s||'').replace(/\s+/g,' ').trim(),hash=x=>crypto.createHash('sha256').update(typeof x==='string'?x:JSON.stringify(x)).digest('hex');
function instrument(s){
 s=s.replace('  bookTitle.innerText = activeWork.title;',`  window.__qa={getState:()=>({...state}),getData:()=>fullData,view:()=>viewData,reload,setState,selectView,selectCanonicalView,currentIdBase,canonicalNieseStartEntries,antiquitiesNieseStartEntries,traditionalRangeView,antiquitiesNieseFragmentView:typeof antiquitiesNieseFragmentView==='function'?antiquitiesNieseFragmentView:null,identityRegistry:nieseIdentityRegistry,traditionalRows,bambergRows,bambergSelection,traditionalRegistry:()=>traditionalRegistry,alignmentRegistry:()=>alignmentRangeRegistry,bambergRegistry:()=>bambergRegistry,setSectionSelectOptions,assign:patch=>Object.assign(state,patch)};\n  bookTitle.innerText = activeWork.title;`);
 s=s.replaceAll('setState(() => {','window.__qaPending=setState(() => {');
 s=s.replace('    syncNavigationControls();','    syncNavigationControls(); window.__qaRenderedState={...state};');
 return s.replace('  reload().then(() => {','  reload().then(() => { window.__qaReady=true; document.querySelector("#collapse-settings")?.classList.add("show");');
}
function serve(site,qa=true){return http.createServer((req,res)=>{
 const u=new URL(req.url,'http://localhost');let f=path.resolve(site,'.'+decodeURIComponent(u.pathname));
 if(!f.startsWith(path.resolve(site)+path.sep)){res.statusCode=403;return res.end();}
 if(fs.existsSync(f)&&fs.statSync(f).isDirectory())f=path.join(f,'index.html');
 if(!fs.existsSync(f)){res.statusCode=404;return res.end();}
 let raw=fs.readFileSync(f);if(qa&&f.endsWith('renderTei.js'))raw=Buffer.from(instrument(raw.toString()));
 const types={'.xml':'application/xml','.json':'application/json','.js':'text/javascript','.css':'text/css','.html':'text/html','.png':'image/png','.svg':'image/svg+xml'};
 res.setHeader('Content-Type',types[path.extname(f)]||'application/octet-stream');res.end(raw);
});}
async function listen(s,port=0){try{await new Promise((r,j)=>{s.once('error',j);s.listen(port,'127.0.0.1',r)});}catch(e){if(e.code!=='EADDRINUSE')throw e;await new Promise((r,j)=>{s.once('error',j);s.listen(0,'127.0.0.1',r)});}return `http://127.0.0.1:${s.address().port}`;}
function narrative(node){if(!node)return null;const c=node.cloneNode(true);c.querySelectorAll('tei-num,tei-milestone,tei-note,tei-app,tei-rdg,.niese-context-note,.niese-correspondence-note,.structural-unavailable,.niese-source-passage-label').forEach(x=>x.remove());return [...(c.matches?.('tei-p')?[c]:[]),...c.querySelectorAll('tei-p')].filter(p=>!p.closest('tei-div2[n="0"]')).map(p=>p.textContent).join('').replace(/\s+/g,' ').trim();}
module.exports={fs,path,chromium,runtime,root,load,save,norm,hash,serve,listen,narrative};
