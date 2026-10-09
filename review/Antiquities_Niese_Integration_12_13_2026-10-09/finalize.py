"""Seal new integration evidence, keeping incoming source packets byte-identical."""
from preflight import *
from datetime import datetime,timezone

def manifest():
    files=[{'path':str(p.relative_to(ROOT)).replace(chr(92),'/'),'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size}
           for p in sorted(PACK.rglob('*')) if p.is_file() and p.name!='FILE_MANIFEST.json']
    save('FILE_MANIFEST.json',{'scope':'Integration-specific review additions only; incoming source files are listed separately in INCOMING_SCOPE.json',
        'file_count':len(files),'files':files,'self_excluded':True})

if __name__=='__main__':
    records=['INTEGRITY_QA.json','PRODUCTION_RESOLUTION.json','BUILD_RECORD.json','IX_CURRENT_CANONICAL_QA.json',
             'WHISTON_LAYOUT_QA.json','PROTECTED_BROWSER_QA.json','BOUNDED_BASELINE_EXCEPTIONS.json']
    for b in [12,13]:records += [f'books/{b}/IMPLEMENTATION_BROWSER_QA.json',f'books/{b}/RANGE_BROWSER_QA.json']
    for name in records:assert read(PACK/name)['result']=='PASS',name
    build=read(PACK/'BUILD_RECORD.json');merge=build['candidate_commit']
    assert textgit(ROOT,'rev-parse','HEAD')==merge
    for name in ['IX_CURRENT_CANONICAL_QA.json','WHISTON_LAYOUT_QA.json','PROTECTED_BROWSER_QA.json']+[f'books/{b}/{n}' for b in [12,13] for n in ['IMPLEMENTATION_BROWSER_QA.json','RANGE_BROWSER_QA.json']]:
        assert read(PACK/name)['build_record']==build,name
    assert textgit(SOURCE,'rev-parse','HEAD')==TIP and not textgit(SOURCE,'status','--porcelain')
    scope=read(PACK/'INCOMING_SCOPE.json');counts={}
    for b in [12,13]:
        browser=read(PACK/f'books/{b}/IMPLEMENTATION_BROWSER_QA.json')
        count=434 if b==12 else 433;intervals=433 if b==12 else 431
        assert browser['actual_select_events']==list(range(1,count+1))
        assert browser['projections']['identities']==count and browser['projections']['Latin_starts']==intervals
        counts[str(b)]={'identities':count,'Latin_intervals':intervals,'retained_starts':68 if b==12 else 83,
            'added_start_milestones':365 if b==12 else 348,'Greek_opening_markers':1,'Latin_end_markers':1 if b==12 else 0,
            'actual_chapter_subchapter_routes':len(read(PACK/f'books/{b}/RANGE_BROWSER_QA.json')['actual_ranges'])}
    coverage=read(PACK/'IX_CURRENT_CANONICAL_QA.json')
    assert coverage['baseline_total_selectable']==3448 and coverage['total_selectable']==4315
    assert sum(x['niese'] for x in read(PACK/'PROTECTED_BROWSER_QA.json')['antiquities'])==3448
    observations={
        'books/12/ranges_READER_248_dark.png':'Displaced dating is explicitly located in XII.246; independent Greek 248 and unchanged English context remain visible in dark theme.',
        'books/12/ranges_READER_434_light.png':'Final exact Latin interval ends at habuisset defunctus est., excluding the preserved subscription; independent Greek and English visible; Next disabled.',
        'books/13/ranges_READER_214_light.png':'Approved Itaque opening and reciprocal dating-in-212 qualification are displayed, with unchanged Greek 214 and broad English 213 context.',
        'books/13/ranges_READER_216_dark.png':'Specific no-independent-interval notice identifies assembly/warning correspondence; Greek 216 and English context remain independently displayed.',
        'books/13/ranges_READER_269_light.png':'Anonymous source paragraph produces the correct nonempty Latin 269 interval, Greek 269 and unchanged English 267 context.',
        'IX240-integration-dark.png':'Retained adjudicated Greek ἔσται δ᾽ and Latin et nullus openings remain visible with unchanged broader English context.',
        'screenshots/AFTER_Book-12_dark_1200.png':'Whiston compiled index has one attribution, Roman labels on the headings first lines, aligned hanging continuations and readable narrow dark-theme panes.'}
    save('VISUAL_REVIEW.json',{'result':'PASS','inspected_at_UTC':datetime.now(timezone.utc).isoformat(),
        'method':'Actual merged-build screenshots opened with view_image and visually examined; automated reports cover all requested states and both themes',
        'screenshots':[{'path':name,'sha256':sha((PACK/name).read_bytes()),'observed':text} for name,text in observations.items()]})
    records.append('VISUAL_REVIEW.json')
    production=[]
    for item in scope['production']:
        p=ROOT/item['path'];assert p.read_bytes()==git(ROOT,'show',f'{merge}:{item["path"]}')
        production.append({'path':item['path'],'merged_blob':textgit(ROOT,'rev-parse',f'{merge}:{item["path"]}'),
            'merged_sha256':sha(p.read_bytes()),'certified_source_blob':item['source_blob'],'certified_source_sha256':item['source_blob_sha256'],
            'resolution':'Canonical plus certified additions' if item['path']=='assets/js/renderTei.js' else 'Byte-identical certified source'})
    save('PRODUCTION_MANIFEST.json',{'tested_merge_commit':merge,'production_count':len(production),'files':production,'result':'PASS'})
    historical=['review/Whiston_Antiquities_Compiled_Index_2026-10-09/REPORT.md','review/Whiston_Niese_Combined_Integration_2026-10-09/REPORT.md',
                'review/Antiquities_Niese_Integration_09_2026-10-09/REPORT.md']
    save('REUSED_EVIDENCE_APPLICABILITY.json',{'reports':[{'path':p,'sha256':sha((ROOT/p).read_bytes())} for p in historical],
        'reused':'Closed philological decisions and source print collation; unaffected Whiston 20-book/59-TOC full source and typography certification',
        'blob_basis':'All unrelated canonical files and the entire incoming source packet retain exact committed blobs; Whiston companions, CSS and English narrative are unchanged',
        'fresh_checks':'867 actual new selections; complete new-book chapter/subchapter routes; all3448 existing Niese menu identities and traditional/Bamberg/Alignment/contents projections; all Bellum witnesses and affected works; fresh IX controls and targeted Whiston readings/layout/roundtrips',
        'result':'PASS'})
    save('CERTIFICATE.json',{'status':'COMBINED_INTEGRATION_VERIFIED_FOR_CANONICAL_FF_AND_NORMAL_PUSH',
        'starting_canonical':START,'starting_remote_directly_verified':START,'certified_source_tip':TIP,'frozen_source_base':BASE,
        'tested_merge_commit':merge,'merge_parents':textgit(ROOT,'show','-s','--format=%P',merge).split(),
        'full_source_history_preserved_as_merge_parent':True,'manual_production_conflicts':1,
        'incoming_production_files':scope['production_count'],'incoming_review_files':scope['review_count'],
        'books':counts,'batch':{'identities':867,'Latin_intervals':864,'retained_starts':151,'added_start_milestones':713,'Greek_openings':2,'Latin_end_markers':1},
        'actual_starting_canonical_selectable':3448,'actual_combined_selectable':4315,'source_historical_local_total':4024,
        'IX_preserved':{'identities':291,'Latin_intervals':232,'unavailable_Latin':list(range(51,110))},
        'no_pending_editorial_decisions':True,'byte_exact_recovery':'PASS','source_certificates_unchanged':True,
        'evidence_sha256':{n:sha((PACK/n).read_bytes()) for n in records},
        'promotion_policy':'Recheck current canonical and remote immediately; preserve and incorporate any advance in isolation; ff-only and normal origin/v2-development push; directly verify remote afterward',
        'preview_actions':'None; preview repository, export, deployment and domain changes are excluded'})
    (PACK/'REPORT.md').write_text(f'''# Antiquities XII–XIII — combined integration verified

The complete certified batch history has been merged with current canonical in isolation and passes new combined-build certification. Source branch and its historical certificates are unchanged. Canonical advancement uses fast-forward only and the explicitly authorized normal push to origin/v2-development; the final handoff supplies the directly verified resulting HEAD. No public-preview export, repository change, deployment or domain action is part of this integration.

Starting canonical and directly verified remote: `{START}`. Source: `{TIP}`, branch antiquities-niese-12-13; frozen base `{BASE}`. Tested merge: `{merge}`, with the complete source tip as its second parent. The first parent is the review-only provenance checkpoint descended from starting canonical. Integration branch: antiquities-niese-12-13-integration. Worktree: {ROOT}. Dedicated runtime: {RUNTIME}. Fresh QA reports record actual free origins and isolated browser profiles, with preferred port8913.

## Exact incoming and integration scope

The complete frozen-base-to-certified-tip delta contains **7 production + 386 review = 393 files**. INCOMING_SCOPE.json gives the full path list, statuses, Git blobs, SHA-256 hashes and source history. The entire 386-file incoming review packet, including source freezes, alternatives, qualifications, images and historical certificates, remains byte-identical. Integration-specific additions are review-only under {PACK}; FILE_MANIFEST.json records their exact count and hashes separately.

Production: assets/js/renderTei.js; Greek book-12.xml and book-13.xml; Latin book-12.xml and book-13.xml; niese/book-12.json and niese/book-13.json under assets/xml/antiquities. PRODUCTION_MANIFEST.json lists exact merged/source hashes. All six corpus/registry files equal the certified source tip. The single conflict was the reader identity map: retain canonical IX and add source XII/XIII beside VIII/X. The anonymous-paragraph and terminal-marker changes combined automatically. PRODUCTION_RESOLUTION.json proves the renderer equals current canonical plus precisely the three certified additions. Canonical IX paratext exclusions and unavailable-witness handling, all intervening Whiston work, English sources, CSS, other works and all other canonical files are preserved. No editorial conflict, narrative alteration, new ID or paragraph restructuring occurred.

## Reconciled coverage and closed decisions

| Book | Selectable identities | Latin intervals | Retained starts | Added starts | Greek openings | Latin end markers |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| XII | 434 | 433 | 68 | 365 | 1 | 1 |
| XIII | 433 | 431 | 83 | 348 | 1 | 0 |
| Batch | 867 | 864 | 151 | 713 | 2 | 1 |

Actual menus across all20 books in both builds establish **3,448 + 867 = 4,315 selectable identities**. The source's4,024 total is historical, from its pre-IX frozen baseline. IX retains291 identities,232 Latin intervals and the59 unavailable Latin identities51–109. The Latin end marker is counted separately from starts, intervals and identities.

XII.248 has no independent Latin interval: its dating correspondence survives within246. XII.249 still begins `nec non etiam eos`, retaining partial/reordered correspondence and the resumed247 ending; reciprocal246–249 notices and extents are intact. XIII.213 has no identifiable separate liberation-account correspondence in the reviewed transcription. XIII.214 begins `Itaque iudaei feliciter`, with dating material in212 and reciprocal distributed-correspondence notices. XIII.215 retains its reviewed interval. XIII.216 has no identifiable assembly/warning correspondence; neighbouring demolition is not reassigned. The visible inherited `[VI.vii.213]` label remains preserved without an executable213 claim, and the existing anonymous269 paragraph remains without an added XML ID. These statuses do not assert a common cause, physical loss or tradition-wide absence. Greek and English are independently accessible at all new selections. Alternatives and recommendation history remain in the unchanged source packets.

## New integration verification

Fresh complete Jekyll candidate and archived-current-canonical builds exited0 with all project Gemfile plugins and a pinned Ruby image. BUILD_RECORD.json identifies the tested commit/tree, code/data digest, actual static-output hashes, executable paths and logs. No source's earlier runtime was used as new-book certification.

All867 new identities were driven through actual selector events and compared with certified expected intervals and notices. Complete actual chapter/subchapter routes and broader views preserve source ordering and full three-witness markup. XII246–250, its final434 interval before the preserved subscription, XIII212–217 and anonymous269 pass. Deep links, opening/final endpoints, previous/next, Back/Forward, reload, panes, IDs, SVG assets and both themes pass; critical URLs also pass with uninstrumented production code. Saved integration screenshots were visually examined.

Fresh IX controls cover50–51,109–110,180–182,215–217,239–241 and endings, including the independently adjudicated240 cut and its complete ChapterXI/subchapterXI.3 views. Actual prior menu availability is unchanged. All3,448 protected current-canonical Niese identities and traditional/Bamberg/Alignment/contents projections match the baseline. Accepted VIII/X inherited-label and qualification controls include VIII367–369 and X101–102,108–109,150–151,276–277. Bellum1–7 under Whiston/Lodge, note/source switching, Apion and DEH pass.

The actual Whiston compiled-index and combined-integration reports were read. Unchanged broader source/layout evidence is reused by exact blobs; fresh checks cover the reported III.8,III.15,V.3 and XII/XIII/XX compiled indexes in both themes at1690/1200 widths:256 original/display pair checks and770 wrapped continuation checks. XII and XIII retain11/16 English index entries, and Contents→Niese→Contents round trips pass alongside IX. All existing source-contents projections match current canonical. The exact inherited Book-I Bamberg route with three apparatus links/two broken targets and unsupported I.1 error were reproduced in both builds; no additional browser, console or failed-request diagnostics occurred.

INTEGRITY_QA.json independently removes only the approved Latin additions and reverses only the two Greek opening additions, recovering the exact frozen working bytes without normalization or reserialization. All node/UTF-8 locators, complete physical narrative partitions, final extents, IDs and sameAs pass. English narrative bytes and all unrelated canonical blobs are preserved. CERTIFICATE.json binds the actual new evidence; the incoming source certificates remain historical and unchanged.

Reproduce fresh reader checks with the versioned book-browser.cjs (books12/13, --ranges, --protected), ix-protected.cjs, whiston-layout.cjs and baseline-exceptions.cjs against the recorded runtime builds. preflight.py and prepare_qa.py are one-time preparation records; use the final versioned harnesses for reruns rather than overwrite a frozen packet. PREPARATION_DIAGNOSTICS.md distinguishes the routine map conflict and corrected verification-helper pattern from passing final gates.
''',encoding='utf8',newline='\n')
    manifest()
    print('PASS final integration certificate; exact incoming7/386 scope; all867 selections; actual4315 coverage; ready for promotion gate')
