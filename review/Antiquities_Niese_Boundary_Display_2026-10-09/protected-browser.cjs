const fs=require('fs'),path=require('path'),http=require('http'),crypto=require('crypto');
const {chromium}=require('C:/Users/Pollard_R/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root=path.resolve(__dirname,'../..'),runtime='C:/workspace/Antiquities-Niese-Boundary-Display-QA-20261009';
const packet=b=>path.join(__dirname,'books',String(b));
const load=p=>JSON.parse(fs.readFileSync(p,'utf8')),save=(p,x)=>fs.writeFileSync(p,JSON.stringify(x,null,2)+'\n');
const hash=x=>crypto.createHash('sha256').update(typeof x==='string'?x:JSON.stringify(x)).digest('hex');
const norm=s=>String(s||'').replace(/\s+/g,' ').trim();
function instrument(s){
 s=s.replace('  bookTitle.innerText = activeWork.title;',`  window.__qa={getState:()=>({...state}),getData:()=>fullData,view:()=>viewData,reload,setState,selectView,selectCanonicalView,currentIdBase,canonicalNieseStartEntries,antiquitiesNieseStartEntries,traditionalRangeView,traditionalRows,bambergRows,bambergSelection,traditionalRegistry:()=>traditionalRegistry,alignmentRegistry:()=>alignmentRangeRegistry,bambergRegistry:()=>bambergRegistry,setChapterSelectOptions,setSectionSelectOptions,assign:patch=>Object.assign(state,patch)};\n  bookTitle.innerText = activeWork.title;`);
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
function narrative(node,exclusions=[]){
 if(!node)return null;const c=node.cloneNode(true);
 c.querySelectorAll('tei-num,tei-milestone,tei-note,tei-app,tei-rdg,.niese-context-note,.niese-correspondence-note,.structural-unavailable').forEach(x=>x.remove());
 const paras=[...(c.matches?.('tei-p')?[c]:[]),...c.querySelectorAll('tei-p')].filter(p=>!p.closest('tei-div2[n="0"]'));
 return paras.map(p=>{
  let text=p.textContent;
  if(!p.id&&text.startsWith('περιέχει ἡ βίβλος χρόνον'))return '';
  for(const e of exclusions.filter(e=>e.original_locator?.stable_id===p.id)){
   const token=e.text,escaped=token.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
   if(e.reason==='plain traditional division label')text=text.replace(new RegExp('(?<![A-Za-z])'+escaped+(token.endsWith('.')?'':'(?![A-Za-z.])')),'');
   else if(e.reason==='terminal book subscription')text=text.replace(token,'');
  }
  return text;
 }).join('').replace(/\s+/g,' ').trim();
}
function originalHTML(node){return node?.outerHTML.replaceAll(location.origin,'LOCAL_ORIGIN')||null;}
async function main(){
 const mode=process.argv.includes('--protected')?'protected':process.argv.includes('--ranges')?'ranges':'new-book',b=Number(process.argv.find(a=>/^--book=/.test(a))?.split('=')[1]||12);
 const routine=process.argv.includes('--routine');
 const report={build_record:load(path.join(__dirname,'BUILD_RECORD.json')),mode,scope:routine?'PROVISIONAL_ROUTINE_REHEARSAL_NOT_CERTIFIED':'DISPLAY_ONLY_CORRECTION_AGAINST_CURRENT_CERTIFIED_CANONICAL',started:new Date().toISOString(),browserExceptions:[],consoleErrors:[],failedRequests:[]};
 const servers=[serve(path.join(runtime,'site')),serve('C:/workspace/Antiquities-Niese-12-13-integration-runtime-20261009/site'),serve(path.join(runtime,'site'),false)];
 async function listen(s,port){try{await new Promise((r,j)=>{s.once('error',j);s.listen(port,'127.0.0.1',r);});}catch(e){if(e.code!=='EADDRINUSE')throw e;await new Promise((r,j)=>{s.once('error',j);s.listen(0,'127.0.0.1',r);});}}
 await listen(servers[0],8913);for(const s of servers.slice(1))await listen(s,0);
 const origins=servers.map(s=>`http://127.0.0.1:${s.address().port}`);report.origins=origins;
 const context=await chromium.launchPersistentContext(path.join(runtime,`browser-profile-${mode}-${b}`),{headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',viewport:{width:1500,height:1000}});
 const page=await context.newPage();let currentRoute='';
 page.on('pageerror',e=>report.browserExceptions.push({route:currentRoute,error:String(e)}));
 page.on('console',m=>{if(m.type()==='error')report.consoleErrors.push({route:currentRoute,error:m.text()});});
 page.on('requestfailed',r=>report.failedRequests.push({route:currentRoute,url:r.url(),error:r.failure()?.errorText}));
 async function open(route,which=0){currentRoute=route;await page.goto(origins[which]+route,{waitUntil:'domcontentloaded'});if(which<2)await page.waitForFunction(()=>window.__qaReady,{},{timeout:60000});else await page.waitForFunction(()=>document.querySelector('#book-selector')?.options.length>1&&document.querySelector('#latin tei-p, #latin .structural-unavailable'),{},{timeout:60000});}
 async function change(selector,value){await page.selectOption(selector,value);await page.evaluate(()=>window.__qaPending);}
 try{
 if(mode==='new-book'){
  const expected=load(path.join(packet(b),routine?'ROUTINE_EXPECTED_INTERVALS.json':'EXPECTED_INTERVALS.json')),max=Object.keys(expected.Greek).length;
  if(routine)report.excluded_from_final_certification=expected.excluded_from_final_certification;
  await open(`/antiquities/?book=${b}&niese=1`);
  const projection=await page.evaluate(({expected,code})=>{
   const text=eval('('+code+')'),q=window.__qa,data=q.getData(),errors=[],records=[],starts={};
   for(const l of ['Greek','Latin']){starts[l]=q.antiquitiesNieseStartEntries(l,data[l]).map(e=>e.number);if(new Set(starts[l]).size!==starts[l].length)errors.push('Duplicate '+l+' identity');}
   for(const section of expected.registry.sections){
    const n=section.number;q.assign({viewingLevel:'niese-level',nieseNum:String(n),chapterNum:null,subchapterNum:null,sectionNum:null,bambergId:null});const record={n};
    for(const l of ['Greek','Latin','English']){
     const v=q.selectView(l,data[l],q.currentIdBase());record[l]=text(v,expected.exclusions[l]||[]);
     if(l!=='English'&&record[l]!==String(expected[l][n]||'').replace(/\s+/g,' ').trim())errors.push(`${l} ${n} interval mismatch`);
     if(l==='Latin'&&!section.Latin.available&&!v?.querySelector('.structural-unavailable'))errors.push(`${n} unavailable state missing`);
     if(l==='Latin'&&section.Latin.note&&!v?.textContent.includes(section.Latin.note))errors.push(`${n} exact explanatory notice missing`);
     if(l==='English'&&(!v?.querySelector('.niese-context-note')||!record[l]))errors.push(`English ${n} broader context missing`);
     if(l==='English'&&expected.English&&record[l]!==String(expected.English[n]).replace(/\s+/g,' ').trim())errors.push(`English ${n} source context mismatch`);
     const ids=[...v?.querySelectorAll('[id]')||[]].map(x=>x.id);if(ids.length!==new Set(ids).size)errors.push(`${l} ${n} repeated DOM ID`);
    }records.push(record);
   }
   return {errors,starts,records,menu:[...document.querySelector('#niese-selector').options].filter(o=>o.value).map(o=>Number(o.value))};
  },{expected,code:narrative.toString()});
  if(projection.errors.length)throw Error(JSON.stringify(projection.errors.slice(0,20)));
  if(projection.menu.length!==max||projection.menu.some((n,i)=>n!==i+1))throw Error('Selection inventory');
  report.projections={identities:max,Greek_starts:projection.starts.Greek.length,Latin_starts:projection.starts.Latin.length,all_intervals:'PASS',English_independently_available:'PASS',qualification_notices:'PASS',digest:hash(projection.records)};
  report.actual_select_events=[];
  for(let n=1;n<=max;n++){
   await change('#niese-selector',String(n));
   const actual=await page.evaluate(({code,exclusions})=>{
    const text=eval('('+code+')'),v=window.__qa.view(),ids=[...document.querySelectorAll('[id]')].map(x=>x.id);
    return {n:window.__qa.getState().nieseNum,Greek:text(v.Greek,exclusions.Greek),Latin:text(v.Latin,exclusions.Latin),English:text(v.English),duplicates:ids.filter((id,i)=>ids.indexOf(id)!==i)};
   },{code:narrative.toString(),exclusions:expected.exclusions});
   if(actual.n!==String(n)||actual.Greek!==norm(expected.Greek[n])||actual.Latin!==norm(expected.Latin[n])||!actual.English||(expected.English&&actual.English!==norm(expected.English[n]))||actual.duplicates.length)throw Error(`Rendered selection ${b}.${n}`);
   report.actual_select_events.push(n);
  }
  report.navigation=[];
  const cases=b===12?[1,147,148,246,247,248,249,250,331,332,366,367,434]:[1,37,38,105,106,111,115,116,117,170,171,186,187,212,213,214,215,216,217,218,237,269,274,306,333,334,347,365,378,386,415,420,427,432,433];
  async function rendered(n){await page.waitForFunction(n=>window.__qaRenderedState?.nieseNum===String(n),n);const actual=await page.locator('#latin').evaluate((node,{code,exclusions})=>eval('('+code+')')(node,exclusions),{code:narrative.toString(),exclusions:expected.exclusions.Latin});if(actual!==norm(expected.Latin[n]))throw Error('Navigation interval '+n);}
  for(const n of cases){
   await open(`/antiquities/?book=${b}&niese=${n}`);await rendered(n);await page.reload();await page.waitForFunction(()=>window.__qaReady);await rendered(n);
   if(n<max){await page.click('#niese-next');await rendered(n+1);await page.click('#niese-previous');await rendered(n);await page.goBack();await rendered(n+1);await page.goForward();await rendered(n);}else if(!await page.locator('#niese-next').isDisabled())throw Error('Final next endpoint');
   if(n===1&&!await page.locator('#niese-previous').isDisabled())throw Error('First previous endpoint');
   for(const lang of ['english','greek']){await page.uncheck(`#${lang}-pane-select`);await page.check(`#${lang}-pane-select`);}if(!await page.locator('#latin-pane-select').isDisabled())throw Error('Fixed Latin pane control changed');await rendered(n);
   const themes=[];for(const theme of ['light','dark']){await page.evaluate(t=>setTheme(t),theme);await page.waitForTimeout(550);themes.push(await page.evaluate(()=>({theme:document.documentElement.dataset.theme,stored:localStorage.getItem('theme'),background:getComputedStyle(document.body).backgroundColor})));if((b===12?[1,248,249,434]:[1,213,214,216,269,274,433]).includes(n))await page.screenshot({path:path.join(packet(b),`${mode}_${routine?'ROUTINE_':''}READER_${n}_${theme}.png`),fullPage:true});}
   if(themes[0].background===themes[1].background||themes.some(t=>t.theme!==t.stored))throw Error('Theme application');report.navigation.push({n,reload_history_previous_next:'PASS',pane_switches:'PASS',themes});
  }
  report.uninstrumented=[];
  for(const n of cases){await open(`/antiquities/?book=${b}&niese=${n}`,2);const text=await page.locator('#latin').evaluate((node,{code,exclusions})=>eval('('+code+')')(node,exclusions),{code:narrative.toString(),exclusions:expected.exclusions.Latin});if(text!==norm(expected.Latin[n]))throw Error('Production selection '+n);report.uninstrumented.push(n);}
  await open(`/antiquities/?book=${b}`);
  report.broader_ranges=await page.evaluate(()=>{
   const q=window.__qa,data=q.getData(),results=[];
   for(const kind of ['chapter','subchapter']){
    const rows=q.traditionalRows(kind),counts={};
    for(const row of rows){const v=q.traditionalRangeView('Latin',data.Latin,row),ids=[...v.querySelectorAll('tei-milestone[unit="niese"][n]')].map(m=>m.getAttribute('n'));for(const n of ids)counts[n]=(counts[n]||0)+1;const dom=[...v.querySelectorAll('[id]')].map(x=>x.id);if(new Set(dom).size!==dom.length)throw Error('Range duplicate IDs '+row.id);}
    results.push({kind,rows:rows.length,counts});
   }return results;
  });
  const allInserted=(routine?expected:load(path.join(packet(b),'EXECUTABLE_IDENTITIES.json'))).inserted;
  for(const range of report.broader_ranges){const missing=allInserted.filter(n=>(range.counts[n]||0)!==1);if(range.kind==='chapter'&&missing.length)throw Error('Chapter marker completeness '+missing);range.markers_present_once=allInserted.length-missing.length;range.without_subchapter=missing;}
  // Drive every actual Chapter and Subchapter selector; compare its final DOM
  // with the range resolver and the unchanged baseline in protected mode.
  report.actual_range_selectors=[];
  await page.check('#chapter-level');await page.evaluate(()=>window.__qaPending);
  const chapters=await page.locator('#chapter-selector').evaluate(n=>[...n.options].filter(o=>o.value&&o.value!=='contents').map(o=>o.value));
  for(const chapter of chapters){await change('#chapter-selector',chapter);report.actual_range_selectors.push(await page.evaluate(()=>({kind:'chapter',chapter:window.__qa.getState().chapterNum,Latin:document.querySelector('#latin').textContent.length,Greek:document.querySelector('#greek').textContent.length,English:document.querySelector('#english').textContent.length})));const subs=await page.locator('#subchapter-selector').evaluate(n=>[...n.options].filter(o=>o.value&&o.value!=='contents').map(o=>o.value));if(subs.length){await page.check('#subchapter-level');await page.evaluate(()=>window.__qaPending);for(const sub of subs){await change('#subchapter-selector',sub);const rec=await page.evaluate(()=>({kind:'subchapter',chapter:window.__qa.getState().chapterNum,subchapter:window.__qa.getState().subchapterNum,Latin:document.querySelector('#latin').textContent.length,Greek:document.querySelector('#greek').textContent.length,English:document.querySelector('#english').textContent.length}));if(!rec.Latin||!rec.Greek||!rec.English)throw Error('Empty range');report.actual_range_selectors.push(rec);}await page.check('#chapter-level');await page.evaluate(()=>window.__qaPending);}}
  await open(`/antiquities/?book=${b}`);if(b===12&&!await page.locator('#latin').textContent().then(t=>t.includes('LIBER DUODECIMUS EXPLICIT')))throw Error('Colophon lost in book view');
  await change('#book-selector','09');if(await page.locator('#niese-level').isDisabled())throw Error('Integrated IX disabled');await change('#book-selector',String(b));await page.check('#niese-level');await page.evaluate(()=>window.__qaPending);await change('#niese-selector','1');report.book_switching='PASS';
 }else if(mode==='ranges'){
  const expected=load(path.join(packet(b),routine?'ROUTINE_EXPECTED_INTERVALS.json':'EXPECTED_INTERVALS.json'));report.actual_ranges=[];
  await open(`/antiquities/?book=${b}`);
  const rows=await page.evaluate(()=>window.__qa.traditionalRows('chapter').concat(window.__qa.traditionalRows('subchapter')));
  for(const row of rows){
   const route=`/antiquities/?book=${b}&chapter=${row.chapter}${row.subchapter&&row.subchapter!=='0'?'&subchapter='+row.subchapter:''}`;
   const captures=[];
   for(const which of [1,0]){
    await open(route,which);
    captures.push(await page.evaluate(({book,code})=>Object.fromEntries(['Latin','Greek','English'].map(l=>[l,eval('('+code+')')(document.getElementById(l.toLowerCase()),book,l)])),{book:b,code:originalHTML.toString()}));
   }
   if(JSON.stringify(captures[0])!==JSON.stringify(captures[1]))throw Error('Actual range baseline DOM mismatch '+row.id);
   const details=await page.evaluate(({row,code,exclusions})=>{
    const q=window.__qa,text=eval('('+code+')'),data=q.getData(),result={id:row.id,chapter:row.chapter,subchapter:row.subchapter||null,languages:{}};
    for(const l of ['Greek','Latin','English']){
     const range=q.traditionalRangeView(l,data[l],row),pane=document.getElementById(l.toLowerCase());
     if(text(range,exclusions[l]||[])!==text(pane,exclusions[l]||[]))throw Error('Rendered range differs from registered range '+row.id+' '+l);
     const actual=[...pane.querySelectorAll('tei-milestone[unit="niese"][n]')].map(n=>n.getAttribute('n')),wanted=[...range.querySelectorAll('tei-milestone[unit="niese"][n]')].map(n=>n.getAttribute('n'));
     if(JSON.stringify(actual)!==JSON.stringify(wanted))throw Error('Rendered markers missing/repeated '+row.id+' '+l);
     const ids=[...pane.querySelectorAll('[id]')].map(n=>n.id);if(ids.length!==new Set(ids).size)throw Error('Duplicate range IDs '+row.id+' '+l);
     result.languages[l]={narrative_characters:text(pane,exclusions[l]||[]).length,markers:actual,result:'PASS'};
    }return result;
   },{row,code:narrative.toString(),exclusions:expected.exclusions});
   report.actual_ranges.push(details);
  }
  const focused=b===12?[246,247,248,249,434]:[1,212,213,214,215,216,217,269,274,433];report.visuals=[];
  for(const n of focused){await open(`/antiquities/?book=${b}&niese=${n}`);for(const theme of ['light','dark']){await page.evaluate(t=>setTheme(t),theme);await page.waitForTimeout(550);const p=path.join(packet(b),`${mode}_${routine?'ROUTINE_':''}READER_${n}_${theme}.png`);await page.screenshot({path:p,fullPage:true});report.visuals.push(path.basename(p));}if(!await page.locator('.lj-brand__light').evaluate(n=>n.complete&&n.naturalWidth>0))throw Error('Local SVG logo serving');}
  if(b===12){
   await open('/antiquities/?book=12&chapter=5');
   const broader=await page.locator('#latin').textContent();
   const clauses=['centesima quinquagesima tertia olimpiade','Ingres susque','nec non etiam eos','multasque abeo','Post quam autem expoliauit templum'];
   let at=-1;for(const phrase of clauses){const next=broader.indexOf(phrase);if(next<=at||next!==broader.lastIndexOf(phrase))throw Error('Adjoining 246–250 order/multiplicity '+phrase);at=next;}report.adjudicated_broader_range={route:'/antiquities/?book=12&chapter=5',all_approved_clauses_once_and_transmitted_order:'PASS'};
  }
  if(b===13&&!routine){
   await open('/antiquities/?book=13&chapter=6');
   const phrases=['De sepultura quidem ionathae','in mutuis documentis publicisque','Itaque iudaei feliciter','cum simon gazara ciuitatem','quo multitudo cunctique ingressi'];
   const broader=await page.locator('#latin').textContent();let at=-1;
   for(const phrase of phrases){const next=broader.indexOf(phrase);if(next<=at||next!==broader.lastIndexOf(phrase))throw Error('Adjudicated 212–217 order/multiplicity '+phrase);at=next;}
   if(!broader.includes('[VI.vii.213]'))throw Error('Inherited XIII label lost');
   const nieseData=await page.evaluate(()=>({starts:window.__qa.antiquitiesNieseStartEntries('Latin',window.__qa.getData().Latin).map(e=>e.number),paragraph:window.__qa.getData().Latin.querySelector('[id="latin-book13-num213"]')?.outerHTML}));
   if(nieseData.starts.includes(213)||nieseData.starts.includes(216)||!nieseData.starts.includes(214)||!nieseData.paragraph.includes('[VI.vii.213]'))throw Error('Inherited/approved XIII identities');
   const containing=await page.evaluate(()=>{
    const q=window.__qa,data=q.getData(),date='in mutuis documentis publicisque',prosperity='Itaque iudaei feliciter';
    return q.bambergRows().filter(r=>{const t=q.traditionalRangeView('Latin',data.Latin,r)?.textContent||'';return t.includes(date)||t.includes(prosperity);}).map(r=>r.id);
   });
   report.adjudicated_containing_views=[];
   for(const route of ['/antiquities/?book=13&chapter=6','/antiquities/?book=13&chapter=6&subchapter=6','/antiquities/?book=13&chapter=6&subchapter=7','/antiquities/?book=13&num=208','/antiquities/?book=13&num=213',...containing.map(id=>`/antiquities/?book=13&bamberg=${id}`)]){
    const captures=[];for(const which of [1,0]){await open(route,which);captures.push(await page.evaluate(({code})=>Object.fromEntries(['Latin','Greek','English'].map(l=>[l,eval('('+code+')')(document.getElementById(l.toLowerCase()),13,l)])),{code:originalHTML.toString()}));}
    if(JSON.stringify(captures[0])!==JSON.stringify(captures[1]))throw Error('Adjudicated containing view source DOM '+route);
    report.adjudicated_containing_views.push({route,three_witness_text_markup_order:'PASS',digest:hash(captures[1])});
   }
   await open('/antiquities/?book=13&niese=212');const before=await page.locator('#latin').textContent();
   if(!before.includes('in mutuis documentis publicisque')||before.includes('Itaque iudaei feliciter')||!before.includes(expected.registry.sections[211].Latin.note))throw Error('Approved212 interval/reciprocal notice');
   await open('/antiquities/?book=13&niese=214');const after=await page.locator('#latin').evaluate((node,{code,exclusions})=>eval('('+code+')')(node,exclusions),{code:narrative.toString(),exclusions:expected.exclusions.Latin});
   if(after!==norm('Itaque iudaei feliciter aduersarios uicinos superauerunt,')||!await page.locator('#latin').textContent().then(t=>t.includes(expected.registry.sections[213].Latin.note)))throw Error('Approved214 interval/reciprocal notice');
   const english=await page.locator('#english').textContent();if(!english.includes('in the first year of Simon')||!english.includes('very happy'))throw Error('Approved214 unchanged English context');
   report.adjudicated_broader_range={route:'/antiquities/?book=13&chapter=6',all_approved_clauses_once_and_transmitted_order:'PASS',inherited_label_visible:true,executable213_suppressed:true,English214_original_context:'PASS'};
  }
 }else{
  report.antiquities=[];
  for(const book of ['preface',...Array.from({length:20},(_,i)=>String(i+1))]){
   const captures=[];
   for(const which of [1,0]){await open(`/antiquities/?book=${book}`,which);captures.push(await page.evaluate(({book,code})=>{
    const html=eval('('+code+')'),q=window.__qa,data=q.getData(),capture=()=>Object.fromEntries(Object.entries(data).map(([l,d])=>[l,html(q.selectView(l,d,q.currentIdBase()),book,l)]));
    const whole=capture(),traditional=(q.traditionalRegistry()||[]).filter(r=>book==='preface'?r.context==='Proem':r.context!=='Proem'&&Number(r.book)===Number(book)).map(r=>[r.id,Object.fromEntries(Object.entries(data).map(([l,d])=>[l,html(q.traditionalRangeView(l,d,r),book,l)]))]);
    const bamberg=q.bambergRows().map(r=>[r.id,Object.fromEntries(Object.entries(data).map(([l,d])=>[l,html(q.traditionalRangeView(l,d,r),book,l)]))]);
    q.assign({viewingLevel:'section-level',sectionNum:null});const units=[...document.querySelector('#section-selector').options].filter(o=>o.value&&o.value!=='contents').map(o=>o.value),alignment=units.map(unit=>{q.assign({sectionNum:unit});return [unit,capture()];});
    const niese=[];if(false)for(const e of [...document.querySelector('#niese-selector').options].filter(o=>o.value).map(o=>({number:Number(o.value)}))){q.assign({viewingLevel:'niese-level',nieseNum:String(e.number),chapterNum:null,subchapterNum:null,sectionNum:null});niese.push([e.number,capture()]);}
    return {whole,traditional,bamberg,alignment,niese};
   },{book,code:originalHTML.toString()}));}
   if(JSON.stringify(captures[0])!==JSON.stringify(captures[1])){save(path.join(runtime,`FAIL_protected_${book}.json`),captures);throw Error('Protected three-language DOM/order mismatch '+book);}
   const contents=[];for(const which of [1,0]){await open(`/antiquities/?book=${book}&view=contents`,which);contents.push(await page.evaluate(()=>Object.fromEntries(Object.entries(window.__qa.view()).map(([l,d])=>[l,d?.outerHTML||null]))));}
   if(JSON.stringify(contents[0])!==JSON.stringify(contents[1]))throw Error('Source contents '+book);
   report.antiquities.push({book,traditional:captures[1].traditional.length,bamberg:captures[1].bamberg.length,alignment:captures[1].alignment.length,niese:captures[1].niese.length,full_DOM_order_and_contents:'PASS',digest:hash(captures[1])});console.log('protected Antiquities',book);
  }
  report.cross_works=[];
  for(const [work,count] of [['bellum-judaicum',7],['contra-apionem',2],['deh',5]])for(let book=1;book<=count;book++)for(const source of work==='bellum-judaicum'?['whiston','lodge1602']:['default']){
   const captures=[];for(const which of [1,0]){await open(`/${work}/?book=${book}${source==='default'?'':'&english='+source}`,which);captures.push(await page.evaluate(()=>{
    const q=window.__qa,data=q.getData(),capture=()=>Object.fromEntries(Object.entries(data).map(([l,d])=>[l,q.selectView(l,d,q.currentIdBase())?.outerHTML.replaceAll(location.origin,'LOCAL_ORIGIN')||null]));const whole=capture(),niese=[];
    for(const e of q.canonicalNieseStartEntries()){q.assign({viewingLevel:'niese-level',nieseNum:String(e.number),chapterNum:null,sectionNum:null});niese.push([e.number,capture()]);}
    const ranges=[],chapters=[...document.querySelector('#chapter-selector').options].filter(o=>o.value&&o.value!=='contents').map(o=>o.value);
    for(const chapter of chapters){q.assign({viewingLevel:'chapter-level',chapterNum:chapter,sectionNum:null,nieseNum:null});ranges.push(['chapter:'+chapter,capture()]);q.assign({viewingLevel:'section-level'});q.setSectionSelectOptions();for(const u of [...document.querySelector('#section-selector').options].filter(o=>o.value&&o.value!=='contents').map(o=>o.value)){q.assign({sectionNum:u});ranges.push(['unit:'+chapter+':'+u,capture()]);}}
    return {whole,niese,ranges};
   }));}if(JSON.stringify(captures[0])!==JSON.stringify(captures[1]))throw Error('Cross-work '+work+book+source);report.cross_works.push({work,book,source,niese:captures[1].niese.length,ranges:captures[1].ranges.length,result:'PASS',digest:hash(captures[1])});console.log('protected',work,book,source);
  }
  report.focused_controls=[];
  for(const [book,n] of [[8,187],[8,255],[8,367],[8,368],[8,369],[10,101],[10,102],[10,108],[10,109],[10,150],[10,151],[10,276],[10,277]]){
   const captures=[];for(const which of [1,2]){await open(`/antiquities/?book=${book}&niese=${n}`,which);captures.push(await page.evaluate(()=>Object.fromEntries(['Latin','Greek','English'].map(l=>[l,document.getElementById(l.toLowerCase()).innerHTML.replaceAll(location.origin,'LOCAL_ORIGIN')]))));}if(JSON.stringify(captures[0])!==JSON.stringify(captures[1]))throw Error('Accepted regression control '+book+'.'+n);report.focused_controls.push({book,n,result:'PASS'});
  }
  await open('/bellum-judaicum/?book=1&niese=1&english=lodge1602');const before=await page.locator('#english').innerHTML();await page.uncheck('#lodge-notes-visible');if(!await page.locator('#english').evaluate(n=>n.classList.contains('lodge-notes-hidden')))throw Error('Lodge hide');await page.reload();await page.waitForFunction(()=>window.__qaReady);if(await page.locator('#lodge-notes-visible').isChecked())throw Error('Lodge reload');await page.check('#lodge-notes-visible');if(before!==await page.locator('#english').innerHTML())throw Error('Lodge restore');await change('#english-source-selector','whiston');if(await page.locator('#lodge-notes-select').isVisible())throw Error('Whiston switching');report.Lodge_Whiston_switching='PASS';
 }
 if(report.browserExceptions.length||report.consoleErrors.length||report.failedRequests.length)throw Error('Browser/network errors');report.result='PASS';report.finished=new Date().toISOString();
 save(mode==='new-book'?path.join(packet(b),routine?'ROUTINE_REHEARSAL_BROWSER_QA.json':'IMPLEMENTATION_BROWSER_QA.json'):mode==='ranges'?path.join(packet(b),routine?'ROUTINE_RANGE_BROWSER_QA.json':'RANGE_BROWSER_QA.json'):path.join(__dirname,'PROTECTED_BROWSER_QA.json'),report);console.log('PASS',mode,b,report.scope);
 }catch(e){report.result='FAIL';report.failure=String(e);save(path.join(runtime,`FAILED_${mode}_${b}.json`),report);throw e;}
 finally{await context.close();for(const s of servers)await new Promise(r=>s.close(r));}
}
module.exports={serve,instrument,narrative,originalHTML};
if(require.main===module)main().catch(e=>{console.error(e);process.exitCode=1;});
