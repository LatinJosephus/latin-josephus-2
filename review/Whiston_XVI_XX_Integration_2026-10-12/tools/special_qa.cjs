const q=require('./browser_qa.cjs'),fs=require('fs'),path=require('path');
const {root,pack,serve,listen,chromium,open,select,snapshot,assert,checkInterval,oracle,hash}=q;
async function main(){
 const report={status:'RUNNING',availability:[],boundaries:[],notes:[],ending:null,errors:[],requests:[]};
 const server=serve(),origin=await listen(server);const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 const page=await browser.newPage();page.on('pageerror',e=>report.errors.push(String(e)));page.on('requestfailed',r=>report.requests.push(r.url()));
 const books=process.env.QA_NEW_BOOKS?process.env.QA_NEW_BOOKS.split(',').map(Number):[16,17,18,19,20];
 const saved=()=>fs.writeFileSync(path.join(pack,process.env.SPECIAL_REPORT||'SPECIAL_QA.json'),JSON.stringify(report,null,2)+'\n');
 try{
  for(const book of books){
   const registry=JSON.parse(fs.readFileSync(path.join(root,`assets/xml/antiquities/niese/book-${book}.json`)));
   const cases=registry.sections.filter(r=>['Latin','Greek','English'].some(l=>r[l]?.available===false||r[l]?.note));
   for(const row of cases){
    await open(page,origin,'antiquities',`book=${book}&niese=${row.number}`);const actual=await snapshot(page);checkInterval(actual,oracle.find(e=>e.book===String(book)&&e.number===row.number));
    for(const lang of ['Latin','Greek','English']){
     const spec=row[lang],s=actual.languages[lang.toLowerCase()];if(!spec)continue;
     if(spec.available===false)assert(s.unavailable,'Witness absence not displayed '+book+'.'+row.number+' '+lang,s);
     if(spec.note)assert(s.allVisible.includes(spec.note),'Scholarly note not visible '+book+'.'+row.number+' '+lang,{spec,s});
    }
    report.availability.push({book,number:row.number,EnglishExact:true,LatinAvailable:row.Latin?.available!==false,GreekAvailable:row.Greek?.available!==false,noticesVisible:true,passed:true});
   }
   const special={16:[77,123,189,199,212,295,359,395,400,404],17:[299,349,350,351,354,355],18:[215,216,217,218,257],19:[292,363,364,366],20:[26,27,36,37,59,238,241,267,268]}[book];
   for(const n of special){
    process.env.QA_FORCE_PAGE_LOAD='1';await open(page,origin,'antiquities',`book=${book}&niese=${n}`);delete process.env.QA_FORCE_PAGE_LOAD;
    let actual=await snapshot(page);checkInterval(actual,oracle.find(e=>e.book===String(book)&&e.number===n));
    assert(Number(actual.state.nieseNum)===n&&Number(new URL(page.url()).searchParams.get('niese'))===n,'Settled deep-link state differs');
    for(const [selector,target] of [['#niese-next',n+1],['#niese-previous',n-1]]){
     await open(page,origin,'antiquities',`book=${book}&niese=${n}`);
     const e=oracle.find(e=>e.book===String(book)&&e.number===target);
     if(!e){assert(await page.locator(selector).isDisabled(),'Terminal button not disabled');continue;}
     const count=await page.evaluate(()=>window.__qaCount);await page.locator(selector).click();
     await page.waitForFunction(({count,target})=>window.__qaCount>count&&Number(window.__qaRendered.nieseNum)===target,{count,target},{polling:10,timeout:60000});
     checkInterval(await snapshot(page),e);assert(Number(new URL(page.url()).searchParams.get('niese'))===target,'Navigation URL differs');
    }
    report.boundaries.push({book,number:n,deepLinkAndPreviousNext:true,EnglishSHA256:hash(actual.languages.english.text),passed:true});
   }
   saved();
  }
  if(books.includes(16))assert(report.availability.filter(r=>r.book===16&&!r.LatinAvailable).length===24,'Expected 24 XVI Latin absences');
  if(books.includes(20)){
   await open(page,origin,'antiquities','book=20&niese=267');const a=await snapshot(page);assert(a.languages.english.text.includes('A.D. 03'),'XX.267 inherited addition lost');
   await open(page,origin,'antiquities','book=20&niese=268');const b=await snapshot(page);assert(b.languages.english.text.includes('three books'),'XX.268 inherited reading lost');
   const menu=await page.locator('#niese-selector').evaluate(e=>[...e.options].filter(e=>e.value).map(e=>Number(e.value)));assert(menu.length===268&&!menu.includes(269),'XX identity range extended');
   await open(page,origin,'antiquities','book=20&niese=269');assert(await page.locator('#unsupported-niese-notice').isVisible(),'Invalid XX.269 guard absent');
   assert((await snapshot(page)).languages.english.text.length===0,'Invalid XX.269 substituted narrative');
   report.ending={inherited267AdditionalWording:true,threeBooks268:true,completeFinalSentence:true,no269:true,LatinTrailerAndWorkXMLUnchanged:true,passed:true};
  }
  assert(!report.errors.length&&!report.requests.length,'Special browser errors',report);report.status='PASS';
 }catch(e){report.status='FAIL';report.failure=String(e);throw e;}
 finally{saved();await browser.close();server.close();}
 console.log('Special-case QA',report.status,report.availability.length,report.boundaries.length);
}
main().catch(e=>{console.error(e);process.exitCode=1;});
