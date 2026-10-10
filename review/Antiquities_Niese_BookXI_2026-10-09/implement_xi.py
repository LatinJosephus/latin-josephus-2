"""Materialize reviewed cuts only; physical ownership and logical assembly are separate."""
from pathlib import Path
import json,re,sys,collections
sys.dont_write_bytecode=True
from mixed_mapper import Book,digest,NS,XMLID
D=Path(__file__).resolve().parent;ROOT=D.parents[1]
def save(name,x):(D/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
def main():
 bs={x:Book(D/'inputs'/f'{x}.xml') for x in ['Latin','Greek','English']};l=bs['Latin'];g=bs['Greek']
 choices=json.loads((D/'review_choices.json').read_text(encoding='utf8'));rows=json.loads((D/'CANDIDATE_REGISTER.json').read_text(encoding='utf8'))
 assert set(map(int,choices['choices']))==set(range(1,302))
 decision=json.loads((D/'INTERPOLATION_DECISION.json').read_text(encoding='utf8'));assert decision['status']=='CLOSED_USER_APPROVED'
 observations=json.loads((D/'PRINT_OBSERVATIONS.json').read_text(encoding='utf8'))
 observed={n:p for p in observations['pages'] for n in p['identities']};assert sorted(observed)==list(range(1,348)) and sum(len(p['identities']) for p in observations['pages'])==347
 physical=[]
 def cut(n,pid,phrase,rank,note):
  u=next(u for u in l.units if u['id']==pid);assert u['text'].count(phrase)==1,(n,pid,phrase)
  at=u['book_start']+u['text'].index(phrase)
  # Only a label directly adjoining this reviewed word-cut can locate it.
  labels=[x for x in l.labels if x['id']==pid and x['book_offset']<=at and not l.stream[x['book_offset']:at].strip()]
  label=next((x for x in labels if re.search(r'(?:^|\.)'+str(n)+r'\]$',x['text'])),None)
  if n==1:offset=0;method='RETAINED_PARAGRAPH_START';label=None
  elif label:offset=label['book_offset'];method='REVIEWED_RETAINED_LABEL'
  else:offset=at;method='REVIEWED_NEW_WORD_CUT'
  physical.append(dict(number=n,rank=rank,offset=offset,label=label,method=method,reviewed_phrase=phrase,review_notes=note))
 for sn,(pid,phrase,note) in choices['choices'].items():cut(int(sn),pid,phrase,1,note)
 for sn,extra in choices['additional_fragments'].items():
  for pid,phrase,rank,note in extra:cut(int(sn),pid,phrase,rank,note)
 tail=json.loads((D/'WINDOW_302_347_PHYSICAL_LEDGER.json').read_text(encoding='utf8'))
 for f in tail:
  keep={k:v for k,v in f.items() if k in ['number','rank','offset','label','method','phrase','identity','role']}
  keep['review_notes']=rows[f['number']-1]['Latin']['review_notes'] if 'number' in f else 'Separately recorded physical Latin Bellum passage; approved affiliation before its corresponding312 portion.'
  if f.get('role'):keep.update(association=312,association_status='CLOSED_USER_APPROVED',Antiquities_identity=False,traditional_affiliation=f['traditional_affiliation'])
  physical.append(keep)
 physical.sort(key=lambda f:f['offset']);assert physical[0]['offset']==0 and len(set(f['offset'] for f in physical))==len(physical)
 additions=[];number_counts=collections.Counter(f.get('number') for f in physical)
 for f in physical:
  f['occurrence']=f'Latin-XI-{f.get("number",f.get("identity"))}-{f["rank"]}'
  if not f.get('label') and f['offset']!=0:
   suffix=f'-{f["rank"]}' if number_counts[f['number']]>1 else ''
   f['new_anchor']=f'latin-book11-niese-{f["number"]}{suffix}'
   tag=f'<milestone unit="niese" n="{f["number"]}" xml:id="{f["new_anchor"]}"/>'
   additions.append(dict(offset=l.locate(f['offset'])['raw_byte'],addition=tag,number=f['number'],rank=f['rank'],id=f['new_anchor'],kind='start-marker'))
 def point(lang,offset,label=None,anchor=None):
  b=bs[lang]
  if offset==len(b.stream):
   u=next(u for u in reversed(b.units) if u['text']);assert u['id'];return dict(available='true',target=u['id'],kind='paragraph-end')
  if anchor:return dict(available='true',target=anchor,kind='element')
  if label:
   u=b.units[label['unit']-1];nums=u['element'].xpath('./t:num',namespaces=NS)
   ordinal=next(i+1 for i,num in enumerate(nums) if ''.join(num.itertext())==label['text']);return dict(available='true',target=u['id'],kind='element-edge',edge=f'num[{ordinal}]')
  u=b.units[b.locate(b.first_content(offset))['paragraph']-1];assert offset==u['book_start'] and u['id'],(lang,offset)
  return dict(available='true',target=u['id'],kind='paragraph')
 latinspans={};sources=[]
 for i,f in enumerate(physical):
  nxt=physical[i+1] if i+1<len(physical) else None;end=nxt['offset'] if nxt else len(l.stream)
  f.update(start=l.locate(f['offset']),end=l.locate(end) if nxt else l.terminal_locator(),text=l.stream[f['offset']:end])
  f['narrative_sha256']=digest(f['text'].encode());f['runtime_span']=dict(start=point('Latin',f['offset'],f.get('label'),f.get('new_anchor')),end=point('Latin',end,nxt.get('label'),nxt.get('new_anchor')) if nxt else point('Latin',end),occurrence=f['occurrence'],role='interpolation' if f.get('role') else 'primary',continuationRank=f['rank'],label=f.get('identity') or f'Antiquities XI.{f["number"]} portion{f["rank"]}')
  if f.get('role'):
   f['runtime_span']['sourceLabel']=f'Interpolated Latin Bellum Judaicum IV.105{f["identity"][-1]}';f['runtime_span']['attachmentBeforeRank']=1 if f['identity'].endswith('a') else 2;sources.append(f)
  else:latinspans.setdefault(f['number'],[]).append(f['runtime_span'])
 for spans in latinspans.values():spans.sort(key=lambda s:s['continuationRank'])
 assert sorted(latinspans)==list(range(1,348))
 primary312=list(latinspans[312]);latinspans[312]=[sources[0]['runtime_span'],primary312[0],sources[1]['runtime_span'],primary312[1]]
 glabels=[x for x in g.labels if re.fullmatch(r'\[\d+\]',x['text'])];gp=[dict(number=1,book_offset=0)]+[dict(number=int(x['text'][1:-1]),book_offset=x['book_offset'],label=x) for x in glabels]
 greekspans={};gledger=[]
 for i,f in enumerate(gp):
  nxt=gp[i+1] if i+1<len(gp) else None;end=nxt['book_offset'] if nxt else len(g.stream)
  span=dict(start=point('Greek',f['book_offset'],f.get('label')),end=point('Greek',end,nxt.get('label')) if nxt else point('Greek',end),occurrence=f'Greek-XI-{f["number"]}',role='primary',continuationRank=1)
  greekspans[f['number']]=[span];gledger.append(dict(number=f['number'],start=g.locate(f['book_offset']),end=g.locate(end) if nxt else g.terminal_locator(),text=g.stream[f['book_offset']:end],runtime_span=span))
 fragmentnotice='Canonical order from separate witness fragments. Book view preserves Bamberg’s manuscript order.'
 interpolation='Bamberg preserves a transposed sequence with two separated portions of Latin Bellum Judaicum IV.105, interpolated before the corresponding portions of Antiquities XI.312. The Antiquities portions appear as 312a then 312b; both Bellum passages remain separately identified.'
 sections=[];expected={}
 for r in rows:
  n=r['number'];p=observed[n];runtime=Path('C:/workspace/Antiquities-Niese-11-runtime-20261009');image=next(q for q in [runtime/f'Niese-body-{p["PDF"]:03}.jpg',runtime/f'tail-{p["PDF"]:03}.jpg',runtime/f'Niese-{p["PDF"]:03}.jpg'] if q.exists())
  r['Greek'].update(print_status='VERIFIED_PAGE_IMAGE',print_observation={k:p[k] for k in ['PDF','print','position']},edition=observations['edition'],image=str(image),word_interpretation='FULL_SECTION_AND_NEIGHBOURS_REVIEWED; inherited Greek word cut retained; marginal numeral observation separately recorded')
  if n==347:r['Greek']['end']=g.terminal_locator()
  fs=[f for f in physical if f.get('number')==n];fs.sort(key=lambda f:f['rank']);note=choices['choices'][str(n)][2] if n<=301 else r['Latin']['review_notes']
  qualification=choices['qualified'].get(str(n),'reviewed-present')
  if n in [318,319,332,344,345,347]:qualification='reviewed-inherited-label-qualified'
  r['Latin'].update(fragments=fs,review_status='INDIVIDUALLY_REVIEWED',correspondence=qualification,review_notes=note)
  r.update(physical_locator_status='FROZEN_LOCATORS_PENDING_INDEPENDENT_FINAL_VALIDATION',editorial_status='CLOSED_ROUTINE_REVIEW' if n!=312 else 'CLOSED_USER_APPROVED_INTERPOLATION_AFFILIATION',implementation_approved=True)
  engpid=r['Greek']['start']['stable_id'].replace('greek-','english-');eu=next(u for u in bs['English'].units if u['id']==engpid)
  lat=dict(available=True,correspondence=qualification,spans=latinspans[n])
  if qualification!='reviewed-present':lat['note']='Latin correspondence: '+note
  if n in [72,326,342]:lat['fragmentNotice']=fragmentnotice
  if n==312:lat['fragmentNotice']=interpolation+' '+fragmentnotice
  sections.append(dict(number=n,Latin=lat,Greek=dict(available=True,spans=greekspans[n],printVerified=True),English=dict(contextTargets=[engpid],correspondence='existing-contextual'),contextTarget=r['Latin']['alignment_window']))
  display=([sources[0],fs[0],sources[1],fs[1]] if n==312 else fs)
  expected[str(n)]=dict(Latin=''.join(f['text'] for f in display),Latin_primary=''.join(f['text'] for f in fs),Greek=r['Greek']['text'],English=eu['text'],English_context_targets=[engpid],occurrences=[f['occurrence'] for f in display],primary_occurrences=[f['occurrence'] for f in fs],qualification=qualification)
 suppressed=[]
 for x in l.labels:
  m=re.search(r'(\d+)([ab]?)\]$',x['text'])
  if not m:continue
  n=int(m[1]);valid=any(f.get('number')==n and f.get('label')==x for f in physical)
  if not valid:suppressed.append(dict(paragraph=x['id'],label=x['text'],reason='Visible inherited label is not an executable Antiquities identity start; use explicit reviewed fragment records.'))
 registry=dict(schema=1,book=11,range=[1,347],suppressedLatinLabels=suppressed,sections=sections,sourcePassages=[dict(identity=f['identity'],occurrence=f['occurrence'],AntiquitiesIdentity=False,primaryAntiquitiesFragment=False,span=f['runtime_span'],association=312,position='before-corresponding-portion',editorialStatus='CLOSED_USER_APPROVED') for f in sources])
 raw=l.raw
 for op in sorted(additions,key=lambda op:op['offset'],reverse=True):raw=raw[:op['offset']]+op['addition'].encode()+raw[op['offset']:]
 latinpath=ROOT/'assets/xml/antiquities/Latin/book-11.xml';registry_path=ROOT/'assets/xml/antiquities/niese/book-11.json'
 assert latinpath.read_bytes() in [l.raw,raw],'Refuse to replace unexpected source edits'
 latinpath.write_bytes(raw);registry_path.write_text(json.dumps(registry,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
 save('IDENTITY_REGISTER.json',rows);save('LATIN_PHYSICAL_COVERAGE.json',physical);save('GREEK_PHYSICAL_COVERAGE.json',gledger);save('EXPECTED_SELECTIONS.json',expected);save('AUTHORIZED_ADDITIONS.json',additions)
 save('EDIT_PLAN.json',dict(status='IMPLEMENTED_REVIEWED_CUTS',Latin='Only zero-width start milestones; no original byte replaced',Greek='No changes; implicit1 explicitly registered and printed evidence confirms it',English='No changes; existing contextual paragraphs reused independently',registry='Explicit primary occurrences with bounded endpoints and continuation ranks; two separately recorded Bellum source occurrences before312 portions',unresolved_decisions=[],counts=dict(logical_identities=347,identities_with_Latin=347,identities_without_independent_Latin=[],primary_Latin_fragments=sum(len([f for f in physical if f.get('number')==n]) for n in latinspans),source_only_fragments=len(sources),retained_physical_boundaries=sum(bool(f.get('label')) or f['offset']==0 for f in physical),added_start_markers=len(additions),added_end_markers=0,other_new_anchors=0),files=['assets/xml/antiquities/Latin/book-11.xml','assets/xml/antiquities/niese/book-11.json','assets/js/renderTei.js','assets/css/tei.css']))
 choices['status']='COMPLETE_INDIVIDUAL_REVIEW_1_301; tail302_347 separately complete';save('review_choices.json',choices)
 observations['all347_reviewed']=True;observations['inspected_body_pages']=67;observations['word_boundary_interpretation']='Recorded separately per identity, not inferred solely from marginal numeral position';save('PRINT_OBSERVATIONS.json',observations)
 print(json.dumps(json.loads((D/'EDIT_PLAN.json').read_text())['counts']))
if __name__=='__main__':main()
