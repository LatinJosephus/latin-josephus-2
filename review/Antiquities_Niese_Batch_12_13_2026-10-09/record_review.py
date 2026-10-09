"""Apply individually authored observations to review registers, never source XML."""
from prepare_review import *
def independent_node(book,loc):
 path=loc['text_node_path'];tail=path.endswith('/tail()');p=path.rsplit('/',1)[0]
 xp=re.sub(r'(?<=/)([A-Za-z][A-Za-z0-9_-]*)(?=\[)',r't:\1',p)
 el=book.tree.xpath(xp,namespaces={'t':'http://www.tei-c.org/ns/1.0'})
 assert len(el)==1,(path,len(el))
 text=el[0].tail if tail else el[0].text
 assert text is not None
 node=next(n for n in book.nodes if n['path']==path)
 assert text==node.get('source_node_text',node['text'])
 k=loc['node_offset'];assert k<len(text)
 raw=book.raw[loc['raw_byte']:]
 expected=text[k]
 if raw.startswith(b'&'):assert raw[:raw.index(b';')+1].decode() in ['&amp;','&lt;','&gt;','&quot;','&apos;',f'&#{ord(expected)};',f'&#x{ord(expected):x};']
 elif expected=='\n':assert raw.startswith((b'\n',b'\r'))
 else:assert raw.startswith(expected.encode('utf8'))
 return 'PASS: independent lxml .text/.tail and exact raw UTF-8/entity start'
def apply(b):
 d=packet(b);bs=books(b);g,l=bs['Greek'],bs['Latin'];rows=json.loads((d/'CANDIDATE_REGISTER.json').read_text(encoding='utf8'))
 choices=json.loads((d/'LATIN_REVIEW_CHOICES.json').read_text(encoding='utf8'))
 observations=json.loads((d/'PRINT_OBSERVATIONS.json').read_text(encoding='utf8'))
 for n,obs in observations.items():
  r=rows[int(n)-1];assert r['niese']==int(n);image=d/obs['image'];assert image.exists()
  r['Greek']['print_status']='VISUALLY_INSPECTED';r['Greek']['printed_observation']={**obs,'image_sha256':digest(image.read_bytes())};r['Greek']['word_boundary_status']=obs['word_boundary_status'];r['Greek']['independent_locator_validation']=independent_node(g,r['Greek']['locator'])
 for n,choice in choices.items():
  if choice.get('phrase') is None:
   r=rows[int(n)-1];r['Latin']['locator']=None;r['Latin']['review_status']='INDIVIDUALLY_REVIEWED';r['Latin']['individual_assessment']=choice['assessment'];r['Latin']['correspondence_limits']=choice['limits'];r['Latin']['physical_placement_status']='NO_INDEPENDENT_INTERVAL' if choice['status']=='USER_APPROVED' else 'NO_INDEPENDENT_START_PENDING_DECISION';r['editorial_status']=choice['status'];r['implementation_approved']=choice['status']=='USER_APPROVED';r['Latin']['notice']=choice.get('notice');r['Latin']['correspondence']=choice.get('correspondence')
   continue
  r=rows[int(n)-1];target=choice.get('paragraph',r['Latin']['alignment_window_paragraph']);lu=next(u for u in l.units if u['id']==target);phrase=choice['phrase'];hits=[m.start() for m in re.finditer(re.escape(phrase),lu['text'])];assert len(hits)==1,(b,n,phrase,hits)
  at=lu['book_start']+hits[0];loc=l.locate(at);r['Latin']['locator']=loc;r['Latin']['anchor_phrase']=phrase;r['Latin']['individual_assessment']=choice['assessment'];r['Latin']['review_status']='INDIVIDUALLY_REVIEWED';r['Latin']['independent_locator_validation']=independent_node(l,loc)
  label=next((x for x in l.labels if x['id']==target and x['book_offset']<=at and l.first_content(x['book_offset'])==at),None)
  r['Latin']['physical_placement_status']='RETAINED_LABEL_POSITION' if label else 'INTERNAL_START';r['Latin']['retained_label']=label
  r['Latin']['correspondence_limits']=choice.get('limits','Correspondence present; no unresolved boundary alternative identified in reviewed adjoining context.')
  r['editorial_status']=choice.get('status','ROUTINE_SOURCE_SUPPORTED')
  r['Latin']['notice']=choice.get('notice');r['Latin']['correspondence']=choice.get('correspondence')
  r['implementation_approved']=r['editorial_status'] in ['ROUTINE_SOURCE_SUPPORTED','USER_APPROVED'] and r['Greek']['word_boundary_status']=='XML_WORD_START_CONFIRMED_FROM_PRINT'
 positioned=[r for r in rows if r['Latin']['locator']]
 assert all(a['Latin']['locator']['book_offset']<z['Latin']['locator']['book_offset'] for a,z in zip(positioned,positioned[1:]))
 for i,r in enumerate(positioned):
  end=positioned[i+1]['Latin']['locator'] if i+1<len(positioned) else None
  r['Latin']['extent_status']='CLOSED_BY_REVIEWED_NEXT_START' if end else ('CLOSED_BY_DOCUMENTED_NARRATIVE_END' if r['niese']==len(rows) else 'OPEN_UNTIL_NEXT_BOUNDARY_REVIEW')
  if end:r['Latin']['end_book_offset']=end['book_offset'];r['Latin']['interval']=l.stream[r['Latin']['locator']['book_offset']:end['book_offset']]
  elif r['niese']==len(rows):r['Latin']['end_book_offset']=len(l.stream);r['Latin']['interval']=l.stream[r['Latin']['locator']['book_offset']:]
 save(d/'CANDIDATE_REGISTER.json',rows);save(d/'BOUNDARIES.json',rows)
 reviewed=[r for r in rows if r['Latin']['review_status']=='INDIVIDUALLY_REVIEWED'];print('Book',b,'Greek inspected',len(observations),'Latin reviewed',len(reviewed),'locators validated',sum(bool(r['Latin']['locator']) for r in reviewed),'approved boundaries',sum(r['implementation_approved'] for r in rows))
 with (d/'BOUNDARIES.md').open('w',encoding='utf8',newline='\n') as f:
  f.write(f'# Book {b}: individual boundary review\n\nProvisional while review is incomplete. XML candidates are not source approval.\n\n')
  for r in reviewed:
   obs=r['Greek'].get('printed_observation');loc=r['Latin']['locator']
   if loc is None:
    f.write(f'## {b}.{r["niese"]}\n\nGreek: {r["Greek"]["section"].strip()}\n\nLatin: {r["Latin"]["individual_assessment"]}\n\nLimits: {r["Latin"]["correspondence_limits"]}\n\nStatus: {r["editorial_status"]}\n\n')
    continue
   f.write(f'## {b}.{r["niese"]}\n\nGreek: {r["Greek"]["section"].strip()}\n\nLatin start: `{r["Latin"]["anchor_phrase"]}` in `{loc["stable_id"]}`; Unicode book offset {loc["book_offset"]}, node offset {loc["node_offset"]}, raw byte {loc["raw_byte"]}.\n\n{r["Latin"]["individual_assessment"]}\n\nLimits: {r["Latin"]["correspondence_limits"]}\n\n')
   if obs:f.write(f'Print: Niese III p.{obs["printed_page"]}, PDF{obs["PDF_page"]}. [{obs["observed_numeral_position"]}]({obs["image"]}). Word assessment: {obs["word_boundary_status"]}.\n\n')
if __name__=='__main__':apply(int(sys.argv[1]))
