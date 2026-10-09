from pathlib import Path
import json,hashlib
V=Path(__file__).resolve().parent;R=V.parents[1];P=V/'presentation-correction'
def read(n):return json.loads((V/n).read_text(encoding='utf-8'))
def dump(n,d):(V/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def put(n,s):(V/n).write_text(s.rstrip()+'\n',encoding='utf-8')
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
# Earlier presentation evidence is preserved; the layout addendum certifies the current state.
if (V/'layout-correction/LAYOUT_QA.json').exists():
 import runpy
 runpy.run_path(str(V/'certify-layout.py'),run_name='__main__')
 raise SystemExit(0)
data=read('DATA_QA.json');browser=read('BROWSER_QA.json');reg=read('REGRESSION_BROWSER_QA.json');bam=read('BAMBERG_BROWSER_QA.json');align=read('ALIGNMENT_ALL_QA.json');follow=read('FOLLOWUP_GATE_QA.json');multi=read('XI_MULTISPAN_GATE_QA.json');interact=read('INTERACTION_QA.json');bellum=read('PROTECTED_SOURCE_GATE_QA.json');integrity=read('INTEGRITY_QA.json');scope=read('presentation-correction/CSS_SCOPE_QA.json');fc=read('presentation-correction/FILE_CHANGES.json')
for x in [data,browser,bam,align,follow,interact,bellum,integrity,scope]:assert x['result']=='PASS'
assert browser['books']==20 and browser['headings']==256 and browser['themeDisplays']==40 and len(browser['existing'])==39
assert reg['traditional']['rows']==1689 and reg['traditional']['executable']==5034 and reg['traditional']['unavailable']==33 and not reg['errors']
assert sum(x['selections'] for x in reg['niese'].values())==2456 and sum(x['alignment_units'] for x in align['checks'])==1441
assert len(bellum['checks'])==14 and all(x['result']=='PASS' for x in bellum['checks']);assert len(follow['availability'])==257 and len(follow['prefixChecks'])==227 and len(multi['checks'])==18
assert all(multi[x]=='PASS' for x in ['canonical_membership_no_duplication','interpolations_retained','disclosure_and_witness_link','book_and_alignment_views_vs_base'])
assert len(scope['checks'])==16 and len(fc['changes'])==22
for x in fc['changes']:assert h(R/x['path'])==x['presentation_after_sha256']
base=read('BASELINE.json');imp=read('presentation-correction/initial-integration/IMPLEMENTATION_MANIFEST.json')
for x in imp['production_changes']:
 x['initial_integration_sha256']=x['after_sha256'];x['after_sha256']=h(R/x['path']);x['presentation_before_sha256']=next(y['presentation_before_sha256'] for y in fc['changes'] if y['path']==x['path']);x['presentation_correction']='Reversible orig/reg display and one companion provenance note; registry clears duplicate Whiston notes only'
imp['production_changes'].append({'path':'assets/css/tei.css','before_sha256':base['worktree_files']['assets/css/tei.css']['sha256'],'after_sha256':h(R/'assets/css/tei.css'),'presentation_correction':'English compiled-index subtype only: left alignment, hidden orig, visible reg, nonitalic note; no font/size/colour/spacing/loading changes'})
imp.update({'heading_original_text_changes':0,'heading_display_changes':256,'summary_display_changes':40,'book_designation_display_changes':20,'CSS_changes':1,'renderer_changes':0,'production_file_count':22});dump('IMPLEMENTATION_MANIFEST.json',imp)
con=read('presentation-correction/initial-integration/SOURCE_ENTRY_CONCORDANCE.json');display={x['id']:x for x in read('presentation-correction/ORIGINAL_DISPLAY_CONCORDANCE.json')['entries']}
for e in con['entries']:e.update({'display_heading':display[e['id']]['display'],'original_encoding':'choice/orig','display_encoding':'choice/reg','case_only_display':True})
dump('SOURCE_ENTRY_CONCORDANCE.json',con)
qa=read('presentation-correction/initial-integration/QA.json');qa.update({'base_commit':base['base'],'source_schema_data_checks':data['executed_checks'],'CSS_changes':1,'renderer_changes':0,'source_audit':data['packets'],'presentation_correction':{'original_headings_exact':256,'sentence_case_headings_reviewed':256,'interval_summaries':40,'book_designations':20,'orig_reg_pairs':316,'single_provenance_notes':20,'notes_immediately_below_title':20,'both_theme_displays':40,'existing_contents_exact':39,'out_of_scope_style_comparisons':16,'III8_no_terminal_point':'PASS','III15_wording_and_punctuation':'PASS','V3_THEM':'PASS','left_alignment':'PASS','Roman_labels':'PASS','double_rendering':0,'overflow':0,'duplicate_DOM_IDs':0}})
qa['browser'].update({'contrast_light':min(x['contrast'] for x in browser['checks'] if x['theme']=='light'),'contrast_dark':min(x['contrast'] for x in browser['checks'] if x['theme']=='dark'),'screenshots':len(browser['screenshots']),'manual_screenshot_inspection':['BEFORE_STABLE_Whiston-20_light.png','BEFORE_STABLE_Whiston-20_dark.png','AFTER_Whiston-20_light.png','AFTER_Whiston-20_dark.png','AFTER_Whiston-3-8_light.png','AFTER_Whiston-3-15_light.png','AFTER_Whiston-5-3_dark.png','AFTER_Whiston-12_light.png'],'Coelacanth':'Unchanged; LJ Coelacanth / Georgia / Times New Roman / serif','notes':'Single attribution below title; no orig/reg double display'})
qa['integrity']={'canonical_start_files_identical':integrity['canonical']['files_checked'],'protected_worktree_files_identical':integrity['worktree']['protected_files'],'protected_XML_files_identical':integrity['worktree']['XML_files_unchanged'],'canonical_start_inventory_sha256':integrity['canonical']['original_inventory_sha256'],'canonical_same_files_final_inventory_sha256':integrity['canonical']['final_inventory_sha256'],'protected_worktree_before_inventory_sha256':integrity['worktree']['protected_original_inventory_sha256'],'protected_worktree_after_inventory_sha256':integrity['worktree']['protected_final_inventory_sha256'],'worktree_index_byte_identical':True,'canonical_raw_index_changed_externally':integrity['canonical_raw_index_changed_externally'],'canonical_index_clean':True,'both_external_packets_unchanged':True,'prior_certifications_unchanged':True,'no_staged_changes':True,'canonical_HEAD':integrity['canonical_HEAD'],'canonical_origin':integrity['canonical_origin'],'concurrent_canonical_commit':integrity['observed_concurrent_commit']}
qa['test_harness_qualification']='Corrected test expectations for metadata-relocated technical notes and existing paragraph-based Greek TOCs. Theme differential timing details recorded in presentation-correction/HARNESS_NOTES.md. Prior findings and diagnostics preserved; final validations rerun.'
qa['unrelated_existing_presentation_issue']='Early captures included intermediate global theme-transition values; settled light/dark captures are legible. No persistent index presentation issue remains.'
dump('QA.json',qa)
counts=qa['per_book'];table='\n'.join(f'| {b} | {n} | PASS | PASS |' for b,n in enumerate(counts,1));filetable='\n'.join(f'| `{x["path"]}` | `{x["presentation_before_sha256"]}` | `{x["presentation_after_sha256"]}` |' for x in fc['changes'])
note="Compiled from the chapter headings printed in the Auburn and Rochester edition of Whiston's translation (Alden & Beardsley, 1856). The arrangement as an index is editorial, not an original printed table of contents."
correction=f'''# Whiston compiled index: presentation correction — 9 October 2026

**GO for final human browser review.** Twenty indexes now have one attribution below their title, sentence-case headings and interval summaries, and left alignment. Every accepted historical reading remains recoverable exactly.

The registry supplied the ordinary note before the companion; the companion supplied the italic note after its title. Only the twenty Whiston registry note fields were cleared. The one companion note, immediately below Whiston’s chapter headings (compiled index), reads:

> {note}

Capitals came from literal transcription, not CSS. Justification was inherited from the ordinary pane and confirmed by before computed styles. All 256 headings, forty summary paragraphs and twenty book designations now use TEI choice/orig/reg. The exact accepted source string and inline source pointers remain in orig; a responsibility-marked case-only form is in reg. The complete 256-row ORIGINAL_DISPLAY_CONCORDANCE.json preserves both. SUMMARY_DISPLAY_CONCORDANCE.json covers forty summaries and twenty book labels. Roman chapter labels remain unchanged outside the choices.

The editorial policy preserves proper personal, place, ethnic and religious names, God, historical spelling, ligatures, punctuation, whitespace and source pointers. Common nouns are lowercased; sentence beginnings are capitalized. Named epithets retain Alexander/Herod the Great and Mount Sinai/Gerizzim. Judas Maccabeus was separately checked in interval material. No lexical replacement, spelling correction, abbreviation expansion or automatic CSS title case is used. All 256 display headings and forty summaries were reviewed. Exact originals remain authoritative; this display layer is not a new 1856 transcription.

Seven technical adjudication/footnote-pointer notes remain verbatim in source metadata with corresp where appropriate, rather than interrupting displayed headings. Their old parents and text are recorded in FILE_CHANGES.json. Bibliographical attribution, source-image locations and earlier edition variants remain in the TEI header and certification. No source heading, numeral or pointer was deleted.

Only CSS scoped to #english .source-contents tei-div[subtype="editorially-compiled-chapter-index"] selects visible reg / hidden orig, left alignment and a nonitalic attribution. Display:none prevents visible/accessibility double rendering of orig while preserving the original in XML. Coelacanth, font loading, font sizes, colours and spacing are inherited unchanged. No JavaScript was changed; no global TEI behavior was introduced.

Executed QA: {data['executed_checks']} data/schema/source checks; twenty companions and registry valid against the unchanged TEI All Relax NG schema; 256 exact originals, every case-only display, original inline evidence, labels/IDs, forty original summaries, all 39 old registry records and bytes. All 342 original audit and 106 final Book III manifest entries verify. III.8 has no terminal point; III.15 retains all approved punctuation and words; V.3 retains THEM. No other adopted source reading changed.

Forty browser displays (20 books × 2 themes) passed all visible heading/summary readings, one note correctly placed, hidden orig, Roman labels, no duplicate DOM IDs, no clipping/overflow and Coelacanth availability. Contents contrast is at least 13.93:1 in light and 11.85:1 in dark mode. All 39 earlier TOCs match exactly. Sixteen differential style checks cover Greek, Bamberg, Lodge and ordinary Antiquities/DEH/Apion text in both themes. Twenty copied-URL/reload/history/pane round trips, nineteen book changes and keyboard operation passed. Book XX before/after screenshots in both themes, III.8/III.15/V.3 details, and Books I/XII examples are retained here.

Full regressions rerun: 5,034 executable traditional language ranges plus 33 expected Book IX unavailable states; 257 Chapters / 1,432 Subchapters / 1,689 rows / 1,441 physical points; 2,456 I–VII Niese selections / 7,368 language comparisons; 198 Bamberg identities / 594 displays and all six different-position pairs; 1,441 Alignment units / 4,323 comparisons; 257 chapter-availability checks including nine zero-Subchapter chapters; 227 prefix-clipping checks; eighteen XI multi-span and two internal-citation checks; fourteen DEH/Bellum/Apion book configurations, fourteen Bellum Whiston/Lodge source-book configurations and five protected interaction configurations. The existing Book VI/XI behavior is retained. These results concern this isolated base, not the separately advanced VIII/X work.

All 122 pre-existing worktree XML files and all 593 protected tracked worktree files are SHA-256 identical. Worktree HEAD and Git index are unchanged; changes are unstaged and uncommitted. All 1,066 files from the canonical start inventory remain byte-identical. Canonical independently advanced from 2b07ac2 to ad3158b during this task, adding thirteen VIII/X certification files and updating its raw index; origin advanced too. This concurrent work was observed, not modified, reverted or integrated by this task. INTEGRITY_QA.json records it; this report does not claim the entire concurrent checkout/index remained byte-identical.

Earlier implementation reports, QA, scripts, screenshots and manifest are preserved under initial-integration/ (73 files). That subset excludes authority/ because the unchanged curated archive remains at the review root; its copied original manifest describes the initial full review, not the subset snapshot. Original human-browser findings, before-source files and before screenshots are preserved. The two external research packets and prior October 6/7 certification directories remain unchanged. Test-harness diagnostics are documented in HARNESS_NOTES.md.

No residual index presentation or textual issue was identified. Earlier quick captures included intermediate theme-transition styling; BEFORE_STABLE_BROWSER_QA.json and settled after captures distinguish those transient findings from the final state. No unrelated style change was made.

## Exact changed production paths and presentation hashes

| Path | Before correction SHA-256 | After correction SHA-256 |
|---|---|---|
{filetable}

Only these 22 production files changed. Review changes are recorded recursively by FILE_MANIFEST.json. Reproduce with validate.py, integrity.py, build_disposable.rb, built-site.test.cjs, css-scope.test.cjs, regression.test.cjs and its four gates, bamberg-regression.test.cjs, interaction-regression.test.cjs, then certify.py. The disposable build excludes review, disables disk caching, and omits the locally unavailable responsive-image plugin from temporary options only. Production config remains unchanged.
'''
put('presentation-correction/PRESENTATION_CORRECTION.md',correction)
put('REPORT.md',f'''# Whiston Antiquities compiled index — current implementation

9 October 2026. **GO for final human browser review.** All twenty indexes and 256 accepted Alden & Beardsley 1856 headings are implemented. The registry contains 59 records: 39 earlier records unchanged and 20 Whiston additions. This report includes the human-review presentation correction; initial results remain under presentation-correction/initial-integration/.

Worktree: `{R}`. Branch: codex/whiston-antiquities-compiled-index. Base HEAD: `{base['base']}`. Nothing is staged or committed. No merge, rebase, push or configuration change occurred. This task did not modify canonical; its independent later VIII/X commits and concurrent ad3158b certification are recorded in INTEGRITY_QA.json.

| Book | Headings | Exact source original | Both-theme display |
|---|---:|---|---|
{table}
| **Total** | **256** | **PASS** | **40 displays** |

The human editor chose the identified Auburn and Rochester: Alden & Beardsley, 1856 witness and the designation Whiston’s chapter headings (compiled index). The per-book arrangement is editorial, not an original printed TOC. One concise note now appears below the title. Historical uppercase strings remain in orig; case-only display readings are in reg. Forty interval summaries and twenty book designations receive the same reversible treatment; Roman labels remain unchanged. No claim is made about 1737 Contents or its precise heading text.

The duplicate came from registry plus companion notes. Only new Whiston registry notes were cleared. Capitals were literal source text; excessive spacing came from inherited justification. One narrowly scoped CSS addition selects the display reading and left-aligns the Whiston index. No JavaScript or navigation change was needed. Seven technical notes remain in source metadata. Greek, Bamberg and Lodge provenance behavior is unchanged.

QA passed {data['executed_checks']} data/schema/source checks; all twenty books in both themes, all 39 earlier TOCs exact, all 256 original/display pairs, sixteen out-of-scope typography comparisons, twenty URL/history/pane round trips, nineteen book changes and keyboard operation. No duplicate DOM IDs, double-rendering or overflow occurred. Contents text contrast: 13.93:1 light / 11.85:1 dark. All 342 original-audit and 106 supplementary manifest entries verify. III.8 has no terminal point; III.15 retains the certified full clause; V.3 preserves THEM.

Full regressions: 5,034 executable traditional ranges and 33 expected unavailable states; 2,456 I–VII Niese selections; 198 Bamberg identities / 594 displays and all six different-position pairs; 1,441 Alignment units; Book VI/XI and all DEH/Bellum/Lodge/Apion and interaction suites pass. All 122 existing XML files and 593 protected worktree files remain byte-identical. Exact counts and preservation digests are in QA.json.

Authorized production paths: twenty Whiston companions, assets/xml/source-contents.xml, and assets/css/tei.css. IMPLEMENTATION_MANIFEST.json records every path and source/output hash; presentation-correction/FILE_CHANGES.json records before/after correction hashes. No narrative XML, source packets, existing IDs/sameAs, structural registry, segmentation or other witness was modified.

See presentation-correction/PRESENTATION_CORRECTION.md for diagnosis, capitalization policy, complete concordances, hashes, screenshots, historical evidence and concurrent canonical state. Source metadata and unchanged curated archival text/manifests remain under authority/. No residual index presentation issue was identified in the settled theme checks. Stop for human browser review; do not commit or push.
''')
authority=(P/'initial-integration/SOURCE_AUTHORITY.md').read_text(encoding='utf-8').replace('The implementation introduces no additional normalization.','The initial implementation introduced no additional normalization. The authorized correction adds a separate case-only reg layer; exact accepted source readings remain in orig.')
put('SOURCE_AUTHORITY.md',authority+'\n## Presentation addendum — 9 October 2026\n\nSentence case is a modern display distinction, not a revised transcription. All 256 historical headings, forty summaries and twenty book designations remain exact in orig. Every original/display pair and responsibility is recorded in the companion and presentation concordances. No digital variant is adopted. Full printed evidence, bibliographical attribution and Book III variants remain in the unchanged authority archive. The registry delegates the one visible provenance note to each Whiston companion.\n')
ed=(P/'initial-integration/EDITORIAL_DECISIONS.md').read_text(encoding='utf-8');put('EDITORIAL_DECISIONS.md',ed+'\n## Authorized human-review presentation correction\n\n6. One note after the title, editorial sentence-case headings/summaries and left alignment were authorized. Exact 1856 originals remain in orig; case-only display forms are in reg. Punctuation, wording, spelling, source pointers, Roman labels and identities remain unchanged. III.8, III.15 and V.3 remain certified. The policy applies only to the Whiston compiled index.\n')
manifest={'date':'2026-10-09','scope':str(V),'excluded':['FILE_MANIFEST.json'],'entries':[{'path':p.relative_to(V).as_posix(),'bytes':p.stat().st_size,'sha256':h(p)} for p in sorted(V.rglob('*')) if p.is_file() and p != V/'FILE_MANIFEST.json']};manifest['entry_count']=len(manifest['entries']);dump('FILE_MANIFEST.json',manifest)
for x in manifest['entries']:assert (V/x['path']).stat().st_size==x['bytes'] and h(V/x['path'])==x['sha256']
print('CERTIFICATION_PASS',data['executed_checks'],'checks;',len(manifest['entries']),'verified manifest entries');print('MANIFEST_SHA256',h(V/'FILE_MANIFEST.json'))
