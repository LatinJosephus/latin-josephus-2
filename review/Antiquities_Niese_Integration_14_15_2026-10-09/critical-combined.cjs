const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {chromium}=require('C:/Users/Pollard_R/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const {serve,narrative}=require('./book-browser.cjs');
const packet=__dirname,root=path.resolve(packet,'../..'),runtime='C:/workspace/Antiquities-Niese-14-15-integration-runtime-20261009';
const norm=s=>String(s||'').replace(/\s+/g,' ').trim(),digest=x=>crypto.createHash('sha256').update(JSON.stringify(x)).digest('hex');
async function main(){
 const report={result:'PENDING',build_record:JSON.parse(fs.readFileSync(path.join(packet,'BUILD_RECORD.json'))),selections:[],containing_views:[],new_book_original_views:[],uninstrumented:[],errors:[],consoleErrors:[],failedRequests:[]};
 const servers=[serve(path.join(runtime,'site')),serve(path.join(runtime,'baseline-site')),serve(path.join(runtime,'site'),false)];
 for(const s of servers)await new Promise(r=>s.listen(0,'127.0.0.1',r));
 const origins=servers.map(s=>`http://127.0.0.1:${s.address().port}`);report.origins=origins;
 const context=await chromium.launchPersistentContext(path.join(runtime,'profile-critical-combined'),{headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',viewport:{width:1500,height:1000}}),page=await context.newPage();
 page.on('pageerror',e=>report.errors.push(String(e)));page.on('console',m=>{if(m.type()==='error')report.consoleErrors.push(m.text())});page.on('requestfailed',r=>report.failedRequests.push(r.url()));
 const expected=Object.fromEntries([12,13].map(b=>[b,JSON.parse(fs.readFileSync(path.join(packet,'books',String(b),'EXPECTED_INTERVALS.json')))]));
 async function open(route,which=0){await page.goto(origins[which]+route,{waitUntil:'domcontentloaded'});if(which<2)await page.waitForFunction(()=>window.__qaReady,{},{timeout:60000});else await page.waitForFunction(()=>document.querySelector('#book-selector')?.options.length>1&&document.querySelector('#latin [type="niese-section"]')&&document.querySelector('#greek tei-p')&&document.querySelector('#english tei-p'),{},{timeout:60000});}
 async function capture(b){return page.evaluate(({code,exclusions})=>{const text=eval('('+code+')'),out={};for(const l of ['Latin','Greek','English']){const node=document.querySelector('#'+l.toLowerCase());out[l]={text:text(node,exclusions[l]||[]),unavailable:!!node.querySelector('.structural-unavailable'),notice:node.querySelector('.niese-correspondence-note')?.textContent||node.querySelector('.structural-unavailable')?.textContent||'',context:!!node.querySelector('.niese-context-note')};}const ids=[...document.querySelectorAll('[id]')].map(n=>n.id);out.duplicates=ids.filter((id,i)=>ids.indexOf(id)!==i);return out;},{code:narrative.toString(),exclusions:expected[b].exclusions});}
 function verify(b,n,v){const e=expected[b],s=e.registry.sections.find(s=>s.number===n);for(const l of ['Greek','Latin','English']){if(e[l]&&v[l].text!==norm(e[l][n]))throw Error(`Exact current-canonical ${b}.${n} ${l}`);if(l==='Latin'&&!s.Latin.available&&!v[l].unavailable)throw Error('Missing qualified unavailable '+b+'.'+n);if(l==='Latin'&&s.Latin.note&&!v[l].notice.includes(s.Latin.note))throw Error('Missing exact qualification '+b+'.'+n);}if(v.duplicates.length||!v.English.context||!v.Greek.text||!v.English.text)throw Error('Independent witnesses/IDs '+b+'.'+n);}
 async function rendered(n){await page.waitForFunction(n=>window.__qaRenderedState?.nieseNum===String(n),n);}
 async function snapshot(b,strip=false){return page.evaluate(({b,strip})=>Object.fromEntries(Object.entries(window.__qa.view()).map(([l,v])=>{if(!v)return[l,null];const c=v.cloneNode(true);if(strip&&[14,15].includes(b)){c.querySelectorAll('tei-milestone[unit="niese"],.niese-correspondence-note').forEach(n=>n.remove());if(l==='Greek'){const p=c.querySelector(`[id="greek-book${b}-num1"]`);[...p?.querySelectorAll('tei-num')||[]].find(n=>n.textContent==='[1]')?.remove();}}return[l,c.outerHTML.replaceAll(location.origin,'LOCAL_ORIGIN')];})),{b,strip});}
 try{
  for(const [b,numbers] of [[12,[246,247,248,249,250,434]],[13,[212,213,214,215,216,217,269]]]){
   for(const n of numbers){
    const pair=[];for(const which of [1,0]){await open(`/antiquities/?book=${b}&niese=${n}`,which);const v=await capture(b);verify(b,n,v);pair.push(v);}
    if(JSON.stringify(pair[0])!==JSON.stringify(pair[1]))throw Error('Predecessor selection changed '+b+'.'+n);
    await page.reload();await page.waitForFunction(()=>window.__qaReady);verify(b,n,await capture(b));
    if(n<expected[b].registry.range[1]){await page.click('#niese-next');await rendered(n+1);verify(b,n+1,await capture(b));await page.click('#niese-previous');await rendered(n);verify(b,n,await capture(b));await page.goBack();await rendered(n+1);verify(b,n+1,await capture(b));await page.goForward();await rendered(n);}
    for(const l of ['english','greek']){await page.uncheck('#'+l+'-pane-select');await page.check('#'+l+'-pane-select');verify(b,n,await capture(b));}
    report.selections.push({book:b,niese:n,exact_Greek_Latin_and_notices:'PASS',English_context_equal_actual_canonical:'PASS',canonical_equivalence:'PASS',reload_history_navigation_panes:'PASS',digest:digest(pair[1])});
    await open(`/antiquities/?book=${b}&niese=${n}`,2);verify(b,n,await capture(b));report.uninstrumented.push({book:b,niese:n,result:'PASS'});
   }
   await open(`/antiquities/?book=${b}`);
   const facts=await page.evaluate(b=>{const q=window.__qa,d=q.getData().Latin,starts=q.antiquitiesNieseStartEntries('Latin',d).map(e=>e.number),m=d.querySelector('tei-milestone[unit="niese"][n="269"]');return{starts,visible213:d.querySelector('[id="latin-book13-num213"]')?.textContent.includes('[VI.vii.213]'),anonymous269:m? !m.closest('tei-p').hasAttribute('id'):null};},b);
   if(b===13&&(facts.starts.includes(213)||facts.starts.includes(216)||!facts.starts.includes(214)||!facts.starts.includes(215)||!facts.visible213||!facts.anonymous269))throw Error('Preserved XIII representation/anonymous269');
   report['book'+b+'_representation']={...facts,result:'PASS'};
   const routes=await page.evaluate(({b,numbers})=>{const q=window.__qa,d=q.getData();const hit=row=>{const g=q.traditionalRangeView('Greek',d.Greek,row),l=q.traditionalRangeView('Latin',d.Latin,row);return [...g?.querySelectorAll('tei-num')||[]].some(x=>numbers.includes(Number(x.textContent.match(/\d+/g)?.at(-1))))||(l?.textContent||'').includes(b===12?'centesima quinquagesima tertia olimpiade':'in mutuis documentis publicisque');};return [...new Set([...['chapter','subchapter'].flatMap(s=>q.traditionalRows(s).filter(hit).map(r=>`/antiquities/?book=${b}&chapter=${r.chapter}`+(s==='subchapter'?`&subchapter=${r.subchapter}`:''))),...q.bambergRows().filter(hit).map(r=>`/antiquities/?book=${b}&bamberg=${r.id}`)])];},{b,numbers});
   for(const route of routes){const pair=[];for(const which of [1,0]){await open(route,which);pair.push(await snapshot(b));}if(JSON.stringify(pair[0])!==JSON.stringify(pair[1]))throw Error('Complete predecessor containing DOM '+route);report.containing_views.push({route,all_text_markup_order_and_notes:'PASS',digest:digest(pair[1])});}
  }
  for(const b of [14,15]){
   await open(`/antiquities/?book=${b}`);
   const routes=await page.evaluate(b=>{const q=window.__qa,data=q.getData(),phrases=b===14?['antipatrum, faciebat','Quibus uerbis compulsus','senatu uero dimisso']:['seditiones domesticas pacando'];const bamberg=q.bambergRows().filter(r=>{const t=q.traditionalRangeView('Latin',data.Latin,r)?.textContent||'';return phrases.some(p=>t.includes(p));}).map(r=>`/antiquities/?book=${b}&bamberg=${r.id}`);const units=[...document.querySelector('#section-selector').options].filter(o=>o.value&&o.value!=='contents').slice(0,2).map(o=>`/antiquities/?book=${b}&unit=${o.value}`);return [...bamberg,...units];},b);
   if(!routes.length)throw Error('No new-book protected original views '+b);
   for(const route of routes){const pair=[];for(const which of [1,0]){await open(route,which);pair.push(await snapshot(b,true));}if(JSON.stringify(pair[0])!==JSON.stringify(pair[1]))throw Error('Preserved new-book Bamberg/Alignment '+route);report.new_book_original_views.push({route,original_three_witness_DOM_preserved:'PASS',digest:digest(pair[1])});}
  }
  if(report.errors.length||report.consoleErrors.length||report.failedRequests.length)throw Error('Unexpected diagnostics');report.result='PASS';
 }catch(e){report.result='FAIL';report.failure=String(e);throw e;}finally{fs.writeFileSync(path.join(packet,'CRITICAL_COMBINED_READER_QA.json'),JSON.stringify(report,null,2)+'\n');console.log(report.result,report.selections.length,'critical predecessor selections',report.containing_views.length,'containing views',report.new_book_original_views.length,'new-book Bamberg/Alignment views');await context.close();for(const s of servers)await new Promise(r=>s.close(r));}
}
main().catch(e=>{console.error(e);process.exitCode=1});
