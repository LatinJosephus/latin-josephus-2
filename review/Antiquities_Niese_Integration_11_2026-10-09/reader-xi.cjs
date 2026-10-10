const {fs,path,chromium,runtime,load,save,norm,hash,serve,listen,narrative}=require('./qa-common.cjs');
async function main(){
 const build=load(path.join(__dirname,'BUILD_CONTEXT.json')),expected=load(path.join(__dirname,'EXPECTED_SELECTIONS.json')),added=new Set(load(path.join(__dirname,'AUTHORIZED_ADDITIONS.json')).map(x=>x.id));
 const resume=process.argv.includes('--finish-interactions');
 const report=resume?load(path.join(__dirname,'READER_XI_RESULTS.json')):{started:new Date().toISOString(),build,scope:'Actual fresh built Book XI reader; every selector and all containing views',selectors:[],ranges:[],containing:[],navigation:[],errors:[]};
 if(resume){if(report.selectors.length!==347||report.ranges.length!==9||report.containing.length!==120||report.navigation.length!==22||report.errors.length||JSON.stringify(report.build)!==JSON.stringify(build))throw Error('Incomplete prior core proof');report.test_harness_repairs=[{failure:report.failure,reason:'Single-source controls are intentionally hidden; verify their fixed sources and exercise actual alternative-source controls in protected Bellum tests.'}];delete report.failure;report.result='PENDING';}
 const s=serve(build.site),bs=serve(build.baseline_site),origin=await listen(s,8912),baseline=await listen(bs);
 const context=await chromium.launchPersistentContext(path.join(runtime,'browser-profile-xi-final'),{headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',viewport:{width:1600,height:1000}}),page=await context.newPage();
 page.on('pageerror',e=>report.errors.push(String(e)));page.on('requestfailed',r=>report.errors.push(r.url()+':'+r.failure()?.errorText));page.on('console',m=>{if(m.type()==='error')report.errors.push(m.text())});
 const open=async(route,o=origin)=>{await page.goto(o+route);await page.waitForFunction(()=>window.__qaReady)};
 const change=async(id,v)=>{await page.selectOption(id,v);await page.evaluate(()=>window.__qaPending)};
 const capture=()=>page.evaluate(code=>{const text=eval('('+code+')'),q=window.__qa,v=q.view();return {n:q.getState().nieseNum,text:Object.fromEntries(['Latin','Greek','English'].map(l=>[l,text(v[l])])),occurrences:[...(v.Latin.matches('[data-source-occurrence]')?[v.Latin]:[]),...v.Latin.querySelectorAll('[data-source-occurrence]')].map(x=>x.dataset.sourceOccurrence),ids:[...document.querySelectorAll('[id]')].map(x=>x.id),labels:[...v.Latin.querySelectorAll('tei-num')].map(x=>x.textContent),interpolations:[...v.Latin.querySelectorAll('[data-source-role="interpolation"]')].map(x=>({heading:x.querySelector('.niese-source-passage-label')?.textContent,label:x.querySelector('tei-num')?.textContent,next:x.nextElementSibling?.dataset.sourceOccurrence})),notes:[...v.Latin.querySelectorAll('.niese-correspondence-note')].map(x=>x.textContent)}},narrative.toString());
 try{
 if(!resume){
 await open('/antiquities/?book=11&niese=1');
 const menu=await page.locator('#niese-selector').evaluate(n=>[...n.options].filter(o=>o.value).map(o=>Number(o.value)));if(JSON.stringify(menu)!==JSON.stringify(Array.from({length:347},(_,i)=>i+1)))throw Error('347 identity inventory');report.menu=menu;
 for(let n=1;n<=347;n++){
  await change('#niese-selector',String(n));const actual=await capture();
  for(const l of ['Latin','Greek','English'])if(actual.text[l]!==norm(expected[n][l])||!actual.text[l])throw Error(`${n} ${l} exact content/endpoint mismatch`);
  if(actual.n!==String(n)||new Set(actual.ids).size!==actual.ids.length||JSON.stringify(actual.occurrences)!==JSON.stringify(expected[n].occurrences))throw Error('State, IDs or occurrences '+n);
  if([311,342].includes(n)&&actual.interpolations.length)throw Error('Wrong independent interpolation affiliation');
  if(n===312){if(actual.interpolations.length!==2||actual.interpolations[0].label!=='[BJ 4.105a]'||actual.interpolations[1].label!=='[BJ 4.105b]'||actual.interpolations[0].next!=='Latin-XI-312-1'||actual.interpolations[1].next!=='Latin-XI-312-2'||!actual.notes.join(' ').includes('Latin Bellum Judaicum IV.105'))throw Error('Interpolation labels, placement or notice');}
  report.selectors.push({n,result:'PASS',content_sha256:hash(actual.text),Latin_start:actual.text.Latin.slice(0,80),Latin_end:actual.text.Latin.slice(-80),occurrences:actual.occurrences,qualification:expected[n].qualification});if(n%50===0)console.log('XI selectors',n);
 }
 for(const [a,b] of [[68,74],[311,313],[325,327],[341,343],[310,314],[325,329],[340,347],[302,347],[1,347]]){
  const ns=Array.from({length:b-a+1},(_,i)=>a+i);
  const actual=await page.evaluate(({ns,code})=>{const q=window.__qa,text=eval('('+code+')');return Object.fromEntries(['Latin','Greek','English'].map(l=>{const v=q.antiquitiesNieseFragmentView(l,q.getData()[l],ns);return[l,{text:text(v),occurrences:[...v.querySelectorAll('[data-source-occurrence]')].map(x=>x.dataset.sourceOccurrence),ids:[...v.querySelectorAll('[id]')].map(x=>x.id),labels:[...v.querySelectorAll('tei-num')].map(x=>x.textContent)}]}))},{ns,code:narrative.toString()});
  const contextIds=[...new Set(ns.flatMap(n=>expected[n].English_context_targets))],english=contextIds.map(id=>expected[ns.find(n=>expected[n].English_context_targets.includes(id))].English).join('');
  for(const l of ['Latin','Greek','English']){
   const want=l==='English'?english:ns.map(n=>expected[n][l]).join(''),v=actual[l];if(v.text!==norm(want)||new Set(v.ids).size!==v.ids.length||new Set(v.occurrences).size!==v.occurrences.length)throw Error('Range content/occurrences/IDs '+a+'–'+b+' '+l);
  }
  if(ns.includes(312)&&actual.Latin.labels.filter(x=>x==='[BJ 4.105a]'||x==='[BJ 4.105b]').length!==2)throw Error('Combined interpolation duplication');
  report.ranges.push({a,b,result:'PASS',Latin_occurrences:actual.Latin.occurrences,English_context_targets:contextIds,three_pane_content_sha256:hash(actual)});
 }
 // A deliberately shuffled declaration exercises rank rather than physical or array order.
 const reversed=await page.evaluate(code=>{const q=window.__qa,registry=q.canonicalNieseStartEntries();return {entries:registry.length,text:eval('('+code+')')(q.antiquitiesNieseFragmentView('Latin',q.getData().Latin,[327,326,325,326])),claimed105:q.antiquitiesNieseStartEntries('Latin',q.getData().Latin).filter(e=>e.number===105).map(e=>e.occurrence)}},narrative.toString());
 if(reversed.text!==norm([325,326,327].map(n=>expected[n].Latin).join(''))||reversed.claimed105.length!==1||reversed.claimed105[0]!=='Latin-XI-105-1')throw Error('Canonical identity order/dedup or Bellum false105 claim');report.identity_order_and_false105='PASS';
 await open('/antiquities/?book=11');
 const records=await page.evaluate(()=>({traditional:window.__qa.traditionalRows('chapter').concat(window.__qa.traditionalRows('subchapter')),bamberg:window.__qa.bambergRows(),units:[...document.querySelector('#section-selector').options].filter(o=>o.value&&o.value!=='contents').map(o=>o.value)}));
 const routes=['/antiquities/?book=11','/antiquities/?book=11&view=contents',...records.traditional.map(r=>`/antiquities/?book=11&chapter=${r.chapter}${r.scheme==='subchapter'?'&subchapter='+r.subchapter:''}`),...records.bamberg.map(r=>`/antiquities/?book=11&bamberg=${r.id}`),...records.units.map(u=>`/antiquities/?book=11&unit=${u}`)];
 report.population={traditional:records.traditional.length,bamberg:records.bamberg.length,alignment:records.units.length};
 for(const route of routes){
  const captures=[];for(const o of [baseline,origin]){await open(route,o);captures.push(await page.evaluate(ids=>{const q=window.__qa,v=q.view();return {panes:Object.fromEntries(['Latin','Greek','English'].map(l=>{const c=v[l]?.cloneNode(true);if(c)c.querySelectorAll('tei-milestone[unit="niese"]').forEach(m=>{if(ids.includes(m.id))m.remove()});return[l,c?.outerHTML.replaceAll(location.origin,'LOCAL_ORIGIN')||null]})),notice:document.getElementById('traditional-reader-notice')?.outerHTML.replaceAll(location.origin,'LOCAL_ORIGIN')||null}},[...added]));}
  const expectedTitle='<strong>Canonical order from separate witness fragments</strong>';
  const candidateNotice=captures[1].notice?.replace(expectedTitle,'')||null;
  if(JSON.stringify({...captures[0],notice:null})!==JSON.stringify({...captures[1],notice:null})||captures[0].notice!==candidateNotice){save(path.join(runtime,'FAIL-XI-containing.json'),{route,captures});throw Error('Containing view differs '+route)}
  report.containing.push({route,result:'PASS',digest:hash(captures[1])});
 }
 for(const n of [1,64,72,234,310,311,312,313,314,325,326,327,328,329,340,341,342,343,344,345,346,347]){
  await open('/antiquities/?book=11&niese='+n);await page.reload();await page.waitForFunction(()=>window.__qaReady);
  if(n<347){await page.click('#niese-next');await page.evaluate(()=>window.__qaPending);if((await capture()).n!==String(n+1))throw Error('Next '+n);await page.click('#niese-previous');await page.evaluate(()=>window.__qaPending);await page.goBack();await page.waitForFunction(n=>window.__qaRenderedState?.nieseNum===String(n),n+1);await page.goForward();await page.waitForFunction(n=>window.__qaRenderedState?.nieseNum===String(n),n);}else if(!await page.locator('#niese-next').isDisabled())throw Error('Final next');
  if(n===1&&!await page.locator('#niese-previous').isDisabled())throw Error('Opening previous');
  const actual=await capture();for(const l of ['Latin','Greek','English'])if(actual.text[l]!==norm(expected[n][l]))throw Error('Reload/history content '+n);
  report.navigation.push({n,reload_history_previous_next:'PASS'});
 }
 }
 await open('/antiquities/?book=11&niese=312');
 report.panes=[];for(const l of ['english','greek']){await page.uncheck('#'+l+'-pane-select');if(await page.locator('#'+l).isVisible())throw Error('Pane hide');await page.check('#'+l+'-pane-select');if(!await page.locator('#'+l).isVisible())throw Error('Pane show');report.panes.push(l)}
 report.source_options=await page.evaluate(()=>Object.fromEntries(['latin','english','greek'].map(l=>[l,[...document.querySelector('#'+l+'-source-selector').options].map(o=>({value:o.value,text:o.textContent}))])));
 report.source_controls=[];
 for(const [l,options] of Object.entries(report.source_options))for(const option of options){const visible=await page.locator('#'+l+'-source-selector').isVisible();if(visible)await change('#'+l+'-source-selector',option.value);else if(options.length!==1)throw Error('Hidden multi-source control '+l);if((await capture()).text[l[0].toUpperCase()+l.slice(1)]!==norm(expected[312][l[0].toUpperCase()+l.slice(1)]))throw Error('Source content '+l);report.source_controls.push({language:l,source:option.value,mode:visible?'selectable':'fixed single source',result:'PASS'})}
 report.themes=[];for(const theme of ['light','dark']){await page.evaluate(t=>setTheme(t),theme);await page.waitForTimeout(550);const styles=await page.locator('#latin [data-source-role="interpolation"]').evaluateAll(ns=>ns.map(n=>({background:getComputedStyle(n).backgroundColor,border:getComputedStyle(n).borderInlineStartWidth,text:getComputedStyle(n).color,heading:n.querySelector('.niese-source-passage-label').textContent})));if(styles.length!==2||styles.some(x=>x.border!=='3px'))throw Error('Source passage visual distinction');const image=path.join(runtime,'XI-312-'+theme+'.png');await page.screenshot({path:image,fullPage:true});report.themes.push({theme,styles,image});}
 await page.locator('#latin .niese-correspondence-note a').first().click();await page.waitForFunction(()=>window.__qaReady);if(windowDummy(await page.evaluate(()=>window.__qa.getState().viewingLevel))!=='book-level')throw Error('Notice Book link');
 await page.check('#section-level');await page.evaluate(()=>window.__qaPending);await change('#section-selector','306');await page.check('#chapter-level');await page.evaluate(()=>window.__qaPending);await change('#chapter-selector','8');await page.check('#subchapter-level');await page.evaluate(()=>window.__qaPending);await change('#subchapter-selector','2');if(!await page.locator('#traditional-reader-notice').textContent().then(x=>x.includes('Canonical order from separate witness fragments')))throw Error('Traditional notice retained');await page.check('#niese-level');await page.evaluate(()=>window.__qaPending);await change('#niese-selector','312');if((await capture()).text.Latin!==norm(expected[312].Latin))throw Error('Structural to Niese switch');report.view_switches='PASS';
 if(report.errors.length)throw Error('Reader errors');report.result='PASS';
 }catch(e){report.result='FAIL';report.failure=String(e)}finally{report.origin=origin;report.finished=new Date().toISOString();save(path.join(__dirname,'READER_XI_RESULTS.json'),report);await context.close();await new Promise(r=>s.close(r));await new Promise(r=>bs.close(r));}
 console.log(JSON.stringify({result:report.result,failure:report.failure,selectors:report.selectors.length,ranges:report.ranges.length,containing:report.containing.length,errors:report.errors}));if(report.result!=='PASS')process.exitCode=1;
}
function windowDummy(x){return x}
main().catch(e=>{console.error(e);process.exitCode=1});
