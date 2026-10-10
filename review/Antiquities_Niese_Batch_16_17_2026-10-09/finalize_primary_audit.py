"""Record completed human source review; never infer reader certification.

The explicit absence and qualification lists below are editorial observations
from the complete readings. Hashes and locator checks corroborate their source
coordinates; string matching is not used to decide survival or correspondence.
"""
from pathlib import Path
import sys, json, re, hashlib
from collections import Counter
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
BATCH = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'review/Antiquities_Niese_BookVIII_2026-10-08'))
from mixed_mapper import Book, digest, NS, raw_char_positions

ABSENT = [77, 123, *range(189, 200), 359, *range(395, 405)]
PARTIAL = {
    16: [5,18,21,22,25,28,34,35,37,40,42,76,87,93,106,115,120,122,125,
         134,139,141,143,145,154,187,188,200,202,218,220,237,239,270,272,
         291,292,358,378],
    17: [42,47,53,56,63,106,133,172,181,209,215,216,313],
}
VARIATION = {
    16: [93,99,177,220,265,274,301,303,312,384,394],
    17: [8,124,141,177,188,223,224,270,278,300,346],
}
REJOINED = {16:[18,97,103,106,122,139,143,154,202],17:[53,113]}
VARIATION_DETAILS = {
    (16,301): 'Greek Εὐρυκλῆς is represented by transmitted Latin eurides; Lacedemo nius and maius autem animo luxuriosus are preserved literally, without correcting the name or wording.',
    (16,312): 'The transmitted Euaretus clause cum uero euaretum...non libenter accusantem...conscium ab horrebat differs in formulation from the Greek Εὐάρατον...Ἀλεξάνδρῳ συνειδέναι and Herod\'s reception. Preserve both witnesses and segment at the first permission counterpart.',
}
PENDING = {16: {294:63,295:64,351:72,355:73},17:{25:88,75:97,76:97}}
ABSENT_PAGE = {77:29,123:36,189:46,190:46,
    **{n:47 for n in range(191,197)}, **{n:48 for n in range(197,200)},
    359:73, **{n:79 for n in range(395,400)}, **{n:80 for n in range(400,405)}}

def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf8', newline='\n')

def check_point(model, point):
    path = point['text_node_path']; tail = path.endswith('/tail()')
    expr = re.sub(r'(?<=/)([A-Za-z][A-Za-z0-9]*)(?=\[)',r't:\1',path.rsplit('/',1)[0])
    matches = model.tree.xpath(expr, namespaces=NS)
    assert len(matches)==1, path
    text = matches[0].tail if tail else matches[0].text
    char = text[point['node_offset']]
    assert char==model.stream[point['book_offset']]
    assert raw_char_positions(model.raw,point['raw_byte'],char)==[point['raw_byte']]

def absence_reason(n):
    if n==77:
        return ('The comparative choice between outward prosperity and domestic evils has no '
                'individually surviving counterpart. Latin 76 states the cause of grief and 78 '
                'begins Turbatus ergo. Other court-reflection passages are their own narratives.')
    if n==123:
        return ('The improved hope and the king\'s need to defend his accusations are not separately '
                'surviving between the speech effects in 122 and Caesar\'s intervention in 124.')
    if 189<=n<=193:
        return ('The detailed court dissension, Antipater/Ptolemy arrangements and Glaphyra hostility '
                'are not individually surviving after the general domestic affliction in 188. '
                'The literal [...] is preserved; its cause is not established.')
    if 194<=n<=199:
        return ('The Pheroras marriage episode, Phasael/Cypros arrangements, Ptolemy\'s advice and '
                'thirty-day promise are not individually surviving here. The num194 label precedes '
                '[...] Nam multi, whose first narrative counterpart is 200. Latin num220\'s later '
                'Pheroras marriage retrospective corresponds to Greek 227–228; it is not survival '
                'of the complete earlier narrative.')
    if n==359:
        return ('The contrast between former restraint and the new emboldened intention to destroy '
                'the sons is not separately surviving between the letter\'s joyful reception in '
                '358 and the summons Statim arcessiit in 360.')
    return ('The final philosophical and moral discussion after execution and burial is not '
            'individually surviving. The final coarse num395 contains only literal [...]. '
            'Earlier reflections in num150 correspond to their own Greek 150–159 context, '
            'and cannot substitute for this book-ending discussion.')

def main():
    summaries = {}
    for b, roman, expected, pages in [(16,'XVI',404,(18,80)),(17,'XVII',355,(83,151))]:
        p = ROOT / f'review/Antiquities_Niese_Book{roman}_2026-10-09'
        rows = json.loads((p/'BOUNDARIES.json').read_text(encoding='utf8'))
        g,l = Book(p/'frozen-inputs/Greek.xml'),Book(p/'frozen-inputs/Latin.xml')
        assert [r['number'] for r in rows]==list(range(1,expected+1))
        before = [(r['number'],r['Latin_review_status'],r['editorial_status']) for r in rows]
        for r in rows:
            n=r['number']
            if b==16 and n in ABSENT:
                r.update(Latin_review_status='INDIVIDUALLY_REVIEWED_UNAVAILABLE_AFTER_FULL_BOOK_REVIEW',
                    Latin_locator=None, correspondence_status='ABSENT_IN_TRANSCRIPTION',
                    physical_placement_status='NO_LATIN_NIESE_START_NO_FALLBACK',
                    editorial_status='ROUTINE_FULL_BOOK_SURVIVAL_REVIEW_COMPLETE',
                    review_reason=absence_reason(n),cause='UNDETERMINED',
                    implementation_approved=True,applied=False,reader_certified=False,
                    source_sha256=digest(l.raw))
            elif n in PENDING[b]:
                r.update(Latin_review_status='INDIVIDUALLY_REVIEWED_EDITOR_DECISION_PENDING',
                    correspondence_status='SURVIVING_CORRESPONDENCE_REPRESENTATION_PENDING',
                    physical_placement_status='ALTERNATIVES_IN_PENDING_DECISION_PACKET',
                    editorial_status='PENDING_EDITOR_ADJUDICATION',
                    implementation_approved=False,applied=False,reader_certified=False,
                    source_sha256=digest(l.raw))
            else:
                assert r['Latin_review_status']=='INDIVIDUALLY_REVIEWED',n
                check_point(l,r['Latin_locator'])
            if not r.get('Greek_reviewed_locator'):
                r['Greek_reviewed_locator']=r['Greek_candidate_locator']
            check_point(g,r['Greek_reviewed_locator'])
            if b==16 and n in ABSENT or n in PENDING[b]:
                page=ABSENT_PAGE[n] if b==16 and n in ABSENT else PENDING[b][n]
                r.update(Greek_print_status='VISUALLY_REVIEWED_NUMBER_AND_CLAUSE_CONTEXT',
                    Greek_start_choice=g.stream[r['Greek_reviewed_locator']['book_offset']:][:100],
                    print_observation=dict(edition='Niese IV (1890)',pdf_page=page,printed_page=page-14,
                        image=f'evidence/Niese-IV-PDF{page:03}.jpg',image_inspected=True,
                        numeral_observation='Marginal numeral and full adjoining clause visually inspected; the printed line position is not an exact word tag.',
                        OCR_is_authority=False))
            tags=[]
            if n in PARTIAL[b]: tags.append('PARTIAL_LOCAL_CORRESPONDENCE')
            if n in VARIATION[b]: tags.append('TRANSMITTED_LEXICAL_OR_ARGUMENT_VARIATION')
            if n in REJOINED[b]: tags.append('SYNTACTICALLY_REATTACHED_CORRESPONDENCE')
            if tags:
                r.update(correspondence_status='PRESENT_WITH_EXPLICIT_QUALIFICATION',
                    correspondence_qualifications=tags,correspondence_note=r['review_reason'],cause='UNDETERMINED')
                if (b,n) in VARIATION_DETAILS:
                    r['correspondence_note'] += ' '+VARIATION_DETAILS[(b,n)]
            elif r['Latin_review_status']=='INDIVIDUALLY_REVIEWED':
                r['correspondence_qualifications']=[]
            r['complete_interval_and_neighbours_read']=True
            r['whole_Latin_book_read']=True
            r['implementation_state']='NOT_APPLIED'
            r['certification_state']='SOURCE_REVIEW_ONLY_NO_READER_CERTIFICATION'
        offsets=[r['Greek_reviewed_locator']['book_offset'] for r in rows]+[len(g.stream)]
        assert offsets[0]==34 and all(a<z for a,z in zip(offsets,offsets[1:]))
        for r,a,z in zip(rows,offsets,offsets[1:]):
            r['Greek_reviewed_interval']=dict(start=a,end=z,text=g.stream[a:z],
                source_sha256=digest(g.raw),status='APPROVED_PRINT_SUPPORTED_GREEK_INTERVAL_NOT_APPLIED')
        save(p/'BOUNDARIES.json',rows)
        absent=[r for r in rows if r['correspondence_status']=='ABSENT_IN_TRANSCRIPTION']
        narrative=[u for u in l.units if not u.get('excluded_reason')]
        audit=dict(book=b,status='COMPLETE_HUMAN_PRIMARY_AND_LATIN_REVIEW_EDITORIAL_HOLDS_REMAIN',
            identity_count=len(rows),printed_Niese_pages=dict(pdf=list(range(pages[0],pages[1]+1)),
                printed=list(range(pages[0]-14,pages[1]-13)),all_visually_inspected=True),
            Greek_intervals_read=len(rows),individual_Latin_decisions_reviewed=len(rows),
            complete_narrative_Latin_paragraphs_read=len(narrative),
            Latin_paratext_preserved=True,
            complete_Latin_reading_scope=[dict(stable_id=u['id'],book_offset=u['book_start'],
                characters=len(u['text']),text_sha256=digest(u['text'].encode('utf8'))) for u in narrative],
            whole_book_survival_review_not_keyword_matching=True,
            routine_present_starts=sum(r['Latin_review_status']=='INDIVIDUALLY_REVIEWED' for r in rows),
            unavailable_identities=[r['number'] for r in absent],
            pending_editorial_identities=sorted(PENDING[b]),
            qualified_present_identities=[r['number'] for r in rows if r.get('correspondence_qualifications')],
            cause_of_omission_or_variation='UNDETERMINED_UNLESS_ESTABLISHED_BY_FURTHER_EVIDENCE',
            input_hashes=dict(Greek=digest(g.raw),Latin=digest(l.raw)),
            physical_word_reordering=False,philological_emendation=False,source_edits=False,
            new_start_milestones=0,new_end_or_other_anchors=0,implemented_selectable_identities=0,
            source_byte_recovery='NOT_APPLICABLE_NO_PRODUCTION_EDITS',
            new_Niese_reader_selections_tested=0,independent_book_certification=False)
        save(p/'COMPLETE_PRIMARY_SOURCE_AUDIT.json',audit)
        if b==16:
            contexts={id:next(u['text'] for u in narrative if u['id']==id) for id in [
                'latin-book16-num73','latin-book16-num78','latin-book16-num121','latin-book16-num127',
                'latin-book16-num188','latin-book16-num194','latin-book16-num150',
                'latin-book16-num220','latin-book16-num356','latin-book16-num361',
                'latin-book16-num392','latin-book16-num395']}
            save(p/'UNAVAILABLE_AFTER_COMPLETE_LATIN_REVIEW.json',dict(status='SOURCE_REVIEW_ONLY_NOT_READER_CERTIFICATION',
                source_sha256=digest(l.raw),identity_count=24,full_book_scope=audit['complete_Latin_reading_scope'],
                method='Complete Greek intervals, complete Latin narrative and neighbouring contexts were read. Later related episodes were compared by event and context, not by recurring words or coarse labels.',
                records=[dict(number=r['number'],Greek=r['Greek_reviewed_interval'],
                    printed_evidence=r['print_observation'],finding=r['review_reason'],
                    Latin_start=None,no_fake_fallback=True,cause='UNDETERMINED') for r in absent],
                literal_Latin_contexts=contexts,English_and_Greek_availability_independent=True))
        history=json.loads((p/'DECISION_HISTORY.json').read_text(encoding='utf8'))
        if not any(x.get('kind')=='COMPLETE_PRIMARY_REVIEW_RECORDED' for x in history):
            history.append(dict(kind='COMPLETE_PRIMARY_REVIEW_RECORDED',previous_review_states=before,
                identities=list(range(1,expected+1)),absence_decisions=[r['number'] for r in absent],
                pending_editorial_identities=sorted(PENDING[b]),source_edits=False,reader_certified=False))
        save(p/'DECISION_HISTORY.json',history)
        plan=json.loads((p/'APPROVED_MARKER_PLAN_PARTIAL.json').read_text(encoding='utf8'))
        plan.update(unreviewed_count=0,pending_editorial_count=len(PENDING[b]),
            unavailable_count=len(absent),complete_individual_source_review=True,
            full_book_complete=False,full_book_implementation_complete=False,
            note='Marker proposals remain unapplied and may reuse existing exact anchors. Closed routine starts are not a book certificate; unavailable identities require data entries without fake Latin starts.')
        save(p/'APPROVED_MARKER_PLAN_PARTIAL.json',plan)
        summaries[str(b)]=audit
        print(roman,'complete review',len(rows),'routine starts',audit['routine_present_starts'],
            'unavailable',len(absent),'editorial pending',len(PENDING[b]),'implemented 0; certified false')
    sources=json.loads((BATCH/'PRINTED_SOURCES.json').read_text(encoding='utf8'))
    sources.update(authority_status='ACTUAL_TITLES_AND_COMPLETE_XVI_XVII_PRIMARY_BODY_IMAGES_VISUALLY_VERIFIED',
        Niese_edition_verification=dict(title_pdf_page=5,editor='B. Niese',volume='IV',year=1890,
            publisher='Weidmann, Berlin',printed_page_equals_pdf_page_minus=14,
            XVI_argumenta_pdf=[17,18],XVI_narrative_pdf=[18,80],
            XVII_argumenta_pdf=[81,82,83],XVII_narrative_pdf=[83,151],next_book_argumenta_pdf=152),
        Loeb_independent_control=dict(title_pdf_page=9,publication_pdf_page=10,year=1963,
            authors='R. Marcus; completed by Allen Wikgren',role='INDEPENDENT_CONTROL_NOT_NIESE_AUTHORITY',
            printed_page_equals_pdf_page_minus=16,XVI_narrative_pdf=[224,387],XVII_narrative_pdf=[388,553]))
    save(BATCH/'PRINTED_SOURCES.json',sources)
    rendered=[]
    for folder in [BATCH,ROOT/'review/Antiquities_Niese_BookXVI_2026-10-09',ROOT/'review/Antiquities_Niese_BookXVII_2026-10-09']:
        for path in sorted((folder/'evidence').glob('*.jpg')):
            raw=path.read_bytes();rendered.append(dict(path=str(path),relative_to_worktree=path.relative_to(ROOT).as_posix(),
                bytes=len(raw),sha256=digest(raw),role='SOURCE_PAGE_IMAGE_NOT_AUTOMATIC_PROOF_OF_REVIEW'))
    save(BATCH/'RENDERED_SOURCE_MANIFEST.json',rendered)
    save(BATCH/'COMPLETE_PRIMARY_SOURCE_AUDIT.json',dict(status='BOTH_BOOKS_REVIEWED_EDITORIAL_HOLDS_REMAIN',
        books=summaries,reviewed_identities=759,pending_editorial_choices=4,pending_identity_starts=7,
        routine_present_starts=728,unavailable_identities=24,implemented_new_identities=0,
        baseline_selectable_identities=5231,expected_total_after_certified_implementation=5990,
        all_759_new_reader_test_status='NOT_RUN_NO_IMPLEMENTATION',batch_certified=False))

if __name__=='__main__':main()
