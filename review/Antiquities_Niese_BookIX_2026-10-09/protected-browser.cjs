const fs=require('fs'),path=require('path'),http=require('http'),crypto=require('crypto');
const {chromium}=require('C:/Users/Pollard_R/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const packet=__dirname,root=path.resolve(packet,'../..'),build='C:/workspace/Antiquities-Niese-09-runtime-20261009/build';
const expected=JSON.parse(fs.readFileSync(path.join(packet,'EXPECTED_INTERVALS.json'),'utf8'));
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
 res.setHeader('Content-Type',f.endsWith('.xml')?'application/xml':f.endsWith('.json')?'application/json':f.endsWith('.js')?'text/javascript':f.endsWith('.css')?'text/css':f.endsWith('.html')?'text/html':'application/octet-stream');res.end(raw);
});}
const normalize=s=>String(s||'').replace(/\s+/g,' ').trim();
function narrative(node){
 if(!node)return null;const c=node.cloneNode(true);
 c.querySelectorAll('tei-num,tei-milestone,tei-note,tei-app,tei-rdg,.niese-context-note,.niese-correspondence-note,.structural-unavailable').forEach(x=>x.remove());
 return [...(c.matches?.('tei-p')?[c]:[]),...c.querySelectorAll('tei-p')].filter(p=>!p.closest('tei-div2[n="0"]')).map(p=>p.textContent).join('').replace(/\s+/g,' ').trim();
}
function canonicalHTML(node,book,language){
 if(!node)return null;const c=node.cloneNode(true);
 if([8,9,10].includes(Number(book))){c.querySelectorAll('tei-milestone[unit="niese"],.niese-correspondence-note').forEach(n=>n.remove());if(language==='Greek')c.querySelectorAll('tei-num').forEach(n=>n.remove());}
 return c.outerHTML;
}
async function main(){
 const report={scope:'ACTUAL_BUILT_IMPLEMENTATION',mode:'protected-regressions',errors:[],consoleErrors:[],networkFailures:[],started:new Date().toISOString()};
 const servers=[serve(path.join(build,'site')),serve(path.join(build,'baseline-site')),serve(path.join(build,'site'),false)];
 await Promise.all(servers.map(s=>new Promise(r=>s.listen(0,'127.0.0.1',r))));const origins=servers.map(s=>`http://127.0.0.1:${s.address().port}`);report.origins=origins;
 const context=await chromium.launchPersistentContext('C:/workspace/Antiquities-Niese-09-runtime-20261009/profile-protected',{headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 const page=await context.newPage();
 page.on('pageerror',e=>report.errors.push(String(e)));page.on('console',m=>{if(m.type()==='error')report.consoleErrors.push(m.text());});
 page.on('requestfailed',r=>report.networkFailures.push({url:r.url(),reason:r.failure()?.errorText}));
 async function open(route,which=0){await page.goto(origins[which]+route,{waitUntil:'domcontentloaded'});if(which<2)await page.waitForFunction(()=>window.__qaReady,{},{timeout:60000});else await page.waitForFunction(()=>document.querySelector('#book-selector')?.options.length>1&&document.querySelector('#latin tei-p, #latin .structural-unavailable'),{},{timeout:60000});}
 async function change(selector,value){await page.selectOption(selector,value);await page.evaluate(()=>window.__qaPending);}
 try{
  report.antiquities={traditional:[],bamberg:[],alignment:[],niese:[],contents:[]};
  for(const book of process.argv.includes('--cross-only')?[]:['preface',...Array.from({length:20},(_,i)=>String(i+1))]){
   const captures=[];
   for(const which of [1,0]){
    await open(`/antiquities/?book=${book}`,which);
    captures.push(await page.evaluate(({book,htmlCode})=>{
     const html=eval('('+htmlCode+')'),q=window.__qa,data=q.getData(),capture=()=>Object.fromEntries(Object.entries(data).map(([l,d])=>[l,html(q.selectView(l,d,q.currentIdBase()),book,l)]));
     const traditional=(q.traditionalRegistry()||[]).filter(r=>book==='preface'?r.context==='Proem':r.context!=='Proem'&&Number(r.book)===Number(book)).map(r=>[r.id,Object.fromEntries(Object.entries(data).map(([l,d])=>[l,html(q.traditionalRangeView(l,d,r),book,l)]))]);
     const bamberg=q.bambergRows().map(r=>[r.id,Object.fromEntries(Object.entries(data).map(([l,d])=>[l,html(q.traditionalRangeView(l,d,r),book,l)]))]);
     q.assign({viewingLevel:'section-level',sectionNum:null});const units=[...document.querySelector('#section-selector').options].filter(o=>o.value&&o.value!=='contents').map(o=>o.value);const alignment=units.map(unit=>{q.assign({sectionNum:unit});return [unit,capture()];});
     const niese=[];if(Number(book)<=10 && Number(book)!==9){for(const entry of q.canonicalNieseStartEntries()){q.assign({viewingLevel:'niese-level',nieseNum:String(entry.number),chapterNum:null,subchapterNum:null,sectionNum:null});niese.push([entry.number,capture()]);}}
     return {traditional,bamberg,alignment,niese};
    },{book,htmlCode:canonicalHTML.toString()}));
   }
   for(const category of ['traditional','bamberg','alignment','niese']){
    if(JSON.stringify(captures[0][category])!==JSON.stringify(captures[1][category])){
     fs.writeFileSync(path.join(packet,`FAIL_${category}_${book}.json`),JSON.stringify(captures,null,2));throw Error(`${category} baseline mismatch book ${book}`);
    }
    report.antiquities[category].push({book,identities:captures[1][category].length,three_language_DOM_and_order:'PASS',digest:digest(captures[1][category])});
   }
   // Actual source contents are fetched/rendered by the current registry.
   const contents=[];for(const which of [1,0]){await open(`/antiquities/?book=${book}&view=contents`,which);contents.push(await page.evaluate(()=>Object.fromEntries(Object.entries(window.__qa.view()).map(([l,d])=>[l,d?.outerHTML||null]))));}
   if(JSON.stringify(contents[0])!==JSON.stringify(contents[1]))throw Error('source contents '+book);report.antiquities.contents.push({book,result:'PASS'});console.log('protected Antiquities',book);
  }
  report.crossWorks=[];
  for(const [work,count] of [['bellum-judaicum',7],['contra-apionem',2],['deh',5]]){
   for(let book=1;book<=count;book++){
    const captures=[];
    for(const which of [1,0]){
     await open(`/${work}/?book=${book}`,which);
     captures.push(await page.evaluate(()=>{
      // The two disposable servers have different ports. Compare the full
      // DOM after removing only each server's origin from local deep links.
      const q=window.__qa,data=q.getData(),capture=()=>Object.fromEntries(Object.entries(data).map(([l,d])=>[l,q.selectView(l,d,q.currentIdBase())?.outerHTML.replaceAll(location.origin,'LOCAL_ORIGIN')||null]));
      const whole=capture(),niese=[];for(const e of q.canonicalNieseStartEntries()){q.assign({viewingLevel:'niese-level',nieseNum:String(e.number)});niese.push([e.number,capture()]);}
      return {whole,niese};
     }));
    }
    if(JSON.stringify(captures[0])!==JSON.stringify(captures[1])){fs.writeFileSync(path.join(packet,`FAIL_cross_${work}_${book}.json`),JSON.stringify(captures,null,2));throw Error(`Cross-work ${work} ${book}`);}report.crossWorks.push({work,book,niese:captures[1].niese.length,result:'PASS',digest:digest(captures[1])});console.log('protected',work,book);
   }
  }
  // Existing dedicated suites additionally cover Lodge notes, source switching,
  // Bellum chapter ranges and DEH/Contra Apionem URLs against the same build.
 
 if(report.errors.length)throw Error('Browser exceptions '+JSON.stringify(report.errors));
 report.finished=new Date().toISOString();report.result='PASS';
 fs.writeFileSync(path.join(packet,report.mode==='new-books'?'NEW_BOOK_BROWSER_QA.json':report.mode==='ui-supplement'?'UI_SUPPLEMENT_QA.json':'PROTECTED_BROWSER_QA.json'),JSON.stringify(report,null,2));console.log('PASS',report.mode);
 }catch(error){report.result='FAIL';report.failure=String(error);fs.writeFileSync(path.join(packet,'FAILED_BROWSER_QA.json'),JSON.stringify(report,null,2));throw error;}
 finally{await context.close();await Promise.all(servers.map(s=>new Promise(r=>s.close(r))));}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
