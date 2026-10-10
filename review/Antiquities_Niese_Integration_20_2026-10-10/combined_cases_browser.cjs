const {fs,path,P,norm,sha,narrative,session}=require('./browser_common.cjs');
// The reader has an individual Niese selector. Combined QA exercises its real
// exact-view function for every member and native DOM ranges over the same loaded
// source; it does not invent a multi-Niese URL or change production navigation.
async function main(){
 const s=await session('final'),groups=JSON.parse(fs.readFileSync(path.join(P,'COMBINED_EXPECTED_INTERVALS.json'))),expected=JSON.parse(fs.readFileSync(path.join(P,'FINAL_EXPECTED_INTERVALS.json')));
 const r={scope:'FOUR_ADJUDICATED_CASE_GROUPS_INDIVIDUAL_AND_COMBINED',sourceBuild:JSON.parse(fs.readFileSync(path.join(P,'CANDIDATE_BUILD.json'))).source_commit,status:'RUNNING',method:'Actual built reader selections and exact-view function; native DOM combined ranges over actual loaded source, compared with independently frozen raw-source projections. No multi-Niese URL exists or is claimed.',groups:[],errors:s.errors};
 try{
  for(const g of groups){
   await s.open('book=20&niese='+g.first);for(const l of ['greek','english'])await s.page.check('#'+l+'-pane-select');
   const individual=[];
   for(const n of g.members){await s.select(n);const a=await s.snapshot(),e=expected[n-1];
    if(a.duplicates.length||norm(a.languages.Greek)!==norm(e.Greek)||norm(a.languages.English)!==norm(e.English)||norm(a.languages.Latin)!==norm(e.Latin)||!a.EnglishContext)throw Error('Case member exact texts/IDs '+n);
    if(e.unavailable&&!a.unavailable?.includes(e.qualification))throw Error('Case availability '+n);
    if(!e.unavailable&&a.note!==e.qualification)throw Error('Case qualification '+n);
    individual.push({number:n,LatinAvailable:!e.unavailable,Greek:'PASS',EnglishContext:'PASS',Latin:'PASS',duplicates:0});
   }
   const combined=await s.page.evaluate(({g,code})=>{
    const text=eval('('+code+')'),q=window.__qa,d=q.getData();
    function range(language){
     const entries=q.antiquitiesNieseStartEntries(language,d[language]);
     const start=entries.find(e=>e.number===g.first),end=entries.find(e=>e.number===g.last+1);
     if(!start||!end)throw Error('Missing combined source boundary');
     const r=document.createRange();if(start.kind==='num')r.setStartBefore(start.node);else r.setStartAfter(start.node);r.setEndBefore(end.node);
     const w=document.createElement('tei-div'),p=start.node.closest('tei-p');
     if(r.commonAncestorContainer===p){const shell=p.cloneNode(false);shell.append(r.cloneContents());w.append(shell);}else w.append(r.cloneContents());
     const ids=[...w.querySelectorAll('[id]')].map(e=>e.id);
     return {text:text(w),duplicateIDs:ids.filter((id,i)=>ids.indexOf(id)!==i),sourceParagraphIDs:[...w.querySelectorAll('tei-p')].map(p=>p.id),annotationParent:[...w.querySelectorAll('tei-p')].find(p=>p.textContent.includes('[Niese sections 26'))?.id||null};
    }
    const fragments=Object.fromEntries(['Greek','Latin'].map(l=>[l,g.members.map(n=>text(q.antiquitiesNieseExactView(l,d[l],n))).join('')]));
    return {physical:{Greek:range('Greek'),Latin:range('Latin')},fragments};
   },{g,code:narrative.toString()});
   if(norm(combined.physical.Greek.text)!==norm(g.Greek)||norm(combined.fragments.Greek)!==norm(g.Greek))throw Error('Combined Greek '+g.first);
   if(norm(combined.physical.Latin.text)!==norm(g.Latin_physical_source)||norm(combined.fragments.Latin)!==norm(g.Latin_independent_fragments))throw Error('Combined Latin source/fragment accounting '+g.first);
   if(combined.physical.Greek.duplicateIDs.length||combined.physical.Latin.duplicateIDs.length)throw Error('Combined range duplicate IDs '+g.first);
   if(g.first===25){if(combined.physical.Latin.annotationParent!=='latin-book20-num34'||combined.fragments.Latin.includes('[Niese sections'))throw Error('Annotation source identity or narrative leakage');}
   if(g.first===57){if((combined.fragments.Latin.match(/habe inquit fiducia/g)||[]).length!==1||!norm(expected[58].Latin).startsWith('habe inquit fiducia')||expected[57].Latin.includes('habe inquit'))throw Error('Reassurance duplication or wrong cut');}
   if(g.first===237&&!norm(expected[238].Latin).startsWith('quo per insidias moriente'))throw Error('Relative-clause opening');
   if(g.first===239&&(!expected[239].Latin.includes('cum et pontificatum tenuisset et regnum')||!norm(expected[240].Latin).startsWith('Is namque primus')||expected[240].Latin.includes('cum et pontificatum')))throw Error('Kingship/diadem boundary');
   r.groups.push({range:[g.first,g.last],individual,unavailable:g.unavailable,fullGreekAndLatinSource:'PASS',LatinIndependentFragments:'PASS',annotationSeparatelyAccounted:g.first===25,annotationParent:combined.physical.Latin.annotationParent,combinedDuplicateIDs:0,physicalLatin_sha256:sha(norm(combined.physical.Latin.text)),fragmentLatin_sha256:sha(norm(combined.fragments.Latin)),Greek_sha256:sha(norm(combined.physical.Greek.text)),sourceParagraphIDs:combined.physical.Latin.sourceParagraphIDs});
   console.log('Adjudicated individual and combined group',g.first+'–'+g.last,'PASS');
  }
  if(s.errors.length)throw Error(JSON.stringify(s.errors));r.status='PASS';
 }catch(e){r.status='FAIL';r.failure=String(e);throw e;}finally{r.finished=new Date().toISOString();fs.writeFileSync(path.join(P,'ADJUDICATED_CASES_BROWSER.json'),JSON.stringify(r,null,2)+'\n');await s.close();}
 console.log(JSON.stringify({status:r.status,combinedGroups:r.groups.length,individualCaseChecks:r.groups.reduce((n,g)=>n+g.individual.length,0)}));
}
main().catch(e=>{console.error(e);process.exitCode=1;});
