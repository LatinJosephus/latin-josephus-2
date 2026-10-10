// Differential live-DOM replay: every prior selectable identity, not just a census.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {chromium}=require('C:/Program Files/WindowsApps/OpenAI.CodexPrimaryRuntime.v26-1007-641-0_26.1007.641.0_x64__3k8sg7r9htsxt/dependencies/node/node_modules/playwright');
const {serve,narrative}=require('./final_reader.cjs');
const P=__dirname,runtime='C:/workspace/Antiquities-Niese-18-19-integration-runtime-20261010',sha=x=>crypto.createHash('sha256').update(x).digest('hex');
async function main(){
 const result={scope:'ALL_5231_PRIOR_IDENTITIES_ACTUAL_BROWSER_BASELINE_VS_ACTUAL_FINAL_PRODUCTION',status:'RUNNING',started:new Date().toISOString(),books:[],selections:[],protectedRoutes:[],errors:[],knownBaselineIssues:[]};
 const resume=false; // Final certification always replays every prior identity afresh.
 if(resume){const raw=fs.readFileSync(path.join(P,'PROTECTED_FINAL_BROWSER_CHECKPOINT.json')),old=JSON.parse(raw);if(old.selections.length!==5231||old.books.length!==14||old.errors.length)throw Error('Incomplete or failed replay checkpoint');result.books=old.books;result.selections=old.selections;result.reusedCompletedReplay={checkpoint_sha256:sha(raw),started:old.started,identities:old.selections.length,reason:'All actual selections completed before the separately expected unsupported I.1 exception timed out the initial diagnostic harness.'};}
 const servers=['baseline-site','final-site'].map(s=>serve(path.join(runtime,s)));await Promise.all(servers.map(s=>new Promise((r,j)=>{s.once('error',j);s.listen(0,'127.0.0.1',r);})));
 const origins=servers.map(s=>'http://127.0.0.1:'+s.address().port),context=await chromium.launchPersistentContext(path.join(runtime,'browser-protected-final-exhaustive'),{headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'}),pages=await Promise.all([context.newPage(),context.newPage()]);
 pages.forEach((p,i)=>{p.on('pageerror',e=>result.errors.push({side:i,error:String(e),url:p.url()}));p.on('requestfailed',r=>result.errors.push({side:i,error:r.failure()?.errorText,url:r.url()}));p.on('console',m=>{if(m.type()==='error')result.errors.push({side:i,error:m.text(),url:p.url()});});});
 async function open(route){await Promise.all(pages.map(async(p,i)=>{await p.goto(origins[i]+route,{waitUntil:'domcontentloaded'});await p.waitForFunction(()=>window.__qaReady,{},{timeout:60000});}));}
 async function snapshots(){return Promise.all(pages.map(p=>p.evaluate(code=>{const text=eval('('+code+')'),norm=s=>s.replace(/\s+/g,' ').trim();return Object.fromEntries(['latin','greek','english'].map(l=>{const pane=document.querySelector('#'+l);return [l,pane?{text:norm(text(pane)),notes:[...pane.querySelectorAll('.niese-correspondence-note,.structural-unavailable,.niese-context-note')].map(n=>n.textContent),ids:[...pane.querySelectorAll('[id]')].map(n=>n.id),paragraphs:[...pane.querySelectorAll('tei-p')].map(n=>({id:n.id,sameAs:n.getAttribute('sameAs')}))}:null];}));},narrative.toString())));}
 try{
  for(const b of (resume?[]:[1,2,3,4,5,6,7,8,9,10,12,13,14,15])){
   await open(`/antiquities/?book=${b}&niese=${b===1?27:1}`);await Promise.all(pages.map(async p=>{for(const l of ['greek','english'])await p.check('#'+l+'-pane-select');}));
   const menus=await Promise.all(pages.map(p=>p.evaluate(()=>[...document.querySelector('#niese-selector').options].filter(o=>o.value).map(o=>Number(o.value)))));
   if(JSON.stringify(menus[0])!==JSON.stringify(menus[1]))throw Error('Prior menu changed '+b);
   result.books.push({book:b,identities:menus[0].length,range:[menus[0][0],menus[0].at(-1)]});
   for(const n of menus[0]){
    await Promise.all(pages.map(p=>p.evaluate(async n=>{
      const menu=document.querySelector('#niese-selector');menu.value=String(n);menu.dispatchEvent(new Event('change',{bubbles:true}));
      const started=Date.now();await new Promise((resolve,reject)=>{const check=()=>{
        if(window.__qaRenderedState?.nieseNum===String(n)&&['latin','greek','english'].every(l=>document.querySelector(`#${l} [n="${n}"][type^="niese-"]`)))return resolve();
        if(Date.now()-started>30000)return reject(Error('Actual selection did not render '+n));setTimeout(check,5);
      };check();});
    },n)));
    const a=await snapshots();if(JSON.stringify(a[0])!==JSON.stringify(a[1])){fs.writeFileSync(path.join(P,'PROTECTED_FINAL_DIFFERENCE.json'),JSON.stringify({book:b,number:n,baseline:a[0],review:a[1]},null,2));throw Error('Prior live DOM changed '+b+'.'+n);}
    result.selections.push({book:b,number:n,status:'IDENTICAL_LIVE_DOM',sha256:sha(JSON.stringify(a[0]))});
   }
   fs.writeFileSync(path.join(P,'PROTECTED_FINAL_BROWSER_CHECKPOINT.json'),JSON.stringify(result,null,2)+'\n');
   console.log('Protected',b,menus[0].length,'complete');
  }
  if(result.selections.length!==5231)throw Error('Frozen total differs '+result.selections.length);
  await open('/antiquities/?book=15&chapter=7');const lastBamberg=await pages[0].evaluate(()=>window.__qa.bambergRows().at(-1).id);
  const routes=['/antiquities/?book=15&chapter=7',`/antiquities/?book=15&bamberg=${lastBamberg}`,'/antiquities/?book=15&view=contents','/antiquities/?book=17','/antiquities/?book=20','/antiquities/?book=20&chapter=1','/antiquities/?book=20&view=contents','/bellum-judaicum/?book=1&niese=1&latin=cardwell','/bellum-judaicum/?book=1&niese=1&english=whiston','/bellum-judaicum/?book=1&niese=1&english=lodge1602','/bellum-judaicum/?book=4&chapter=1','/deh/?book=1&chapter=1&unit=1','/contra-apionem/?book=2&unit=1'];
  for(const route of routes){await open(route);const a=await snapshots();if(JSON.stringify(a[0])!==JSON.stringify(a[1]))throw Error('Protected work DOM changed '+route);const sources=await Promise.all(pages.map(p=>p.evaluate(()=>window.__qa.getState().sources)));if(JSON.stringify(sources[0])!==JSON.stringify(sources[1]))throw Error('Protected sources changed '+route);const params=new URL(route,'http://localhost').searchParams;for(const l of ['Latin','Greek','English'])if(params.has(l.toLowerCase())&&sources[0][l]!==params.get(l.toLowerCase()))throw Error('Requested protected source not selected '+route);result.protectedRoutes.push({route,sourceSelections:sources[0],status:'IDENTICAL_LIVE_DOM',sha256:sha(JSON.stringify(a[0]))});}
  // Precisely reproduce the two authorized known baseline defects.
  await open('/antiquities/?book=1&bamberg=B78-table1-row005');
  const links=await Promise.all(pages.map(p=>p.evaluate(()=>[...document.querySelectorAll('#latin a[href],#greek a[href],#english a[href]')].map(a=>a.getAttribute('href')).filter(h=>h.startsWith('undefinednote_')))));
  if(links[0].length!==3||JSON.stringify(links[0])!==JSON.stringify(links[1]))throw Error('Known Book-I apparatus links changed');
  const targets=[];for(let i=0;i<2;i++)for(const href of new Set(links[i])){const response=await pages[i].request.get(new URL(href,pages[i].url()).href);if(response.status()!==404)throw Error('Known apparatus target no longer matches baseline');targets.push({side:i,href,status:response.status()});}
  result.knownBaselineIssues.push({case:'Book-I inherited apparatus links',identical:true,links:links[0],targets});
  if(result.errors.length)throw Error('Unexpected errors before unsupported I.1');
  const unsupported=await Promise.all(pages.map(async(p,i)=>{const errorPromise=p.waitForEvent('pageerror',{timeout:30000});await p.goto(origins[i]+'/antiquities/?book=1&niese=1',{waitUntil:'domcontentloaded'});const error=String(await errorPromise);const inventory=await p.evaluate(()=>({selected:document.querySelector('#niese-selector').value,firstSupported:[...document.querySelector('#niese-selector').options].find(o=>o.value)?.value}));return {error,inventory};}));
  const expectedError="TypeError: Cannot read properties of null (reading 'querySelector')";
  if(JSON.stringify(unsupported[0])!==JSON.stringify(unsupported[1])||unsupported[0].error!==expectedError||unsupported[0].inventory.firstSupported!=='27')throw Error('Unsupported I.1 baseline signature changed');
  result.knownBaselineIssues.push({case:'Unsupported I.1',identical:true,observed:unsupported[0],excludedFromSelectableTotal:true});
  if(result.errors.length!==2||result.errors.some(e=>e.error!==expectedError||!e.url.endsWith('/antiquities/?book=1&niese=1')))throw Error('Unknown baseline exception');result.expectedUnsupportedErrors=result.errors;result.errors=[];
  if(result.errors.length)throw Error('Browser errors '+JSON.stringify(result.errors));result.status='PASS';
 }catch(e){result.status='FAIL';result.failure=String(e);throw e;}finally{result.finished=new Date().toISOString();fs.writeFileSync(path.join(P,'PROTECTED_FINAL_BROWSER.json'),JSON.stringify(result,null,2)+'\n');await context.close();await Promise.all(servers.map(s=>new Promise(r=>s.close(r))));}
 console.log(JSON.stringify({status:result.status,oldSelections:result.selections.length,protectedRoutes:result.protectedRoutes.length}));
}
main().catch(e=>{console.error(e);process.exitCode=1;});
