"""Reproduce the read-only candidate register. Never edits a production file.

Manual phrases are hypotheses, not application authority. Frozen print starts
can certify a retained start only when the Greek incipit agrees and no specific
case is open. Every other row remains pending. Offsets refer to pinned LF bytes.
"""
from pathlib import Path
import argparse, csv, json, re, hashlib, unicodedata, collections
from lxml import etree
from mixed_mapper import Book, fixtures, digest, NS

def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def norm(s):return ''.join(c.lower() for c in unicodedata.normalize('NFKD',s) if c.isalpha())
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--book',type=int,choices=[8,10],required=True);ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--packet',type=Path,required=True);args=ap.parse_args()
 p=args.packet;b=args.book;baseline=json.loads((p/'BASELINE.json').read_text(encoding='utf-8'));anchors=json.loads((p/'CANDIDATE_ANCHORS.json').read_text(encoding='utf-8'));cases=json.loads((p/'CASES.json').read_text(encoding='utf-8'));frozen=json.loads((p/'FROZEN_PRINT_STARTS.json').read_text(encoding='utf-8'))
 paths={lang:args.repo/f'assets/xml/antiquities/{lang}/book-{b:02}.xml' for lang in ['Greek','Latin','English']}
 for lang,path in paths.items():
  assert digest(path.read_bytes())==baseline['inputs'][lang]['worktree_before_sha256'],f'Pinned {lang} hash mismatch; refuse audit'
 fixtures();g=Book(paths['Greek']);l=Book(paths['Latin']);total=baseline['niese']['expected_count']
 nums={int(re.search(r'\d+',m['text'])[0]):m for m in g.labels};assert sorted(nums)==list(range(2,total+1));assert len(g.labels)==total-1
 starts={n:g.first_content(m['book_offset']) for n,m in nums.items()};starts[1]=g.first_content(next(u['book_start'] for u in g.units if u['text'].strip()))
 labels={int(re.findall(r'\d+',m['text'])[-1]):m for m in l.labels}
 rows=[]
 for n in range(1,total+1):
  gp=g.locate(starts[n]);gu=g.units[gp['paragraph']-1];gt=g.stream[starts[n]:starts.get(n+1,len(g.stream))].strip();case=cases.get(str(n));ev=[r for r in frozen if int(r['niese_printed_section'])==n]
  before=[r for r in frozen if int(r['niese_printed_section'])<=n];after=[r for r in frozen if int(r['niese_printed_section'])>n]
  lo=max(before,key=lambda r:int(r['niese_printed_section']))
  hi=min(after,key=lambda r:int(r['niese_printed_section'])) if after else None
  span=[int(lo['niese_printed_page']),int(hi['niese_printed_page']) if hi else baseline['printed']['niese_last_page']]
  if ev:span=[min(int(r['niese_printed_page']) for r in ev),max(int(r['niese_printed_page']) for r in ev)]
  # A within-section traditional start only brackets a search; it does not
  # certify the Greek section incipit (notably VIII.255).
  print_ok=any(r['verification_status']=='CONFIRMED_NIESE_START' and norm(gt).startswith(norm(r['greek_text_anchor'])) for r in ev)
  direct=baseline['direct_verified_internal_starts'].get(str(n))
  if direct:print_ok=True;span=direct['niese_printed_pages']
  if case and case.get('niese_printed_pages'):span=case['niese_printed_pages']
  lp=None;phrase=anchors.get(str(n));status='REQUIRES_ADJUDICATION';placement=None;inherited=False
  if phrase:
   target=gu['element'].get('sameAs','').lstrip('#')
   if (b,n)==(8,255):target='latin-book08-num251'
   if (b,n)==(10,150):target='latin-book10-num151'
   lu=next(u for u in l.units if u['id']==target)
   assert lu['text'].count(phrase)==1,(b,n,phrase,target,'anchor must be unique in its specified paragraph')
   offset=lu['book_start']+lu['text'].index(phrase);lp=l.locate(offset)
   inherited=n in labels and labels[n]['id']==lu['id'] and offset==l.first_content(labels[n]['book_offset'])
   placement='INHERITED_START' if inherited else 'PROPOSED_INTERNAL_MILESTONE'
   if print_ok and not case:status='EXACT' if inherited else ('INTERNAL-BUT-EXACT' if direct else 'REQUIRES_ADJUDICATION')
  elif case and case['kind']=='UNAVAILABLE':status='UNAVAILABLE';placement='NO_LATIN_START'
  else:raise AssertionError(('Unaccounted boundary',b,n))
  if case and case['kind']!='UNAVAILABLE':status='REQUIRES_ADJUDICATION'
  reason=(case['reason'] if case else ('Independent printed Greek start and individually read Latin counterpart agree.' if status in ['EXACT','INTERNAL-BUT-EXACT'] else 'Complete candidate alignment; exact internal Greek word boundary has not received independent full-book print collation. Arithmetic and a unique XML byte locator do not certify this boundary.'))
  alts=[]
  if case:
   for alt in case.get('alternatives',[]):
    found=[]
    for u in l.units:
     start=0
     while alt in u['text'][start:]:
      k=u['text'].index(alt,start);found.append(l.locate(u['book_start']+k));start=k+len(alt)
    alts.append(dict(phrase=alt,locators=found))
  rawlabel=labels.get(n)
  rows.append(dict(book=b,niese=n,greek_start=gt[:240],greek_section=gt,greek_locator=gp,greek_opening_representation='implicit at printed book opening' if n==1 else 'existing num',latin_start=l.stream[lp['book_offset']:lp['book_offset']+240] if lp else None,latin_anchor_phrase=phrase,latin_locator=lp,latin_paragraph_id=lp['stable_id'] if lp else None,placement=placement,inherited_start_retained=inherited,existing_composite_label=rawlabel['text'] if rawlabel else None,existing_label_paragraph=rawlabel['id'] if rawlabel else None,existing_label_is_physical_Niese_start=inherited,classification=status,confidence='HIGH' if status in ['EXACT','INTERNAL-BUT-EXACT'] else ('HIGH_ABSENCE_IN_THIS_TRANSCRIPTION' if status=='UNAVAILABLE' else 'PENDING_EDITORIAL_VERIFICATION'),verification_reason=reason,print_start_verified=print_ok,independent_source_evidence=dict(niese_volume='II (1885)',niese_pdf_sha256=baseline['printed']['niese_pdf_sha256'],niese_printed_page_search_range=span,niese_pdf_page_search_range=[v+8 for v in span],word_start_independently_verified=print_ok,page_search_range_basis='frozen printed starts bracketing this citation, or identified current-run scan control',frozen_rows=ev,direct_current_run=direct,remaining_print_work=None if print_ok else 'Verify canonical Greek word start against Niese scan; a marginal number on a line is not a word-offset locator.',loeb_role='independent contextual control; not numbering authority'),alternative_positions=alts,human_decision=None,implementation_approved=False))
 positioned=[r for r in rows if r['latin_locator']]
 assert all(a['latin_locator']['book_offset']<z['latin_locator']['book_offset'] for a,z in zip(positioned,positioned[1:]))
 prefix=l.stream[:positioned[0]['latin_locator']['book_offset']];pieces=[]
 for i,r in enumerate(positioned):
  k=r['latin_locator']['book_offset'];end=positioned[i+1]['latin_locator']['book_offset'] if i+1<len(positioned) else len(l.stream)
  r['candidate_latin_end_book_offset']=end;r['candidate_latin_section']=l.stream[k:end];pieces.append(l.stream[k:end]);assert l.stream[k:end].strip()
 assert prefix+''.join(pieces)==l.stream
 # In-memory technical rehearsal of all candidate additions, including
 # unresolved positions. It is deliberately not an approved insertion plan.
 additions=[(r['latin_locator']['raw_byte'],f'<milestone unit="niese" n="{r["niese"]}"/>'.encode()) for r in positioned if not r['inherited_start_retained']]
 raw=l.raw;test=raw
 assert not re.search(rb'<milestone\s+unit="niese"',raw)
 for offset,tag in sorted(additions,reverse=True):test=test[:offset]+tag+test[offset:]
 restored=test
 for _,tag in additions:assert restored.count(tag)==1;restored=restored.replace(tag,b'',1)
 assert restored==raw
 etree.fromstring(test)
 counts=dict(collections.Counter(r['classification'] for r in rows));placements=dict(collections.Counter(r['placement'] for r in rows))
 save(p/'BOUNDARIES.json',rows)
 columns=['book','niese','classification','confidence','placement','latin_paragraph_id','latin_anchor_phrase','greek_start','latin_start','verification_reason','greek_locator','latin_locator','independent_source_evidence','alternative_positions','human_decision','implementation_approved']
 with (p/'BOUNDARIES.tsv').open('w',encoding='utf-8',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=columns,delimiter='\t',extrasaction='ignore');writer.writeheader()
  for r in rows:writer.writerow({k:json.dumps(r[k],ensure_ascii=False) if isinstance(r[k],(dict,list)) else r[k] for k in columns})
 nodes=[]
 for u in l.units:
  for node in u['nodes']:nodes.append(dict(paragraph_id=u['id'],text_node_path=node['path'],text=node['text'],unit_start=node['unit_start'],book_start=node['book_start'],raw_byte_positions=node['raw_positions'],raw_unit_sha256=u['raw_hash']))
 save(p/'LATIN_TEXT_NODE_LEDGER.json',nodes)
 save(p/'CANDIDATE_DRY_RUN.json',dict(status='TECHNICAL_REHEARSAL_ONLY_NOT_APPROVED',candidate_markers=len(additions),source_sha256=digest(raw),candidate_bytes_sha256=digest(test),removed_authorized_candidate_strings_recovers_original=True,parsed_candidate_XML=True,application_permitted=False,source_files_written=0,warning='This rehearsal proves byte-safe insertion mechanics only. It neither certifies Greek/Latin correspondence nor resolves duplicate inherited labels or unavailable sections.'))
 save(p/'INSERTION_PLAN.json',dict(status='NO_GO',book=b,approved_insertions=[],approved_greek_repairs=[],source_sha256=digest(raw),apply_permitted=False,reason='Book-wide scholarly gate not passed. Candidate anchors and technical rehearsal are not editorial approval.'))
 save(p/'AUDIT_RESULT.json',dict(book=b,expected_niese_count=total,boundary_records=len(rows),classifications=counts,placements=placements,raw_inherited_label_claims=len(labels),retained_candidate_inherited_starts=sum(r['inherited_start_retained'] for r in rows),proposed_candidate_milestones=len(additions),unavailable=[r['niese'] for r in rows if r['classification']=='UNAVAILABLE'],specific_review_cases=[int(n) for n in cases],new_markers_applied=0,greek_repairs_applied=0,GO=False,mixed_content_mapper_fixtures='PASS',all_locators_unique_in_specified_paragraph=True,all_positioned_candidates_strictly_ordered=True,candidate_narrative_partition_recovers_original=True,all_candidate_sections_nonempty=True,independent_full_book_print_collation='INCOMPLETE',application='NOT_ATTEMPTED'))
 print(b,counts,placements,'candidate byte rehearsal PASS; implementation NO-GO')
if __name__=='__main__':main()
