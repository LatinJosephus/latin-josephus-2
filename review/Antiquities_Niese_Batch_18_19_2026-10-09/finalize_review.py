"""Seal truthful per-book HOLD certificates, never certify unresolved books."""
from reconnaissance import *
from collections import Counter
from datetime import datetime,timezone

def main():
    def save_book(p,x):
        if '--batch-only' not in sys.argv:save(p,x)
    browser=json.loads((PACK/'SECURE_REVIEW_BROWSER.json').read_text(encoding='utf8'))
    prior=json.loads((PACK/'PROTECTED_REVIEW_BROWSER.json').read_text(encoding='utf8'))
    protection=json.loads((PACK/'PRODUCTION_PROTECTION_QA.json').read_text(encoding='utf8'))
    transition=json.loads((PACK/'TRANSITION_REVIEW_BROWSER.json').read_text(encoding='utf8'))
    assert browser['status']==prior['status']==protection['status']=='PASS'
    assert transition['status']=='PASS'
    assert len(browser['selections'])==745 and len(prior['selections'])==5231
    assert sum(r['Latin']=='SECURE_INTERVAL_PASS' for r in browser['selections'])==736
    scope=git('diff','--name-only',BASE).decode().splitlines()
    assert all(p.startswith('review/Antiquities_Niese_') for p in scope)
    commits=[dict(commit=line.split('\t')[0],subject=line.split('\t')[1]) for line in git('log','--reverse','--format=%H%x09%s',BASE+'..HEAD').decode().splitlines()]
    save(PACK/'SCOPED_COMMITS.json',dict(baseline=BASE,local_commits_before_final_seal=commits,
        final_seal_receipt='Obtain final seal commit and clean status with git log/status after committing this packet; a commit cannot contain its own hash.',
        branch='antiquities-niese-18-19',merge_push_publication=False))
    now=datetime.now(timezone.utc).isoformat();certificates=[]
    for b in [18,19]:
        d=packet(b);rows=json.loads((d/'IDENTITIES.json').read_text(encoding='utf8'))
        plan=json.loads((d/'APPROVED_SECURE_MARKER_PLAN.json').read_text(encoding='utf8'))
        proof=json.loads((d/'INDEPENDENT_REVIEW_PRESERVATION_QA.json').read_text(encoding='utf8'))
        expected=json.loads((d/'REVIEW_EXPECTED_INTERVALS.json').read_text(encoding='utf8'))
        select=[r for r in browser['selections'] if r['book']==b];views=[r for r in browser['views'] if r['book']==b]
        qa=dict(book=b,scope=browser['scope'],status='PASS_REVIEW_HARNESS_ONLY',
            selections=select,containing_views=views,legacy_ranges=browser['books'][str(b)]['legacyRanges'],
            interactions=[r for r in browser['interactions'] if r['book']==b],
            Greek_exact_selections=len(select),English_context_selections=len(select),
            secure_Latin_intervals=sum(r['Latin']=='SECURE_INTERVAL_PASS' for r in select),
            uncertified_Latin_intervals=[r['number'] for r in select if r['Latin']!='SECURE_INTERVAL_PASS'],
            errors=browser['errors'],book_transitions=transition['transitions'],sources=transition['sources'],themes=[r for r in transition['themes'] if r['book']==b],prototype_registry=info(d/'REVIEW_IDENTITY_REGISTRY.json'),
            prototype_Latin=info(d/'review-output/Latin.xml'),prototype_renderer=info(PACK/'REVIEW_RENDERER.js'),
            production_files_changed=False,final_book_reader_certified=False)
        save_book(d/'SECURE_REVIEW_BROWSER.json',qa)
        frozen=json.loads((d/'BASELINE.json').read_text(encoding='utf8'))
        cert=dict(book=b,status='HOLD_HUMAN_EDITORIAL_CHOICES_REQUIRED',certified=False,ready_for_integration=False,
            utc=now,baseline=BASE,worktree=str(ROOT),branch='antiquities-niese-18-19',runtime=str(RUNTIME),
            complete_primary_source_review=True,Greek_identities=len(rows),Latin_identities_individually_reviewed=len(rows),
            Greek_explicit_starts=len(frozen['explicit_Greek_numbers']),Greek_implicit_opening_reused_anchor=rows[0]['Greek_physical_start'],
            Latin_review_implementation=dict(scope='REVIEW_OUTPUT_ONLY',retained_numeric_starts=len(plan['retained_starts']),
                reused_existing_physical_starts=len(plan['reused_physical_starts']),new_milestones=len(plan['markers']),
                represented_approved_starts=len(plan['retained_starts'])+len(plan['reused_physical_starts'])+len(plan['markers']),
                secure_independently_compared_intervals=qa['secure_Latin_intervals'],approved_unavailable_identities=plan['approved_unavailable_sections'],
                absence_claims_pending=[216,217] if b==18 else [],
                correspondence_counts=dict(Counter(r['candidate']['correspondence'] for r in rows)),
                actual_production_additions=0,production_availability_enabled=False),
            pending_sections=plan['pending_sections'],uncertified_intervals=qa['uncertified_Latin_intervals'],
            human_decisions_received=False,
            exact_byte_inverse_of_candidate_XML=proof['independent_exact_byte_reversal'],
            source_Latin_sha256=proof['source_sha256'],candidate_Latin_sha256=proof['candidate_sha256'],
            all_source_bytes_including_Greek_English_protected=True,protected_production_files=protection['production_files'],
            independent_current_physical_locator_checks=len(proof['structural_locators']),
            review_browser=dict(Greek=qa['Greek_exact_selections'],English=qa['English_context_selections'],
                Latin_secure=qa['secure_Latin_intervals'],all_Latin_certified=False,containing_views=len(views),
                legacy_chapter_ranges=len(qa['legacy_ranges']),all_prior_5231_selections_identical=True),
            final_production_browser_tests='NOT_RUN: production enablement awaits human choices; review harness is explicitly distinct',
            authority_records='PRIMARY_REVIEW_COMPLETE.json; PRINTED_SOURCES.json; FROZEN_*_RECORDS.json; STRUCTURAL_RECORDS.json',
            case_packets=['CASE_007.md','CASE_094.md','CASE_216_217.md'] if b==18 else ['CASE_188.md'],
            governing_hold='Section 5: Request ONLY that specific human editorial choice. After scholarly gates close, apply minimal reversible production additions.',
            no_merge_push_preview_export_or_deployment=True)
        save_book(d/'CERTIFICATE.json',cert);certificates.append(cert)
        files=[info(p) for p in sorted(d.rglob('*')) if p.is_file() and p.name!='FILE_MANIFEST.json']
        save_book(d/'FILE_MANIFEST.json',dict(scope='THIS_BOOK_REVIEW_PACKET_ONLY',files=files,self_hash_excluded=True))
    rows18,rows19=certificates
    report=f'''# Antiquities XVIII–XIX: complete review, editorial hold

**HOLD — neither book is finally certified or ready for canonical integration.** Complete primary-source review is finished. A concrete, reversible implementation of every secure routine Latin cut has passed independent preservation checks and local browser comparison in an explicitly labelled review harness. Four focused human choices affecting five identities remain pending. No choice has been inferred from silence.

## Pinned source and scope

- Immutable baseline: `{BASE}`. Assigned branch: `antiquities-niese-18-19`.
- Worktree: `{ROOT}`.
- Disposable runtime: `{RUNTIME}`; local QA port 8918, isolated headless browser profiles.
- At reconnaissance canonical HEAD, tracking tip and directly read remote tip were `65b3256fe202a06e33a59aa2d1dcbd7107358271`. Its delta from the preferred baseline affected only two Whiston-layout stylesheet lines; assigned XML, registries, controls and renderer matched. `BASELINE.json` records the choice and original status.
- All {protection['production_files']} protected production paths retain their frozen hashes. Production XML, renderer, controls, availability and English are unchanged. All task changes are confined to the three assigned review directories. Other worktrees and canonical were read-only.

## Scholarly review and implementation figures

| Gate / actual review-output figure | XVIII | XIX |
|---|---:|---:|
| Individually reviewed Greek/Niese identities | 379 | 366 |
| Individually reviewed Latin identities | 379 | 366 |
| Existing explicit Greek numerals retained | 378 | 365 |
| Greek implicit opening, existing narrative anchor reused | 1 | 1 |
| Latin numeric starts retained | 0 | 0 |
| Existing Latin physical starts reused declaratively | 61 | 46 |
| New approved Latin milestones in review XML | 314 | 319 |
| Positive approved Latin starts in review harness | 375 | 365 |
| Secure Latin intervals independently compared in browser | 372 | 364 |
| Approved unavailable Latin identities | 0 | 0 |
| Production marker additions / new public selections | 0 | 0 |

The zero retained-numeric-start count reflects these actual Latin files, which contain no inherited narrative `<num>` starts. Existing paragraph IDs and literal manuscript Roman labels are preserved; 107 exact current structural points are reused rather than duplicated. The reviewed unavailable proposal for XVIII.216–217 is **pending**, not an approved absence claim. No gap, supplied narrative or witness correction was introduced.

Controlling print is Niese, *Flavii Iosephi Opera*, IV, Berlin: Weidmann, 1890. The actual scan title, XVIII body PDF154–223 (printed140–209), XIX body PDF225–287 (printed211–273), contents, complete final tails and transition to XX were visually examined. PDF page = printed page +14 in this body. Every identity carries its own evidence image/page and full Greek/Latin review record. OCR was used only for finding pages. Independent Loeb control is the supplied Feldman IX edition (1965), with the relevant physical pages retained for material cases; frozen October4–7 records remain source-qualified and hash-verified.

The Greek book-extent notices remain before narrative opening anchors, at current Greek Unicode offsets34 and48 respectively. Source-only contents, nested containers, annotations, spelling, punctuation, whitespace, manuscript images and all existing IDs/sameAs remain literal. XVIII.63–64 and116–119 were reviewed individually without harmonization. XIX.366 includes its whole continuation through printed273; no text or marker was borrowed from XX.

## Focused editorial choices

| Case | Recommendation | Consequence |
|---|---|---|
| [XVIII.7](../Antiquities_Niese_BookXVIII_2026-10-09/CASE_007.md) | A: start at `et supra quam dici potest` | Keeps the adverbial introduction with its Latin sentence; qualify the compressed relationship to Greek6–7. |
| [XVIII.94](../Antiquities_Niese_BookXVIII_2026-10-09/CASE_094.md) | B: start at `Transacta uero festiuitate` | Keeps the transmitted relative clause with the candelabrum in93; qualify garment/candelabrum differences. |
| [XVIII.216–217](../Antiquities_Niese_BookXVIII_2026-10-09/CASE_216_217.md) | A: both unavailable as independent Latin intervals | Full Latin-witness examination finds no independent corresponding passage; preserve Greek/English and cause-neutral notices, without inserting a gap. |
| [XIX.188](../Antiquities_Niese_BookXIX_2026-10-09/CASE_188.md) | A: start at `Erant enim cohortes` | Keeps `qui senatui consentiebant` with its grammatical antecedent in187; qualify the compressed watchword/troops correspondence. |

Each packet includes full neighbouring Greek and Latin, exact mixed-content/Unicode/UTF-8 candidates, print evidence, alternative consequences and recommendation. All proposals and prior review history remain preserved. Governing §5 explicitly requires the specific human editorial choice for materially unresolved alternatives and says production application follows closure of the scholarly gates. Those choices prevent final certification of **both** books.

## Preservation and actual browser evidence

Two separate inversion implementations recover the exact frozen Latin bytes from the candidate output. They agree without trusting each other's shifted coordinates. Existing IDs/sameAs, paragraphs/chapter topology, notes/TOCs, image/page/column markers and all old milestones pass tree checks. All462 source-qualified structural locators retain their exact coordinates and text.

| Latin file | Baseline SHA-256 | Candidate-review SHA-256 |
|---|---|---|
| XVIII | `{rows18['source_Latin_sha256']}` | `{rows18['candidate_Latin_sha256']}` |
| XIX | `{rows19['source_Latin_sha256']}` | `{rows19['candidate_Latin_sha256']}` |

The review reader performs **745 actual selections**: all745 Greek exact ranges and English contextual witnesses pass, and736 independently secure Latin intervals pass. The nine uncertified Latin interval selections are XVIII6,7,93,94,215,216,217 and XIX187,188; pending cuts also affect their adjoining extents. They were not passed off as certified intervals. Source-pane notices in the harness explicitly say the editorial choice is pending.

All267 actual containing views (154 traditional/subchapter/Bamberg +109 alignment +4 Book/contents) match the frozen baseline in all three languages. All29 legacy chapter ranges (21 XVIII /8 XIX), with87 language-range comparisons, preserve their old complete endpoints. Traditional counts remain9/9; subchapters57/52; Bamberg19/8. Reload, direct URLs, previous/next, history, panes and settled light/dark themes pass for the named section cases. Actual XVII→XVIII→XIX→XX book-selector transitions pass, including the ordinary Book-view fallback; each XVIII/XIX language retains its one available source, so its source selector is intentionally hidden. Source switching between Whiston and Lodge is separately covered in protected Bellum routes. Section DOM IDs are unique; the Niese selector has its associated label and previous/next accessible names. The baseline full Book views already contain a duplicate `annotations` ID; it is recorded explicitly and remains identical in the review harness, with no new duplicate introduced.

XVIII257 preserves traditional VIII at the paragraph start and Bamberg `XVIIII` later at Greek153/Latin156/English187. XIX292 preserves traditional VI at the paragraph start and literal Bamberg `V` at Greek146/Latin133/English153. Current-byte proof and all relevant complete containing views agree; shared Niese numbers never collapse the physical identities.

The prototype's generic addition resolves declared per-language starts through the current source-qualified locator resolver. No XVIII/XIX boundary conditional was added. Its registry preserves **all original milestone types**, including unqualified manuscript-image milestones, when resolving old ordinal edges. An initial chapter-only filter failed a real XVIII containing-view comparison; that failed prototype was corrected and superseded before the final passes. All5231 prior selectable identities were then independently selected in two actual browser tabs and compared against the pinned baseline, with identical language texts, paragraph identities, notes and absence states. Protected-work replays cover prior IX/XII–XV and VIII/X, the XV endpoint class, XVII/XX, Bellum Cardwell/Whiston/Lodge configurations, DEH and Contra Apionem. The three inherited Book-I apparatus links and their two404 targets are identical in both readers; unsupported I.1 reproduces the exact known null-querySelector exception in both and is excluded from selectable totals. These are separately recorded known baseline defects, with no new reader error excused.

**This is review-harness evidence, not final production certification.** The review site overlays the explicitly frozen and successfully built baseline with the candidate data/renderer; `REVIEW_HARNESS_PROVENANCE.json` distinguishes that setup from a final build. After human choices, apply final byte manifests and registries, build the actual enabled production reader, rerun all745 complete Latin/Greek/context selections plus all relevant containing/interaction checks, and seal each book independently.

The unchanged production source has5231 selectable identities. The requested5976 =5231+745 is the future local total after both books are properly enabled and certified. It is not present production/public availability and does not include provisional XI/XVI–XVII work.

## Durable artifacts and coordinator handoff

- Per-book `CERTIFICATE.json` files explicitly say `HOLD_HUMAN_EDITORIAL_CHOICES_REQUIRED`, `certified:false`, `ready_for_integration:false`.
- Authority/baseline ledgers, full printed evidence, 379/366 identity/candidate rows, decision history/cases, secure marker plans, exact inverse manifests, independent preservation tests and per-book browser results reside in the respective assigned directories.
- `PRODUCTION_PROTECTION_QA.json` lists every protected production path/hash. Per-book and batch `FILE_MANIFEST.json` list all affected review paths/hashes. `REVIEW_RENDERER.patch` is the concrete generic-support proposal. `SCOPED_COMMITS.json` records local checkpoint provenance before this final seal; obtain the seal's own hash from Git.
- Primary-review checkpoints are separately committed for XVIII and XIX. The routine implementation and final HOLD packet have separate local checkpoints. Final clean status is verified after sealing the packet.

No canonical integration, merge, push, preview export, deployment, publication or domain change occurred. Integration must remain on hold until the four requested human choices arrive and the final production certification is completed.
'''
    (PACK/'REPORT.md').write_text(report,encoding='utf8',newline='\n')
    save(PACK/'FILE_MANIFEST.json',dict(scope='BATCH_REVIEW_PACKET_ONLY',self_hash_excluded=True,
        files=[info(p) for p in sorted(PACK.rglob('*')) if p.is_file() and p.name!='FILE_MANIFEST.json' and '__pycache__' not in p.parts]))
    print('Two truthful HOLD certificates; complete review and secure implementation evidence sealed.')
if __name__=='__main__':main()
