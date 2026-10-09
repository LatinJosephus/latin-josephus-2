"""Rebuild the print-collation addendum from committed candidate audits.
Only the three review packets may be written. Never changes XML, code or Git state.
Visual observations are human-readable evidence inputs, not automated certification.
Usage: python followup_collation.py [isolated-repository-root]
"""
import pathlib,sys,json,hashlib,subprocess,unicodedata,csv,collections,copy
from followup_decisions import DECISIONS
W=pathlib.Path(sys.argv[1]).resolve() if len(sys.argv)>1 else pathlib.Path(__file__).resolve().parents[2]
B=W/'review/Antiquities_Niese_Batch_08_10_2026-10-08'
sys.path.insert(0,str(W/'review/Antiquities_Niese_BookVIII_2026-10-08'))
from mixed_mapper import Book,fixtures
BASE='1cf003beeb03f7b0acf2c42057ace062cdb7ebff'
COMMITS={8:'cc86a1d3ef3626a04b44032b9c8fc60293a44bff',10:'da28ec5abd7084fe5199549e2e38488171505c0e', 'batch':'39c9b60803f38806872a9c0a6a905c92ffa03d3e'}
def sha(x):return hashlib.sha256(x).hexdigest()
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
def oldfile(commit,p):return subprocess.check_output(['git','show',f'{commit}:{p.relative_to(W).as_posix()}'],cwd=W)
def normalize(s):
 chars=[];offset=[]
 for i,c in enumerate(s):
  for q in unicodedata.normalize('NFD',c.lower().replace('ς','σ')):
   if q.isalpha():chars.append(q);offset.append(i)
 return ''.join(chars),offset
def find(book,phrase,around):
 lo=max(0,around-2500);hi=min(len(book.stream),around+2500);text=book.stream[lo:hi]
 norm,offset=normalize(text);needle=normalize(phrase)[0];positions=[];at=norm.find(needle)
 while at>=0:positions.append(lo+offset[at]);at=norm.find(needle,at+1)
 assert len(positions)==1,(phrase,positions)
 return book.locate(positions[0])
def locator_text(loc):
 if not loc:return 'No Latin start locator (historical unavailable record).'
 return f"`{loc['stable_id']}`; `{loc['text_node_path']}`; node offset **{loc['node_offset']}**, paragraph offset **{loc['unit_offset']}**, UTF-8 byte **{loc['raw_byte']}** (zero-based, pinned LF bytes)."
def snippet(book,loc,left=150,right=340):
 if not loc:return '(No start locator.)'
 p=loc['book_offset'];return book.stream[max(0,p-left):p]+' **⟦candidate cut⟧** '+book.stream[p:p+right]
def table(cross):
 out=['| Placement | EXACT | INTERNAL-BUT-EXACT | REQUIRES_ADJUDICATION | UNAVAILABLE | Total |','|---|---:|---:|---:|---:|---:|']
 for place,cc in cross.items():out.append('| '+place+' | '+' | '.join(str(cc.get(k,0)) for k in ['EXACT','INTERNAL-BUT-EXACT','REQUIRES_ADJUDICATION','UNAVAILABLE'])+' | '+str(sum(cc.values()))+' |')
 return '\n'.join(out)
summaries={};allrepairs=[]
for b,roman,end in [(8,'VIII',420),(10,'X',281)]:
 d=W/f'review/Antiquities_Niese_Book{roman}_2026-10-08'
 checkpoint=oldfile(COMMITS[b],d/'BOUNDARIES.json');rows=json.loads(checkpoint)
 observations=json.loads((d/'PRINT_OBSERVATIONS.json').read_text(encoding='utf8'));assert len(observations)==end
 books={lang:Book(path=W/f'assets/xml/antiquities/{lang}/book-{b:02}.xml') for lang in ['Greek','Latin']}
 baseline=json.loads((d/'BASELINE.json').read_text(encoding='utf8'))
 for lang,item in baseline['inputs'].items():assert sha((W/item['path']).read_bytes())==item['worktree_before_sha256']
 current_cases={};history=[];repairs=[];cross=collections.defaultdict(collections.Counter);confidence_cross=collections.defaultdict(collections.Counter);work=collections.Counter();printcounts=collections.Counter()
 for row,obs in zip(rows,observations):
  n=row['niese'];assert n==obs['niese'];case=copy.deepcopy(DECISIONS[b].get(n))
  original={k:copy.deepcopy(row[k]) for k in ['classification','confidence','print_start_verified','greek_start','greek_locator','latin_anchor_phrase','latin_locator','placement']}
  status='AGREES_WITH_FROZEN_CLAUSE_LOCATOR';obstacle=None
  if n==1:status='IMPLICIT_PRINTED_OPENING_VERIFIED'
  if case and case.get('greek_proposal'):status='DISAGREES_WITH_FROZEN_PROPOSED_RELOCATION'
  if case and case.get('word_obstacle'):
   status='WORD_START_REQUIRES_SOURCE_INTERPRETATION'
   obstacle=f'{roman}.{n}: Niese II p.{obs["printed_page"]}/PDF{obs["pdf_page"]}; Loeb control PDF pages {case.get("loeb",[])}. '+case['reason']+' All attempted pages are legible and were read; the concrete obstacle is marginal-line precision, not access or unfinished page reading.'
  if b==8 and n in [376,377]:status='PRINT_NUMERAL_ANOMALY_XML_SEQUENCE_INDEPENDENTLY_SUPPORTED'
  collation=dict(obs,greek_print_status=status,canonical_word_cut_verified=status not in ['DISAGREES_WITH_FROZEN_PROPOSED_RELOCATION','WORD_START_REQUIRES_SOURCE_INTERPRETATION'],
    routine_image_collation_complete=True,verification_obstacle=obstacle,printed_line_is_not_a_word_tag=True,
    agreement_scope='Citation identity and passage location, interpreting the marginal line with its clause context. This is not a full spelling/variant collation or a claim that the print embeds word delimiters.',
    confidence_scope='Greek source collation only; does not promote Latin classification or approve implementation.')
  if case:
   case.update(book=b,niese=n,human_decision=None,implementation_approved=False,greek_source=collation,checkpoint_classification=row['classification'],checkpoint_confidence=row['confidence'])
   case['earlier_candidate']=original
   case['proposed_candidate']=None
   if case.get('greek_proposal') or case.get('greek_alternative') or case.get('latin_only_alternative'):
    phrase=case.get('greek_proposal',case.get('greek_alternative'));lp=case.get('latin_proposal',case.get('latin_alternative',case.get('latin_only_alternative')))
    gl=find(books['Greek'],phrase,row['greek_locator']['book_offset']) if phrase else row['greek_locator'];phrase=phrase or row['greek_start'][:40]
    ll=find(books['Latin'],lp,row['latin_locator']['book_offset'])
    proposal=dict(approved=False,apply=False,kind='RELOCATION_RECOMMENDED' if case.get('greek_proposal') else 'LATIN_ONLY_REASSESSMENT' if case.get('latin_only_alternative') else 'ALTERNATIVE_REQUIRES_WORD_DECISION',greek_phrase_as_canonical=gl['right'][:len(phrase)+60],greek_locator=gl,latin_phrase_as_canonical=ll['right'][:len(lp)+60],latin_locator=ll,
      neighbouring_extents={'previous_niese':n-1,'current_niese':n,'following_niese':n+1,'previous_Greek_end_changes_from':row['greek_locator']['book_offset'],'previous_Greek_end_changes_to':gl['book_offset'],'previous_Latin_end_changes_from':row['latin_locator']['book_offset'],'previous_Latin_end_changes_to':ll['book_offset'],
       'following_start_unchanged':rows[n]['greek_locator']['book_offset'] if n<end else None,'rule':'Only proposed adjacent extents change. No text moves, disappears or overlaps; interval endpoints are half-open book offsets. No actual section or XML is changed.'})
    marker=next(l for l in books['Greek'].labels if l['text'].strip()==f'[{n}]');mstart=marker['raw_start'];mend=books['Greek'].raw.index(b'</num>',mstart)+len(b'</num>')
    proposal['existing_Greek_marker_on_pinned_input']={'raw_start':mstart,'raw_end_exclusive':mend,'text_node_path':marker['path'],'exact_XML':books['Greek'].raw[mstart:mend].decode('utf8'),'replacement_location':'greek_locator above, measured against original input before any removal; no executable patch or replacement has been approved.'}
    case['proposed_candidate']=proposal;row['source_collation_reassessment']=proposal
    if not case.get('latin_only_alternative'):repairs.append(dict(niese=n,**proposal))
   current_cases[n]=case
  if obstacle:state='GREEK_START_AWAITING_WORD_LEVEL_SOURCE_DECISION'
  elif row['classification']=='UNAVAILABLE':state='ABSENCE_OR_SOURCE_ANOMALY_REQUIRES_REPRESENTATION_DECISION'
  elif case and not case.get('resolved'):state='GREEK_COLLATED_LATIN_OR_REPRESENTATION_EDITORIAL_DECISION'
  elif row['classification'] in ['EXACT','INTERNAL-BUT-EXACT'] or case and case.get('resolved'):state='GREEK_VERIFIED_WITH_SECURE_LATIN_COUNTERPART'
  else:state='GREEK_COLLATED_LATIN_CANDIDATE_AWAITING_INDIVIDUAL_VERIFICATION'
  row['checkpoint_verification_state']=original
  row['print_collation']=collation;row['verification_work_state']=state
  row['print_start_verified']=collation['canonical_word_cut_verified']
  row['independent_source_evidence']['word_start_independently_verified']=collation['canonical_word_cut_verified']
  row['independent_source_evidence']['remaining_print_work']=obstacle
  row['independent_source_evidence']['followup_current_run']=collation
  row['editorial_case_status']='RESOLVED_CANDIDATE_ONLY' if case and case.get('resolved') else 'HUMAN_DECISION_REQUIRED' if case else 'NO_NAMED_EDITORIAL_QUESTION'
  row['latin_individual_verification_status']='SECURE_AT_CHECKPOINT_OR_RESOLVED_SOURCE_CASE' if state=='GREEK_VERIFIED_WITH_SECURE_LATIN_COUNTERPART' else 'NOT_PROMOTED_BY_GREEK_PRINT_COLLATION'
  assert row['human_decision'] is None and not row['implementation_approved']
  if b==8 and n==367:
   row['absence_scope_addendum']='The main second-embassy narrative is absent. Whole-section absence is conditional on retaining the earlier 368 cut. The quotation tail survives; omission cause is unproved.'
   row['conditional_partial_survival_candidate']={'condition':'If section 368 begins at Ἄχαβος / Achab itaque','latin_locator':rows[367]['latin_locator'],'greek_surviving_counterpart_locator':rows[367]['greek_locator'],'approved':False,'apply':False}
  cross[row['placement']][row['classification']]+=1;confidence_cross[row['placement']][row['confidence']]+=1;work[state]+=1;printcounts[status]+=1
  history.append(dict(book=b,niese=n,checkpoint_commit=COMMITS[b],checkpoint_register_sha256=sha(checkpoint),earlier=original,followup_greek_status=status,classification_changed=False,confidence_changed=False,
    proposed_reassessment=row.get('source_collation_reassessment'),human_decision=None,applied=False))
 # Opening repair is proposed separately from citation existence.
 repairs.insert(0,dict(niese=1,kind='EXPLICIT_OPENING_LABEL_PROPOSAL',approved=False,apply=False,greek_locator=rows[0]['greek_locator'],reason='Existing printed citation 1 is implicit at the verified opening. Greek XML has nums 2..end only; this proposal represents the existing opening identity, not an additional citation. Exact marker syntax remains for a later approved implementation.'))
 write(d/'BOUNDARIES.json',rows);write(d/'PRINT_COLLATION.json',{'book':b,'status':'ROUTINE_IMAGE_COLLATION_COMPLETE_WITH_EXPLICIT_WORD_DECISION' if b==8 else 'ROUTINE_IMAGE_COLLATION_COMPLETE','observations':observations,'greek_status_counts':dict(printcounts),'cases':list(current_cases.values())})
 write(d/'DECISION_HISTORY.json',history);write(d/'GREEK_REPAIR_PROPOSALS.json',{'book':b,'status':'PROPOSALS_ONLY_NOT_APPLIED','proposals':repairs})
 write(d/'FOLLOWUP_DECISIONS.json',{'book':b,'cases':list(current_cases.values())})
 write(d/'VERIFICATION_OBSTACLES.json',{'book':b,'unread_body_pages':[],'obstacles':[r['print_collation']['verification_obstacle'] for r in rows if r['print_collation']['verification_obstacle']], 'additional_provenance_limitation':'The earlier provenance investigation did not identify an independently accepted Greek source/master for VIII/X. This follow-up does not substitute a duplicate; canonical frozen XML remains the compared transcription. See SOURCE_AUTHORITY.md and the preserved batch provenance record.'})
 fields=['book','niese','classification','confidence','placement','verification_work_state','editorial_case_status','latin_paragraph_id','latin_anchor_phrase','greek_start','latin_start','verification_reason','greek_locator','latin_locator','print_collation','source_collation_reassessment','independent_source_evidence','alternative_positions','human_decision','implementation_approved']
 with (d/'BOUNDARIES.tsv').open('w',encoding='utf8',newline='') as f:
  wr=csv.DictWriter(f,fieldnames=fields,delimiter='\t');wr.writeheader()
  for r in rows:wr.writerow({k:json.dumps(r[k],ensure_ascii=False) if isinstance(r.get(k),(dict,list)) else r.get(k,'') for k in fields})
 # REVIEW_CASES gives actual decisions; hundreds of historical REQUIRES rows are not silently recast as human questions.
 pending=[n for n,c in current_cases.items() if not c.get('resolved')];resolved=[n for n,c in current_cases.items() if c.get('resolved')]
 md=[f'# Book {roman}: editorial decisions after printed collation', '', '**NO-GO. Candidate audit only; implementation is not approved. No human decisions have been supplied.**', '',
  f'All {end} citation starts were checked against the supplied Niese body images. The routine page-reading queue is complete. '+('VIII.110, VIII.172 and VIII.368 retain the specific word-precision obstacles described below.' if b==8 else 'No unread or inaccessible Niese start remains.'), '',
  'The historical EXACT / INTERNAL-BUT-EXACT / REQUIRES_ADJUDICATION / UNAVAILABLE classifications and confidence values are unchanged. Greek print verification alone does not certify a Latin cut. Routine Latin candidates still needing individual verification are counted separately from the decisions here. The earlier register and case packet remain recoverable in checkpoint commit `'+COMMITS[b]+'`.', '',
  f'Human decision records: **{len(pending)}**, sections '+', '.join(map(str,pending))+'. Resolved source cases: '+(', '.join(map(str,resolved)) or 'none')+'. Paired sections should be decided jointly.', '',
  'Every context below reproduces canonical text. The symbol ⟦candidate cut⟧ is editorial display only, never inserted into XML. Text-node offsets and UTF-8 bytes refer to the pinned LF worktree inputs; canonical CRLF hashes remain separately recorded in BASELINE.json.', '',
  '## Concise decision list', '', '| Section | Exact judgement requested |', '|---|---|']
 for n in pending:md.append(f'| {roman}.{n} | {current_cases[n]["decision"]} |')
 md+=['','## Verification work states', '', '| State | Records |','|---|---:|']
 for k,v in work.items():md.append(f'| {k} | {v} |')
 md+=['','## Placement against retained confidence classifications','',table(cross),'',
  'These are candidate placement counts, not inserted markers or certified availability.'+(' The historical unavailable record for VIII.367 is conditional on the VIII.368 decision; its surviving tail must not be discarded.' if b==8 else ''), '',
  '| Placement | HIGH | PENDING_EDITORIAL_VERIFICATION | HIGH_ABSENCE_IN_THIS_TRANSCRIPTION |','|---|---:|---:|---:|']
 for place,cc in confidence_cross.items():md.append('| '+place+' | '+' | '.join(str(cc.get(k,0)) for k in ['HIGH','PENDING_EDITORIAL_VERIFICATION','HIGH_ABSENCE_IN_THIS_TRANSCRIPTION'])+' |')
 md+=['',
  '## Decisions and resolved source cases','']
 for n,c in current_cases.items():
  r=rows[n-1];obs=r['print_collation'];gl=r['greek_locator'];ll=r['latin_locator'];p=c['proposed_candidate']
  title=f"### {roman}.{n} — "+('resolved source check' if c.get('resolved') else 'decision required')
  md += [title,'',f"Affected Latin: `{r['latin_paragraph_id'] or ('latin-book08-num363' if b==8 else 'latin-book10-num108')}`"+(' (see neighbouring extents and inherited-label discussion).' if not ll else '.'),'',
   f"Printed authority: Niese, *Flavii Iosephi Opera* II (1885), **p. {obs['printed_page']}**, PDF **{obs['pdf_page']}**. [Full page image]({obs['image']})."]
  if n==108 and b==10:md.append('[Following page, p.354/PDF362](evidence/print-collation/niese-II-pdf-362.jpg).')
  for pn in c.get('loeb',[]):
   name=f'loeb-{"V" if b==8 else "VI"}-followup-{pn}.png';md.append(f'[Loeb {"V" if b==8 else "VI"}, p.{pn-(8 if b==8 else 16)}, PDF{pn}](evidence/print-collation/{name}) (independent control; Niese supplies numbering).')
  md += ['', '**Greek, earlier canonical cut with adjoining text:**', '',snippet(books['Greek'],gl),'','**Latin, earlier candidate with adjoining text:**','']
  if ll:md += [snippet(books['Latin'],ll),'',locator_text(ll)]
  else:
   near=rows[n]['latin_locator'] if n<end else rows[n-2]['latin_locator'];md += [snippet(books['Latin'],near),'', 'This displayed cut belongs to the following surviving section, not to the unavailable section. '+locator_text(near)]
  if p:md += ['', '**Reassessed proposal / alternative, not applied:**', '',snippet(books['Greek'],p['greek_locator']),'',snippet(books['Latin'],p['latin_locator']),'',locator_text(p['latin_locator']), '',f"Neighbouring extent change: {n-1} ends at the proposed cut instead of the old cut; {n} begins there and still ends at {n+1}. Exact before/after offsets are in the boundary reassessment and DECISION_HISTORY.json."]
  md += ['', '**Difficulty.** '+c['reason'],'','**Recommended treatment.** '+c['recommendation'],'','**Credible alternatives.** '+c['alternatives'],'','**Decision requested.** '+c['decision'],'']
 md+=['## Displaced inherited labels and future representation','',
  'An eventual implementation must preserve every visible composite `<num>` label, existing xml:id, sameAs, paragraph and traditional chapter/subchapter division. Certified citation locators would separately define executable Niese starts and suppress displaced inherited numeric claims. The current reader scans labels and milestones, so inserting a new milestone alone would leave duplicate/false identities. A future data-driven locator/override facility and full rendering QA are prerequisites. No such production change is included here.','',
  'The candidate dry-run and arithmetic in the checkpoint are mechanical evidence only. They must be recomputed if a proposed Greek/Latin cut or the VIII.367 representation is accepted. No candidate plan is authorized for application.','']
 (d/'REVIEW_CASES.md').write_text('\n'.join(md),encoding='utf8',newline='\n')
 summary=dict(book=b,citations=end,explicit_Greek_labels=end-1,missing_explicit_Greek_label=1,routine_print_collation_records=end,body_pages=90 if b==8 else 63,greek_status_counts=dict(printcounts),verification_work_states=dict(work),classification_counts=dict(collections.Counter(r['classification'] for r in rows)),placement_classification_crosstab={k:dict(v) for k,v in cross.items()},placement_confidence_crosstab={k:dict(v) for k,v in confidence_cross.items()},human_decision_sections=pending,resolved_source_case_sections=resolved,new_milestones_applied=0,Greek_repairs_applied=0,book_implementation='NO_GO',certified=False,checkpoint_commit=COMMITS[b],checkpoint_register_sha256=sha(checkpoint))
 write(d/'COLLATION_SUMMARY.json',summary);summaries[b]=summary
 # Preserve the original QA verbatim, then append the new evidence; no browser claim is made for disabled books.
 qraw=oldfile(COMMITS[b],d/'QA.json');(d/'CHECKPOINT_QA.json').write_bytes(qraw);qa=json.loads(qraw)
 qa['followup_print_collation']=summary;qa['candidate_inventory']['independent_full_print_collation']='ROUTINE_IMAGE_COLLATION_COMPLETE; see followup word/source decisions'
 qa['followup_warning']='Historical classifications and unapproved dry-run are unchanged; proposed relocations have not been applied. Newly supported-book browser QA is NOT RUN because both books remain disabled.'
 write(d/'QA.json',qa)
 for name in ['REPORT.md','SOURCE_AUTHORITY.md','REPRODUCE.md']:
  raw=oldfile(COMMITS[b],d/name).decode('utf8').replace('\r\n','\n');add='\n\n## Follow-up after the committed candidate checkpoint\n\n'
  add+=f'Checkpoint `{COMMITS[b]}` remains candidate-audit evidence; implementation is NOT APPROVED. The follow-up read all {90 if b==8 else 63} Niese body pages and recorded all {end} starts in PRINT_OBSERVATIONS.json and BOUNDARIES.json. See COLLATION_SUMMARY.json for separate source, Latin-verification and editorial counts; REVIEW_CASES.md now states precise decisions. All original classifications, source hashes, candidate locators and provenance are retained.\n\n'
  add+='Greek XML explicitly labels 2–'+str(end)+f'; the exact absent explicit label is 1, at the printed opening (Niese II p.{177 if b==8 else 330}/PDF{185 if b==8 else 338}). The opening is already the first citation, not an additional section. Proposed opening representation and later relocations are in GREEK_REPAIR_PROPOSALS.json, unapplied.\n\n'
  if b==8:add+='Niese p.257/PDF265 also omits a numeral at the 376 clause and prints 376 at the canonical 377 clause. Loeb V p.772/PDF780 independently supports retaining the canonical 376/377 sequence; this is separate from the absent XML opening label. VIII.110, VIII.172 and VIII.368 retain word-precision decisions after both scans were read. The unavailable classification at 367 is historical and conditional: the surviving quotation tail must be preserved. No omission cause is established. VIII.83 retains an earlier dimensional counterpart before the historical mirum proposal; see its revised candidate and decision history.\n\n'
  add+='Run the batch followup_collation.py to reconstruct this addendum from the committed candidate register and saved observations; run verify_followup.py for hashes, locators, source preservation and scope. These scripts cannot independently reproduce human visual judgements. Do not rerun the older audit_book.py to overwrite this follow-up. No Greek/Latin source, renderer, registry or navigation file has been changed.\n'
  (d/name).write_text(raw+add,encoding='utf8',newline='\n')
 write(d/'CONFIDENCE_CROSSTAB.json',{'book':b,'historical_classifications_retained':True,'placement_against_classification':summary['placement_classification_crosstab'],'placement_against_confidence':summary['placement_confidence_crosstab'],'work_states':dict(work)})
 araw=oldfile(COMMITS[b],d/'AUDIT_RESULT.json');(d/'CHECKPOINT_AUDIT_RESULT.json').write_bytes(araw);ar=json.loads(araw)
 ar['independent_full_book_print_collation']='ROUTINE_IMAGE_COLLATION_COMPLETE_WITH_SEPARATELY_RECORDED_WORD_DECISIONS' if b==8 else 'ROUTINE_IMAGE_COLLATION_COMPLETE'
 ar['followup_collation_summary']=summary;ar['checkpoint_mechanical_results']='CHECKPOINT_AUDIT_RESULT.json; proposed relocations and conditional partial survival were not applied to the checkpoint dry-run.'
 write(d/'AUDIT_RESULT.json',ar)
 # Put the current state before the preserved checkpoint text so old queue language cannot be mistaken for current findings.
 for name in ['REPORT.md','SOURCE_AUTHORITY.md','REPRODUCE.md']:
  raw=oldfile(COMMITS[b],d/name).decode('utf8').replace('\r\n','\n');current=(d/name).read_text(encoding='utf8')[len(raw):]
  (d/name).write_text(f'# Book {roman}: current candidate-collation status\n'+current+'\nCASES.json is the preserved checkpoint input. FOLLOWUP_DECISIONS.json and REVIEW_CASES.md carry current source assessments and editorial questions.\n\n## Preserved candidate checkpoint text\n\n'+raw,encoding='utf8',newline='\n')
allsummary={'status':'CANDIDATE_AUDIT_PRINT_COLLATION_ADDENDUM_IMPLEMENTATION_NOT_APPROVED','checkpoint_commits':COMMITS,'base':BASE,'books':summaries,'total_citations_audited':701,'new_citations_enabled':0,'existing_certified_Antiquities_Niese_selections':2456,'cumulative_certified_Antiquities_Niese_selections':2456,'all_human_decisions_null':True,'new_Greek_or_Latin_edits':False,'push_authorized':False,'followup_changes_left_unstaged':True}
write(B/'PRINT_COLLATION_SUMMARY.json',allsummary)
write(B/'COMMITTED_CHECKPOINT.json',{'commits':COMMITS,'scope':'141 review-only files; explicitly staged per packet before commit','implementation_approved':False,'production_files_in_commits':[],'push':False})
bm=['# VIII / X printed-collation addendum','', '**Both books remain NO-GO. No Greek or Latin changes, reader enablement or certification.**','',
 'The authorized candidate checkpoint was committed in three independent audit-only commits:', '',f"- VIII: `{COMMITS[8]}`",f"- X: `{COMMITS[10]}`",f"- Shared batch: `{COMMITS['batch']}`",'',
 'All 153 Niese body pages were visually examined, covering 420 VIII starts and 281 X starts. Full page images and precise page references accompany every row. OCR was used only to find passages; PDF242 in VIII has no useful body OCR and was collated directly from its image. X281 begins at the final word ἐγὼ on PDF399 and continues PDF400.','',
 'The explicit XML label deficits are VIII.1 and X.1: both openings already have printed first-citation identities, established by the opening and running-head ranges. The unapplied proposal would represent those existing identities. Niese’s separate VIII.376/377 numeral anomaly is documented against independent Loeb control.','',
 'Recommended paired Greek/Latin relocations: VIII.59, VIII.245, VIII.353, VIII.409, X.33. Earlier candidates and neighbouring extents remain in DECISION_HISTORY.json; proposed alternatives never replace the frozen source. Word-precision obstacles remain at VIII.110 (Niese p.200/PDF208; Loeb p.630/PDF638), VIII.172 (Niese p.214/PDF222; Loeb p.662/PDF670), and VIII.368 (Niese p.256/PDF264; Loeb Greek p.768/PDF776 and English p.769/PDF777). The last affects partial survival versus unavailability at 367. No scan is unread or inaccessible. VIII.83 also has a reassessed earlier Latin dimensional counterpart.','',
 '## Independent book states','', '| Book | Routine print records | Named human decision records | Historical EXACT / internal / uncertain / unavailable | Applied milestones / Greek repairs |','|---|---:|---:|---|---|']
for b in [8,10]:
 x=summaries[b];c=x['classification_counts'];bm.append(f"| {b} | {x['routine_print_collation_records']} | {len(x['human_decision_sections'])} | {c.get('EXACT',0)} / {c.get('INTERNAL-BUT-EXACT',0)} / {c.get('REQUIRES_ADJUDICATION',0)} / {c.get('UNAVAILABLE',0)} | 0 / 0 |")
bm += ['', 'The named editorial decisions are separate from routine Latin candidates still awaiting individual verification. No confidence classification was promoted by the Greek image pass. Read each book’s REVIEW_CASES.md for decisions, Greek/Latin cut contexts, mixed-content byte locators, alternatives and linked image evidence.','',
 '[Book VIII editorial packet](../Antiquities_Niese_BookVIII_2026-10-08/REVIEW_CASES.md) · [Book X editorial packet](../Antiquities_Niese_BookX_2026-10-08/REVIEW_CASES.md). Placement/classification and placement/confidence cross-tabulations are in both packets and CONFIDENCE_CROSSTAB.json.','',
 '## Integrity and existing systems','',
 'All six Greek/Latin/English input and output hashes remain unchanged; before/after values are in each BASELINE.json and the follow-up verification. The source PDFs and frozen research packets remain unchanged. Existing source provenance limitations are preserved. No renderer, availability registry, TOC, other book or other work changed. Certified Antiquities Niese coverage remains **2,456 selections in I–VII**, with **0 newly enabled**. VIII, IX and X remain unavailable in Niese mode.','',
 'The checkpoint contains actual built-site browser and regression results for the existing systems. Those historical results are retained; this addendum does not claim a new browser run or QA of VIII/X Niese displays. Production Git blobs are unchanged from the checkpoint base, so there is no renderer delta to certify.','',
 '## Scope and next review','',
 'The collation addendum is left unstaged and uncommitted. The three authorized checkpoint commits contain review files only and explicitly say implementation is not approved. No push occurred. The batch stays based on 1cf003b. CANONICAL_ADVANCE.json preserves the earlier TOC typography reconciliation. During final verification canonical advanced to a480215 through the separately documented Greek source-contents v1.1 integration; CANONICAL_ADVANCE_FOLLOWUP.json records its commits, exact scope and certification hashes. All six VIII/X narrative inputs and renderer code are unchanged. No merge or rebase occurred in this audit.','',
 'Finish these two books: decide the named source/representation questions, independently verify the remaining Latin candidates, then recompute extents and candidate arithmetic. Any later implementation requires separate approval, byte-preservation checks and actual new-book browser QA. No other batch has been selected.','']
(B/'PRINT_COLLATION_SUMMARY.md').write_text('\n'.join(bm),encoding='utf8',newline='\n')
# Update batch report by addendum, retaining the checkpoint narrative.
for name in ['REPORT.md','REPRODUCE.md']:
 raw=oldfile(COMMITS['batch'],B/name).decode('utf8').replace('\r\n','\n')
 (B/name).write_text('# Current printed-collation follow-up\n\nSee PRINT_COLLATION_SUMMARY.md and PRINT_COLLATION_SUMMARY.json. The routine Niese image pass is complete; exact source-interpretation and editorial decisions are separately enumerated. Both books remain NO-GO. The three review-only checkpoint commits are recorded in COMMITTED_CHECKPOINT.json; follow-up changes remain unstaged. Run followup_collation.py, then verify_followup.py.\n\n## Preserved candidate checkpoint text\n\n'+raw,encoding='utf8',newline='\n')
fixtures();print(json.dumps({'books':summaries,'mixed_content_fixtures':'PASS'},ensure_ascii=False,indent=2))
