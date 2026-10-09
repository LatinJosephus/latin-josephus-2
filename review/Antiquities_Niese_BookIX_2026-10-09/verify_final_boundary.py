"""Certify the adjudicated neighbouring partition against frozen and final bytes."""
from pathlib import Path
import json
from mixed_mapper import Book,digest
P=Path(__file__).resolve().parent;W=P.parents[1]
def read(p):return json.loads(p.read_text(encoding='utf8'))
base=read(P/'BASELINE.json');rows=read(P/'BOUNDARIES.json')
prior=read(P/'qa-history/pre-decision-5794785/BOUNDARIES.json')
packet=read(P/'DECISION_240_ALTERNATIVES.json');decision=read(P/'EDITORIAL_DECISIONS.json')['240']
assert decision['choice']=='A' and not read(P/'EXECUTABLE_IDENTITIES.json')['pending']
assert packet['adopted_alternative']=='A' and packet['rejected_alternative']=='B'
results={}
for lang,anchor,tag in [('Greek','ἔσται δ᾽','<num>[240]</num>'),('Latin','et nullus','<milestone unit="niese" n="240"/>')]:
    rel=f'assets/xml/antiquities/{lang}/book-09.xml'
    original=Path(base['inputs'][rel]['snapshot']).read_bytes();actual=(W/rel).read_bytes()
    frozen=Book(raw=original);final=Book(raw=actual)
    assert frozen.stream==final.stream
    changed=[]
    for before,after in zip(prior,rows):
        assert before['niese']==after['niese']
        if before[lang+'_locator']!=after[lang+'_locator'] or before[lang+'_section']!=after[lang+'_section']:
            changed.append(after['niese'])
    assert changed==[239,240],changed
    adopted=packet['alternatives']['A'][lang];rejected=packet['alternatives']['B'][lang]
    assert {k:rows[239][lang+'_locator'][k] for k in adopted['chosen_cut']}==adopted['chosen_cut']
    assert rows[239][lang+'_locator']['input_sha256']==digest(original)
    assert rows[239][lang+'_section'].startswith(anchor)
    assert rows[238][lang+'_section']==adopted['section_239']
    assert rows[239][lang+'_section']==adopted['section_240']
    assert rows[240][lang+'_locator']==prior[240][lang+'_locator']
    assert rows[240][lang+'_section']==prior[240][lang+'_section']
    intervals=[]
    for n in [239,240,241]:
        row=rows[n-1];start=row[lang+'_locator']['book_offset'];end=row[lang+'_end_book_offset']
        assert final.stream[start:end]==row[lang+'_section']
        start_loc=final.locate(start)
        assert start_loc['stable_id']==row[lang+'_locator']['stable_id']
        assert actual[start_loc['raw_byte']:].startswith(row[lang+'_section'][0].encode('utf8'))
        intervals.append({'section':n,'narrative_extent':[start,end],'narrative':row[lang+'_section'],
          'frozen_locator':row[lang+'_locator'],'final_locator':start_loc,'final_input_sha256':digest(actual)})
    assert intervals[0]['narrative_extent'][1]==intervals[1]['narrative_extent'][0]
    assert intervals[1]['narrative_extent'][1]==intervals[2]['narrative_extent'][0]
    joined=''.join(i['narrative'] for i in intervals)
    assert joined==frozen.stream[intervals[0]['narrative_extent'][0]:intervals[-1]['narrative_extent'][1]]
    start240=intervals[1]['final_locator']['raw_byte'];tag_bytes=tag.encode()
    assert actual[start240-len(tag_bytes):start240]==tag_bytes
    assert len(actual.split(tag_bytes))==2
    results[lang]={'before_sha256':digest(original),'after_sha256':digest(actual),'only_changed_reviewed_extents':[239,240],
      'section_241_unchanged':True,'adopted_packet_locator_exact':True,'actual_marker_immediately_before_anchor':True,
      'continuous_neighbouring_partition':True,'intervals':intervals,'rejected_B':rejected}
out={'result':'PASS','phase':'POST_EXPLICIT_240_RESOLUTION','decision':decision,
     'printed_word_ambiguity_resolved_editorially':True,'no_claim_of_unambiguous_printed_word_cut':True,
     'Greek_marker_relocations':[181,216,240],'languages':results}
(P/'FINAL_BOUNDARY_239_241.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
human=['# Final IX.239–241 extents','',
 'A was adopted by explicit user editorial resolution. The shared printed line remains ambiguous at word level; rejected B is retained in DECISION_240.md and the machine packet.',
 '', 'Only the extents of239 and240 change from the preceding provisional review.241 is unchanged. The three adjoining intervals form the identical frozen narrative span, without loss, duplication or altered wording.']
for lang,result in results.items():
    human+=['',f'## {lang}']
    for i in result['intervals']:
        loc=i['frozen_locator'];current=i['final_locator']
        human+=['',f"### §{i['section']}",'',f"Unicode book extent {i['narrative_extent']}; original raw UTF-8 cut {loc['raw_byte']}; final raw cut {current['raw_byte']}. Paragraph `{loc['stable_id']}`. Exact text/tail paths, unit hashes and alternatives are in FINAL_BOUNDARY_239_241.json.",'',i['narrative'].rstrip()]
(P/'FINAL_BOUNDARY_239_241.md').write_text('\n'.join(human)+'\n',encoding='utf8',newline='\n')
print('PASS: exact A locators, actual paired markers, continuous239–241 extents and unchanged241/all other boundaries')
