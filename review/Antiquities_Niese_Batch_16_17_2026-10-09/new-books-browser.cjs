const {fs,path,chromium,packet,root,runtime,candidate,baseline,sha,serve,listen,normalize,narrative,open,change,capture,builtHashes}=require('./qa-common.cjs');
const expected={};
for(const [b,roman] of [[16,'XVI'],[17,'XVII']]){
 const folder=path.join(root,`review/Antiquities_Niese_Book${roman}_2026-10-09`);
 const rows=JSON.parse(fs.readFileSync(path.join(folder,'BOUNDARIES.json'),'utf8'));
 const proof=JSON.parse(fs.readFileSync(path.join(folder,'INDEPENDENT_IMPLEMENTATION_SOURCE_PROOF.json'),'utf8'));
 const Latin={};for(const r of proof.independently_resolved_registry_ranges)(Latin[r.number]||=[]).push(r.text);
 expected[b]={rows,Latin:Object.fromEntries(rows.map(r=>[r.number,Latin[r.number]?normalize(Latin[r.number].join('')):null])),Greek:Object.fromEntries(rows.map(r=>[r.number,normalize(r.Greek_reviewed_interval.text)])),count:rows.length};
}
async function main(){
 let report={status:'RUNNING',purpose:'ACTUAL_BUILT_READER_ALL_759_NEW_IDENTITIES',started:new Date().toISOString(),books:{},errors:[],consoleErrors:[],requestFailures:[],built_source_hashes:builtHashes()};
 const resumeUI=process.argv.includes('--resume-ui');
 if(resumeUI){
  const file=path.join(packet,'NEW_BOOK_BROWSER_FAILURE.json'),raw=fs.readFileSync(file),seed=JSON.parse(raw);
  if(JSON.stringify(seed.built_source_hashes)!==JSON.stringify(report.built_source_hashes)||seed.pane_switches!=='PASS'||seed.direct_navigation.length!==50||seed.themes.length!==2||seed.errors.length||seed.consoleErrors.length||seed.requestFailures.length)throw Error('UI resumption requires identical build and completed successful selection/navigation/theme phases');
  for(const [b,count] of [[16,404],[17,355]])if(seed.books[b].identity_count!==count||seed.books[b].selections.some((r,i)=>r.number!==i+1||r.actual_selector!=='PASS'||r.next_previous!=='PASS'))throw Error('Invalid completed selection evidence');
  report={...seed,status:'RUNNING',resumed_UI_UTC:new Date().toISOString(),completed_selection_evidence:{file:'NEW_BOOK_BROWSER_FAILURE.json',sha256:sha(raw),all_759_selections_already_passed_on_identical_build:true}};delete report.failure;
 }
 const servers=[serve(candidate),serve(baseline),serve(candidate,false)];const origins=[];
 for(let i=0;i<servers.length;i++)origins.push(await listen(servers[i],i===0?8916:0));report.origins=origins;
 const context=await chromium.launchPersistentContext(path.join(runtime,'browser-candidate-new-books'),{headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',viewport:{width:1500,height:1000}});
 const page=await context.newPage();page.on('pageerror',e=>report.errors.push(String(e)));page.on('console',m=>{if(m.type()==='error')report.consoleErrors.push(m.text());});page.on('requestfailed',r=>report.requestFailures.push({url:r.url(),error:r.failure()?.errorText}));
 const expectedEnglish={};const knownDuplicates={};
 async function verify(b,n,actual){
  const e=expected[b],row=e.rows[n-1];
  for(const lang of ['Latin','Greek']){
   const wanted=e[lang][n],out=actual.languages[lang];
   if(wanted===null){if(!out.unavailable||out.text)throw Error(`${b}.${n} ${lang} must be source-unavailable without fallback`);}
   else if(out.unavailable||out.text!==wanted){
    fs.writeFileSync(path.join(packet,'NEW_BOOK_TEXT_MISMATCH.json'),JSON.stringify({b,n,lang,actual:out.text,expected:wanted},null,2));
    throw Error(`${b}.${n} ${lang} source interval mismatch`);
   }
  }
  const en=actual.languages.English;if(!en.context||en.unavailable||en.text!==expectedEnglish[b][row.number].text)throw Error(`${b}.${n} independent Whiston context`);
  const notes=row.registry_Latin.note;if(notes!==actual.languages.Latin.note&&expected[b].Latin[n]!==null)throw Error(`${b}.${n} correspondence notice`);
  const fragments=row.registry_Latin.spans?.length||0;if(fragments>1&&actual.languages.Latin.fragments!==fragments)throw Error(`${b}.${n} physical fragments`);
  const allowed=knownDuplicates[b][n]||[];
  for(const id of actual.duplicateIDs)if(!allowed.includes(id))throw Error(`${b}.${n} new duplicate DOM ID ${id}`);
  if(actual.nieseValue!==String(n))throw Error('Actual selector identity');
  if(actual.previousDisabled!==(n===1)||actual.nextDisabled!==(n===e.count))throw Error('Navigation endpoints '+b+'.'+n);
 }
 try{
  for(const b of [16,17]){
   // Independent English expectations come from the immutable built baseline's
   // existing alignment; new Latin registry cuts cannot supply their own oracle.
   await open(page,origins[1],`book=${b}`);
   const targets=expected[b].rows.map(r=>({number:r.number,target:r.Latin_locator?.stable_id||r.registry_Latin?.spans?.[0]?.start?.paragraph||''}));
   const registry=JSON.parse(fs.readFileSync(path.join(root,`assets/xml/antiquities/niese/book-${b}.json`),'utf8'));
   const english=await page.evaluate(({rows,textCode})=>{
    const text=eval('('+textCode+')'),q=window.__qa,d=q.getData();const output={};
    for(const r of rows){const holder=document.createElement('div');q.alignedParagraphsForCanonicalId('English',d.English,r.contextTarget).forEach(p=>holder.append(p.cloneNode(true)));
     const ids=[...holder.querySelectorAll('[id]')].map(n=>n.id);output[r.number]={text:text(holder),duplicates:ids.filter((id,i)=>ids.indexOf(id)!==i)};}
    return output;
   },{rows:registry.sections,textCode:narrative.toString()});
   expectedEnglish[b]=english;knownDuplicates[b]=Object.fromEntries(Object.entries(english).map(([n,x])=>[n,x.duplicates]));
   await open(page,origins[0],`book=${b}&niese=1`);
   for(const lang of ['english','greek'])if(!await page.locator('#'+lang+'-pane-select').isChecked())await page.check('#'+lang+'-pane-select');
   const inventory=await page.evaluate(()=>({options:[...document.querySelector('#niese-selector').options].filter(o=>o.value).map(o=>Number(o.value)),starts:Object.fromEntries(['Latin','Greek'].map(l=>[l,window.__qa.antiquitiesNieseStartEntries(l,window.__qa.getData()[l]).map(e=>e.number)])),radioDisabled:document.querySelector('#niese-level').disabled}));
   if(inventory.radioDisabled||JSON.stringify(inventory.options)!==JSON.stringify(Array.from({length:expected[b].count},(_,i)=>i+1)))throw Error('Complete Niese menu '+b);
   for(const [lang,numbers] of Object.entries(inventory.starts))if(numbers.length!==new Set(numbers).size)throw Error('Duplicate executable starts '+b+' '+lang);
   const selections=[];
   for(let n=1;!resumeUI&&n<=expected[b].count;n++){
    await change(page,'#niese-selector',n);const actual=await capture(page);await verify(b,n,actual);
    if(n<expected[b].count){await page.click('#niese-next');await page.waitForFunction(n=>window.__qaRenderedState?.nieseNum===String(n),n+1);await verify(b,n+1,await capture(page));
     await page.click('#niese-previous');await page.waitForFunction(n=>window.__qaRenderedState?.nieseNum===String(n),n);await verify(b,n,await capture(page));}
    selections.push({number:n,actual_selector:'PASS',next_previous:'PASS',Latin:actual.languages.Latin.unavailable?'UNAVAILABLE':'PRESENT',Greek:'PRESENT',English:'BASELINE_CONTEXT',fragments:actual.languages.Latin.fragments,known_baseline_duplicate_ids:actual.duplicateIDs,digest:sha(actual.languages)});
    if(n%50===0){fs.writeFileSync(path.join(packet,'NEW_BOOK_BROWSER_PROGRESS.json'),JSON.stringify({book:b,selected:n,total:expected[b].count},null,2));console.log('new-book',b,n,'/',expected[b].count);}
   }
   if(!resumeUI)report.books[b]={identity_count:selections.length,Latin_present:selections.filter(x=>x.Latin==='PRESENT').length,Latin_unavailable:selections.filter(x=>x.Latin==='UNAVAILABLE').length,inventory,selections,status:'ALL_INDIVIDUAL_SELECTIONS_PASS'};
   console.log('new-book complete',b,resumeUI?'retained identical-build PASS evidence':selections.length);
  }
  if(!resumeUI){
  report.direct_navigation=[];
  const clusters={16:[1,77,123,188,189,194,199,200,234,235,236,294,295,350,351,352,354,355,356,357,367,368,369,394,395,404],17:[1,24,25,26,30,31,32,74,75,76,77,105,106,107,145,146,147,298,299,300,354,355]};
  for(const [book,sections] of Object.entries(clusters))for(const n of sections){
   const b=Number(book);await open(page,origins[0],`book=${b}&niese=${n}`);await verify(b,n,await capture(page));
   await page.reload();await page.waitForFunction(()=>window.__qaReady);await verify(b,n,await capture(page));
   if(n<expected[b].count){await page.click('#niese-next');await page.waitForFunction(n=>window.__qaRenderedState?.nieseNum===String(n),n+1);
    await page.goBack();await page.waitForFunction(n=>window.__qaRenderedState?.nieseNum===String(n),n);await verify(b,n,await capture(page));
    await page.goForward();await page.waitForFunction(n=>window.__qaRenderedState?.nieseNum===String(n),n+1);await verify(b,n+1,await capture(page));}
   await open(page,origins[2],`book=${b}&niese=${n}`, 'antiquities',false);await verify(b,n,await capture(page));
   report.direct_navigation.push({book:b,n,direct_URL_reload_history_uninstrumented:'PASS'});
   if([[16,294],[16,351],[16,368],[16,395],[17,25],[17,76],[17,106],[17,146],[17,299],[17,355]].some(([x,y])=>x===b&&y===n))await page.screenshot({path:path.join(packet,'evidence',`candidate-Book${b}-Niese${n}.png`),fullPage:true});
  }
  // Established selection query parameters coexist with an independent anchor
  // fragment; hash-only selection parameters are not supported by the reader.
  for(const b of [16,17]){
   await page.goto(`${origins[0]}/antiquities/?book=${b}&niese=1#latin-book${b}-num1`);await page.waitForFunction(()=>window.__qaReady);await verify(b,1,await capture(page));
   report.direct_navigation.push({book:b,n:1,fragment_parameters:'PASS'});
  }
  }
  report.themes=[];await open(page,origins[0],'book=16&niese=351');
  for(const theme of ['light','dark']){
   const baselineStyle=JSON.parse(fs.readFileSync(path.join(packet,'THEME_BASELINE_DIAGNOSTIC.json'),'utf8')).find(x=>x.which===0&&x.theme===theme).style;
   await page.evaluate(t=>setTheme(t),theme);
   // Theme transitions animate for 750 ms. Certify their final computed color,
   // rather than reading the previous color in the same animation frame.
   await page.waitForFunction(({theme,body})=>document.documentElement.dataset.theme===theme&&getComputedStyle(document.body).backgroundColor===body,{theme,body:baselineStyle.body});
   const style=await page.evaluate(()=>({theme:document.documentElement.dataset.theme,background:getComputedStyle(document.body).backgroundColor,noticeColor:getComputedStyle(document.querySelector('.niese-correspondence-note')).color,stored:localStorage.getItem('theme')}));
   if(style.stored!==theme)throw Error('Theme storage');report.themes.push(style);
   await page.screenshot({path:path.join(packet,'evidence',`candidate-Book16-Niese351-${theme}.png`),fullPage:true});
  }
  if(report.themes[0].background===report.themes[1].background)throw Error('Theme colors unchanged');
  for(const lang of ['english','greek']){await page.uncheck('#'+lang+'-pane-select');await page.check('#'+lang+'-pane-select');}await verify(16,351,await capture(page));
  report.pane_switches='PASS';
  report.book_transitions=[];
  for(const [from,to,last] of [[15,16,425],[16,17,404],[17,18,355]]){
   await open(page,origins[0],`book=${from}&niese=${last}`);
   await change(page,'#book-selector',to);
   const state=await page.evaluate(()=>window.__qa.getState());
   if(Number(state.bookNum)!==to)throw Error('Book transition '+from+' to '+to);
   const actual=await capture(page);
   if([16,17].includes(to)){await page.check('#niese-level');await page.evaluate(()=>window.__qaPending);await change(page,'#niese-selector',1);await verify(to,1,await capture(page));}
   else if(actual.nieseValue||!actual.languages.Latin.text)throw Error('Unimplemented XVIII transition');
   report.book_transitions.push({from,to,result:'PASS',retained_destination_whole_or_first_section:true});
  }
  if(report.errors.length||report.consoleErrors.length||report.requestFailures.length)throw Error('Unexpected browser diagnostics '+JSON.stringify({errors:report.errors,console:report.consoleErrors,network:report.requestFailures}));
  report.status='PASS_ALL_759_NEW_SELECTIONS_AND_NAVIGATION';report.finished=new Date().toISOString();
  fs.writeFileSync(path.join(packet,'NEW_BOOK_BROWSER_QA.json'),JSON.stringify(report,null,2)+'\n');console.log(report.status);
 }catch(e){report.status='FAIL';report.failure=String(e);fs.writeFileSync(path.join(packet,'NEW_BOOK_BROWSER_FAILURE.json'),JSON.stringify(report,null,2)+'\n');throw e;}
 finally{await context.close();await Promise.all(servers.map(s=>new Promise(r=>s.close(r))));}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
