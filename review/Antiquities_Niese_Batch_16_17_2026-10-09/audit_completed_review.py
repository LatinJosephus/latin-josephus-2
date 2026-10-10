"""Independent checks of complete review evidence and protected coordinates.

This checks source-audit records against actual pinned bytes. It deliberately
does not certify unimplemented Niese selections or substitute for browser QA.
"""
from pathlib import Path
import sys,json,re
from collections import Counter
from lxml import etree
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];BATCH=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'review/Antiquities_Niese_BookVIII_2026-10-08'))
from mixed_mapper import Book,digest,NS,raw_char_positions
XML_ID='{http://www.w3.org/XML/1998/namespace}id'

def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
def point_check(model,p):
    path=p['text_node_path'];expr=re.sub(r'(?<=/)([A-Za-z][A-Za-z0-9]*)(?=\[)',r't:\1',path.rsplit('/',1)[0])
    node=model.tree.xpath(expr,namespaces=NS);assert len(node)==1
    value=node[0].tail if path.endswith('/tail()') else node[0].text
    char=value[p['node_offset']]
    assert char==model.stream[p['book_offset']]
    assert raw_char_positions(model.raw,p['raw_byte'],char)==[p['raw_byte']]
    unit=next(u for u in model.units if u['id']==p['stable_id'])
    assert unit['book_start']+p['unit_offset']==p['book_offset']

def main():
    outputs={}
    for b,roman,expected in [(16,'XVI',404),(17,'XVII',355)]:
        p=ROOT/f'review/Antiquities_Niese_Book{roman}_2026-10-09'
        baseline=read(p/'BASELINE.json');rows=read(p/'BOUNDARIES.json')
        models={lang:Book(p/f'frozen-inputs/{lang}.xml') for lang in ['Greek','Latin','English']}
        preservation=[]
        for lang,model in models.items():
            actual=(ROOT/baseline['inputs'][lang]['relative']).read_bytes()
            assert actual==model.raw and digest(actual)==baseline['inputs'][lang]['sha256']
            tree=etree.fromstring(actual)
            ids=[x.get(XML_ID) for x in tree.iter() if x.get(XML_ID)]
            assert ids==baseline['inputs'][lang]['xml_ids'] and len(ids)==len(set(ids))
            preservation.append(dict(language=lang,sha256=digest(actual),bytes=len(actual),
                existing_xml_ids=len(ids),exact_input_bytes_preserved=True,
                apparatus_wrappers_sameAs_labels_notes_and_material_marking_preserved_by_exact_bytes=True,
                new_niese_markers=0,CRLF=actual.count(b'\r\n'),LF=actual.count(b'\n')))
        assert [x['number'] for x in rows]==list(range(1,expected+1))
        greek_checks=0;latin_checks=0;pages=[]
        for x in rows:
            assert x['complete_interval_and_neighbours_read'] and x['whole_Latin_book_read']
            point_check(models['Greek'],x['Greek_reviewed_locator']);greek_checks+=1
            interval=x['Greek_reviewed_interval']
            assert interval['text']==models['Greek'].stream[interval['start']:interval['end']]
            assert x['Greek_print_status']=='VISUALLY_REVIEWED_NUMBER_AND_CLAUSE_CONTEXT'
            observation=x['print_observation'];image=p/observation['image']
            assert image.is_file() and observation['image_inspected'] and not observation['OCR_is_authority']
            assert observation['printed_page']==observation['pdf_page']-14
            pages.append(observation['pdf_page'])
            assert x['implementation_state']=='NOT_APPLIED' and not x['reader_certified']
            if x['Latin_review_status']=='INDIVIDUALLY_REVIEWED':
                point_check(models['Latin'],x['Latin_locator']);latin_checks+=1
            elif x['correspondence_status']=='ABSENT_IN_TRANSCRIPTION':
                assert b==16 and x['Latin_locator'] is None and x['cause']=='UNDETERMINED'
            else:
                assert x['editorial_status']=='PENDING_EDITOR_ADJUDICATION' and not x['implementation_approved']
        assert greek_checks==expected
        assert set(pages)==set(range(18,81) if b==16 else range(83,152))
        retained=[]
        for x in read(p/'INHERITED_STRUCTURAL_RECORDS.json'):
            n=str(x['values'].get('canonical-niese'))
            if n not in (['235','356','368'] if b==16 else ['106','146','299']):continue
            for lang,loc in x['locators'].items():
                model=models[lang];unit=next(u for u in model.units if u['id']==loc['paragraph'])
                offset=int(loc['offset']);literal=unit['text'][offset:offset+160]
                # Greek/English preserved paragraph labels can be followed by a
                # formatting space. Frozen structural edges and first-word
                # review coordinates are recorded separately, never conflated.
                assert literal.lstrip().startswith(loc['anchor'][:35].lstrip()),(x['id'],lang,literal)
                targets=model.tree.xpath('//*[@xml:id=$id]',id=loc['target'],namespaces=NS)
                assert len(targets)==1
                retained.append(dict(boundary=x['id'],scheme=x['values'].get('scheme'),Niese_association=n,
                    language=lang,paragraph=loc['paragraph'],frozen_offset=offset,
                    kind=loc['kind'],target=loc['target'],literal_current_text=literal,
                    exact_coordinate_preserved=True))
        if b==16:
            bamberg=next(x for x in retained if x['boundary']=='B78-table1-row151' and x['language']=='Latin')
            assert rows[367]['Latin_locator']['unit_offset']==bamberg['frozen_offset']==177
            trad=next(x for x in retained if x['boundary']=='LOEB-16-Chapter-11-0' and x['language']=='Latin')
            assert rows[355]['Latin_locator']['unit_offset']==trad['frozen_offset']==95
            assert models['Greek'].stream[:34]=='περιέχει ἡ βίβλος χρόνον ἐτῶν ιβ. '
        else:
            assert models['Greek'].stream[:34]=='περιέχει ἡ βίβλος χρόνον ἐτῶν ιδ. '
            decision=read(p/'DECISION_XVII_030_031.json')
            assert rows[30]['Greek_reviewed_locator']==decision['approved_locator']
            assert rows[29]['Greek_reviewed_interval']['end']==decision['approved_locator']['book_offset']
            assert not decision['applied']
        save(p/'PROTECTED_STRUCTURAL_COORDINATES.json',dict(status='PASS_PINNED_SOURCE_COORDINATES_ONLY',
            records=retained,note='Frozen element edges can precede a formatting space while the Niese audit gives the first narrative word. Latin XVI.368 and XVI.356 physically coincide with their retained anchors; Greek/English source edges remain independent.'))
        data=dict(status='PASS_INDEPENDENT_COMPLETE_SOURCE_AUDIT_CHECK_ONLY',book=b,
            expected_identities=expected,reviewed_identities=len(rows),
            Greek_raw_byte_and_independent_lxml_coordinates_checked=greek_checks,
            routine_Latin_raw_byte_and_independent_lxml_coordinates_checked=latin_checks,
            all_primary_body_page_evidence_present=True,
            source_preservation=preservation,retained_exceptional_coordinates_checked=len(retained),
            unavailable=sum(x['correspondence_status']=='ABSENT_IN_TRANSCRIPTION' for x in rows),
            pending_editorial_starts=sum(x['editorial_status']=='PENDING_EDITOR_ADJUDICATION' for x in rows),
            source_byte_recovery_after_edit='NOT_APPLICABLE_NO_SOURCE_EDITS',
            Niese_registry_implementation=False,new_selection_browser_QA=False,book_certified=False)
        save(p/'INDEPENDENT_SOURCE_AUDIT_CHECK.json',data);outputs[str(b)]=data
        print(roman,'PASS source audit only;',greek_checks,'Greek and',latin_checks,'Latin coordinates;',len(retained),'exceptional structural coordinates unchanged')
    save(BATCH/'INDEPENDENT_SOURCE_AUDIT_CHECK.json',dict(status='PASS_SOURCE_REVIEW_ONLY_PENDING_EDITOR',
        books=outputs,implemented_new_identities=0,batch_certified=False))

if __name__=='__main__':main()
