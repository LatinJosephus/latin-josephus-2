const q=require('./browser_qa.cjs'),fs=require('fs'),path=require('path');
const {pack,serve,listen,chromium,open,select,snapshot,assert,checkInterval,oracle,compareWitnesses,hash}=q;
const whole=JSON.parse(fs.readFileSync(path.join(pack,'CONTAINING_ORACLE.json'))).whole;
async function main(){
 const result={status:'RUNNING',transitions:[],errors:[],requests:[]};
 const current=serve(),old=serve(true),[a,b]=await Promise.all([listen(current),listen(old)]);
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 const page=await browser.newPage(),prior=await browser.newPage();
 for(const p of [page,prior]){p.on('pageerror',e=>result.errors.push(String(e)));p.on('requestfailed',r=>result.requests.push(r.url()));}
 try{
  await open(page,a,'antiquities','book=11&niese=347');
  for(const book of [12,13,14,15,16,15,11]){
   const count=await page.evaluate(()=>window.__qaCount);
   await page.locator('#book-selector').selectOption(String(book));
   await page.waitForFunction(({count,book})=>window.__qaCount>count&&Number(window.__qaRendered.bookNum)===book,{count,book},{timeout:60000,polling:10});
   let actual=await snapshot(page);assert(actual.state.viewingLevel==='book-level','Native book change did not reset the view');
   await open(prior,b,'antiquities',`book=${book}`);let before=await snapshot(prior);compareWitnesses(actual,before,'Native book '+book);
   assert(actual.languages.english.text===(whole[String(book)]||before.languages.english.text),'Native whole-book content differs');
   const wholeSHA256=hash(actual.languages.english.text);
   await page.locator('#niese-level').check();
   await page.waitForFunction(()=>window.__qaRendered.viewingLevel==='niese-level',null,{timeout:60000,polling:10});
   await select(page,1);actual=await snapshot(page);
   if(book<=15)checkInterval(actual,oracle.find(r=>r.book===String(book)&&r.number===1));
   else{
    await open(prior,b,'antiquities',`book=${book}&niese=1`);before=await snapshot(prior);
    assert(actual.languages.english.context&&!actual.languages.english.exact&&actual.languages.english.html===before.languages.english.html,'Native fallback changed');
   }
   result.transitions.push({book,wholeSHA256,selectedSection:1,exact:book<=15,passed:true,URL:page.url()});
  }
  assert(!result.errors.length&&!result.requests.length,'Native navigation browser errors');result.status='PASS';
 }catch(e){result.status='FAIL';result.failure=String(e);throw e;}
 finally{fs.writeFileSync(path.join(pack,'BOOK_NAVIGATION_QA.json'),JSON.stringify(result,null,2)+'\n');await browser.close();current.close();old.close();}
 console.log('Native book navigation PASS',result.transitions.length);
}
main().catch(e=>{console.error(e);process.exitCode=1;});
