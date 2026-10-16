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
const loci=[[13, 120, "ptolomeimilitiam", "ptolomei militiam"], [13, 154, "iniudaea", "in iudaea"], [13, 225, "tradensad", "tradens ad"], [13, 232, "magisimpetu", "magis impetu"], [13, 247, "Iudaeiuero", "Iudaei uero"], [13, 263, "prouinciamaestiment", "prouinciam aestiment"], [13, 271, "incursionibusfratris", "incursionibus fratris"], [13, 293, "illiposse", "illi posse"], [13, 327, "cedereocio", "cedere ocio"], [13, 341, "exercitumulti", "exercitu multi"], [13, 358, "redissematremque", "redisse matremque"], [13, 394, "antiochidicitur,", "antiochi dicitur,"], [13, 408, "hyrcanussocer", "hyrcanus socer"], [13, 414, "nomenauditum.", "nomen auditum."], [13, 430, "regninono,", "regni nono,"]];
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
const report={status:'RUNNING',locus_views:[],book_views:[],retained_views:[],neighbor_views:[],prior_76_views:[],direct_book_views:[],errors:[],renderer_source_unchanged:true,source_script:'review/Whiston_XVI_XX_Integration_2026-10-12/tools/browser_qa.cjs',script_adaptations:'Only test root, baseline, installed Playwright path and output location; normal rendering/selection logic unchanged.'};
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
  for(const book of [3, 9, 12, 13, 14, 15, 16, 17, 18])report.book_views.push(await compare(book,`book=${book}`,loci.filter(l=>l[0]===book)));
  for(const [book,n] of [[9,154],[14,413]])report.retained_views.push(await compare(book,`book=${book}&niese=${n}`,[]));
  for(const [book,n] of [[13, 119], [13, 121], [13, 153], [13, 155], [13, 224], [13, 226], [13, 231], [13, 233], [13, 246], [13, 248], [13, 262], [13, 264], [13, 270], [13, 272], [13, 292], [13, 294], [13, 326], [13, 328], [13, 340], [13, 342], [13, 357], [13, 359], [13, 393], [13, 395], [13, 407], [13, 409], [13, 413], [13, 415], [13, 429], [13, 431]])report.neighbor_views.push(await compare(book,`book=${book}&niese=${n}`,loci.filter(l=>l[0]===book&&l[1]===n)));
  for(const [book,n] of [[3, 65], [9, 22], [9, 122], [9, 143], [9, 146], [9, 152], [9, 179], [9, 192], [9, 208], [9, 221], [9, 236], [12, 29], [12, 45], [12, 80], [12, 98], [12, 411], [13, 66], [13, 131], [13, 163], [13, 169], [13, 374], [13, 433], [14, 396], [15, 165], [16, 1], [16, 28], [16, 94], [16, 143], [16, 250], [16, 283], [16, 329], [17, 1], [17, 13], [17, 32], [17, 38], [17, 58], [17, 68], [17, 74], [17, 81], [17, 99], [17, 104], [17, 125], [17, 140], [17, 146], [17, 158], [17, 164], [17, 171], [17, 177], [17, 183], [17, 190], [17, 195], [17, 210], [17, 217], [17, 229], [17, 230], [17, 233], [17, 239], [17, 244], [17, 251], [17, 269], [17, 285], [17, 293], [17, 299], [17, 305], [17, 318], [17, 323], [17, 333], [17, 354], [18, 35], [18, 41], [18, 139], [18, 150], [18, 220], [18, 271], [18, 301]])report.prior_76_views.push(await compare(book,`book=${book}&niese=${n}`,loci.filter(l=>l[0]===book&&l[1]===n)));
  process.env.QA_FORCE_PAGE_LOAD="1";report.direct_book_views.push(await compare(13,"book=13",loci));delete process.env.QA_FORCE_PAGE_LOAD;
  assert.equal(report.errors.length,0);report.status='PASS';
  await q.open(page,a,'antiquities','book=13&niese=247');await page.screenshot({path:path.join(runtime,'XIII_247_separator_display.png'),fullPage:true});
 }catch(e){report.status='FAIL';report.failure=String(e);throw e;}
 finally{fs.writeFileSync(path.join(out,'display_regression_results.json'),JSON.stringify(report,null,2)+'\n');await browser.close();candidate.close();baseline.close();}
 console.log(JSON.stringify({status:report.status,locus_views:report.locus_views.length,whole_book_views:report.book_views.length,retained_views:report.retained_views.length,neighbor_views:report.neighbor_views.length,prior_76_views:report.prior_76_views.length,direct_book_views:report.direct_book_views.length}));
}
main().catch(e=>{console.error(e);process.exitCode=1;});
