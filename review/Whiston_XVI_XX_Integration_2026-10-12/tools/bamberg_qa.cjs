const q=require('./browser_qa.cjs'),fs=require('fs'),path=require('path');
const {pack,serve,listen,chromium,open,snapshot,assert,hash,compareWitnesses}=q;
async function main(){
 const report={status:'RUNNING',views:[],errors:[]};const current=serve(),old=serve(true),[a,b]=await Promise.all([listen(current),listen(old)]);
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 const ctx=await browser.newContext(),page=await ctx.newPage(),base=await ctx.newPage();for(const p of [page,base])p.on('pageerror',e=>report.errors.push(String(e)));
 try{
  const books=process.env.QA_BOOKS?process.env.QA_BOOKS.split(','):['preface',...Array.from({length:20},(_,i)=>i+1)];
  for(const book of books){
   await Promise.all([open(page,a,'antiquities',`book=${book}`),open(base,b,'antiquities',`book=${book}`)]);
   const units=await page.locator('#bamberg-selector').evaluate(e=>[...e.options].filter(e=>e.value).map(e=>e.value));
   const prior=await base.locator('#bamberg-selector').evaluate(e=>[...e.options].filter(e=>e.value).map(e=>e.value));assert(JSON.stringify(units)===JSON.stringify(prior),'Bamberg navigation inventory changed');
   for(const unit of units){
    const query=`book=${book}&bamberg=${encodeURIComponent(unit)}`;
    await Promise.all([open(page,a,'antiquities',query),open(base,b,'antiquities',query)]);
    const [actual,before]=await Promise.all([snapshot(page),snapshot(base)]);compareWitnesses(actual,before,query);
    assert(actual.state.viewingLevel==='bamberg-level'&&actual.state.bambergId===unit,'Bamberg deep link did not select its actual identity');
    assert(actual.languages.english.text===before.languages.english.text,'Bamberg English content changed '+query,{actual,before});
    assert(actual.languages.english.hiddenNarrative.length===0,'Bamberg hidden narrative');
    report.views.push({book,unit,state:actual.state,EnglishSHA256:hash(actual.languages.english.text),GreekLatinUnchanged:true,passed:true});
   }
   fs.writeFileSync(path.join(pack,'BAMBERG_QA.json'),JSON.stringify(report,null,2));console.log('Bamberg book',book,'views',units.length);
  }
  assert(!report.errors.length,'Bamberg script errors');report.status='PASS';
 }catch(e){report.status='FAIL';report.failure=String(e);throw e;}
 finally{fs.writeFileSync(path.join(pack,'BAMBERG_QA.json'),JSON.stringify(report,null,2));await browser.close();current.close();old.close();}
 console.log('BAMBERG PASS',report.views.length);
}
main().catch(e=>{console.error(e);process.exitCode=1;});
