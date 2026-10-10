// Actual combined menus, uninstrumented approved cases and independent structural controls.
const {fs,path,chromium,runtime,root,load,save,norm,hash,serve,listen,narrative}=require('./qa-common18.cjs');
async function main(){
 const build=load(path.join(__dirname,'BUILD_CONTEXT.json')),report={scope:'ACTUAL_ALL_BOOK_IDENTITY_SET_AND_UNINSTRUMENTED_APPROVED_CASES',started:new Date().toISOString(),books:[],uninstrumented:[],physical_navigation:[],errors:[]};
 const servers=[serve(build.site),serve(build.site,false)],origins=[];for(const s of servers)origins.push(await listen(s));
 const context=await chromium.launchPersistentContext(path.join(runtime,'browser-combined-extra'),{headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'}),page=await context.newPage();
 page.on('pageerror',e=>report.errors.push(String(e)));page.on('requestfailed',r=>report.errors.push(r.url()+':'+r.failure()?.errorText));
 const open=async(book,n,plain=false)=>{await page.goto(origins[plain?1:0]+`/antiquities/?book=${book}`+(n?'&niese='+n:''),{waitUntil:'domcontentloaded'});if(!plain)await page.waitForFunction(()=>window.__qaReady);else await page.waitForFunction(n=>['latin','greek','english'].every(l=>document.querySelector(`#${l} [type^="niese-"][n="${n}"]`)),n);};
 try{
  for(const book of ['preface',...Array.from({length:20},(_,i)=>i+1)]){
   await open(book);const inventory=await page.evaluate(()=>({menu:[...document.querySelector('#niese-selector').options].filter(o=>o.value).map(o=>Number(o.value)),disabled:document.querySelector('#niese-level').disabled,entries:window.__qa.canonicalNieseStartEntries().map(x=>x.number)}));
   if(JSON.stringify(inventory.menu)!==JSON.stringify(inventory.entries))throw Error('Menu versus actual identity entries '+book);
   report.books.push({book,...inventory});
  }
  report.identity_set=report.books.flatMap(b=>b.menu.map(n=>`${b.book}.${n}`));
  if(report.identity_set.length!==7082||new Set(report.identity_set).size!==7082)throw Error('Actual combined identity set');
  if(report.books.filter(b=>[20].includes(b.book)).some(b=>b.menu.length||!b.disabled))throw Error('Unintegrated book scope changed');
  for(const [book,roman,cases] of [[18,'XVIII',[6,7,8,93,94,95,215,216,217,218,256,257,258]],[19,'XIX',[187,188,189,291,292,293]]]){
   const expected=load(path.join(root,`review/Antiquities_Niese_Book${roman}_2026-10-09/FINAL_EXPECTED_INTERVALS.json`));
   for(const n of cases){await open(book,n,true);const actual=await page.evaluate(code=>({helper:!!window.__qa,text:Object.fromEntries(['Latin','Greek','English'].map(l=>[l,eval('('+code+')')(document.getElementById(l.toLowerCase()))])),unavailable:document.querySelector('#latin .structural-unavailable')?.textContent,note:document.querySelector('#latin .niese-correspondence-note')?.textContent}),narrative.toString());
    if(actual.helper)throw Error('Uninstrumented page has helper');const e=expected[n-1];for(const l of ['Greek','English'])if(actual.text[l]!==norm(e[l]))throw Error('Uninstrumented context '+book+'.'+n+' '+l);
    if(e.unavailable){if(actual.text.Latin!==''||!actual.unavailable.includes(e.qualification)||!actual.unavailable.includes('No nearby text has been substituted.'))throw Error('Uninstrumented unavailable '+n);}else if(actual.text.Latin!==norm(e.Latin)||(actual.note||null)!==e.qualification)throw Error('Uninstrumented Latin '+book+'.'+n);
    report.uninstrumented.push({book,n,Latin:e.unavailable?'SPECIFIC_EMPTY_NOTICE':'EXACT_INTERVAL',Greek:'EXACT',English:'EXACT_CONTEXT',sha256:hash(actual)});
   }
  }
  const proof=load(path.join(__dirname,'DISTINCT_PHYSICAL_POINT_PROOF.json'));
  for(const b of [18,19]){
   const p=proof.find(x=>x.book===b),chapter=Number(p.traditional.match(/Chapter-(\d+)-/)[1]);await open(b);
   await page.check('#chapter-level');await page.evaluate(()=>window.__qaPending);await page.selectOption('#chapter-selector',String(chapter));await page.evaluate(()=>window.__qaPending);
   const captures=[await page.evaluate(code=>({state:window.__qa.getState(),text:Object.fromEntries(['Latin','Greek','English'].map(l=>[l,eval('('+code+')')(window.__qa.view()[l])]))}),narrative.toString())];
   await page.check('#bamberg-level');await page.evaluate(()=>window.__qaPending);await page.selectOption('#bamberg-selector',p.bamberg);await page.evaluate(()=>window.__qaPending);
   captures.push(await page.evaluate(code=>({state:window.__qa.getState(),text:Object.fromEntries(['Latin','Greek','English'].map(l=>[l,eval('('+code+')')(window.__qa.view()[l])]))}),narrative.toString()));
   for(const row of proof.filter(x=>x.book===b)){const a=norm(row.traditional_coordinate.right).slice(0,80),z=norm(row.bamberg_coordinate.right).slice(0,80);if(!captures[0].text[row.language].startsWith(a)||!captures[1].text[row.language].startsWith(z)||captures[0].text[row.language]===captures[1].text[row.language])throw Error('Physical navigation collapsed '+b+' '+row.language);}
   report.physical_navigation.push({book:b,traditional:p.traditional,bamberg:p.bamberg,shared_niese:p.shared_niese,status:'INDEPENDENT_ACTUAL_CONTROLS_DISTINCT_STARTS',sha256:hash(captures)});
  }
  if(report.errors.length)throw Error('Combined extra errors');report.result='PASS';
 }catch(e){report.result='FAIL';report.failure=String(e);}finally{report.finished=new Date().toISOString();save(path.join(__dirname,'COMBINED_EXTRA_RESULTS.json'),report);await context.close();for(const s of servers)await new Promise(r=>s.close(r));}
 console.log(JSON.stringify({result:report.result,failure:report.failure,identities:report.identity_set?.length,uninstrumented:report.uninstrumented.length,physical_navigation:report.physical_navigation.length,errors:report.errors}));if(report.result!=='PASS')process.exitCode=1;
}
main().catch(e=>{console.error(e);process.exitCode=1;});
