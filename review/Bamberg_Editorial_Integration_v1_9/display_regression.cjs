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
const loci=[[9, 152, "illicinterfecit", "illic interfecit"], [9, 179, "Numquamcontra", "Numquam contra"], [9, 192, "triamilia", "tria milia"], [9, 236, "autemiustus", "autem iustus"], [12, 29, "adaegyptum", "ad aegyptum"], [12, 45, "principisacerdotum", "principi sacerdotum"], [12, 98, "stansregi", "stans regi"], [13, 163, "pro uidentia", "prouidentia"], [13, 169, "auaritiamvicinorum,", "auaritiam vicinorum,"], [13, 374, "ezcilicasnam", "ezcilicas nam"], [16, 28, "eissecundum", "eis secundum"], [16, 94, "molestumaut", "molestum aut"], [16, 143, "nomina uit.", "nominauit."], [16, 283, "herodesarabiam", "herodes arabiam"], [16, 329, "liga tum", "ligatum"], [17, 1, "haudsane", "haud sane"], [17, 13, "infantulosfiliorum", "infantulos filiorum"], [17, 32, "paterpromptius", "pater promptius"], [17, 38, "fratemproprium", "fratem proprium"], [17, 58, "amoreconiugis", "amore coniugis"], [17, 68, "nequitiaiussitque", "nequitia iussitque"], [17, 74, "uenenumin", "uenenum in"], [17, 81, "filleogerebat", "filleo gerebat"], [17, 99, "etmodum", "et modum"], [17, 104, "accusatio nes", "accusationes"], [17, 125, "solanequitia", "sola nequitia"], [17, 140, "scriptaerat", "scripta erat"], [17, 146, "uerocaesaris", "uero caesaris"], [17, 158, "gessimusquae", "gessimus quae"], [17, 164, "promouetaut", "promouet aut"], [17, 171, "aliquaremedia", "aliqua remedia"], [17, 177, "superceteros", "super ceteros"], [17, 183, "etquamquam", "et quamquam"], [17, 190, "disposuitetiam", "disposuit etiam"], [17, 195, "roburfirmitatemque", "robur firmitatemque"], [17, 210, "sualibidine", "sua libidine"], [17, 217, "impetumfrangeret", "impetum frangeret"], [17, 229, "recenscenscongregabat", "recenscens congregabat"], [17, 233, "cummorereturuiuendo", "cummoreretur uiuendo"], [17, 239, "porrorex", "porro rex"], [17, 244, "patremsana", "patrem sana"], [17, 251, "tumultuacionibusqueturbata,", "tumultuacionibusque turbata,"], [17, 269, "lucricupidine", "lucri cupidine"], [17, 285, "ciuiumquesuorum", "ciuiumque suorum"], [17, 293, "propterfestiuitatem", "propter festiuitatem"], [17, 299, "aliorumnegotiorum", "aliorum negotiorum"], [17, 305, "etiameis", "etiam eis"], [17, 318, "Alteramuero", "Alteram uero"], [17, 323, "perfilios", "per filios"], [17, 333, "quiprudenter", "qui prudenter"], [17, 354, "quaecirca", "quae circa"], [18, 35, "cala fas", "calafas"], [18, 41, "argumen tis", "argumentis"], [18, 139, "capra docorum", "capradocorum"], [18, 220, "mag nitudinem", "magnitudinem"], [18, 271, "manda ta", "mandata"], [18, 301, "con uenit", "conuenit"]];
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
const report={status:'RUNNING',locus_views:[],book_views:[],retained_views:[],held_views:[],prior_approved_views:[],direct_book_views:[],errors:[],renderer_source_unchanged:true,source_script:'review/Whiston_XVI_XX_Integration_2026-10-12/tools/browser_qa.cjs',script_adaptations:'Only test root, baseline, installed Playwright path and output location; normal rendering/selection logic unchanged.'};
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
  for(const [book,n] of [[13, 120], [13, 154], [13, 225], [13, 232], [13, 247], [13, 263], [13, 271], [13, 293], [13, 327], [13, 341], [13, 358], [13, 394], [13, 408], [13, 414], [13, 430]])report.held_views.push(await compare(book,`book=${book}&niese=${n}`,loci.filter(l=>l[0]===book&&l[1]===n)));
  for(const [book,n] of [[3, 65], [9, 22], [9, 122], [9, 143], [9, 146], [9, 208], [9, 221], [12, 80], [12, 411], [13, 66], [13, 131], [13, 433], [14, 396], [15, 165], [16, 1], [16, 250], [17, 230], [18, 150]])report.prior_approved_views.push(await compare(book,`book=${book}&niese=${n}`,loci.filter(l=>l[0]===book&&l[1]===n)));
  process.env.QA_FORCE_PAGE_LOAD='1';
  for(const book of [...new Set(loci.map(l=>l[0]))])report.direct_book_views.push(await compare(book,`book=${book}`,loci.filter(l=>l[0]===book)));
  delete process.env.QA_FORCE_PAGE_LOAD;
  assert.equal(report.errors.length,0);report.status='PASS';
  await q.open(page,a,'antiquities','book=17&niese=1');await page.screenshot({path:path.join(runtime,'XVII_1_mechanical_display.png'),fullPage:true});
 }catch(e){report.status='FAIL';report.failure=String(e);throw e;}
 finally{fs.writeFileSync(path.join(out,'display_regression_results.json'),JSON.stringify(report,null,2)+'\n');await browser.close();candidate.close();baseline.close();}
 console.log(JSON.stringify({status:report.status,locus_views:report.locus_views.length,whole_book_views:report.book_views.length,retained_views:report.retained_views.length,held_views:report.held_views.length,prior_approved_views:report.prior_approved_views.length,direct_book_views:report.direct_book_views.length}));
}
main().catch(e=>{console.error(e);process.exitCode=1;});
