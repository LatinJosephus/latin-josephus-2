/* Real reader comparisons, with unchanged repository harness and rendering logic. */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve(process.env.READER_TEST_ROOT),packet=path.resolve(__dirname,'..'),out=path.resolve(process.env.READER_TEST_OUTPUT),baseline=process.env.READER_BASELINE_ROOT,site=process.env.BAMBERG_BUILD_SITE;
assert(baseline&&site);fs.mkdirSync(out,{recursive:true});const runtime=path.join(out,'runtime');fs.mkdirSync(runtime,{recursive:true});
const pack=path.join(root,'review/Whiston_XVI_XX_Integration_2026-10-12');let h=fs.readFileSync(path.join(pack,'tools/browser_qa.cjs'),'utf8');
const originalRoot="const root=path.resolve(__dirname,'../../..'),pack=path.resolve(__dirname,'..');",originalBase="const canonical=path.resolve(root,'../baseline');";assert(h.includes(originalRoot)&&h.includes(originalBase));h=h.replace(originalRoot,`const root=${JSON.stringify(root)},pack=${JSON.stringify(pack)};`).replace(originalBase,`const canonical=${JSON.stringify(baseline)};`);fs.writeFileSync(path.join(runtime,'harness.cjs'),h);process.env.WHISTON_SITE=site;const q=require(path.join(runtime,'harness.cjs'));
const loci=[
 [1,91,'et ad ad egrediendum','et ad egrediendum'],
 [2,179,'iael, hoc ergo ergo genus','iael, hoc ergo genus'],
 [2,38,'unius filii pater esset aliorum consolatione','unius filii pater esset aliorumque consolatione'],
 [5,146,'a suo feruore pro pro peregrina recederent','a suo feruore pro peregrina recederent'],
 [6,219,'quae hoc necessitatis causa, et non uoluntatis efficerit','quae hoc necessitatis causa, non uoluntatis causa et non uoluntatis efficerit'],
 [7,169,'at ille non non adquieuit','at ille non adquieuit'],
 [8,362,'sed eius filiis temporibus temporibus inferendum','sed eius filiis temporibus inferendum'],
 [11,256,'omnen spemaudiuit mente','omnen spem audiuit mente'],
 [11,16,'uenditioni oleum dragmas dragmas cc','uenditioni oleum dragmas cc'],
 [11,312,'et hostiliter in eos amimatus tamque','et hostiliter in eos animatus tamque'],
 [19,127,'dudum scirent sibi met utilem','dudum scirent sibimet utilem'],
 [19,169,'Ego siquidem prioris libertatis','Ego siquidem iam prioris libertatis'],
 [20,126,'prosua uel sique fuisset laesione','prosua uel siqua fuisset laesione']
];
const report={status:'RUNNING',locus_views:[],neighbor_views:[],book_views:[],prior_91_views:[],retained_views:[],direct_views:[],errors:[],Book_XI_BJ105b_tested_with_logical_312_view:true,renderer_logic_changed:false};
const norm=s=>s.replace(/\s+/g,' ').trim();
function expected(text,changes){for(const [,n,old,next] of changes){assert.equal(text.split(old).length-1,1,`Unique approved visible context ${n}: ${old}`);text=text.replace(old,next);}return norm(text);}
async function main(){const aServer=q.serve(),bServer=q.serve(true),[a,b]=await Promise.all([q.listen(aServer),q.listen(bServer)]);const browser=await q.chromium.launch({headless:true,executablePath:process.env.CHROME_EXECUTABLE});const ctx=await browser.newContext({viewport:{width:1440,height:1000}}),pg=await ctx.newPage(),prior=await ctx.newPage();for(const p of [pg,prior])p.on('pageerror',e=>report.errors.push(String(e)));
 async function compare(book,query,changes){await Promise.all([q.open(pg,a,'antiquities',query),q.open(prior,b,'antiquities',query)]);const [after,before]=await Promise.all([q.snapshot(pg),q.snapshot(prior)]);for(const lang of ['greek','english'])assert.equal(after.languages[lang].html,before.languages[lang].html,`${query} ${lang}`);assert.equal(after.languages.latin.text,expected(before.languages.latin.text,changes),`${query} exact approved Latin`);assert.deepEqual(after.languages.latin.duplicateIds,before.languages.latin.duplicateIds);return {book,query,authorized_changes:changes.length,Latin_exact_approved_projection:true,Greek_English_unchanged:true};}
 try{
  for(const l of loci){report.locus_views.push(await compare(l[0],`book=${l[0]}&niese=${l[1]}`,[l]));console.log('Displayed approved locus',l[0],l[1]);}
  for(const book of [...new Set(loci.map(l=>l[0]))])report.book_views.push(await compare(book,`book=${book}`,loci.filter(l=>l[0]===book)));
  const neighbors=new Set(loci.flatMap(l=>[-1,1].map(d=>`${l[0]},${l[1]+d}`)));for(const v of neighbors){const [book,n]=v.split(',').map(Number);report.neighbor_views.push(await compare(book,`book=${book}&niese=${n}`,loci.filter(l=>l[0]===book&&l[1]===n)));}
  const old=JSON.parse(fs.readFileSync(path.join(packet,'inputs/baselines/Bamberg_Editorial_Promotion_v2_1__cumulative_correction_inventory.json'))).actions;const views=[...new Set(old.map(p=>`${p.book},${p.niese}`))];for(const v of views){const [book,n]=v.split(',').map(Number);report.prior_91_views.push(await compare(book,`book=${book}&niese=${n}`,loci.filter(l=>l[0]===book&&l[1]===n)));}
  for(const [book,n] of [[9,154],[14,413]])report.retained_views.push(await compare(book,`book=${book}&niese=${n}`,[]));
  process.env.QA_FORCE_PAGE_LOAD='1';for(const book of [5,6,11])report.direct_views.push(await compare(book,`book=${book}`,loci.filter(l=>l[0]===book)));delete process.env.QA_FORCE_PAGE_LOAD;
  assert.equal(report.errors.length,0);report.status='PASS';await q.open(pg,a,'antiquities','book=5&niese=146');await pg.screenshot({path:path.join(out,'V146_pro_peregrina.png'),fullPage:true});
 }catch(e){report.status='FAIL';report.failure=String(e);throw e;}finally{fs.writeFileSync(path.join(out,'display_regression_results.json'),JSON.stringify(report,null,2)+'\n');await browser.close();aServer.close();bServer.close();}
 console.log(JSON.stringify({status:report.status,loci:report.locus_views.length,neighbors:report.neighbor_views.length,whole_books:report.book_views.length,prior_correction_views:report.prior_91_views.length,retained:report.retained_views.length,direct:report.direct_views.length}));
}
main().catch(e=>{console.error(e);process.exitCode=1;});
