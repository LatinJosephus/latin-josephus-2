/* Reuse the repository's real reader test harness; no renderer source changes. */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const wt=path.resolve(__dirname,'../..'),out=process.env.READER_TEST_OUTPUT;
assert(out,'Set READER_TEST_OUTPUT to a disposable output directory');fs.mkdirSync(out,{recursive:true});
const runtime=path.join(out,'runtime'),pack=path.join(wt,'review/Whiston_XVI_XX_Integration_2026-10-12');fs.mkdirSync(runtime,{recursive:true});
const site=process.env.BAMBERG_BUILD_SITE;
assert(site&&fs.existsSync(path.join(site,'antiquities/index.html')),'A successful built site is required');
const source=path.join(pack,'tools/browser_qa.cjs');
let harness=fs.readFileSync(source,'utf8');
harness=harness.replace("const root=path.resolve(__dirname,'../../..'),pack=path.resolve(__dirname,'..');",`const root=${JSON.stringify(wt)},pack=${JSON.stringify(pack)};`);
assert(process.env.READER_BASELINE_ROOT,'Set READER_BASELINE_ROOT to the unchanged development baseline checkout');
harness=harness.replace("const canonical=path.resolve(root,'../baseline');",`const canonical=${JSON.stringify(process.env.READER_BASELINE_ROOT)};`);
harness=harness.replace('function compareWitnesses(a,b,label){','function compareWitnesses(a,b,label){');
const harnessFile=path.join(runtime,'reader_harness.cjs');fs.writeFileSync(harnessFile,harness);
assert(process.env.PLAYWRIGHT_MODULE,'Set PLAYWRIGHT_MODULE to the installed Playwright package');
process.env.WHISTON_SITE=site;
const q=require(harnessFile);
const loci=[
 [3,65,'contigistisent','contigissent'],
 [9,22,'quiquaginta','quinquaginta'],[9,122,'Bonus in quid seruus','Bonus inquid seruus'],[9,143,'suasit ut consisterent','suasit ut ei consisterent'],
 [9,146,'sarcerdotes','sacerdotes'],[9,208,'amissuraciuitas','amissura ciuitas'],[9,221,'ob pressiones','obpressiones'],
 [12,80,'quattuordignotorum','quattuor digitorum'],[12,411,'euasis','euasit'],
 [13,66,'multitudinemuariamque','multitudinem uariamque'],[13,131,'ei restituere dicebat','ei restituere se dicebat'],[13,433,'mortem compleuit mortem compleuit','mortem compleuit'],
 [14,396,'ma sadam','masadam'],[15,165,'guber nationem','gubernationem'],
 [16,1,'ad confusion nem','ad confusionem'],[16,250,'dumterram','dum terram'],
 [17,230,'archelao infestus','archelao satis infestus'],[18,150,'uirum uirum consularem','uirum consularem'],
];
const norm=x=>x.replace(/\s+/g,' ').trim();
function expected(before,changes){
 let text=before;
 for(const [book,n,old,newText] of changes){
  const occurrences=text.split(old).length-1;
  assert.equal(occurrences,1,`Expected exactly one visible source context at ${book}.${n}: ${old}`);
  text=text.replace(old,newText);
 }
 return norm(text);
}
const report={status:'RUNNING',locus_views:[],book_views:[],retained_views:[],errors:[],renderer_source_unchanged:true,source_script:'review/Whiston_XVI_XX_Integration_2026-10-12/tools/browser_qa.cjs',script_adaptations:'Only test root, baseline, installed Playwright path and output location; normal rendering/selection logic unchanged.'};
async function main(){
 const candidate=q.serve(),baseline=q.serve(true),[a,b]=await Promise.all([q.listen(candidate),q.listen(baseline)]);
 const browser=await q.chromium.launch({headless:true,executablePath:process.env.CHROME_EXECUTABLE});
 const ctx=await browser.newContext({viewport:{width:1440,height:1000}}),page=await ctx.newPage(),prior=await ctx.newPage();
 for(const p of [page,prior])p.on('pageerror',e=>report.errors.push(String(e)));
 async function compare(book,query,changes){
  await Promise.all([q.open(page,a,'antiquities',query),q.open(prior,b,'antiquities',query)]);
  const [after,before]=await Promise.all([q.snapshot(page),q.snapshot(prior)]);
  for(const lang of ['english','greek'])assert.equal(after.languages[lang].html,before.languages[lang].html,`${query}: ${lang} changed`);
  assert.equal(after.languages.latin.text,expected(before.languages.latin.text,changes),`${query}: displayed Latin differs from exactly approved replacements`);
  assert.deepEqual(after.languages.latin.duplicateIds,before.languages.latin.duplicateIds,`${query}: identifier duplication changed`);
  return {book,query,approved_loci:changes.length,Greek_and_English_unchanged:true,Latin_exact_authorized_projection:true};
 }
 try{
  for(const locus of loci){const [book,n]=locus;report.locus_views.push(await compare(book,`book=${book}&niese=${n}`,[locus]));console.log('Verified displayed locus',book,n);}
  for(const book of [...new Set(loci.map(l=>l[0]))])report.book_views.push(await compare(book,`book=${book}`,loci.filter(l=>l[0]===book)));
  for(const [book,n] of [[9,154],[14,413]])report.retained_views.push(await compare(book,`book=${book}&niese=${n}`,[]));
  assert.equal(report.errors.length,0);report.status='PASS';
  await q.open(page,a,'antiquities','book=12&niese=80');await page.screenshot({path:path.join(runtime,'XII_80_display.png'),fullPage:true});
 }catch(e){report.status='FAIL';report.failure=String(e);throw e;}
 finally{fs.writeFileSync(path.join(out,'display_regression_results.json'),JSON.stringify(report,null,2)+'\n');await browser.close();candidate.close();baseline.close();}
 console.log(JSON.stringify({status:report.status,locus_views:report.locus_views.length,whole_book_views:report.book_views.length,retained_views:report.retained_views.length}));
}
main().catch(e=>{console.error(e);process.exitCode=1;});
