const {fs,path,chromium,packet,root,runtime,candidate,serve,listen,open,narrative,normalize,sha}=require('./qa-common16.cjs');
async function main(){
 const report={status:'RUNNING',scope:'Four approved B groups, neighbours, combined ranges, unavailable identities and inherited physical points',ranges:[],points:[],unavailable:[],errors:[]};
 const server=serve(candidate),origin=await listen(server),ctx=await chromium.launchPersistentContext(path.join(runtime,'browser-editorial-structural-extra'),{headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'}),page=await ctx.newPage();page.on('pageerror',e=>report.errors.push(String(e)));page.on('requestfailed',r=>report.errors.push(r.url()+':'+r.failure()?.errorText));
 try{
 for(const [book,roman,groups] of [[16,'XVI',[[293,294,295,296],[294,295],[350,351,352],[354,355,356,357],[351,355,356],[234,235,236],[367,368,369]]],[17,'XVII',[[23,24,25,26],[24,25],[74,75,76,77],[75,76],[105,106,107],[145,146,147],[298,299,300]]]]){
  const folder=path.join(root,`review/Antiquities_Niese_Book${roman}_2026-10-09`),proof=JSON.parse(fs.readFileSync(path.join(folder,'INDEPENDENT_IMPLEMENTATION_SOURCE_PROOF.json'))),reg=JSON.parse(fs.readFileSync(path.join(root,`assets/xml/antiquities/niese/book-${book}.json`)));
  await open(page,origin,`book=${book}&niese=1`);
  for(const numbers of groups){
   const expected=normalize(numbers.map(n=>proof.independently_resolved_registry_ranges.filter(r=>r.number===n).map(r=>r.text).join('')).join(''));
   const actual=await page.evaluate(({numbers,code})=>{const q=window.__qa,v=q.antiquitiesNieseFragmentView('Latin',q.getData().Latin,numbers),ids=[...v.querySelectorAll('[id]')].map(x=>x.id);return {text:eval('('+code+')')(v),fragments:v.querySelectorAll('tei-div[type="physical-fragment"]').length,ids,notes:[...v.querySelectorAll('.niese-correspondence-note')].map(x=>x.textContent)};},{numbers,code:narrative.toString()});
   const fragments=numbers.reduce((s,n)=>s+reg.sections[n-1].Latin.spans.length,0);
   if(actual.text!==expected||actual.fragments!==fragments||new Set(actual.ids).size!==actual.ids.length)throw Error('Combined logical fragment order/content/IDs '+book+'.'+numbers.join('-'));
   for(const n of numbers){const note=reg.sections[n-1].Latin.note;if(note&&!actual.notes.includes(note))throw Error('Reciprocal notice lost '+book+'.'+n);}
   report.ranges.push({book,numbers,physical_fragments:fragments,assembly:'Niese identity order; physical witness order within each identity',status:'PASS',sha256:sha(actual.text)});
  }
  const coordinates=JSON.parse(fs.readFileSync(path.join(folder,'PROTECTED_STRUCTURAL_COORDINATES.json'))).records;
  const actual=await page.evaluate(rows=>rows.map(row=>{
   const q=window.__qa,data=q.getData()[row.language],record=[...q.traditionalRows('chapter'),...q.traditionalRows('subchapter'),...q.bambergRows()].find(r=>r.id===row.boundary),locator=record[row.language],point=q.traditionalPoint(data,locator),p=point.node.closest('tei-p'),prefix=document.createRange(),suffix=document.createRange();prefix.setStart(p,0);suffix.setEnd(p,p.childNodes.length);
   if(point.kind==='paragraph'){prefix.setEnd(point.node,0);suffix.setStart(point.node,0);}else{prefix.setEndBefore(point.node);suffix.setStartBefore(point.node);}
   const clean=r=>{const c=document.createElement('div');c.append(r.cloneContents());c.querySelectorAll('tei-num,tei-milestone,tei-note,tei-app,tei-rdg').forEach(n=>n.remove());return c.textContent;};
   return {boundary:row.boundary,language:row.language,paragraph:p.id,offset:Array.from(clean(prefix)).length,right:clean(suffix)};
  }),coordinates);
  for(let i=0;i<coordinates.length;i++){const r=coordinates[i],a=actual[i];if(a.paragraph!==r.paragraph||a.offset!==r.frozen_offset||!normalize(a.right).startsWith(normalize(r.literal_current_text)))throw Error('Inherited physical point moved '+r.boundary+' '+r.language);report.points.push({...r,actual:a,status:'PASS_UNCHANGED_PHYSICAL_POSITION'});}
  for(const identity of reg.sections.filter(r=>r.Latin.available===false)){
   await open(page,origin,`book=${book}&niese=${identity.number}`);
   const a=await page.evaluate(code=>({Latin:eval('('+code+')')(document.querySelector('#latin')),Greek:eval('('+code+')')(document.querySelector('#greek')),English:eval('('+code+')')(document.querySelector('#english')),LatinParagraphs:document.querySelectorAll('#latin tei-p').length,message:document.querySelector('#latin .structural-unavailable')?.textContent,EnglishContext:!!document.querySelector('#english .niese-context-note')}),narrative.toString());
   if(a.Latin||a.LatinParagraphs||!a.Greek||!a.English||!a.EnglishContext||!a.message.includes(identity.Latin.note))throw Error('Unavailable identity independent access '+book+'.'+identity.number);
   report.unavailable.push({book,number:identity.number,status:'PASS_EMPTY_LATIN_AND_INDEPENDENT_GREEK_ENGLISH',notice:identity.Latin.note,sha256:sha(a)});
  }
 }
 if(report.unavailable.length!==24||report.errors.length)throw Error('Incomplete or failed editorial certification');report.status='PASS';
 }catch(e){report.status='FAIL';report.failure=String(e);throw e;}finally{fs.writeFileSync(path.join(packet,'EDITORIAL_STRUCTURAL_EXTRA_RESULTS.json'),JSON.stringify(report,null,2)+'\n');await ctx.close();await new Promise(r=>server.close(r));}
 console.log(JSON.stringify({status:report.status,ranges:report.ranges.length,points:report.points.length,unavailable:report.unavailable.length}));
}
main().catch(e=>{console.error(e);process.exitCode=1;});
