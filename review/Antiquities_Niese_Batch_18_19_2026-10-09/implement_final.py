"""Apply the human's A/B/A/A adjudication to the isolated XVIII/XIX source.

Earlier HOLD records are archived verbatim. No other workspace is written.
"""
from reconnaissance import *
from mixed_mapper import Book
from prepare_secure_plan import validate, physical_points
from copy import deepcopy
from datetime import datetime, timezone

HOLD = '1938fa015ec9273ed396754a362f25f14ae6c6f8'
HISTORY = 'history/pre-adjudication-1938fa0'
APPROVAL = '''# Human editorial adjudication — 2026-10-10

Adopt the four recommended decisions: A, B, A, A.
All four editorial holds are now closed.

1. XVIII.7 — A APPROVED. Begin the independent Latin interval at:
et supra quam dici potest
Retain the transmitted Latin wording and the appropriate preceding material in XVIII.6. Preserve any correspondence qualification established in CASE_007.md.

2. XVIII.94 — B APPROVED. Begin the independent Latin interval at:
Transacta uero festiuitate
Preserve the immediately preceding material under its established correspondence. Record the rationale and adjacent extents from CASE_094.md.

3. XVIII.216–217 — A APPROVED. Represent both identities as having no independent Latin interval in the present Bamberg transcription.
This is an editorial representation of the evidence established by the complete-book survival review. It is not a declaration that the original Latin translation necessarily lacked the material, nor evidence of a particular scribal, exemplar or physical-loss mechanism.
Preserve any wording elsewhere in the transcription that corresponds partially or indirectly to these sections, together with the relevant qualifications and cross-references.
Do not manufacture Latin starts, assign neighbouring text to these sections merely to supply an interval, insert conjectural text, or add an automatic physical-gap claim.
Both Greek Niese identities and their English context must remain independently selectable. Their Latin panes must display an accurate, specific availability notice.

4. XIX.188 — A APPROVED. Begin the independent Latin interval at:
Erant enim cohortes
Preserve the preceding Latin under its established identity, and record the section-boundary reasoning in CASE_188.md.

Implementation authorization: Proceed through the existing governing WorkBot instructions to implement and independently certify Books XVIII–XIX. Preserve source wording, Unicode, punctuation, paragraph order, existing IDs, sameAs relationships, inherited labels, traditional/Bamberg chapter structures and English bytes. Retain the separately certified physical distinction at XVIII.257 and XIX.292. Actual baseline: 9527578f361d48adb3094110254e627292bca2c5. Expected local total: 5,976 selectable identities. Continue on antiquities-niese-18-19. Do not merge, push, publish or alter the public preview. Do not interfere with WorkBot XI.

This transcript preserves the substantive approval and constraints from the human's current message. Exact earlier alternatives, evidence, coordinates and HOLD state are preserved verbatim in the pre-adjudication archive and at the pinned HOLD commit.
'''

def main():
    assert git('branch','--show-current').decode().strip()=='antiquities-niese-18-19'
    assert git('rev-parse','HEAD').decode().strip()==HOLD
    assert not (PACK/'ADJUDICATION_APPROVAL.json').exists()
    timestamp=datetime.now(timezone.utc).isoformat()
    archives=[]
    for directory in [packet(18),packet(19),PACK]:
        dest=directory/HISTORY;dest.mkdir(parents=True,exist_ok=False)
        names=[p for p in directory.iterdir() if p.is_file() and p.suffix in ['.json','.md']]
        for p in names:
            shutil.copyfile(p,dest/p.name)
            archives.append(dict(path=str(p.relative_to(ROOT)),archive=str((dest/p.name).relative_to(ROOT)),sha256=sha(p.read_bytes())))
    (PACK/'ADJUDICATION_USER_APPROVAL_2026-10-10.txt').write_text(APPROVAL,encoding='utf8',newline='\n')
    save(PACK/'ADJUDICATION_ARCHIVE.json',dict(hold_commit=HOLD,archived_files=archives,status='VERBATIM_HOLD_HISTORY_PRESERVED'))
    approvals=[]
    for b in [18,19]:
        d=packet(b);rows=json.loads((d/'IDENTITIES.json').read_text(encoding='utf8'))
        history=json.loads((d/'DECISION_HISTORY.json').read_text(encoding='utf8'))
        for file,choice,numbers in ([('CASE_007','A',[7]),('CASE_094','B',[94]),('CASE_216_217','A',[216,217])] if b==18 else [('CASE_188','A',[188])]):
            original=(d/(file+'.json')).read_bytes();case=json.loads(original)
            selected=next(c for c in case['choices'] if c['choice']==choice)
            prior={str(n):deepcopy(rows[n-1]['candidate']) for n in numbers}
            for n in numbers:
                c=rows[n-1]['candidate'];c['approved']=True;c['adjudication']=dict(choice=choice,case=file+'.json',timestamp=timestamp,authority='Human approval in current chat, 2026-10-10')
                c['reason']=case['reason'];c['correspondence']='PARTLY_SURVIVING' if n in [94,188] else 'OVERLAPPING_CORRESPONDENCE'
                if 'locator' in selected:
                    c['locator']=deepcopy(selected['locator']);c['incipit']=selected['phrase']
                else:
                    c['locator']=None;c['available']=False;c['correspondence']='NO_INDEPENDENT_LATIN_INTERVAL_IN_PRESENT_TRANSCRIPTION'
                    subject='Tiberius’s astrology and Galba' if n==216 else 'the general account of reliance on divination'
                    c['note']=f'No independent Latin interval for Antiquities XVIII.{n} ({subject}) survives in the present Bamberg transcription. Latin 215 passes directly to 218. The succession-omen and foreknowledge wording remains at Latin 218 as indirect context; it is not assigned a second interval here. Greek and Whiston English context remain independently available. This representation does not establish absence from the original Latin translation or any scribal, exemplar or physical-loss cause.'
                    c['cross_references']=[215,218]
            for key,note in case.get('proposed_notes',{}).items():
                c=rows[int(key)-1]['candidate'];c['note']=note
                if c['correspondence']=='PRESENT':c['correspondence']='OVERLAPPING_CORRESPONDENCE'
            if b==18 and numbers==[216,217]:
                rows[214]['candidate']['note']='The present Latin passes directly from this account to the remorse narrative at 218. Sections 216–217 have no independent Latin intervals here; no cause of the difference is established.'
                rows[217]['candidate']['note']='The succession-omen and foreknowledge wording survives in this Latin interval. It provides indirect context for Greek 216–217, which have no independent Latin intervals in the present transcription; this occurrence remains assigned to 218. No original-translation absence or physical-loss mechanism is established.'
                rows[217]['candidate']['cross_references']=[216,217]
            event=dict(kind='HUMAN_EDITORIAL_ADJUDICATION',book=b,sections=numbers,approved_choice=choice,status='APPROVED_HOLD_CLOSED',timestamp=timestamp,hold_commit=HOLD,prior_status=case['status'],prior_candidates=prior,original_case_sha256=sha(original),verbatim_case_archive=HISTORY+'/'+file+'.json',selected_alternative=deepcopy(selected),reason=case['reason'],source_evidence={k:deepcopy(case[k]) for k in ['Niese','Loeb'] if k in case},approved_candidates={str(n):deepcopy(rows[n-1]['candidate']) for n in numbers})
            history.append(event);approvals.append(event)
            case['prior_status']=case['status'];case['status']='APPROVED_HOLD_CLOSED';case['adjudication']=event
            save(d/(file+'.json'),case)
            with (d/(file+'.md')).open('a',encoding='utf8',newline='\n') as f:
                f.write('\n\n## Human adjudication — 2026-10-10\n\n**'+choice+' APPROVED; HOLD CLOSED.** The earlier pending statement above is retained as proposal history. The exact pre-approval record is preserved in `'+HISTORY+'/'+file+'.json` and `.md`, at commit `'+HOLD+'`. The selected alternative, source evidence, original coordinates, neighbouring approved extents and qualifications are recorded in the appended adjudication history. Source wording remains literal; no conjecture or physical-loss cause is supplied.\n')
        save(d/'IDENTITIES.json',rows);save(d/'DECISION_HISTORY.json',history)
        old=Book(raw=(d/'frozen-inputs/Latin.xml').read_bytes())
        structural=json.loads((d/'STRUCTURAL_RECORDS.json').read_text(encoding='utf8'))
        points=physical_points(old,structural,'Latin');retained=[];reused=[];markers=[];unavailable=[]
        for r in rows:
            c=r['candidate'];n=r['number'];assert c['approved']
            loc=c.get('locator')
            if not loc:unavailable.append(n);continue
            validate(old,loc)
            label=next((x for x in old.labels if x['book_offset']==loc['book_offset'] and int(re.findall(r'\d+',x['text'])[-1])==n),None)
            matches=[x for x in points if x['coordinate']==loc['book_offset']]
            if label:retained.append(dict(number=n,locator=loc,label=label))
            elif matches:reused.append(dict(number=n,locator=loc,physical_identity=matches[0]['identity'],physical_locator=matches[0]['locator'],all_coincident_identities=matches))
            else:markers.append(dict(number=n,at=loc['raw_byte'],marker=f'<milestone unit="niese" n="{n}"/>',locator=loc,approval=c.get('adjudication') or 'Governing section 5 individually reviewed secure routine cut',print_evidence=r['print_evidence'],correspondence=c['correspondence']))
        assert len(retained)+len(reused)+len(markers)+len(unavailable)==len(rows)
        assert len({m['at'] for m in markers})==len(markers)
        plan=dict(book=b,baseline=BASE,status='ALL_EDITORIAL_GATES_CLOSED',source_sha256=sha(old.raw),retained_starts=retained,reused_physical_starts=reused,markers=markers,pending_sections=[],approved_unavailable_sections=unavailable)
        save(d/'FINAL_MARKER_PLAN.json',plan)
        output=old.raw
        for op in sorted(markers,key=lambda x:x['at'],reverse=True):output=output[:op['at']]+op['marker'].encode()+output[op['at']:]
        inverse=[];shift=0
        for op in sorted(markers,key=lambda x:x['at']):
            inverse.append(dict(number=op['number'],at=op['at']+shift,length=len(op['marker'].encode()),expected=op['marker']));shift+=len(op['marker'].encode())
        recovered=output
        for op in reversed(inverse):
            assert recovered[op['at']:op['at']+op['length']]==op['expected'].encode();recovered=recovered[:op['at']]+recovered[op['at']+op['length']:]
        assert recovered==old.raw
        target=ROOT/f'assets/xml/antiquities/Latin/book-{b:02}.xml';assert target.read_bytes()==old.raw;target.write_bytes(output)
        save(d/'APPLIED_MARKERS.json',dict(book=b,baseline=BASE,source_sha256=sha(old.raw),output_sha256=sha(output),recovered_sha256=sha(recovered),operations=markers,inverse_operations=inverse,new_markers=len(markers),existing_physical_starts=len(reused),retained_numeric_starts=len(retained),independent_Latin_intervals=len(rows)-len(unavailable),unavailable=unavailable,Greek_edits=0,English_edits=0,end_anchors=0,other_anchors=0,production_applied=True))
        models={l:Book(raw=(d/'frozen-inputs'/f'{l}.xml').read_bytes()) for l in ['Latin','Greek','English']}
        reuses={r['number']:r for r in reused};expected=[];sections=[]
        for r in rows:
            c=r['candidate'];n=r['number'];loc=c.get('locator');latin=dict(available=bool(loc),correspondence=c['correspondence'],note=c.get('note'))
            if n in reuses:latin['start']=reuses[n]['physical_locator']
            if c.get('cross_references'):latin['crossReferences']=c['cross_references']
            section=dict(number=n,Latin=latin,contextTarget=(loc or {}).get('stable_id') or r['Latin_alignment_paragraph'])
            if n==1:section['Greek']=dict(available=True,start=dict(available='true',kind='anchor',target=r['Greek_physical_start']['target']))
            sections.append(section)
            later=next((z for z in rows[n:] if z['candidate'].get('locator')),None)
            end=later['candidate']['locator']['book_offset'] if later else len(old.stream)
            ep=[u for u in models['English'].units if u['element'].get('sameAs','')=='#'+section['contextTarget']]
            assert ep
            expected.append(dict(number=n,safe_Latin_interval=bool(loc),Latin=old.stream[loc['book_offset']:end] if loc else None,Greek=r['Greek_text'],English=''.join(u['text'] for u in ep),Latin_start=loc,Latin_end=end if loc else None,context_target=section['contextTarget'],qualification=c.get('note'),pending=False,unavailable=not bool(loc)))
        units=list(dict.fromkeys(e.get('unit') for m in models.values() for e in m.tree.xpath('//t:milestone',namespaces=NS)))
        registry=dict(schema=1,book=b,range=[1,len(rows)],status='LOCAL_EDITORIAL_APPROVED',structuralMilestoneUnits=units,suppressedLatinLabels=[],sections=sections)
        save(ROOT/f'assets/xml/antiquities/niese/book-{b:02}.json',registry);save(d/'FINAL_EXPECTED_INTERVALS.json',expected)
        print(b,'identities',len(rows),'Latin intervals',sum(e['safe_Latin_interval'] for e in expected),'new markers',len(markers),'physical reuses',len(reused),'unavailable',unavailable)
    original=(ROOT/'assets/js/renderTei.js').read_bytes()
    provenance=json.loads((PACK/'REVIEW_HARNESS_PROVENANCE.json').read_text(encoding='utf8'))
    assert sha(original)==provenance['production_renderer_sha256']
    candidate=(PACK/'REVIEW_RENDERER.js').read_bytes();assert sha(candidate)==provenance['prototype_renderer_sha256']
    (ROOT/'assets/js/renderTei.js').write_bytes(candidate)
    save(PACK/'FINAL_RENDERER_PROVENANCE.json',dict(baseline=BASE,original_sha256=sha(original),output_sha256=sha(candidate),proposal='REVIEW_RENDERER.patch',author='This assigned WorkBot; independently developed against this pinned baseline',changes='18/19 declarative availability paths; generic per-language physical start resolution with existing traditionalPoint; no book-specific range conditional',prior_exhaustive_reproducer='PROTECTED_REVIEW_BROWSER.json',final_browser_replay_required=True))
    save(PACK/'ADJUDICATION_APPROVAL.json',dict(status='ALL_FOUR_HOLDS_CLOSED',timestamp=timestamp,authority='Human current chat message 2026-10-10',hold_commit=HOLD,choices=['A','B','A','A'],events=approvals,primary_review_accepted_by_human=True,no_new_general_authorization_required=True))

if __name__=='__main__':main()
