"""Independent full-book certification: actual markers, DOM, raw bytes, partition."""
from pathlib import Path
import json,re,sys,bisect
from source_scope import Book,digest
from verify_locators import validate,validate_all_nodes
ROOT=Path(__file__).resolve().parents[2]
b=int(sys.argv[1]);roman={14:'XIV',15:'XV'}[b];total={14:491,15:425}[b]
P=ROOT/f'review/Antiquities_Niese_Book{roman}_2026-10-09'
load=lambda name:json.loads((P/name).read_text(encoding='utf8'))
rows=load('BOUNDARIES.json');assert [r['number'] for r in rows]==list(range(1,total+1))
assert all(r['Latin_review_status']!='UNREVIEWED' and r['Greek_print_status']!='UNREVIEWED' and r['print_observation']['image_inspected'] for r in rows)
assert not any(r['editorial_status']=='PENDING_USER_DECISION' for r in rows)
frozen={lang:(P/f'frozen-inputs/{lang}.xml').read_bytes() for lang in ['Greek','Latin','English']}
actual={lang:(ROOT/f'assets/xml/antiquities/{lang}/book-{b:02}.xml').read_bytes() for lang in frozen}
l=Book(raw=frozen['Latin']);g=Book(raw=frozen['Greek']);after=Book(raw=actual['Latin'])
assert l.stream==after.stream and frozen['English']==actual['English']
# Discover added marker positions from actual bytes independently of the plan.
rx=rb'<milestone unit="niese" n="([0-9]+)"/>'
matches=list(re.finditer(rx,actual['Latin']))
assert re.sub(rx,b'',actual['Latin'])==frozen['Latin']
positions=[p for node in l.nodes for p in node['raw_positions']]
starts=[];shift=0
for m in matches:
 n=int(m[1]);raw=m.start()-shift;shift+=m.end()-m.start()
 off=bisect.bisect_left(positions,raw);assert positions[off]==raw
 r=rows[n-1];assert r['Latin_locator']['raw_byte']==raw and r['Latin_locator']['book_offset']==off
 validate(l,r['Latin_locator']);starts.append((n,off))
# Retained labels are read from original label positions, not semantic incipits.
for r in rows:
 if r['physical_placement_status'].startswith('RETAINED'):
  label=next(v for v in l.labels if v['id']==r['Latin_paragraph_id'])
  assert r['Latin_locator']['book_offset']==label['book_offset'];validate(l,r['Latin_locator'])
  starts.append((r['number'],label['book_offset']))
starts.sort();unavailable=[r['number'] for r in rows if r['correspondence_status']=='UNAVAILABLE']
assert [n for n,_ in starts]==[n for n in range(1,total+1) if n not in unavailable]
assert starts[0][1]==0
segments=[]
for i,(n,start) in enumerate(starts):
 end=starts[i+1][1] if i+1<len(starts) else len(l.stream)
 assert start<end
 text=l.stream[start:end];assert rows[n-1]['Latin_interval']['text']==text
 segments.append(dict(number=n,start=start,end=end,codepoints=end-start,sha256=digest(text.encode())))
assert ''.join(l.stream[s['start']:s['end']] for s in segments)==l.stream
terminal=load('TERMINAL_EXTENT.json');validate(l,terminal['last_narrative_character_locator'])
assert terminal['exclusive_Unicode_end']==len(l.stream)
opening=load('GREEK_OPENING_IMPLEMENTATION.json');op=opening['inverse'];raw=actual['Greek']
assert raw[op['at']:op['at']+op['delete']]==op['expected'].encode()
assert raw[:op['at']]+raw[op['at']+op['delete']:]==frozen['Greek']
ga=Book(raw=raw);assert ga.stream==g.stream
greeknums=[]
for label in ga.labels:
 match=re.fullmatch(r'\[([0-9]+)\]',label['text'].strip())
 if match:greeknums.append(int(match[1]))
assert greeknums==list(range(1,total+1)),greeknums
for r in rows:validate(g,r['locator'])
q=dict(book=b,status='PASS',expected_sections=total,Greek_verified_starts=total,Latin_reviewed_candidates=total,
 selectable_identities=total,nonempty_Latin_intervals=len(starts),added_milestones=len(matches),retained_starts=len(starts)-len(matches),unavailable_sections=unavailable,
 exact_Latin_byte_recovery=True,exact_Greek_byte_recovery=True,English_unchanged=True,Greek_marker_additions=[1],Greek_marker_corrections=[],Greek_marker_moves=[],
 full_narrative_partition=True,leading_whitespace_included=True,narrative_codepoints=len(l.stream),narrative_sha256=digest(l.stream.encode()),
 terminal_exclusive_raw_UTF8_end=terminal['exclusive_raw_UTF8_end'],segments=segments,
 independent_locators=dict(Greek=validate_all_nodes(g),Latin=validate_all_nodes(l)),
 file_hashes=[dict(language=lang,path=str(ROOT/f'assets/xml/antiquities/{lang}/book-{b:02}.xml'),before=digest(frozen[lang]),after=digest(actual[lang])) for lang in frozen],
 scope='This is source/partition verification. Full browser certification is separately required.')
(P/'COMPLETE_PARTITION_QA.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
print(roman,'PASS',total,'identities',len(starts),'nonempty Latin intervals',unavailable,'unavailable; exact partition and byte recovery')
