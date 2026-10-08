from pathlib import Path
from lxml import etree as E
from collections import Counter
import json,hashlib,subprocess
R=Path(r'C:\workspace\LatinJosephus-source-toc-navigation');V=R/'review/Source_TOC_Navigation_2026-10-07';BASE='087c0bf651037d83c5156495836510d250bdcf09'
def read(n):return json.loads((V/n).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,x):(V/n).write_bytes((json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode())
old=read('phase-a-accepted-2026-10-07/QA.json');baseline=read('PHASE_B_BASELINE_2026-10-08.json');integrity=read('INTEGRITY_QA_2026-10-08.json');browser=read('CONTENTS_BROWSER_QA_2026-10-08.json');trad=read('BROWSER_QA.json');bam=read('BAMBERG_BROWSER_QA.json');burl=read('BAMBERG_URL_QA.json');pairs=read('SAME_NIESE_DIFFERENT_POSITION_QA.json');aligned=read('ALIGNMENT_ALL_QA.json');bellum=read('PROTECTED_SOURCE_GATE_QA.json');followup=read('FOLLOWUP_GATE_QA.json');interact=read('INTERACTION_QA.json');multi=read('XI_MULTISPAN_GATE_QA.json');transcript=read('BAMBERG_TRANSCRIPTION_QA_2026-10-08.json');records=read('VERIFIED_CONTENTS_REGISTRY_2026-10-08.json');census=read('SOURCE_TOC_CENSUS.json');extract=read('BAMBERG_WORD_EXTRACTION_2026-10-08.json')
for name in [integrity,browser,bam,burl,pairs,aligned,bellum,followup,interact,transcript]:assert name['result']=='PASS'
assert trad['traditional']['executable']==5034 and trad['traditional']['unavailable']==33 and not trad['errors']
assert browser['source_combinations']==104 and len(browser['interactions'])==29 and not browser['errors']
N={'t':'http://www.tei-c.org/ns/1.0'};d=E.parse(str(R/'assets/xml/antiquities/structure.xml'));rows=d.xpath('//t:list[@type="traditional-boundaries"]/t:item',namespaces=N);scheme=Counter(q.find('.//t:f[@name="scheme"]/t:string',N).text for q in rows);points={q.find('.//t:f[@name="physical-point"]/t:string',N).text for q in rows};statuses=Counter(q.find('.//t:f[@name="verification-status"]/t:string',N).text for q in rows)
assert scheme=={'chapter':257,'subchapter':1432} and len(points)==1441;assert len(d.xpath('//t:list[@type="bamberg-boundaries"]/t:item',namespaces=N))==198
assert sum(q['alignment_units'] for q in aligned['checks'])==1441
assert sum(q['selections'] for q in trad['niese'].values())==2456
cross={w:sum(q['ranges'] for q in trad['crossWork'] if q['work']==w) for w in ['deh','bellum-judaicum','contra-apionem']}
qa={'date':'2026-10-08','base_commit':BASE,'verdict':'GO_FOR_HUMAN_BROWSER_REVIEW','phase_a_accepted_unchanged':old,'phase_a_global_NO_GO_superseded_by':'Human per-source verification authorization 2026-10-08','source_eligibility':{'matrix_rows':104,'eligible_book_witness_combinations':29,'unavailable_or_deferred':75,'Lodge_unique_printed_source_lists':7,'Lodge_unique_entries':136,'Latin_XIV':'Deferred SR-061; no re-adjudication'},'Bamberg_entries':extract['counts'],'Bamberg_supplements':{str(q['book']):q['supplements'] for q in transcript['books']},'Word_italic_span_to_TEI':{'total':64,'supplied_elements':63,'whitespace_only_hi_elements':1,'concordance':'64/64 PASS','invented':0,'omitted':0},'TEI_schema':transcript['schema'],'contents_browser':{'source_combinations':104,'supported_URL_history_copy_reload_cases':29,'book_switching':'PASS','mixed_availability':'PASS','source_switching':'PASS','keyboard':'PASS','contents_display_has_no_duplicate_DOM_IDs':True,'source_entries_nonclickable':True,'themes':browser['themes'],'visual_inspection':'Final light and dark PNGs inspected; no overlap/clipping or annotation intrusion.','note':'Existing Book-view duplicate annotations IDs are baseline source apparatus; unchanged and separately compared, not introduced by contents.'},'traditional':{**trad['traditional'],'schemes':dict(scheme),'independent_verification_statuses':dict(statuses),'synthetic_lower1':0,'availability_checks':257,'prefix_checks':227},'bamberg':{'identities':198,'language_displays':594,'compact_URL_round_trips':198,'same_Niese_different_position_pairs':6,'pair_language_checks':18,'result':'PASS'},'niese_antiquities':{'selections':2456,'three_pane_comparisons':7368,'public_I_VII_scope':'UNCHANGED'},'alignment_units':{'identities':1441,'differential_DOM_and_witness_order':'PASS','Book_VI_bindings':'PASS'},'Book_XI':{'multi_span_language_checks':18,'internal_Niese_citation_checks':2,'canonical_membership_interpolations_notice_witness_order':'PASS'},'cross_work':{'range_comparisons':cross,'Bellum_Whiston_Lodge_ranges':sum(q['ranges'] for q in bellum['checks']),'Bellum_Niese_source_comparisons':sum(q['niese'] for q in bellum['checks']),'Lodge_segmentation_markers':4001,'notes_toggle_and_contents_URL_preference':'PASS','keyboard_history_panes_themes':'PASS'},'integrity':{'existing_XML_files_byte_identical':integrity['all_original_XML_files'],'existing_source_files_unchanged':380,'canonical_clean_expected_HEAD_and_origin':True,'historical_reviews_unchanged':True,'frozen_external_inputs_unchanged':48,'new_DOCX_unchanged':True,'new_empty_anchors':0,'running_text_ID_sameAs_topology_milestones':'UNCHANGED','Git_writes':'NONE','site_build':'NONE'},'supporting_evidence':['CONTENTS_BROWSER_QA_2026-10-08.json','BAMBERG_TRANSCRIPTION_QA_2026-10-08.json','BROWSER_QA.json','BAMBERG_RANGE_QA.json','BAMBERG_URL_QA.json','SAME_NIESE_DIFFERENT_POSITION_QA.json','ALIGNMENT_ALL_QA.json','PROTECTED_SOURCE_GATE_QA.json','FOLLOWUP_GATE_QA.json','XI_MULTISPAN_GATE_QA.json','INTERACTION_QA.json','INTEGRITY_QA_2026-10-08.json']}
dump('QA.json',qa)
report=f'''# Source contents integration Phase B

Date: 2026-10-08. **GO for human browser review.** The human editor’s per-source authorization supersedes the Phase-A global implementation stop. The complete accepted census remains unchanged in SOURCE_TOC_CENSUS.csv / .json. Its original report, authority document and QA/manifest are preserved byte-for-byte in phase-a-accepted-2026-10-07. The historical report follows this amendment.

Worktree: `{R}`. Branch: source-toc-navigation. Base: `{BASE}`. Canonical remains clean on the required HEAD and origin. Nothing is staged, committed, merged or pushed.

## Reader coverage

| Work | Witness | Books enabled |
|---|---|---|
| Antiquities | Greek / Niese | V, XI–XX |
| Antiquities | Latin / Bamberg Msc.Class.78 | II–V, XIII, XV–XX |
| Bellum Judaicum | English / Lodge 1602 | I–VII |

There are 29 eligible book/witness combinations in the separately dated 104-row status matrix. Source existence, transcription verification, encoding and publication eligibility are separate fields. Whiston, Cardwell and other insufficiently verified sources remain deferred. Pollard’s five DEH books retain the accepted no-source-TOC result. Latin Antiquities XIV retains SR-061: its contents/narrative paragraph is neither split nor adjudicated. Greek XIV contents are available independently.

Existing source chapter-zero/list blocks are reused as paratext, never reconstructed from navigation. Lodge’s seven printed lists retain their 136 entries and anomalous printed numbering. Canonical IV displays the existing printed IV and V lists; V displays printed VI; VI displays printed VII. Canonical VII uses that complete printed-VII list from its unchanged location in canonical VI, with an explicit printed-book scope note. No subset is generated from reader chapters.

## New Bamberg text and supplements

The governing file is `{extract['source']}` (19,987 bytes), SHA-256 `{extract['sha256']}`. The four new companion TEI files contain exactly 32 entries:

| Book | Entries | Blatt supplements |
|---|---:|---:|
| II | 3 | 2 |
| III | 11 | 42 |
| IV | 5 | 19 |
| V | 13 | 0 |

II–IV are the human editor’s double-checked marginal transcriptions. V is the governing improved main-text transcription. The source images/folios specified in the Word file are retained in TEI provenance; no fresh manuscript adjudication was undertaken.

The extraction resolves document defaults, inherited paragraph/character styles, OOXML italic toggle properties and direct run formatting. Adjacent italic runs are coalesced without assuming word boundaries. All 64 contiguous italic spans have TEI counterparts: 63 lexical spans use supplied with reason=lost, source=#blatt, resp=#human-editor and italic rendition; one leading whitespace-only italic span before II.II is retained as hi. It is not counted as supplied manuscript letters. Every entry’s complete text, labels, order and surrounding Latin match the Word extraction exactly. All five new XML files validate against the project-retained official TEI P5 schema.

Only II–IV carry the reader note: “Italicized text has been supplied from Blatt’s edition where trimming of the manuscript margins has removed words.” The local project bibliography identifies Franz Blatt, ed., The Latin Josephus (Aarhus, 1958); precise supplement page references were not supplied and are not invented.

Book V’s 26 entry comparisons against earlier Word and Google Sites HTML yield 13 variance records. The new Word governs every import. No chapter numbering/entry-boundary difference or consequential encoding uncertainty blocks V. Literal unusual readings and transcription notation remain unchanged, including factus factusque in II, [...]si in IV, and the insertion notation in V. The editorial register preserves these for review without silently repairing them.

## Generic reader and URLs

A TEI feature-structure index at assets/xml/source-contents.xml registers work, book, witness, verification status, exact source XML block and provenance. Four source-specific Bamberg companion files supply new paratext. No source contents text is stored in JavaScript and no book-specific renderer conditions were added. Existing XML and structure.xml are untouched.

Table of contents is the first Chapter option wherever a verified source is available. It has distinct view=contents semantics, never a chapter identity. Entering removes conflicting chapter/subchapter/bamberg/niese/unit/num parameters while retaining book, source selection, unrelated preferences and fragments. Numbered Chapter selection exits contents mode. Book switching retains contents when eligible and otherwise falls back to Book view. Every pane displays its own source or the neutral unavailable message. Entries are non-clickable.

Contents conversion suppresses default generated note/list decoration so source text appears exactly once. Narrative annotations/highlight controls are cleared/hidden during paratext display and restored by the ordinary reader on exit. Contents styling is scoped to .source-contents; supplied letters remain italic without inserting editorial brackets absent from the transcription. Source data are not appended to narrative ranges. The existing Lodge notes preference is registered generically for contents URL persistence.

## Verification

All 104 book/source combinations and 29 supported dropdown/copy/reload/history cases passed, including mixed availability, source and pane switching, keyboard operation and book fallback. Final light/dark displays were visually inspected. Measured normal-text contrast is 13.23:1 light / 11.85:1 dark. No duplicate DOM IDs occur in contents displays. Some baseline Book views retain a repeated source apparatus ID annotations; exact base comparisons confirm that this feature introduces none of those duplicates.

Traditional counts remain 257 Chapters, 1,432 Subchapters, 1,689 level rows and 1,441 physical positions. All 5,034 executable language ranges and 33 expected Book-IX unavailable states pass. All 257 Chapter availability states and 227 prefix/end checks pass; the nine absent-Loeb-lower-1 cases acquire no synthetic entries. VI.xii.8/XIII and XI’s multi-span membership, interpolation preservation and unchanged notice pass.

All 198 Bamberg identities / 594 language displays, compact URLs and six distinct same-Niese/different-position pairs pass. All 2,456 enabled Antiquities Niese selections / 7,368 pane comparisons match the base. All 1,441 Alignment units and Book-VI bindings match the base. Cross-work differential ranges pass: DEH 1,239; Bellum 1,441; Contra Apionem 693. The additional Whiston/Lodge suite passes 10,340 scenarios including 7,444 Niese/source comparisons. Lodge’s 4,001 segmentation markers are unchanged. Source/pane switching, notes, keyboard, themes and history pass.

All 108 pre-existing XML files are byte-identical, proving unchanged text, IDs, sameAs, milestones, topology and Book-XI order. Antiquities paragraph counts remain Latin 1,622 / Greek 1,681 / English 1,600, with 1,442 identified alignment paragraphs per layer including Proem. No new inline anchors were needed. All 48 original external authorities and the new DOCX pass hash checks. The canonical checkout remains clean at the required base. Its CRLF/LF checkout differences from the implementation worktree are documented as cross-checkout differences, not treated as source changes; no normalization occurred.

## Exact production changes

Modified: assets/js/renderTei.js; assets/css/tei.css.
New: assets/xml/source-contents.xml; assets/xml/antiquities/paratext/bamberg78/book-02-contents.xml, book-03-contents.xml, book-04-contents.xml, book-05-contents.xml.
Review evidence is confined to this existing review directory. The accepted October 6 and October 7 traditional/Bamberg certification packets remain byte-identical. No source PDF was reinterpreted, no website build was run and no recovery file was written.

Reproduction: use the bundled Python with -B for prepare_phase_b.py (Word extraction/TEI import), validate_phase_b.py (schema/text/concordance/variance/status checks) and verify_phase_b_integrity.py. Browser harnesses contents.test.cjs, regression.test.cjs, bamberg-regression.test.cjs and interaction-regression.test.cjs use installed Chrome and the real renderer/CETEI/XML. Optional regression gates are documented by their command-line names in the scripts. Historical test files are not modified. Development failures retained under development-diagnostics are superseded by the final PASS evidence.

---

# Accepted Phase A report (historical; global stop superseded above)

'''
(V/'REPORT.md').write_bytes(report.encode()+(V/'phase-a-accepted-2026-10-07/REPORT.md').read_bytes())
authority=f'''# Source contents authority amendment 8 October 2026

The accepted Phase-A authority record is preserved below and byte-for-byte in phase-a-accepted-2026-10-07. Its global stop is superseded by the human per-source authorization; unrelated unresolved witnesses remain deferred.

## Governing Bamberg II–V transcription

Exact path: `{extract['source']}`

SHA-256: `{extract['sha256']}`

Authority order: this newly supplied human-edited Word transcription; Bamberg Msc.Class.78 as underlying witness; Blatt as the identified source of italicized supplements; earlier Google Sites/Word/HTML as historical comparison only. II–IV are new double-checked marginal transcriptions. V is the improved controlling main-text transcription and is not blocked by disagreement with older versions. No fresh manuscript/source-print adjudication was required or performed.

Source references supplied in Word: II image 29, f.13r, right margin; III image 55, f.26r, right margin; IV image 79, f.38r, right margin; V image 104, f.50v col.B, main text. These references are retained in companion TEI sourceDesc. The manuscript was not fetched to redo transcription.

The project’s unchanged _pages/about.md identifies Franz Blatt, ed., The Latin Josephus (Aarhus, 1958), covering Antiquities I–V. Its file SHA-256 is `{sha(R/'_pages/about.md')}`. This existing local citation is used without inventing additional volume/series details. Exact supplement page references remain unspecified.

OOXML formatting and supplement concordance are fully recorded in BAMBERG_WORD_EXTRACTION_2026-10-08.json, WORD_ITALIC_SPANS_2026-10-08.json and BLATT_TEI_CONCORDANCE_2026-10-08.json. All 63 lexical supplied spans preserve exact character offsets/text and their relation to extant transcription. One italic whitespace-only span is separately retained as hi. The complete 32 entries and source headings/colophon preserve Word text exactly.

## Other eligible sources and boundaries of authorization

Greek Antiquities V/XI–XX and Latin XIII/XV–XX are the accepted census’s existing source contents blocks, identified by actual contents formulas and capitula text, not generated menus or inherited chapter identity. They are reused without changing their transcription. Latin XIV remains deferred under SR-061. The seven Lodge lists retain the accepted frozen master equality result and all 136 entries. Source ZIP SHA-256 `{census['source_authorities']['lodge-tcp']['sha256']}`; A04680.xml entry SHA-256 `{census['source_authorities']['lodge-tcp']['entry_sha256']}`. Their unusual existing file placement and printed-book scope are preserved. No marginal notes or empty Whiston milestones are promoted to contents.

The separately dated eligibility matrix records all 104 combinations and distinguishes existence, text verification, encoded availability and eligibility. It leaves Whiston/Cardwell/other insufficiently verified sources deferred and preserves the five accepted no-TOC results for Pollard. No borrowed, synthesized, reconciled or source-number-linked contents are provided.

FILE_MANIFEST.json records hashes for every eligible source file, new companion/index and review output, plus all original source protections. All frozen research authorities and the human Word remain unchanged.

---

# Accepted Phase A authority record (historical)

'''
(V/'SOURCE_AUTHORITY.md').write_bytes(authority.encode()+(V/'phase-a-accepted-2026-10-07/SOURCE_AUTHORITY.md').read_bytes())
diff=subprocess.check_output(['git','--no-optional-locks','-C',str(R),'diff','--','assets/js/renderTei.js','assets/css/tei.css']);(V/'IMPLEMENTATION_SOURCE.diff').write_bytes(diff)
# Fingerprint final source and review outputs. The manifest excludes its own after-hash.
oldfiles=read('phase-a-accepted-2026-10-07/FILE_MANIFEST.json')['preexisting_worktree_files'];files={};sourcepaths=['assets/js/renderTei.js','assets/css/tei.css','assets/xml/source-contents.xml',*[f'assets/xml/antiquities/paratext/bamberg78/book-{b:02}-contents.xml' for b in range(2,6)]]
for p in [*[R/s for s in sourcepaths],*sorted(V.rglob('*'))]:
 if not p.is_file() or p==V/'FILE_MANIFEST.json':continue
 rel=p.relative_to(R).as_posix();files[rel]={'before_sha256':oldfiles.get(rel,{}).get('sha256') or baseline.get(rel),'after_sha256':sha(p),'bytes':p.stat().st_size}
manifest={'base_commit':BASE,'modified_existing_production_files':['assets/js/renderTei.js','assets/css/tei.css'],'new_production_source_files':sourcepaths[2:],'original_project_files_unchanged':380,'protected_original_XML_files':108,'new_empty_anchors':0,'original_census_and_historical_reviews':'UNCHANGED; original root report metadata archived byte-for-byte','files':files,'eligible_source_files':{r['path']:sha(R/r['path']) for r in records},'governing_DOCX':{'path':extract['source'],'sha256':extract['sha256']},'manifest_self':{'before_sha256':baseline['review/Source_TOC_Navigation_2026-10-07/FILE_MANIFEST.json'],'after_sha256':'SELF_EXCLUDED'}}
dump('FILE_MANIFEST.json',manifest)
for rel,q in files.items():assert sha(R/rel)==q['after_sha256']
print('REVIEW_FINALIZED',len(files),'file fingerprints; manifest',sha(V/'FILE_MANIFEST.json'))