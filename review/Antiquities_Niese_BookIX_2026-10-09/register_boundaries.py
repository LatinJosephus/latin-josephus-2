"""Build a reviewed register from individual decisions, frozen mixed text and print census.
No corpus mutation. Offsets always derive from this book's actual frozen bytes.
"""
from pathlib import Path
import json,re,sys,hashlib
from lxml import etree
from mixed_mapper import Book,fixtures,digest
P=Path(__file__).resolve().parent;W=P.parents[1]
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
base=read(P/'BASELINE.json');books={}
for lang in ['Greek','Latin','English']:
    rel=f'assets/xml/antiquities/{lang}/book-09.xml';raw=Path(base['inputs'][rel]['snapshot']).read_bytes()
    assert digest(raw)==base['inputs'][rel]['worktree_sha256'];books[lang]=Book(raw=raw)
g,l=books['Greek'],books['Latin'];notes={}
for line in (P/'LATIN_REVIEW_NOTES.txt').read_text(encoding='utf8').splitlines():
    if not line.strip() or line.startswith('#'):continue
    n,anchor,reason=line.split('|',2);assert int(n) not in notes;notes[int(n)]=(anchor,reason)
pages={}
for line in (P/'PRINT_PAGE_CENSUS.txt').read_text(encoding='utf8').splitlines():
    if not line.strip() or line.startswith('#'):continue
    pg,extent=line.split('|');a,b=map(int,extent.split('-'))
    for n in range(a,b+1):assert n not in pages;pages[n]=int(pg)
assert sorted(pages)==list(range(1,292))
gstarts={int(re.findall(r'\d+',m['text'])[-1]):g.first_content(m['book_offset']) for m in g.labels};gstarts[1]=g.first_content(0)
choices={1:gstarts[1],181:g.stream.index('τρία βέλη'),216:g.stream.index('τὸν αὐτὸν δὲ τρόπον')}
decision=read(P/'EDITORIAL_DECISIONS.json') if (P/'EDITORIAL_DECISIONS.json').exists() else {'240':{'status':'PENDING','choice':None}}
if decision['240']['choice']=='A':
    choices[240]=g.stream.index('ἔσται δ᾽ οὐδεὶς');notes[240]=('et nullus hanc uoluntatem','Adjudicated A: refusal and explanation are kept together; see DECISION_240.md and EDITORIAL_DECISIONS.json.')
elif decision['240']['choice']=='B':notes[240]=('dum animas suas','Adjudicated B: inherited Greek causal-clause start retained; see decision history.')
gstarts.update(choices)
initial=read(P/'INITIAL_GREEK_CENSUS.json');lstarts={};rows=[];exceptions=[];retained=[]
for n,(anchor,reason) in notes.items():
    target=initial[n-1]['latin_target'];u=next(u for u in l.units if u['id']==target)
    matches=[m.start() for m in re.finditer(re.escape(anchor),u['text'])]
    assert len(matches)==1,(n,target,anchor,matches)
    lstarts[n]=u['book_start']+matches[0]
assert sorted(lstarts)==sorted(gstarts)
assert all(lstarts[a]<lstarts[b] for a,b in zip(sorted(lstarts),sorted(lstarts)[1:])),[(a,b) for a,b in zip(sorted(lstarts),sorted(lstarts)[1:]) if lstarts[a]>=lstarts[b]]
for label in l.labels:
    claim=int(re.findall(r'\d+',label['text'])[-1]);pos=l.first_content(label['book_offset'])
    actual=max((n for n,k in lstarts.items() if k<=pos),default=None)
    item={'paragraph':label['id'],'label':label['text'],'visibleClaim':claim,'actualSection':actual,'label_raw_byte':label['raw_start'],'narrative_after_label':l.locate(pos)}
    if claim in lstarts and lstarts[claim]==pos:retained.append(claim)
    else:exceptions.append(item)
for n in range(1,292):
    available=n in lstarts;lp=lstarts.get(n);gp=gstarts.get(n)
    le=next((lstarts[m] for m in range(n+1,292) if m in lstarts),len(l.stream));ge=next((gstarts[m] for m in range(n+1,292) if m in gstarts),len(g.stream))
    r={'niese':n,'expected_identity':True,'Greek_print_verification':{'status':'VISUALLY_VERIFIED','edition':'Niese, Opera II, Berlin 1885','printed_page':pages[n]-8,'PDF_page':pages[n],'image':f'evidence/Niese-pdf-{pages[n]:03}.png','numeral_position':'implicit section 1 at book opening, no printed numeral' if n==1 else 'right margin beside narrative line; exact chosen word is recorded separately','observation_authority':'full narrative page manually inspected; lower-body supplement checked where needed'},'Latin_review_status':'INDIVIDUALLY_REVIEWED' if available else 'CONTEXTUALLY_VERIFIED_UNAVAILABLE','physical_placement_status':'LOCATED' if available else 'NO_NARRATIVE_START_IN_THIS_FILE','correspondence':'PARTIAL_SURVIVING_TAIL' if n==110 else ('REPRESENTED_WITH_RECORDED_LIMITS' if available else 'UNAVAILABLE_IN_PINNED_TRANSCRIPTIONS'),'correspondence_limits':notes[n][1] if available else 'Greek, Latin and English files each replace the entire 51–109 span with their preserved editorial placeholder. Printed Greek has the span; its cause and the broader Latin tradition are not inferred. Context reviewed across 49–50, placeholder and 110–111.','Greek_locator':g.locate(gp) if available else None,'Latin_locator':l.locate(lp) if available else None,'Greek_section':g.stream[gp:ge] if available else None,'Latin_section':l.stream[lp:le] if available else None,'Latin_paragraph_id':initial[n-1]['latin_target'],'Latin_chosen_anchor':notes[n][0] if available else None,'inherited_start_retained':n in retained,'Latin_end_book_offset':le if available else None,'Greek_end_book_offset':ge if available else None,'editorial_decision_status':'PENDING' if n==240 and decision['240']['status']=='PENDING' else 'CLOSED_ROUTINE_OR_AUTHORIZED','implementation_approved':not(n==240 and decision['240']['status']=='PENDING'),'outstanding_editorial_decision':n==240 and decision['240']['status']=='PENDING'}
    rows.append(r)
    r['extent_status']='PENDING_ADJOINING_BOUNDARY' if n in [239,240] and decision['240']['status']=='PENDING' else ('REVIEWED_REPRESENTED_INTERVAL' if available else 'UNAVAILABLE_IDENTITY_WITHOUT_INTERVAL')
    for lang in ['Greek','Latin']:
        if r[lang+'_locator']:r[lang+'_locator']['input_sha256']=base['inputs'][f'assets/xml/antiquities/{lang}/book-09.xml']['worktree_sha256']
def validate_locator(book,loc):
    if loc is None:return
    path=loc['text_node_path'];nodepath,kind=path.rsplit('/',1)
    # Independent XPath traverses lxml elements, handling sibling positions including comments.
    nodes=book.tree.xpath(nodepath.replace('/', '/t:').replace('t:comment()', 'comment()'),namespaces={'t':'http://www.tei-c.org/ns/1.0'})
    assert len(nodes)==1,(nodepath,len(nodes));value=nodes[0].tail if kind=='tail()' else nodes[0].text
    assert value[loc['node_offset']:].startswith(loc['right'][:min(len(value)-loc['node_offset'],30)])
    assert book.raw[loc['raw_byte']:].decode('utf8').startswith(value[loc['node_offset']:loc['node_offset']+min(15,len(value)-loc['node_offset'])])
for row in rows:
    validate_locator(g,row['Greek_locator']);validate_locator(l,row['Latin_locator'])
write(P/'BOUNDARIES.json',rows)
write(P/'EXECUTABLE_IDENTITIES.json',{'book':9,'expected_sections':291,'represented_Latin_intervals':len(lstarts),'retained_visible_starts':retained,'retained_count':len(retained),'suppressedLatinLabels':exceptions,'new_milestones':sorted(set(lstarts)-set(retained)),'unavailable_sections':list(range(51,110)),'pending':[r['niese'] for r in rows if r['outstanding_editorial_decision']]})
write(P/'GREEK_MARKER_PLAN.json',{'opening_addition':{'niese':1,'locator':g.locate(gstarts[1])},'relocations':[{'niese':n,'original_label':next(m for m in g.labels if m['text']==f'[{n}]'),'chosen_locator':g.locate(gstarts[n]),'authority':'Niese printed line independently checked with Loeb; routine correction' if n in [181,216] else 'User adjudication of DECISION_240.md'} for n in choices if n!=1],'pending_240':decision['240']['status']=='PENDING'})
english={str(r['niese']):(''.join(u['text'] for u in books['English'].units if u['element'].get('sameAs')=='#'+r['Latin_paragraph_id']) if r['Latin_locator'] else None) for r in rows}
expected={'9':{'Greek':{str(r['niese']):r['Greek_section'] for r in rows},'Latin':{str(r['niese']):r['Latin_section'] for r in rows},'EnglishContext':english,'LatinFull':l.stream,'GreekFull':g.stream,'inherited':len(retained),'milestones':len(lstarts)-len(retained)}}
write(P/'EXPECTED_INTERVALS.json',expected)
write(P/'REGISTER_VALIDATION.json',{'status':'PASS','fixtures':fixtures(),'independent_lxml_text_tail_and_raw_byte_locators':len(lstarts)*2,'strictly_ordered_starts':True,'narrative_stream_lengths':{lang:len(b.stream) for lang,b in books.items()},'excluded':{lang:b.excluded for lang,b in books.items()},'pending':[r['niese'] for r in rows if r['outstanding_editorial_decision']]})
lines=['# IX boundary review','',f'291 printed identities; {len(lstarts)} represented Latin intervals; 59 unavailable identities; {len(retained)} retained starts; {len(lstarts)-len(retained)} new milestone candidates.','', '| § | Print page / PDF | Latin paragraph and start | Review and correspondence limits | Decision |','|---|---|---|---|---|']
for r in rows:
    loc=r['Latin_locator'];cut=(f"{loc['stable_id']} · {r['Latin_chosen_anchor']} · node {loc['node_offset']}, UTF-8 byte {loc['raw_byte']}" if loc else 'Unavailable; preserved source placeholder')
    lines.append(f"| {r['niese']} | [{pages[r['niese']]-8} / {pages[r['niese']]}]({r['Greek_print_verification']['image']}) | {cut} | {r['correspondence_limits']} | {r['editorial_decision_status']} / {r['extent_status']} |")
(P/'BOUNDARIES.md').write_text('\n'.join(lines)+'\n',encoding='utf8',newline='\n')
print(json.dumps({'represented':len(lstarts),'retained':len(retained),'milestones':len(lstarts)-len(retained),'suppressed':exceptions,'pending':decision},ensure_ascii=False,indent=2))
