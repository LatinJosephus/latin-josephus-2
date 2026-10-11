const q=require('./browser_qa.cjs'),fs=require('fs'),path=require('path');
const {pack,chromium,serve,listen,open,snapshot,assert,hash}=q;
async function main(){
 const report={status:'RUNNING',crossWork:[],errors:[],requests:[]};
 const current=serve(),old=serve(true),[a,b]=await Promise.all([listen(current),listen(old)]);
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 const context=await browser.newContext(),page=await context.newPage(),base=await context.newPage();
 for(const p of [page,base]){p.on('pageerror',e=>report.errors.push(String(e)));p.on('requestfailed',r=>report.requests.push(r.url()));}
 const both=async(route,query)=>{await Promise.all([open(page,a,route,query),open(base,b,route,query)]);return Promise.all([snapshot(page),snapshot(base)]);};
 try{
  for(let book=1;book<=7;book++)for(const source of ['whiston','lodge1602']){
   await open(page,a,'bellum-judaicum',`book=${book}&english=${source}`);
   const nums=await page.locator('#niese-selector').evaluate(e=>[...e.options].filter(e=>e.value).map(e=>e.value));
   const queries=[`book=${book}&english=${source}`,`book=${book}&english=${source}&chapter=1`,...[nums[0],nums[Math.floor(nums.length/2)],nums.at(-1)].map(n=>`book=${book}&english=${source}&niese=${n}`)];
   for(const query of queries){const [actual,prior]=await both('bellum-judaicum',query);for(const lang of ['english','latin','greek'])assert(actual.languages[lang].html===prior.languages[lang].html,'Bellum changed '+query+' '+lang);assert(actual.languages.english.text.length>0,'Empty Bellum English');report.crossWork.push({work:'Bellum',query,passed:true,witnessHashes:Object.fromEntries(Object.entries(actual.languages).map(([k,v])=>[k,hash(v.html)]))});}
  }
  for(const [route,books] of [['contra-apionem',[1,2]],['deh',[1,2,3,4,5]]])for(const book of books){
   const prefix=route==='deh'?`latin-deh${book}-num`:`latin-contraapionem${book}-num`;
   const xml=fs.readFileSync(path.join(q.root,`assets/xml/${route}/Latin/book-${String(book).padStart(2,'0')}.xml`),'utf8');
   let units=[...xml.matchAll(new RegExp('xml:id="'+prefix+'(\\d+)"','g'))].map(m=>m[1]);
   if(route==='contra-apionem')units=book===1?['1','160','320']:['1','148','296'];
   assert(units.length>0,'Cross-work section inventory empty');
   const selected=route==='contra-apionem'?units:[units[0],units[Math.floor(units.length/2)],units.at(-1)];
   for(const query of [`book=${book}`,`book=${book}&chapter=1`,...selected.map(n=>`book=${book}&${route==='contra-apionem'?'niese':'num'}=${n}`)]){
    const [actual,prior]=await both(route,query);for(const lang of Object.keys(actual.languages))assert(actual.languages[lang].html===prior.languages[lang].html,route+' changed '+query+' '+lang);
    assert(Object.values(actual.languages).some(v=>v.text.length>0),'Empty cross-work content');
    if(/&(num|niese)=/.test(query))assert(actual.state.viewingLevel==='section-level'&&actual.languages.latin.text.length>0,'Direct cross-work section unavailable');
    report.crossWork.push({work:route,query,passed:true,witnessHashes:Object.fromEntries(Object.entries(actual.languages).map(([k,v])=>[k,hash(v.html)]))});
   }
  }
  assert(report.crossWork.length===105&&!report.errors.length&&!report.requests.length,'Incomplete cross-work regression');report.status='PASS';
 }catch(e){report.status='FAIL';report.failure=String(e);throw e;}
 finally{fs.writeFileSync(path.join(pack,'CROSS_WORK_QA.json'),JSON.stringify(report,null,2)+'\n');await browser.close();current.close();old.close();}
 console.log('Standard-built candidate cross-work actual displayed content PASS, 105 views');
}
main().catch(e=>{console.error(e);process.exitCode=1;});
