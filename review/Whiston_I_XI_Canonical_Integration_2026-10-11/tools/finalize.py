from pathlib import Path
import collections,datetime,hashlib,json,re,subprocess
ROOT=Path(__file__).resolve().parents[3];PACK=ROOT/'review/Whiston_I_XI_Canonical_Integration_2026-10-11'
OLD=ROOT/'review/Whiston_I_XI_Renderer_2026-10-11'
PIN='663b8ce318f0aa247d304d8eeda5b8e76e7489c6';PROTO='0c1347a5a947ae5702cf60e4162d09d7510450e5'
sha=lambda b:hashlib.sha256(b).hexdigest()
load=lambda name:json.loads((PACK/name).read_bytes())
save=lambda name,obj:(PACK/name).write_bytes((json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode())
git=lambda *a:subprocess.check_output(['git',*a],cwd=ROOT).decode().strip()
for name in ['EVIDENCE_RECONCILIATION.json','CANDIDATE_XML_INTERVAL_QA.json','BUILD_QA.json','CORPUS_GUARD_QA.json','CANDIDATE_SMOKE_QA.json','CROSS_WORK_QA.json','DEH_LAUNCHER_QA.json',
 'legacy-bellum-corpus/corpus-qa.json','legacy-bellum-static/lodge-bellum-static.json','legacy-bellum-focused/focused-qa.json','legacy-lodge-browser/existing-lodge-browser-qa.json']:
 assert load(name)['status']=='PASS',name
bellum=load('legacy-bellum-corpus/corpus-qa.json');lodge=load('legacy-lodge-browser/existing-lodge-browser-qa.json')
assert lodge['frozen_digest_match'] and len(lodge['contentsChecks'])==7
assert bellum['greek']==bellum['whiston']==bellum['lodge']=={'chapters':111,'subchapters':704,'niese':4001}
assert bellum['xml_count']==143 and len(bellum['results'])==14
smoke=load('CANDIDATE_SMOKE_QA.json');assert len(smoke['exact'])==119 and len(smoke['fallback'])==9
assert len(load('CROSS_WORK_QA.json')['crossWork'])==105
inventory=load('SOURCE_INVENTORY.json')
implementation=git('rev-parse','HEAD');assert implementation=='6edd4229088b2590443eb7e5aaa8f91dc50c49e8'
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
guards=[
 {'id':'G01','files':['bin/deh-parallels-qa.mjs'],'purpose':'Bind DEH excerpt QA to unchanged scholarly authorities.','existing_expectation':'Every one of the historical 100 XML hashes still describes the entire current corpus.','still_valid':'Frozen concordance SHA and all 31 DEH/Bellum excerpt input hashes remain valid; Antiquities-wide historical identity is obsolete.','legitimate_change':'Twelve certified English files and the reviewed IX English structural registry replace earlier Antiquities inputs; earlier canonical source/paratext releases also supersede historical hashes.','minimal_update':'Hash-bind a complete 143-path reviewed manifest; parse every XML; retain every frozen excerpt authority hash and serve only its exact reviewed bytes.','outcome':'PASS: native launcher, 2,115 component checks and 8,193 displayed section occurrences.'},
 {'id':'G02','files':['bin/bellum-greek-range-qa.mjs'],'purpose':'Detect source mutation during Bellum range QA.','existing_expectation':'Exactly 107 tracked XML files, including the historical seven Lodge additions.','still_valid':'The source-mutation safeguard is valid; the fixed tracked count is obsolete. The canonical pin already contains 286 tracked XML, including review evidence.','legitimate_change':'The reviewed production corpus now contains 143 XML paths; review XML is separately preserved evidence.','minimal_update':'Require the exact complete production path/hash manifest, preserve before/after hashes for every production XML, and retain all raw-XML range and baseline DOM assertions. Remove the old static-guard surgery workaround and run the repaired native static guard.','outcome':'PASS: both sources, 111 chapters, 704 subchapters and 4,001 Niese views each; Greek/direct/Latin/English parity preserved; focused state/note/history checks pass.'},
 {'id':'G03','files':['bin/lodge1602-bellum-qa.mjs'],'purpose':'Prevent unknown XML additions and malformed files, including the seven explicitly identified Lodge paths.','existing_expectation':'Historical 100-path set plus exactly seven Lodge files, with only Antiquities Greek/Latin V differing.','still_valid':'Unknown/missing/malformed source rejection and exact seven Lodge identities remain valid; the historical current-corpus census and two-file delta are obsolete.','legitimate_change':'Later pinned canonical releases and certified I–XI English assembly have explicitly reviewed additional paths and source versions.','minimal_update':'Compare the current parsed corpus to the exact reviewed 143 paths; retain historical change records, the exact seven Lodge paths, unknown-file detection and malformed-Lodge rejection.','outcome':'PASS: native inventory and both negative XML checks. The browser body is verified by the complete native Lodge rendered-text suite; its frozen accepted QA document is retained.'},
 {'id':'G04','files':['bin/lodge1602-bellum-qa.ps1'],'purpose':'Independently compare Lodge against its immutable master, protect all source trees and detect deliberate corruption.','existing_expectation':'Physical checkout bytes equal the old master/100-file snapshot and Lodge publication hash.','still_valid':'Master SHA, frozen evidence byte equality, full decoded text/whitespace/tree/ID/milestone assertions and corruption tests remain valid. Fresh Git LF differs from the reviewed CRLF bytes.','legitimate_change':'Whiston source assembly is explicit; Git recovery may change only line-ending representation of unchanged non-Whiston witnesses.','minimal_update':'Use the complete reviewed source guard and exact frozen publication hashes for unchanged Bellum witnesses; retain every independent master/tree assertion and all nine corruption tests.','outcome':'PASS: immutable master SHA, 4,001 HIGH Lodge intervals, 704 coarse links, 111 chapters, all nine deliberate corruption tests rejected. No guard block is removed at runtime.'},
 {'id':'G05','files':['bin/reader-corpus-integrity.mjs','bin/prepare-reader-publication.mjs','bin/reader-corpus-qa.mjs','_docs/reader-corpus-integrity.json'],'purpose':'Retain frozen publication authority hashes across fresh Git/build recovery.','existing_expectation':'Git/build byte representation already equals the reviewed CRLF authority.','still_valid':'Every frozen SHA must still match literally. The implicit EOL assumption is false for a fresh checkout.','legitimate_change':'No text, structural or frozen-hash change; exact known EOL representation is reconstructed in generated output only.','minimal_update':'Accept only recorded checkout hashes, keep certified Whiston bytes exact, and restore generated publication bytes only if their literal SHA equals the frozen authority. Validate all generated XML before writing.','outcome':'PASS: 143 parsed source paths; 38 literal frozen publication hashes; missing, unexpected, corrupt source and altered manifest/concordance/Lodge authority tests all rejected.'},
 {'id':'G06','files':['Gemfile','_config.yml','build/Gemfile.lock','build/im6-build-env.rb'],'purpose':'Run the standard publication build with its required plugins/dependencies.','existing_expectation':'RMagick and compatible native SDK available; all configured plugins load.','still_valid':'Valid and retained. Missing Windows RMagick was a pre-existing environment failure, not a renderer regression.','legitimate_change':'Only isolated task dependencies are prepared; no Gemfile/config/plugin removal.','minimal_update':'Build RMagick 4.3.0 against the installed ImageMagick 6 SDK in the task directory, resolve locally installed gems, then run ordinary bundle exec jekyll build with all plugins. The lock/bootstrap are review evidence only.','outcome':'PASS: bundle check; standard complete-plugin build in 112.326 seconds; generated reader inputs equivalent to the certified preview; inherited Sass warnings only.'},
 {'id':'G07','files':['bin/lodge1602-bellum-browser-qa.js','bin/bellum-greek-range-browser-qa.js'],'purpose':'Require the complete numbered chapter menu and validate actual rendered source words.','existing_expectation':'Every nonempty chapter option is numeric and renders a chapter div.','still_valid':'Exact numeric chapters remain mandatory; the existing canonical source-contents option is a distinct paratext view.','legitimate_change':'This was already present at the canonical pin. Whiston integration introduces no contents feature.','minimal_update':'Allow only the explicitly known contents control alongside exact numeric chapters (including inherited chapter 0); retain numeric counts and frozen digest; additionally compare all seven Lodge contents views with the registry-selected raw XML.','outcome':'PASS: complete numbered views and frozen Lodge digest unchanged; seven exact contents checks pass; no unknown control is silently ignored.'},
 {'id':'G08','files':['Historical review/* English context and IX unavailable assertions','review/BookI_Pilot_2026-10-10/scripts (original delivery archive)','tools/smoke_qa.cjs','tools/xml_intervals.py'],'purpose':'Ensure English appears exactly as the source/version enabled by that release, and preserve independent witness availability.','existing_expectation':'I–XI direct English is contextual, VII.1–6 may recover the complete contextual paragraph, and IX.51–109 English is unavailable.','still_valid':'Correct for the frozen historical release; superseded for certified segmented I–XI. Contextual fallback remains valid for XII–XX. Greek/Latin IX omissions remain valid.','legitimate_change':'Certified exact English rendering replaces paragraph context only for the explicit Proem/I–XI enablement; 59 restored IX English intervals become available independently.','minimal_update':'Preserve immutable old certificates/scripts; replace current acceptance with all 3,821 exact interval hashes/boundaries plus separate 18 inherited fallback views. Fresh standard-built checks cover every restored IX interval, every Book I MEDIUM decision, VII.1–6, XI transitions, native navigation and nine fallback books.','outcome':'PASS: 3,821/3,821 independently reconciled exact displays; 119 fresh exact checks; all 59 restored IX; 10 native neighbour selections; 18 inherited and 9 fresh fallback checks. No failed contextual assertion is counted as a pass.'},
 {'id':'G09','files':['bin/deh-concordance.mjs','assets/js/dehParallelsCore.js','assets/data/deh-josephus-concordance.json','bin/lodge1602-bellum-import.ps1'],'purpose':'Prevent mutation/reimport of frozen scholarly authority and detect corpus changes after an import.','existing_expectation':'An import candidate must still match the corpus and source authority from which it was constructed.','still_valid':'Valid; this integration does not reimport the concordance or Lodge. A historical import against a changed corpus should still refuse acceptance.','legitimate_change':'Only English reader/source integration and reviewed QA corpus identity; no concordance/master authority change.','minimal_update':'None. Preserve the strict importer/production assertions and every frozen data byte.','outcome':'Unchanged; frozen bytes and production module identical to pin; full native displayed extraction suite passes.'},
 {'id':'G10','files':['BookI-original/SCHEMA_QA.json','BookI-original/REPORT.md'],'purpose':'Distinguish XML parsing/project fragment conventions from generic TEI All schema conformance.','existing_expectation':'Baseline and segmented headerless fragments both fail generic TEI All at the missing teiHeader.','still_valid':'Valid inherited qualification. It must not be relabelled schema success.','legitimate_change':'No new schema diagnostic, source wording or non-milestone structure change.','minimal_update':'None; preserve original failed generic-schema receipt and require all current project XML to parse.','outcome':'143/143 production XML parse; generic TEI All remains an acknowledged pre-existing fragment limitation.'}
]
save('LEGACY_GUARD_REGISTER.json',guards)
(PACK/'LEGACY_GUARD_REGISTER.md').write_text('# Legacy test and build guard reconciliation\n\nEvery original safeguard below is retained or replaced by a more explicit assertion. Historical source certificates and their original failed-launcher logs remain unchanged. No failure is hidden by deleting a test or disabling a build plugin.\n\n'+ '\n\n'.join('## '+g['id']+' — '+', '.join(g['files'])+'\n\n'+ '\n\n'.join('**'+label+':** '+g[key] for key,label in [('purpose','Original purpose'),('existing_expectation','Existing expectation'),('still_valid','Validity'),('legitimate_change','Behaviour/source change'),('minimal_update','Minimal disposition'),('outcome','Result')]) for g in guards)+'\n',encoding='utf-8')
historical=[]
pattern=re.compile(r'niese-context-note|INHERITED_UNAVAILABLE|complete context|contextual English|English context',re.I)
for p in (ROOT/'review').rglob('*'):
 if p.suffix not in ('.cjs','.js','.mjs'):continue
 if 'Whiston_I_XI_' in str(p):continue
 lines=p.read_text(encoding='utf-8',errors='replace').splitlines()
 hits=[{'line':i,'excerpt':line[:350]} for i,line in enumerate(lines,1) if pattern.search(line)]
 if hits:historical.append({'path':p.relative_to(ROOT).as_posix(),'hits':hits,'disposition':'Frozen release-specific evidence, retained. Current exact I–XI and contextual XII–XX acceptance are separate and stronger; this script is not silently rewritten.'})
save('HISTORICAL_CONTEXT_GUARD_SCAN.json',historical)
save('QA_ATTEMPT_DISPOSITIONS.json',[
 {'attempt':'Original prototype three launchers','classification':'Documented stale historical inventory guards','evidence':'Original HISTORICAL_GUARD_AUDIT.json and all three logs retained unchanged','resolution':'G01–G05; repaired native guards now pass.'},
 {'attempt':'New evidence reconciliation Greek dictionary key / confidence key','classification':'Evidence compiler assumption','resolution':'Handle absent Greek fields independently and use the original QA confidence field; full proof completed without changing sources or renderer.'},
 {'attempt':'Native Lodge static unchanged Latin byte assertion','classification':'Pre-existing fresh-Git LF versus frozen CRLF authority','resolution':'G04–G05; exact literal publication hashes preserved; full tree and all nine corruption gates pass.'},
 {'attempt':'Native Lodge chapter 1.contents','classification':'Pre-existing test expects every chapter option to be numeric','resolution':'G07; exact contents checks added while numbered count and frozen digest remain unchanged.'},
 {'attempt':'New strict chapter 0 / XML registry field whitespace checks','classification':'New harness implementation assumptions','resolution':'Recognize observed inherited chapter 0 and read the registry value element; no production behaviour change. Full suites restarted and pass.'},
 {'attempt':'Missing RMagick / SDK auto-detection','classification':'Pre-existing Windows build environment','evidence':'All installer logs retained in build/','resolution':'Authentic installed ImageMagick 6 command/SDK selected after RubyInstaller compiler activation; standard complete-plugin build passes. No dependency source patch.'},
 {'attempt':'Corpus manifest structure authority metadata','classification':'Receipt metadata','resolution':'Correct authority_commit to the certified prototype; permitted source bytes and acceptance hashes unchanged; final guards rerun.'}
])
issues=[
 {'severity':'P2 editorial, nonblocking for this scoped English integration','issue':'Greek I.272 label remains inside the preceding quotation.','evidence':'Original Book I adopted English boundary uses So suspecting; printed/Greek control disagreement recorded. Entire canonical Greek Book I equals the pilot Greek bytes; last source edit d79f1930a579e9ecb4412df5959f3d97211ffb0a predates the pilot.','action':'A separate Greek editorial/control adjudication is needed before claiming complete cross-language boundary agreement. No Greek correction is authorized or performed.'},
 {'severity':'P2 inherited transcription, nonblocking for segmentation/display','issue':'35 Book I source differences; I.260–263 shorter extents and severely damaged I.271.','evidence':'Original complete extent review and all surviving English unchanged. Every identity has surviving English; 17 boundaries individually resolved.','action':'Retain the explicit completeness qualification. Any restoration or edition attribution requires a separate source-review mission.'},
 {'severity':'P2 inherited apparatus HOLD, outside this integration','issue':'Canonical Package C contains three unresolved Book I references and two malformed 404 targets.','evidence':'Pinned Postrelease_Reader_Repairs_Integration_2026-10-11/UNRESOLVED_REFERENCES.md/json explicitly retains the editorial hold. No secure correspondence was established.','action':'Preserve the hold; do not invent, redirect, disable or count these apparatus links as repaired.'},
 {'severity':'P3 provenance/publication qualification','issue':'Book IX restored 59 intervals and the older 232-section transcription have distinct recorded provenance; older underlying edition/source licensing is qualified.','evidence':'All original IX provenance and licensing notices retained; restored source is the certified 1856 pp.251–255 delivery.','action':'Keep notices and source qualifications in any later controlled publication; this receipt grants no publication authorization.'},
 {'severity':'P3 inherited technical diagnostics','issue':'Headerless generic TEI All failures, inherited duplicate annotations ID and Sass deprecation warnings.','evidence':'Baseline diagnostics retained; all XML parses, no new reader errors or source changes.','action':'Do not claim generic-schema validation or unrelated defect repair; handle separately if authorized.'}
]
save('REMAINING_ISSUES.json',issues)
original=load('BOOK_I_SUPERSEDING_CERTIFICATION.json')
adjudication=(PACK/'BookI-original/ADJUDICATION.md').read_text()
decisions=re.findall(r'## I\.(\d+)\n\nAlternatives: ([^\n]+).*?Confidence: ([^\n]+)',adjudication,re.S)
assert len(decisions)==17
table='\n'.join('| I.'+n+' | '+alternatives+' | MEDIUM retained; resolved |' for n,alternatives,confidence in decisions)
(PACK/'BOOK_I_RECONCILIATION.md').write_text(f'''# Book I certification reconciliation — 11 October 2026

**A new scoped English certification is justified.** The superseding receipt certifies DATA-GO for segmentation of the preserved project transcription and RENDERER-GO for its 346 exact displayed intervals. It supersedes the historical blanket English integration hold; it does not certify a complete Whiston transcription or complete Greek/English boundary agreement. The original report, all 17 decisions and failed generic-schema receipt are copied byte for byte in `BookI-original/`. The original pilot archive remains unchanged.

The receipt was issued at `{original['issued_UTC']}` from delivery `b8cf6c9d36db610ea1dc4c65d070b016048262e1`. Proem I.1–26 and narrative I.27–346 retain their separate XML files.

## Findings on the five certification questions

1. The original contextual-renderer objection is resolved by all 346 exact English displayed intervals, preserved containing views and the explicit Proem/I.27 transition. The inherited Greek I.272 qualification, 35 English source differences, headerless generic-schema diagnostic and duplicate annotations condition remain applicable in their original scope.
2. All English boundary uncertainties were resolved in the original pilot: 329 HIGH and 17 adjudicated MEDIUM, zero unresolved candidates and zero unexplained textual changes. MEDIUM confidence has not been promoted. No boundary decision was reopened.
3. Greek I.272 is an inherited Greek editorial/control disagreement. Its label is inside the preceding quotation, while the adopted English starts at “So suspecting”. The record cites Niese printed p.65/PDF155 and Lexundria for that English position. Current canonical Greek is byte-identical to the pilot Greek; file history shows no later correction, and inspected canonical records contain no superseding I.272 adjudication. The renderer faithfully preserves the old Greek interval. This is not an English renderer defect and is not claimed resolved by another workstream.
4. The remaining Greek disagreement does not invalidate exact rendering of the already adjudicated English interval. Inherited English losses do limit the completeness claim: I.271 still contains only “Isaac perceivest to be Esau.”, and I.260–263 retain their shorter surviving extents. DATA-GO here means faithful segmentation of that surviving project text. No missing words are supplied or attributed to Whiston's printed edition.
5. The dated superseding receipt is appropriate for that English scope because source preservation, all boundary decisions, exact rendered content and containing views have passed. A complete cross-language agreement certificate remains unavailable until the separate Greek question is adjudicated. Public deployment remains unauthorized.

## Retained individual decisions

| Section | Original alternatives and adopted position | Status |
| --- | --- | --- |
{table}

The original source-difference review also retains corrupt spellings, literal footnote-like numerals and the [GREEK] placeholder. The separate canonical apparatus Package C hold concerns missing reference targets; it is not an adjudication of I.272 and has not been repaired here.
''',encoding='utf-8')
source_table='\n'.join(f"| {b['book']} | {sum(o['sections'] for o in b['outputs'])} | `{b['delivery_commit']}` |" for b in inventory)
hash_table='\n'.join(f"| {Path(o['path']).name} | `{o['sha256']}` |" for b in inventory for o in b['outputs'])
changed=git('diff','--name-only',PIN,'HEAD').splitlines()
production=[p for p in changed if not p.startswith('review/')]
assert len(production)==27
save('PRODUCTION_DIFF_SCOPE.json',{'baseline':PIN,'implementation_HEAD':implementation,'files':production,'runtime_prototype_delta':16,'legacy_guard_and_manifest_delta':11,'Greek_Latin_and_XII_XX_XML_changes':0})
save('INTEGRATION_CERTIFICATE.json',{'status':'CANONICAL-INTEGRATION-READY','issued_UTC':now,'scope':'Isolated certified Whiston Antiquities English Proem/I–XI integration candidate',
 'canonical_integration_authorized':False,'public_deployment_authorized':False,'pinned_canonical_commit':PIN,'original_RENDERER_GO_commit':PROTO,
 'original_RENDERER_GO_certificate_preserved':True,'implementation_commit':implementation,'exact_English_intervals':3821,'traditional_views':967,'alignment_views':823,
 'interval_evidence_method':'All 3821 independently recomputed candidate XML intervals match certified actual displayed content; complete original runtime/evidence byte equivalence verified. 119 fresh actual display checks on the full standard build.',
 'whole_files':12,'navigation_original':57,'navigation_fresh':10,'unsegmented_fallback_original':18,'unsegmented_fallback_fresh_books':9,
 'cross_work_fresh':{'Bellum':70,'contra-apionem':10,'deh':25},'DEH_component_checks':2115,'DEH_section_occurrences':8193,
 'Bellum_complete_Whiston_and_Lodge_each':{'chapters':111,'subchapters':704,'niese':4001},'Lodge_frozen_digest_match':True,'Lodge_exact_contents_views':7,
 'standard_full_plugin_build':'PASS','production_XML_integrity_paths':143,'frozen_publication_inputs':38,'new_reader_regressions':0,
 'BookI_certification':'Superseding scoped English DATA-GO / RENDERER-GO; original Greek and transcription qualifications remain open.',
 'material_blockers_for_this_integration':[],'remaining_qualified_issues':issues,
 'delivery_commit_note':'The exact final delivery commit and ZIP checksum are sealed externally in DELIVERY_RECEIPT.json, avoiding recursive self-commit attribution.'})
commits=git('log','--reverse','--format=%H %s',PIN+'..HEAD')
(PACK/'REPORT.md').write_text(f'''# Whiston Antiquities I–XI canonical integration candidate

**CANONICAL-INTEGRATION-READY.** All substantive blockers for this scoped English integration are resolved and complete essential QA passes. This is an isolated review candidate; no merge, push or public deployment is authorized or performed.

Canonical development is pinned to the verified clean full commit `{PIN}`. The unchanged certified prototype is `{PROTO}`. The candidate branch is `integration/whiston-i-xi-certified-20261011` in `C:/workspace/LatinJosephus-Whiston-I-XI-Integration-20261011`. The prototype used the same canonical baseline, so there are no intervening canonical changes to overwrite. Certified Books XII–XIV remain separate and are not assembled or enabled.

## Certification reconciliation

Book I receives the explicitly dated `BOOK_I_SUPERSEDING_CERTIFICATION.json`; see `BOOK_I_RECONCILIATION.md` for all five questions and 17 retained MEDIUM decisions. Its scope is segmentation of surviving project English, not restoration or a completeness claim. Greek I.272 remains a recorded editorial/control disagreement and Greek stays untouched. The original pilot report and original prototype RENDERER-GO certificate remain unchanged, with their original hashes and recovery archive verified.

DATA-GO certifies the supplied English segmentation/source integrity. The original RENDERER-GO certifies its exact display. This new readiness receipt adds Book I scope reconciliation, repaired meaningful guards, a fresh isolated candidate and standard complete-plugin build verification. None grants publication authorization.

## Candidate and affected files

The twelve certified English XML files are assembled byte for byte. Runtime changes are exactly the four certified prototype files: `assets/js/renderTei.js`, `assets/css/tei.css`, `assets/xml/antiquities/niese/book-09.json` and `assets/xml/antiquities/structure.xml`. They retain explicit exact enablement only for Proem/I–XI, independent IX English availability, ten restored English traditional locators and one English-only restored alignment range. All Greek/Latin source and registry fields remain unchanged. XII–XX retains contextual English.

The eleven additional internal files reconcile guards: the DEH launcher; Bellum launcher/browser harness; Lodge launcher/static/browser harness; the shared corpus integrity, publication preparation and negative-test tools; and their `_docs` manifest/instructions. `PRODUCTION_DIFF_SCOPE.json` lists all 27 non-review files. No other renderer feature, source restoration, cleanup or later-book segmentation is included.

`LEGACY_GUARD_REGISTER.md/json` records every identified documented expectation, original purpose, validity, minimal disposition and outcome. Historical English context scripts remain provenance evidence, with a scan in `HISTORICAL_CONTEXT_GUARD_SCAN.json`; current acceptance replaces their obsolete I–XI expectations with exact source intervals and retains separate XII–XX fallback. Strict concordance import/production assertions and frozen master data are unchanged. No test is deleted or failure suppressed; all substantive failed guard expectations have a recorded replacement and passing outcome. `QA_ATTEMPT_DISPOSITIONS.json` distinguishes stale baseline guards, compiler/test assumptions and native environment failures from renderer regressions.

## Complete QA and standard build

| Gate | Result and evidence |
| --- | --- |
| All English Niese intervals | **3,821/3,821**; candidate XML text events independently recomputed, matched to certified actual displayed hashes and opening/closing boundaries. `CANDIDATE_XML_INTERVAL_QA.json`, complete `PER_SECTION_QA.csv`. |
| Traditional views | **967/967** actual displayed-content evidence independently verified against identical runtime inputs. |
| Alignment views | **823/823** actual displayed-content evidence independently verified against identical runtime inputs. |
| Whole source views | **12/12**; Proem and I.27 remain distinct. |
| Fresh candidate English content | **119 exact views**, including all 59 restored IX sections, all 17 Book I decisions, VII.1–6 and XI physical transitions; source notices and owned notes checked. |
| Navigation/deep links | Original **57** direct/native checks preserved; **119** fresh direct URLs and **10** native neighbouring selections pass. |
| Unsegmented fallback | **18** original whole/direct views plus **9** fresh XII–XX contextual witness checks; exact mode remains disabled. |
| Notes/inline markup/quotation boundaries | Original full interval edges and **18** inline elements in 16 selections preserved; **7** owned restored footnotes visible and text-exact. Inherited apparatus hold is separately qualified. |
| Fresh cross-work content | Bellum **70**, Contra Apionem **10**, DEH **25** actual displayed comparisons pass on the standard build. |
| Full Bellum legacy regression | For **each** Whiston and Lodge: **111** chapters, **704** subchapters, **4,001** Niese views; raw Greek oracle and baseline Latin/English/direct-Greek DOM parity pass. |
| Lodge master/browser regression | Immutable master, exact full source trees, 4,001 HIGH sections, all **9** corruption tests; frozen browser text/ID digest unchanged; **7** exact source-contents views pass. |
| Native DEH launcher | **2,115** component checks and **8,193** displayed section occurrences; frozen extraction eligibility/boundary guards pass. |
| Corpus integrity | **143/143** XML parsed and bound to explicit authority; **38** literal frozen publication hashes preserved; negative source/manifest tests reject corruption. |
| Standard build | **PASS**, ordinary Bundler/Jekyll command, all configured plugins including responsive-image enabled; **112.326 seconds**. |

The original expensive English/traditional/alignment suites are not needlessly repeated: every reader/page/layout/style/source input and every original evidence file matches the certified prototype. Candidate interval extraction is independently recomputed, and fresh standard-built display/legacy regressions supplement that complete evidence. `BUILD_QA.json` proves generated reader runtime equivalence; only DEH cache timestamps and documented nonsemantic EOL representations differ. This is content verification, not page-load certification.

The pre-existing Windows RMagick problem is resolved in task-local dependencies without changing Gemfile, production config, dependency source or plugin checks. Build logs, the local resolved lock and SDK selection bootstrap are retained in `build/`. Frozen DEH/Bellum/Lodge publication hashes bind reviewed CRLF bytes; run the documented postbuild preparation/verification command on generated output. No repository witness XML is rewritten for this representation.

## Exact source identities and checksums

| Book | English sections | Frozen delivery commit |
| --- | ---: | --- |
{source_table}

Book I includes 26 Proem and 320 narrative intervals. IX uses only certified restored-and-segmented delivery `2ce18b40ea8652e5e0d5046f10b1c39935fcdc54`. XI retains physical order 1–311, 326–342, 312–325, 343–347; extraction ends at the next physical English marker while numeric navigation remains independent.

| Certified XML | SHA-256 of assembled delivery bytes |
| --- | --- |
{hash_table}

`SOURCE_INVENTORY.json` records every source identity, Git blob, original recovery ZIP/checksum, QA receipt and EOL-only archive qualification. All eleven original recovery archives were rechecked; all twelve assembled sources equal their delivery Git blobs exactly. `EVIDENCE_RECONCILIATION.json` binds original evidence and sources; `PROTECTED_START/FINISH.json` checks complete tracked working-file hashes and branch cleanliness for canonical, original prototype and XII–XIV.

## Remaining qualified issues

There are **no P0/P1 or new renderer/integration blockers**. P2 inherited qualifications are Greek I.272, Book I transcription damage and the already retained canonical apparatus Package C hold. P3 qualifications are source/provenance rights, headerless generic TEI schema diagnostics, inherited annotation IDs and Sass warnings. `REMAINING_ISSUES.json` supplies evidence and separate future actions. None is silently adjudicated or counted as repaired. This candidate certifies the scoped English integration, not complete cross-language agreement, a corrected Whiston edition or apparatus recovery.

## Review, commits and controlled integration recommendation

Implementation commits currently sealed:

```text
{commits}
```

The report/evidence delivery commit follows. Its exact full identity is in the external `DELIVERY_RECEIPT.json`, together with patch/bundle checksums and the final recovery verification. The full binary Git diff against `{PIN}` and a focused source/renderer/guard diff are provided in the delivery directory.

Proceed through a separately authorized controlled canonical integration after reviewing the source inventory, Book I scoped receipt and guard register. Reverify the canonical HEAD immediately before integration; if it advances, reconcile that delta without overwriting it and rerun affected gates. Preserve the original RENDERER-GO receipt, all source qualifications, separate XII–XIV branches and the required exact publication-byte preparation. Public deployment is a separate authorization and task.

Recovery uses the verified ZIP, entry manifest and SHA-256 sidecar. The archive includes the exact changed files, immutable original evidence, incremental Git bundle/patch and independently runnable static reader preview. `RECOVERY.md` gives isolated restore and revalidation instructions. **STOP: no merge, push, deployment or canonical development change.**
''',encoding='utf-8')
print('Compiled scoped Book I reconciliation, complete guard dispositions, source inventory and CANONICAL-INTEGRATION-READY report')
