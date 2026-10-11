const q=require('./browser_qa.cjs'),fs=require('fs'),path=require('path');
const {pack,oracle,chromium,serve,listen,open,snapshot,assert,compareWitnesses,hash,norm,checkInterval}=q;
const containing=JSON.parse(fs.readFileSync(path.join(pack,'CONTAINING_ORACLE.json')));
const crossOnly=process.argv.includes('--cross-work-only');
const report=crossOnly?JSON.parse(fs.readFileSync(path.join(pack,'REGRESSION_QA.json'))):{status:'RUNNING',book:[],traditional:[],alignment:[],crossWork:[],navigation:[],unsegmented:[],errors:[],requests:[]};
if(crossOnly){assert(report.status==='PASS','Cross-work continuation requires complete structural pass');report.status='RUNNING';report.crossWork=[];}
const save=()=>fs.writeFileSync(path.join(pack,'REGRESSION_QA.json'),JSON.stringify(report,null,2)+'\n');
async function main(){
 const candidate=serve(),baseline=serve(true),[a,b]=await Promise.all([listen(candidate),listen(baseline)]);
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 const ctx=await browser.newContext({viewport:{width:1440,height:1000}}),page=await ctx.newPage(),base=await ctx.newPage();
 for(const p of [page,base]){p.on('pageerror',e=>report.errors.push(String(e)));p.on('requestfailed',r=>report.requests.push({url:r.url(),error:r.failure()?.errorText}));}
 const both=async(route,query)=>{await Promise.all([open(page,a,route,query),open(base,b,route,query)]);return Promise.all([snapshot(page),snapshot(base)]);};
 const interval=(start,end)=>norm(oracle.filter(e=>e.book==='9'&&e.number>=start&&e.number<end).sort((x,y)=>x.number-y.number).map(e=>e.rawText).join(''));
 save();console.log('Regression browsers ready');
 try{
  if(!crossOnly){
  for(const book of Object.keys(containing.whole)){
   if(process.argv.includes('--from-ix')&&book!=='preface'&&Number(book)<9)continue;
   const [actual,prior]=await both('antiquities',`book=${book}`);compareWitnesses(actual,prior,`${book} book`);
   assert(actual.languages.english.text===containing.whole[book],`Book ${book} complete certified content differs`,{expected:containing.whole[book],actual:actual.languages.english});
   assert(actual.languages.english.hiddenNarrative.length===0,'Book narrative hidden',actual.languages.english);
   report.book.push({book,passed:true,certifiedWholeTextSHA256:hash(actual.languages.english.text),GreekLatinPresentationUnchanged:true,notes:actual.languages.english.notes.length});
   const menu=await page.locator('#section-selector').evaluate(e=>[...e.options].filter(e=>e.value).map(e=>e.value));
   for(const unit of menu){
    const query=`book=${book}&num=${unit}`,[actual,prior]=await both('antiquities',query);compareWitnesses(actual,prior,query);
    assert(actual.state.viewingLevel==='section-level'&&String(actual.state.sectionNum)===unit,'Alignment URL resolved to wrong view',actual.state);
    const restored=book==='9'&&unit==='51';
    assert(actual.languages.english.text===(restored?interval(51,110):prior.languages.english.text),`Alignment English differs ${query}`,{actual:actual.languages.english,prior:prior.languages.english});
    assert(actual.languages.english.hiddenNarrative.length===0,`Hidden alignment narrative ${query}`,actual.languages.english);
    report.alignment.push({book,unit,passed:true,restoredEnglish:restored,EnglishSHA256:hash(actual.languages.english.text),GreekLatinPresentationUnchanged:true});
    if(report.alignment.length%100===0){save();console.log('Alignment views',report.alignment.length);}
   }
   const rows=containing.rows.filter(r=>(book==='preface'?r.context==='Proem':r.context!=='Proem'&&Number(r.book)===Number(book)));
   for(const row of rows){
    const query=`book=${book}`+(row.chapter?`&chapter=${row.chapter}`:'')+(row.scheme==='subchapter'?`&subchapter=${row.subchapter}`:'');
    const [actual,prior]=await both('antiquities',query);compareWitnesses(actual,prior,query);
    assert(actual.state.viewingLevel===(row.scheme==='chapter'?'chapter-level':'subchapter-level'),'Traditional URL resolved to wrong view',actual.state);
    const end=containing.rows.find(r=>r.id===row.end),startNum=Number(row['canonical-niese']),endNum=end?Number(end['canonical-niese']):292;
    const restored=book==='9'&&startNum<110&&endNum>51;
    assert(actual.languages.english.text===(restored?interval(startNum,endNum):prior.languages.english.text),`Traditional English differs ${query}`,{row,end,actual:actual.languages.english,prior:prior.languages.english});
    assert(actual.languages.english.hiddenNarrative.length===0,`Hidden traditional narrative ${query}`,actual.languages.english);
    report.traditional.push({book,query,id:row.id,scheme:row.scheme,passed:true,restoredEnglish:restored,EnglishSHA256:hash(actual.languages.english.text),GreekLatinPresentationUnchanged:true});
    if(report.traditional.length%100===0){save();console.log('Traditional views',report.traditional.length);}
   }
   save();console.log('Containing book complete',book);
  }
  // Direct routes and actual Previous/Next clicks at critical boundaries.
  const direct=[['preface',1],['preface',26],['1',27],['1',346],['7',1],...[49,50,51,52,108,109,110,111].map(n=>['9',n]),...[1,311,312,325,326,342,343,347].map(n=>['11',n])];
  process.env.QA_FORCE_PAGE_LOAD='1';
  for(const [book,number] of direct){
   await open(page,a,'antiquities',`book=${book}&niese=${number}`);const actual=await snapshot(page),expected=oracle.find(e=>e.book===book&&e.number===number);
   checkInterval(actual,expected);report.navigation.push({kind:'DIRECT_URL',book,number,passed:true});
   const menu=await page.locator('#niese-selector').evaluate(e=>[...e.options].filter(e=>e.value).map(e=>Number(e.value))),index=menu.indexOf(number);
   for(const [control,target] of [['#niese-next',menu[index+1]],['#niese-previous',menu[index-1]]]){
    await open(page,a,'antiquities',`book=${book}&niese=${number}`);
    if(target===undefined){assert(await page.locator(control).isDisabled(),'Terminal navigation button enabled');continue;}
    const count=await page.evaluate(()=>window.__qaCount);await page.locator(control).click();
    await page.waitForFunction(({count,target})=>window.__qaCount>count&&Number(window.__qaRendered.nieseNum)===target,{count,target},{polling:10});
    checkInterval(await snapshot(page),oracle.find(e=>e.book===book&&e.number===target));
    report.navigation.push({kind:control,book,from:number,to:target,passed:true});
   }
  }
  await open(page,a,'antiquities','book=preface&niese=26');await page.locator('.niese-related-passage a').click();
  await page.waitForFunction(()=>window.__qaReady&&window.__qaRendered.bookNum==='01'&&Number(window.__qaRendered.nieseNum)===27);
  checkInterval(await snapshot(page),oracle.find(e=>e.book==='1'&&e.number===27));report.navigation.push({kind:'PROEM_TRANSITION_LINK',passed:true});
  delete process.env.QA_FORCE_PAGE_LOAD;
  for(let book=12;book<=20;book++){
   for(const query of [`book=${book}&niese=1`,`book=${book}`]){
    const [actual,prior]=await both('antiquities',query);compareWitnesses(actual,prior,query);
    assert(actual.languages.english.html===prior.languages.english.html,'Unsegmented English changed '+query);
    if(query.includes('niese'))assert(actual.languages.english.context&&!actual.languages.english.exact,'Unsegmented context distinction missing');
    report.unsegmented.push({query,passed:true,EnglishSHA256:hash(actual.languages.english.html)});
   }
  }
  }
  // Each Bellum book and English source: book, chapter, and first/middle/final exact citations.
  for(let book=1;book<=7;book++)for(const source of ['whiston','lodge1602']){
   await open(page,a,'bellum-judaicum',`book=${book}&english=${source}`);
   const nums=await page.locator('#niese-selector').evaluate(e=>[...e.options].filter(e=>e.value).map(e=>e.value));
   const queries=[`book=${book}&english=${source}`,`book=${book}&english=${source}&chapter=1`,...([nums[0],nums[Math.floor(nums.length/2)],nums.at(-1)].filter(Boolean).map(n=>`book=${book}&english=${source}&niese=${n}`))];
   for(const query of queries){const [actual,prior]=await both('bellum-judaicum',query);for(const lang of ['english','latin','greek'])assert(actual.languages[lang].html===prior.languages[lang].html,'Bellum changed '+query+' '+lang);assert(actual.languages.english.text.length>0,'Empty Bellum English');report.crossWork.push({work:'Bellum',query,passed:true,witnessHashes:Object.fromEntries(Object.entries(actual.languages).map(([k,v])=>[k,hash(v.html)]))});}
  }
  for(const [route,books] of [['contra-apionem',[1,2]],['deh',[1,2,3,4,5]]])for(const book of books){
   const work=route==='deh'?'deh':'contra-apionem',prefix=route==='deh'?`latin-deh${book}-num`:`latin-contraapionem${book}-num`;
   const xml=fs.readFileSync(path.join(q.root,`assets/xml/${work}/Latin/book-${String(book).padStart(2,'0')}.xml`),'utf8');
   let units=[...xml.matchAll(new RegExp('xml:id="'+prefix+'(\\d+)"','g'))].map(m=>m[1]);
   if(route==='contra-apionem')units=book===1?['1','160','320']:['1','148','296'];
   assert(units.length>0,'Cross-work canonical section inventory empty '+route+book);
   const selected=route==='contra-apionem'?units:[units[0],units[Math.floor(units.length/2)],units.at(-1)];
   const queries=[`book=${book}`,`book=${book}&chapter=1`,...selected.map(n=>`book=${book}&${route==='contra-apionem'?'niese':'num'}=${n}`)];
   for(const query of queries){const [actual,prior]=await both(route,query);for(const lang of Object.keys(actual.languages))assert(actual.languages[lang].html===prior.languages[lang].html,route+' changed '+query+' '+lang);assert(Object.values(actual.languages).some(v=>v.text.length>0),'Empty cross-work displayed content');if(/&(num|niese)=/.test(query))assert(actual.state.viewingLevel==='section-level'&&actual.languages.latin.text.length>0,'Direct cross-work section unavailable',actual);report.crossWork.push({work:route,query,passed:true,state:actual.state,witnessHashes:Object.fromEntries(Object.entries(actual.languages).map(([k,v])=>[k,hash(v.html)]))});}
  }
  for(const [query,name] of [['book=7&niese=1','VII-1'],['book=9&niese=51','IX-51-notes'],['book=9&chapter=5','IX-chapter5'],['book=11&niese=342','XI-342']]){await open(page,a,'antiquities',query);await page.screenshot({path:path.join(pack,'evidence',name+'.png'),fullPage:true});}
  assert(report.errors.length===0,'Browser script errors',report.errors);report.status='PASS';save();
 }catch(e){report.status='FAIL';report.failure=String(e);throw e;}
 finally{save();await browser.close();candidate.close();baseline.close();}
 console.log('Regression QA',report.status,JSON.stringify(Object.fromEntries(['book','traditional','alignment','crossWork','navigation','unsegmented'].map(k=>[k,report[k].length]))));
}
main().catch(e=>{console.error(e);process.exitCode=1;});
