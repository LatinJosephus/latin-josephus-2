"""Per-book hash-pinned marker plan, implementation and exact inverse verification.

Only this assignment's Greek/Latin corpus files and identity registry are written.
Review coordinates are frozen worktree bytes, never Git's LF/CRLF approximation.
"""
from prepare_review import *
from record_review import independent_node
import subprocess

def patch(raw,ops):
 for op in sorted(ops,key=lambda x:(x['at'],x['delete']),reverse=True):
  old=bytes.fromhex(op['before_hex']);new=bytes.fromhex(op['after_hex']);at=op['at']
  assert raw[at:at+len(old)]==old
  raw=raw[:at]+new+raw[at+len(old):]
 return raw

def implement(b,apply=False):
 d=packet(b);rows=json.loads((d/'BOUNDARIES.json').read_text(encoding='utf8'));bs=books(b)
 baseline=json.loads((d/'BASELINE.json').read_text(encoding='utf8'))
 assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='antiquities-niese-12-13'
 assert all(r['implementation_approved'] and r['Greek']['print_status']=='VISUALLY_INSPECTED' and r['Latin']['review_status']=='INDIVIDUALLY_REVIEWED' for r in rows)
 l=bs['Latin'];g=bs['Greek'];positioned=[r for r in rows if r['Latin']['locator']]
 assert positioned[0]['Latin']['locator']['book_offset']==l.first_content(0)
 for r in rows:
  independent_node(g,r['Greek']['locator'])
  if r['Latin']['locator']:independent_node(l,r['Latin']['locator'])
 assert all(a['Latin']['end_book_offset']==z['Latin']['locator']['book_offset'] for a,z in zip(positioned,positioned[1:]))
 assert positioned[-1]['Latin']['end_book_offset']==len(l.stream)
 retained={};suppressed=[]
 for label in l.labels:
  match=re.search(r'(\d+)\]$',label['text'].strip())
  if not match:continue
  n=int(match.group(1));at=l.first_content(label['book_offset'])
  if not 1<=n<=len(rows):continue
  r=rows[n-1]
  keep=bool(r['Latin']['locator'] and r['Latin']['locator']['book_offset']==at)
  if keep:
   assert n not in retained,(n,'duplicate retained claim');retained[n]=label
  else:
   actual=next((x['niese'] for x in reversed(positioned) if x['Latin']['locator']['book_offset']<=at),None)
   suppressed.append({'paragraph':label['id'],'label':label['text'].strip(),'visibleClaim':n,'actualSection':actual})
 operations={'Greek':[{'niese':1,'kind':'ADD_EXPLICIT_IMPLICIT_OPENING_IDENTITY','at':g.locate(g.first_content(0))['raw_byte'],'delete':0,'before_hex':'','after_hex':b'<num>[1]</num>'.hex(),'target_locator':g.locate(g.first_content(0))}],'Latin':[]}
 for r in positioned:
  n=r['niese'];loc=r['Latin']['locator']
  if n not in retained:
   operations['Latin'].append({'niese':n,'kind':'INSERT_LATIN_SECTION_MILESTONE','at':loc['raw_byte'],'delete':0,'before_hex':'','after_hex':f'<milestone unit="niese" n="{n}"/>'.encode().hex(),'target_locator':loc})
 if b==12:
  end=next(x for x in l.inline_excluded if x['reason']=='terminal book subscription')
  operations['Latin'].append({'niese':None,'kind':'INSERT_NARRATIVE_END_MILESTONE','at':end['original_locator']['raw_byte'],'delete':0,'before_hex':'','after_hex':b'<milestone unit="niese-end"/>'.hex(),'target_locator':end['original_locator'],'purpose':'End the final Niese interval before the unchanged unmarked subscription; book/traditional text stays intact.'})
 plan={'book':b,'base_commit':baseline['base_commit'],'input_hashes':{k:digest(v.raw) for k,v in bs.items()},'Greek_authorized_marker_operations':operations['Greek'],'Latin_authorized_marker_operations':operations['Latin'],'retained_starts':[{'number':n,'label':v} for n,v in sorted(retained.items())],'suppressed_executable_claims':suppressed,'narrative_exclusions':{'Greek':g.excluded+g.inline_excluded,'Latin':l.excluded+l.inline_excluded},'sections':len(rows),'represented_Latin_intervals':len(positioned),'no_independent_Latin_intervals':[r['niese'] for r in rows if not r['Latin']['locator']],'pending_decisions':[],'Latin_section_milestones':sum(x['kind']=='INSERT_LATIN_SECTION_MILESTONE' for x in operations['Latin']),'Latin_end_milestones':sum(x['kind']=='INSERT_NARRATIVE_END_MILESTONE' for x in operations['Latin'])}
 save(d/'APPROVED_MARKER_PLAN.json',plan)
 sections=[{'number':r['niese'],'Latin':{'available':bool(r['Latin']['locator']),'correspondence':r['Latin'].get('correspondence') or 'PRESENT','note':r['Latin'].get('notice')},'contextTarget':(r['Latin']['locator']['stable_id'] or r['Latin']['alignment_window_paragraph']) if r['Latin']['locator'] else r['Latin']['alignment_window_paragraph']} for r in rows]
 registry={'schema':1,'book':b,'range':[1,len(rows)],'status':'EDITORIALLY_APPROVED_LOCAL_IMPLEMENTATION','suppressedLatinLabels':suppressed,'sections':sections}
 outputs={};preservation=[]
 for lang in ['Greek','Latin']:
  before=bs[lang].raw;assert digest(before)==baseline['inputs'][lang]['sha256']
  ops=operations[lang];after=patch(before,ops);inverse=[];shift=0
  for op in sorted(ops,key=lambda x:(x['at'],x['delete'])):
   old=bytes.fromhex(op['before_hex']);new=bytes.fromhex(op['after_hex'])
   inverse.append({'at':op['at']+shift,'delete':len(new),'before_hex':new.hex(),'after_hex':old.hex()});shift+=len(new)-len(old)
  recovered=patch(after,inverse);assert recovered==before
  parsed=Book(raw=after);assert parsed.stream==bs[lang].stream
  for query in ['//@xml:id','//@sameAs']:
   assert parsed.tree.xpath(query,namespaces={'xml':'http://www.w3.org/XML/1998/namespace'})==bs[lang].tree.xpath(query,namespaces={'xml':'http://www.w3.org/XML/1998/namespace'})
  rel=f'assets/xml/antiquities/{lang}/book-{b:02}.xml';target=ROOT/rel
  current=target.read_bytes()
  if current not in [before,after]:
   routine=json.loads((d/'ROUTINE_IMPLEMENTATION_PRESERVATION.json').read_text(encoding='utf8'))
   prior=next(s for s in routine['source_records'] if s['language']==lang)
   assert routine['status']=='PROVISIONAL_ROUTINE_MARKERS_APPLIED' and digest(current)==prior['after_sha256']
   assert patch(current,prior['inverse_operations'])==before
  outputs[target]=after
  preservation.append({'language':lang,'path':str(target),'before_sha256':digest(before),'after_sha256':digest(after),'reverse_sha256':digest(recovered),'exact_byte_recovery':True,'narrative_unchanged':True,'IDs_sameAs_unchanged':True,'newline':'LF' if b'\r' not in before else 'CRLF','BOM':before.startswith(b'\xef\xbb\xbf'),'operations':ops,'inverse_operations':inverse})
 english=ROOT/f'assets/xml/antiquities/English/book-{b:02}.xml';assert english.read_bytes()==bs['English'].raw
 if apply:
  for path,raw in outputs.items():path.write_bytes(raw)
  save(ROOT/f'assets/xml/antiquities/niese/book-{b:02}.json',registry)
 save(d/'IMPLEMENTATION_PRESERVATION.json',{'book':b,'status':'APPLIED_AWAITING_READER_CERTIFICATION' if apply else 'REHEARSAL_ONLY','source_records':preservation,'English_unchanged':True,'Greek_marker_additions':1,'Greek_marker_moves':0,'retained_Latin_starts':len(retained),'Latin_section_milestones':plan['Latin_section_milestones'],'Latin_end_milestones':plan['Latin_end_milestones'],'represented_Latin_intervals':len(positioned),'expected_sections':len(rows),'no_independent_Latin_intervals':plan['no_independent_Latin_intervals'],'pending_decisions':[]})
 save(d/'EXPECTED_INTERVALS.json',{'book':b,'Greek':{str(r['niese']):r['Greek']['section'] for r in rows},'Latin':{str(r['niese']):r['Latin'].get('interval') if r['Latin']['locator'] else None for r in rows},'GreekFull':g.stream,'LatinFull':l.stream,'registry':registry,'exclusions':plan['narrative_exclusions']})
 save(d/'EXECUTABLE_IDENTITIES.json',{'book':b,'retained':plan['retained_starts'],'inserted':[x['niese'] for x in operations['Latin'] if x['kind']=='INSERT_LATIN_SECTION_MILESTONE'],'suppressed':suppressed,'no_independent_Latin_interval':plan['no_independent_Latin_intervals']})
 print(json.dumps({k:plan[k] for k in ['book','sections','represented_Latin_intervals','Latin_section_milestones','Latin_end_milestones','no_independent_Latin_intervals','suppressed_executable_claims']},ensure_ascii=False,indent=2));print('APPLIED' if apply else 'REHEARSAL')

if __name__=='__main__':implement(int(sys.argv[1]),'--apply' in sys.argv)
