// New candidate checks strengthen the old contextual-English expectations.
const q=require('./browser_qa.cjs'),fs=require('fs'),path=require('path');
const {pack,oracle,chromium,serve,listen,open,select,snapshot,assert,compareWitnesses,checkInterval,hash}=q;
async function main(){
 const report={status:'RUNNING',exact:[],fallback:[],navigation:[],errors:[],requests:[]};
 const current=serve(),old=serve(true),[origin,baseline]=await Promise.all([listen(current),listen(old)]);
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 const context=await browser.newContext(),page=await context.newPage(),previous=await context.newPage();
 for(const p of [page,previous]){p.on('pageerror',e=>report.errors.push(String(e)));p.on('requestfailed',r=>report.requests.push(r.url()));}
 const identities=new Map();const add=(book,n)=>identities.set(book+':'+n,{book:String(book),number:n});
 for(const book of [...new Set(oracle.map(e=>e.book))]){const rows=oracle.filter(e=>e.book===book).sort((a,b)=>a.number-b.number);add(book,rows[0].number);add(book,rows.at(-1).number);}
 for(const n of [1,25,26])add('preface',n);
 for(const n of [27,81,152,235,260,261,262,263,264,268,269,271,272,273,294,307,312,314,315,335])add('1',n);
 for(let n=1;n<=6;n++)add('7',n);
 for(let n=49;n<=111;n++)add('9',n);
 for(const n of [310,311,312,325,326,342,343])add('11',n);
 try{
  process.env.QA_FORCE_PAGE_LOAD='1';
  for(const {book,number} of identities.values()){
   const query=`book=${book}&niese=${number}`;
   await Promise.all([open(page,origin,'antiquities',query),open(previous,baseline,'antiquities',query)]);
   const [actual,prior]=await Promise.all([snapshot(page),snapshot(previous)]);
   compareWitnesses(actual,prior,query);
   const expected=oracle.find(e=>e.book===book&&e.number===number);
   report.exact.push({...checkInterval(actual,expected),direct_URL:page.url(),Greek_Latin_unchanged:true});
   if(book==='9'&&number>=51&&number<=109){
    assert(actual.languages.latin.unavailable&&actual.languages.greek.unavailable,'Restored English incorrectly invented another witness');
    assert((await page.locator('#english').innerText()).includes('Alden & Beardsley'),'Restoration authority notice missing');
   }
  }
  delete process.env.QA_FORCE_PAGE_LOAD;
  for(const book of ['preface','1','7','9','11']){
   const number=book==='preface'?25:book==='1'?27:book==='7'?1:book==='9'?50:311;
   await open(page,origin,'antiquities',`book=${book}&niese=${number}`);
   for(const n of [number+1,number]){
    await select(page,n);const actual=await snapshot(page);
    checkInterval(actual,oracle.find(e=>e.book===book&&e.number===n));
    report.navigation.push({book,number:n,native_selection:true,passed:true});
   }
  }
  for(let book=12;book<=20;book++){
   const query=`book=${book}&niese=1`;
   await Promise.all([open(page,origin,'antiquities',query),open(previous,baseline,'antiquities',query)]);
   const [actual,prior]=await Promise.all([snapshot(page),snapshot(previous)]);
   assert(actual.languages.english.html===prior.languages.english.html,'Contextual fallback changed '+book);
   assert(actual.languages.english.context&&!actual.languages.english.exact,'Contextual fallback distinction missing '+book);
   report.fallback.push({book,passed:true,English_sha256:hash(actual.languages.english.html)});
  }
  assert(!report.errors.length&&!report.requests.length,'Reader or HTTP failure');report.status='PASS';
 }catch(e){report.status='FAIL';report.failure=String(e);throw e;}
 finally{fs.writeFileSync(path.join(pack,'CANDIDATE_SMOKE_QA.json'),JSON.stringify(report,null,2)+'\n');await browser.close();current.close();old.close();}
 console.log('Candidate actual displayed content PASS',report.exact.length,'exact intervals',report.navigation.length,'native neighbour selections',report.fallback.length,'contextual fallback books');
}
main().catch(e=>{console.error(e);process.exitCode=1;});
