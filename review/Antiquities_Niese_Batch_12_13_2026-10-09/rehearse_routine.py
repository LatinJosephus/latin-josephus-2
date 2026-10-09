"""Enable staged routine identities only in the disposable local build for QA.

The repository reader and registry remain untouched. Pending cases and the
adjoining 212 extent are expressly excluded from final certification.
"""
from prepare_review import *
b=int(sys.argv[1]);d=packet(b);bs=books(b);l=bs['Latin']
rows=json.loads((d/'BOUNDARIES.json').read_text(encoding='utf8'))
routine=json.loads((d/'ROUTINE_IMPLEMENTATION_PRESERVATION.json').read_text(encoding='utf8'))
for r in routine['source_records']:
 assert digest((RUNTIME/'site'/f'assets/xml/antiquities/{r["language"]}/book-{b:02}.xml').read_bytes())==r['after_sha256']
positioned=[r for r in rows if r['implementation_approved'] and r['Latin']['locator']]
starts={r['niese']:r['Latin']['locator']['book_offset'] for r in positioned}
retained=[];suppressed=[]
for label in l.labels:
 m=re.search(r'(\d+)\]$',label['text'].strip())
 if not m:continue
 n=int(m.group(1));at=l.first_content(label['book_offset'])
 if n in starts and starts[n]==at:retained.append(n)
 elif 1<=n<=len(rows):suppressed.append({'paragraph':label['id'],'label':label['text'].strip(),'visibleClaim':n,'actualSection':next((r['niese'] for r in reversed(positioned) if starts[r['niese']]<=at),None)})
sections=[];latin={};english={}
for r in rows:
 n=r['niese'];available=n in starts;context=(r['Latin']['locator']['stable_id'] if r['Latin']['locator'] else '') or r['Latin']['alignment_window_paragraph']
 note=r['Latin'].get('notice')
 if not r['implementation_approved']:note='Editorial decision pending. No approved Latin interval is presented in this local rehearsal; this is not a certified absence claim. Greek and English remain accessible.'
 if n==212:note='Provisional adjoining extent: this rehearsal preserves the dating clause within the 212 interval while the 214 cut is pending. This combined extent is not certified as correspondence exclusively to Greek 212.'
 sections.append({'number':n,'Latin':{'available':available,'correspondence':r['Latin'].get('correspondence') or ('PRESENT' if available else 'PENDING_EDITORIAL_DECISION'),'note':note},'contextTarget':context})
 if available:
  i=positioned.index(r);end=starts[positioned[i+1]['niese']] if i+1<len(positioned) else len(l.stream);latin[str(n)]=l.stream[starts[n]:end]
 else:latin[str(n)]=None
 english[str(n)]=''.join(u['text'] for u in bs['English'].units if context in u['element'].get('sameAs','').replace('#','').split())
 assert english[str(n)].strip(),n
registry={'schema':1,'book':b,'range':[1,len(rows)],'status':'PROVISIONAL_ROUTINE_REHEARSAL_NOT_CERTIFIED','suppressedLatinLabels':suppressed,'sections':sections}
save(RUNTIME/'site'/f'assets/xml/antiquities/niese/book-{b:02}.json',registry)
renderer=RUNTIME/'site/assets/js/renderTei.js';before=renderer.read_bytes();needle=b'12: "assets/xml/antiquities/niese/book-12.json"';assert before.count(needle)==1
after=before.replace(needle,needle+b',\n        13: "assets/xml/antiquities/niese/book-13.json"');renderer.write_bytes(after)
save(d/'ROUTINE_EXPECTED_INTERVALS.json',{'book':b,'status':'PROVISIONAL_ROUTINE_REHEARSAL_NOT_CERTIFIED','Greek':{str(r['niese']):r['Greek']['section'] for r in rows},'Latin':latin,'English':english,'registry':registry,'exclusions':{'Greek':bs['Greek'].excluded+bs['Greek'].inline_excluded,'Latin':l.excluded+l.inline_excluded},'excluded_from_final_certification':[212,213,214,216],'runtime_renderer_before_sha256':digest(before),'runtime_renderer_after_sha256':digest(after),'source_reader_unchanged':digest((ROOT/'assets/js/renderTei.js').read_bytes())==digest(before),'retained':retained,'inserted':[n for n in starts if n not in retained]})
assert (ROOT/'assets/js/renderTei.js').read_bytes()==before
print('Disposable rehearsal prepared; repository reader unchanged; suppressed claims',suppressed)
