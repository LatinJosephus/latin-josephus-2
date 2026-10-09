from pathlib import Path
import json,hashlib
V=Path(__file__).resolve().parent;R=V.parents[1];L=V/'layout-correction'
def read(n):return json.loads((V/n).read_text(encoding='utf-8'))
def dump(n,d):(V/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
layout=read('layout-correction/LAYOUT_QA.json');before=read('layout-correction/BEFORE_QA.json');integrity=read('layout-correction/INTEGRITY_QA.json');contents=read('layout-correction/CONTENTS_REGRESSION_QA.json');scope=read('layout-correction/CSS_SCOPE_QA.json');data=read('DATA_QA.json');reg=read('REGRESSION_BROWSER_QA.json');bam=read('BAMBERG_BROWSER_QA.json');align=read('ALIGNMENT_ALL_QA.json');follow=read('FOLLOWUP_GATE_QA.json');multi=read('XI_MULTISPAN_GATE_QA.json');bellum=read('PROTECTED_SOURCE_GATE_QA.json');interact=read('INTERACTION_QA.json');change=read('layout-correction/FILE_CHANGES.json');baseline=read('layout-correction/BASELINE.json')
for q in [layout,before,integrity,contents,scope,data,bam,align,follow,bellum,interact]:assert q['result']=='PASS'
assert layout['entryChecks']==1024 and len(layout['checks'])==80 and layout['uniqueEntries']==256
assert reg['traditional']['executable']==5034 and reg['traditional']['unavailable']==33 and not reg['errors']
assert sum(x['selections'] for x in reg['niese'].values())==2456;assert bam['division_identities']==198 and bam['language_displays']==594
assert sum(x['alignment_units'] for x in align['checks'])==1441;assert len(follow['availability'])==257 and len(follow['prefixChecks'])==227;assert len(multi['checks'])==18
assert all(multi[x]=='PASS' for x in ['canonical_membership_no_duplication','interpolations_retained','disclosure_and_witness_link','book_and_alignment_views_vs_base'])
assert len(bellum['checks'])==14 and len(interact['checks'])==5
assert h(R/'assets/css/tei.css')==change['after_sha256']
assert all(h(R/p)==s['sha256'] for p,s in baseline['worktree_files'].items() if p!='assets/css/tei.css')
summary={'result':'PASS','date':'2026-10-09','production_files_changed':['assets/css/tei.css'],'XML_changes':0,'JavaScript_changes':0,'registry_changes':0,'books':20,'headings':256,'themes':['light','dark'],'viewports':[1690,1200],'complete_displays':80,'entry_geometry_checks':1024,'wrapped_entry_displays':layout['wrappedEntries'],'continuation_line_alignment_checks':layout['wrappedLineChecks'],'gap_px':{'minimum':min(e['gap'] for x in layout['checks'] for e in x['entries']),'maximum':max(e['gap'] for x in layout['checks'] for e in x['entries'])},'heading_width_px':{'minimum':min(x['itemWidth'] for x in layout['checks']),'maximum':max(x['itemWidth'] for x in layout['checks'])},'single_provenance':'PASS','book_titles_and_intervals_unchanged':'PASS','all_original_and_regularized_readings_preserved':256,'Roman_labels_preserved':256,'registry_records_unchanged':59,'all39_other_TOC_readings_exact':'PASS','out_of_scope_style_comparisons':16,'contents_URL_history_pane_roundtrips':20,'contents_book_switches':19,'keyboard':'PASS','data_schema_checks':data['executed_checks'],'integrity_checks':integrity['executed_checks'],'protected_XML_files':integrity['protected_XML_files'],'protected_source_files':integrity['protected_worktree_files'],'canonical_files_unchanged':integrity['canonical_files'],'canonical_HEAD':integrity['canonical_HEAD'],'worktree_HEAD':integrity['worktree_HEAD'],'indices_byte_identical':True,'traditional_ranges':5034,'traditional_unavailable':33,'Niese_I_VII_selections':2456,'Bamberg_identities':198,'Bamberg_language_displays':594,'Alignment_units':1441,'cross_work_book_configurations':len(reg['crossWork']),'Bellum_source_book_configurations':14,'interaction_configurations':5,'duplicates_overlap_clipping_overflow':0,'prior_evidence_preserved':True,'staged_or_committed':False,'residual_issues':[]}
dump('layout-correction/QA.json',summary)
qa=read('layout-correction/prior-certification/QA.json');qa['final_layout_correction']=summary;qa['final_layout_integrity']={k:integrity[k] for k in ['original_protected_inventory_sha256','final_protected_inventory_sha256','XML_before_inventory_sha256','XML_after_inventory_sha256']};dump('QA.json',qa)
imp=read('layout-correction/prior-certification/IMPLEMENTATION_MANIFEST.json');row=next(x for x in imp['production_changes'] if x['path']=='assets/css/tei.css');row['prior_presentation_sha256']=row['after_sha256'];row['after_sha256']=change['after_sha256'];row['final_layout_correction']='Whiston-only alternating label/item grid; .55em gap and hanging text-column alignment; book/interval blocks unchanged'
for x in imp['production_changes']:assert h(R/x['path'])==x['after_sha256']
imp['final_layout_correction']=summary;dump('IMPLEMENTATION_MANIFEST.json',imp)
record=f'''# Final Whiston chapter-entry layout correction — 9 October 2026

**GO for final human visual approval.** This correction changes only assets/css/tei.css in production. No XML, registry, JavaScript, source reading, font declaration, navigation or canonical file changed. Work remains unstaged and uncommitted on codex/whiston-antiquities-compiled-index at a48021588e0840330388a6055a97bd0f7c2cf827.

Actual DOM inspection found alternating tei-label and tei-item elements under tei-list[type="simple"]. Labels were inline; items were block with .6em vertical margins. The block item therefore forced its heading to a new line. DOM_BEFORE_QA.json preserves the computed positions/styles.

Three new CSS selectors apply only beneath #english .source-contents tei-div[subtype="editorially-compiled-chapter-index"] > tei-list. The list uses a max-content numeral column and minmax(0,1fr) text column. Right-aligned numerals have a .55em gap; a .6em row gap replaces item vertical margins. Continuations remain in the heading column. Titles, provenance and interval paragraphs are outside the grid and stay on their existing lines. There is no global label/item change or JavaScript change. Coelacanth, left alignment, sentence case, font sizes and theme colours are unchanged.

Before CSS SHA-256: `{change['before_sha256']}`.
After CSS SHA-256: `{change['after_sha256']}`.
All previous CSS bytes remain as the prefix; FILE_CHANGES.json records the sole production change. All 143 XML files (including all twenty Whiston companions and the registry), 614 protected source files and {integrity['canonical_files']} canonical files remain byte-identical. Both Git indices and both HEADs are unchanged. Canonical ad3158b was read only; no other worktree was touched.

Executed layout QA: twenty books × two themes × two widths = **80 complete displays**, **1,024 numeral/heading geometry checks**, **{layout['wrappedEntries']} wrapped entry displays** and **{layout['wrappedLineChecks']} continuation-line alignment checks**. All numerals share the heading’s first line; all continuations align with the text. The gap measures 8.796875 px; text columns measure 272–344 px. No overlapping rows, duplicate IDs, overflow or clipping occurred. Roman order and all original/display readings remain exact. One provenance note remains visible. Book III/XII title/interval geometry and styles compare identically before/after in both themes and widths.

The full contents suite passed forty Whiston displays and all fifty-nine records (all thirty-nine earlier source lists exact), twenty URL/reload/history/pane round trips, nineteen book switches and keyboard operation. Sixteen differential style comparisons prove Greek, Bamberg, Lodge and ordinary Antiquities/DEH/Apion typography unchanged. Established source/schema checks passed 1,052/1,052; final integrity and geometry cross-checks passed {integrity['executed_checks']}/{integrity['executed_checks']}.

Full relevant regressions were rerun: 5,034 traditional executable ranges and 33 expected unavailable states; 2,456 I–VII Niese selections; 198 Bamberg identities / 594 displays and all six different-position pairs; 1,441 Alignment units; all 257 availability and 227 clipping checks; eighteen XI multi-span and two generic internal-citation checks; fourteen DEH/Bellum/Apion book configurations, fourteen Bellum Whiston/Lodge configurations and five protected interaction configurations. Book VI boundaries, Book XI witness order and missing-text policy remain unchanged.

Thirty-two focused before/after screenshots cover Books III and XII, both themes and widths, including long-heading details. Earlier approved presentation evidence is unchanged under presentation-correction/. Prior root reports, QA, scripts, manifest and all twenty-six root screenshots are preserved under prior-certification/. Its copied manifest describes the full earlier packet, not just that subset. No source-audit packet or archival source data was rewritten.

Reproduction: build_disposable.rb into the disposable site; layout-qa.test.cjs (use --before with the pre-patch build for baseline captures); layout-contents-regression.test.cjs; layout-css-scope.test.cjs; validate.py; existing regression.test.cjs and its four gates; bamberg-regression.test.cjs; interaction-regression.test.cjs; layout-validate.py; certify-layout.py. Test-only responsive probes and corrected administrative XML-count expectations are documented in HARNESS_NOTES.md. No unexecuted test is marked passed. Existing temporary-build qualifications are unchanged; production configuration and generated site files were not edited.

No residual issue or scholarly decision remains for this layout correction. Stop for final human visual approval. No commit, merge or push occurred.
'''
(L/'RECORD.md').write_text(record,encoding='utf-8')
prior=(L/'prior-certification/REPORT.md').read_text(encoding='utf-8');add=f'''

<!-- FINAL_WHISTON_LAYOUT_2026-10-09 -->

## Final chapter-entry layout correction — 9 October 2026

**GO for final human visual approval.** Numerals now share their headings’ first line, with a modest gap and hanging continuations. Only the stylesheet changed in production during this correction. Original/reg readings, Roman numbering, book titles, interval summaries, registry and navigation are untouched; no JavaScript was needed.

All 256 entries passed at both themes and wide/narrow three-pane widths: eighty displays, 1,024 pair checks and {layout['wrappedLineChecks']} continuation-line checks. All fifty-nine TOCs, URL/history/pane behaviour and relevant full navigation/cross-work regressions pass. All 143 XML files, 614 protected source files, canonical and Git indices are unchanged. Earlier evidence is preserved; exact hashes and Book III/XII before/after screenshots are in layout-correction/RECORD.md, FILE_CHANGES.json and QA.json. No residual issue was found. Changes remain unstaged and uncommitted.
'''
(V/'REPORT.md').write_text(prior.rstrip()+add,encoding='utf-8')
manifest={'date':'2026-10-09','scope':str(V),'excluded':['FILE_MANIFEST.json'],'entries':[{'path':p.relative_to(V).as_posix(),'bytes':p.stat().st_size,'sha256':h(p)} for p in sorted(V.rglob('*')) if p.is_file() and p != V/'FILE_MANIFEST.json']};manifest['entry_count']=len(manifest['entries']);dump('FILE_MANIFEST.json',manifest)
for x in manifest['entries']:assert h(V/x['path'])==x['sha256'] and (V/x['path']).stat().st_size==x['bytes']
print('FINAL_LAYOUT_CERTIFICATION_PASS',len(manifest['entries']),'manifest entries');print('CSS_SHA256',h(R/'assets/css/tei.css'));print('MANIFEST_SHA256',h(V/'FILE_MANIFEST.json'))
