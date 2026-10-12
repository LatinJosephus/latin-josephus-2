const q=require('./browser_qa.cjs'),fs=require('fs'),path=require('path');
const {pack,chromium,serve,listen,open,snapshot,assert,compareWitnesses,hash}=q;
async function main(){
 const expected=JSON.parse(fs.readFileSync(path.join(pack,'STRUCTURAL_ORACLE.json')));
 const report={status:'RUNNING',oracleCounts:expected.counts,views:[],errors:[],requests:[]};
 const current=serve(),old=serve(true),[a,b]=await Promise.all([listen(current),listen(old)]);
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 const ctx=await browser.newContext(),page=await ctx.newPage(),base=await ctx.newPage();
 for(const p of [page,base]){p.on('pageerror',e=>report.errors.push(String(e)));p.on('requestfailed',r=>report.requests.push(r.url()));}
 const rows=expected.rows.filter(r=>!process.env.QA_BOOKS||process.env.QA_BOOKS.split(',').includes(r.book));
 const save=()=>fs.writeFileSync(path.join(pack,process.env.STRUCTURAL_REPORT||'STRUCTURAL_QA.json'),JSON.stringify(report,null,2)+'\n');
 try{
  for(const r of rows){
   await Promise.all([open(page,a,'antiquities',r.query),open(base,b,'antiquities',r.query)]);
   const [actual,before]=await Promise.all([snapshot(page),snapshot(base)]);compareWitnesses(actual,before,r.query);
   const states={chapter:'chapter-level',subchapter:'subchapter-level',alignment:'section-level',bamberg:'bamberg-level',book:'book-level'};
   assert(actual.state.viewingLevel===states[r.scheme],'Structural view state differs '+r.query,actual);
   const english=actual.languages.english;
   assert(!english.allVisible.includes('Whiston English: exact Niese interval.'),'Spurious exact English notice');
   if(r.available)assert(!english.unavailable&&english.text===r.text,'Independent structural English differs '+r.query,{expected:r,actual:english});
   else assert(english.unavailable,'Missing genuine unavailable-witness notice '+r.query,english);
   assert(!english.hiddenNarrative.length,'Hidden containing narrative '+r.query);
   if(r.readerNote){const notice=await page.locator('#traditional-reader-notice').innerText();assert(notice.includes(r.readerNote),'Scholarly traditional notice lost '+r.query);}
   report.views.push({book:r.book,scheme:r.scheme,id:r.id,query:r.query,available:r.available,passed:true,EnglishSHA256:hash(english.text),GreekLatinUnchanged:true,notes:english.notes.length});
   if(report.views.length%100===0){save();console.log('Independent containing views',report.views.length);}
  }
  assert(report.views.length===rows.length&&!report.errors.length&&!report.requests.length,'Incomplete structural QA or browser errors',report);
  report.counts=Object.fromEntries(['book','chapter','subchapter','bamberg','alignment'].map(k=>[k,report.views.filter(v=>v.scheme===k).length]));report.status='PASS';
 }catch(e){report.status='FAIL';report.failure=String(e);throw e;}
 finally{save();await browser.close();current.close();old.close();}
 console.log('Independent structural QA',report.status,report.counts);
}
main().catch(e=>{console.error(e);process.exitCode=1;});
