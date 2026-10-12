const q=require('./browser_qa.cjs'),fs=require('fs'),path=require('path');
const {pack,serve,listen,chromium,open,snapshot,assert,hash,checkInterval,oracle}=q;
async function main(){
 const report={status:'RUNNING',direct:[],navigation:[],fallback:[],themes:[],errors:[]};const current=serve(),old=serve(true),[a,b]=await Promise.all([listen(current),listen(old)]);
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});const ctx=await browser.newContext({viewport:{width:1440,height:1000}}),page=await ctx.newPage(),base=await ctx.newPage();for(const p of [page,base])p.on('pageerror',e=>report.errors.push(String(e)));
 const books=process.env.QA_NEW_BOOKS?process.env.QA_NEW_BOOKS.split(',').map(Number):[16,17,18,19,20];fs.mkdirSync(path.join(pack,'evidence'),{recursive:true});
 try{
  for(const book of books){
   const rows=oracle.filter(e=>e.book===String(book)),first=rows[0],last=rows.at(-1),selection=[first,last,...rows.filter(e=>[77,123,189,199,212,215,216,217,218,257,267,268,292,295,299,349,350,351,354,355,359,363,364,365,366,395,400,404].includes(e.number))];
   for(const expected of selection){
    process.env.QA_FORCE_PAGE_LOAD='1';await open(page,a,'antiquities',`book=${book}&niese=${expected.number}`);delete process.env.QA_FORCE_PAGE_LOAD;
    const actual=await snapshot(page);const result=checkInterval(actual,expected);assert(await page.locator('#english h3').count()===1,'English heading count changed');
    report.direct.push({...result,deepLink:page.url()});
   }
   await open(page,a,'antiquities',`book=${book}&niese=${first.number}`);
   let count=await page.evaluate(()=>window.__qaCount);await page.locator('#niese-next').click();await page.waitForFunction(c=>window.__qaCount>c,count,{polling:10});let actual=await snapshot(page);checkInterval(actual,rows[1]);report.navigation.push({book,from:first.number,to:rows[1].number,kind:'native-next',passed:true});
   count=await page.evaluate(()=>window.__qaCount);await page.locator('#niese-previous').click();await page.waitForFunction(c=>window.__qaCount>c,count,{polling:10});checkInterval(await snapshot(page),first);assert(await page.locator('#niese-previous').isDisabled(),'Opening previous enabled');report.navigation.push({book,kind:'native-previous-and-opening-limit',passed:true});
   await open(page,a,'antiquities',`book=${book}&niese=${last.number}`);assert(await page.locator('#niese-next').isDisabled(),'Closing next enabled');
   for(const width of [1440,375]){
    await page.setViewportSize({width,height:1000});await open(page,a,'antiquities',`book=${book}&niese=${first.number}`);
    for(const theme of ['light','dark']){
     await page.evaluate(theme=>setTheme(theme),theme);checkInterval(await snapshot(page),first);
     const layout=await page.evaluate(()=>({theme:document.documentElement.dataset.theme,width:innerWidth,scrollWidth:document.documentElement.scrollWidth,background:getComputedStyle(document.body).backgroundColor,EnglishVisible:!!document.querySelector('#english').getClientRects().length}));
     assert(layout.theme===theme&&layout.EnglishVisible&&layout.scrollWidth<=layout.width+1,'Theme or mobile layout failed',layout);
     report.themes.push({book,width,theme,...layout,passed:true});await page.screenshot({path:path.join(pack,'evidence',`book-${book}-${width}-${theme}.png`),fullPage:true});
    }
   }
   await page.setViewportSize({width:1440,height:1000});await page.evaluate(()=>setTheme('light'));
  }
  for(const book of Array.from({length:20-books.at(-1)},(_,i)=>books.at(-1)+i+1))for(const number of [1,Math.ceil({14:491,15:425,16:404,17:355,18:379,19:366,20:268}[book]/2),{14:491,15:425,16:404,17:355,18:379,19:366,20:268}[book]]){
   const query=`book=${book}&niese=${number}`;await Promise.all([open(page,a,'antiquities',query),open(base,b,'antiquities',query)]);const [actual,before]=await Promise.all([snapshot(page),snapshot(base)]);
   assert(actual.languages.english.context&&!actual.languages.english.exact,'Unintegrated fallback incorrectly enabled');assert(actual.languages.english.html===before.languages.english.html,'Fallback source changed');assert(actual.languages.english.text.length>0,'Empty contextual fallback');report.fallback.push({book,number,EnglishSHA256:hash(actual.languages.english.html),passed:true});
  }
  assert(!report.errors.length,'UI script errors');report.status='PASS';
 }catch(e){report.status='FAIL';report.failure=String(e);throw e;}
 finally{fs.writeFileSync(path.join(pack,'UI_QA.json'),JSON.stringify(report,null,2));await browser.close();current.close();old.close();}
 console.log('UI PASS',report.direct.length,report.navigation.length,report.fallback.length,report.themes.length);
}
main().catch(e=>{console.error(e);process.exitCode=1;});
