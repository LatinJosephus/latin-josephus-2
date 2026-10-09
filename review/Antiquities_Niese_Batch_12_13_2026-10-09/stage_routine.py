"""Stage only individually approved physical markers while decisions remain open.

No identity registry or reader availability is enabled by this checkpoint.
Unresolved representations are excluded and certification remains provisional.
"""
from prepare_review import *
from record_review import independent_node
from implement_book import patch
import subprocess

b=int(sys.argv[1]);d=packet(b);bs=books(b)
rows=json.loads((d/'BOUNDARIES.json').read_text(encoding='utf8'))
pending=[r['niese'] for r in rows if not r['implementation_approved']]
assert pending and subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='antiquities-niese-12-13'
approved=[r for r in rows if r['implementation_approved'] and r['Latin']['locator']]
assert all(r['Greek']['print_status']=='VISUALLY_INSPECTED' and r['Latin']['review_status']=='INDIVIDUALLY_REVIEWED' for r in approved)
retained=[];ops={'Greek':[], 'Latin':[]}
first=rows[0];assert first['implementation_approved']
ops['Greek']=[{'niese':1,'kind':'ADD_EXPLICIT_IMPLICIT_OPENING_IDENTITY','at':first['Greek']['locator']['raw_byte'],'delete':0,'before_hex':'','after_hex':b'<num>[1]</num>'.hex(),'target_locator':first['Greek']['locator']}]
for r in approved:
 n=r['niese'];loc=r['Latin']['locator'];independent_node(bs['Latin'],loc)
 keep=[label for label in bs['Latin'].labels if re.search(r'(\d+)\]$',label['text'].strip()) and int(re.search(r'(\d+)\]$',label['text'].strip()).group(1))==n and bs['Latin'].first_content(label['book_offset'])==loc['book_offset']]
 assert len(keep)<=1
 if keep:retained.append(n)
 else:ops['Latin'].append({'niese':n,'kind':'INSERT_LATIN_SECTION_MILESTONE','at':loc['raw_byte'],'delete':0,'before_hex':'','after_hex':f'<milestone unit="niese" n="{n}"/>'.encode().hex(),'target_locator':loc})
records=[]
for lang in ['Greek','Latin']:
 before=bs[lang].raw;after=patch(before,ops[lang]);target=ROOT/f'assets/xml/antiquities/{lang}/book-{b:02}.xml'
 assert target.read_bytes() in [before,after]
 shift=0;inverse=[]
 for op in sorted(ops[lang],key=lambda o:o['at']):
  new=bytes.fromhex(op['after_hex']);inverse.append({'at':op['at']+shift,'delete':len(new),'before_hex':new.hex(),'after_hex':''});shift+=len(new)
 assert patch(after,inverse)==before
 independent_recovery=re.sub(rb'<milestone unit="niese" n="[1-9]\d*"/>',b'',after) if lang=='Latin' else after[:ops[lang][0]['at']]+after[ops[lang][0]['at']+14:]
 assert independent_recovery==before
 parsed=Book(raw=after);assert parsed.stream==bs[lang].stream
 for q in ['//@xml:id','//@sameAs']:assert parsed.tree.xpath(q,namespaces={'xml':'http://www.w3.org/XML/1998/namespace'})==bs[lang].tree.xpath(q,namespaces={'xml':'http://www.w3.org/XML/1998/namespace'})
 target.write_bytes(after)
 records.append({'language':lang,'path':str(target),'before_sha256':digest(before),'after_sha256':digest(after),'inverse_operations':inverse,'exact_two_method_recovery':True,'narrative_IDs_sameAs_preserved':True})
assert (ROOT/f'assets/xml/antiquities/English/book-{b:02}.xml').read_bytes()==bs['English'].raw
save(d/'ROUTINE_MARKER_PLAN.json',{'book':b,'status':'PROVISIONAL_ROUTINE_MARKERS_ONLY','pending_representations':pending,'Greek_authorized_marker_operations':ops['Greek'],'Latin_authorized_marker_operations':ops['Latin'],'approved_retained_starts':retained,'approved_physical_starts':len(approved),'proposed_no_interval_sections':[r['niese'] for r in rows if not r['Latin']['locator']],'absence_representations_implemented':False,'reader_registry_enabled':False})
save(d/'ROUTINE_IMPLEMENTATION_PRESERVATION.json',{'book':b,'status':'PROVISIONAL_ROUTINE_MARKERS_APPLIED','source_records':records,'pending_representations':pending,'Latin_section_milestones':len(ops['Latin']),'retained_approved_starts':len(retained),'Greek_marker_additions':1,'English_unchanged':True,'reader_certification':'NOT_PERFORMED; book remains disabled pending adjudication','whole_section_absence_claims':[]})
print('Routine markers applied',b,'Latin additions',len(ops['Latin']),'retained',len(retained),'pending',pending)
