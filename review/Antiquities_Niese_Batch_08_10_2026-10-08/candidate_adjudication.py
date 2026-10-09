"""Rebuild candidate audit only from the accepted printed-collation commit.
Never writes production XML, stages, commits, enables navigation or pushes.
Human decisions select candidate locators, not implementation permission.
"""
import pathlib,json,subprocess,sys,hashlib,re,unicodedata,collections,csv,argparse
from copy import deepcopy
P=pathlib.Path(__file__).resolve().parent;W=P.parents[1]
sys.path.insert(0,str(W/'review/Antiquities_Niese_BookVIII_2026-10-08'))
from mixed_mapper import Book,fixtures
CHECKPOINT='dec5f783b1af936803150536ed5aaa031b21c479'
def sha(x):return hashlib.sha256(x).hexdigest()
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
def oldfile(p):return subprocess.check_output(['git','show',f'{CHECKPOINT}:{p.relative_to(W).as_posix()}'],cwd=W)
LATIN={8:{59:'Ita contingebant',83:'quarum altitudo fuit cubiti unius et dimidii',87:'aqua plenum',97:'mirabilis',110:'quod ipse quoque non dum nato',167:'cum auro et aromatibus',172:'Licet multorum minor',187:'maxima[s] res omni prouidentia',224:'potius quidem narrabo',245:'Haec ergo dicens',255:'Inuadens itaque hebraeorum regionem',334:'Commemorabatque ei',353:'Haec audiens helias',367:'et quae displucuerint sola relinquerent',368:'Achab itaque secunda legatione',369:'nunc inquit denuo missa legatione',408:'quibus ab illo sic prophetatis',409:'Cumque percusisset micheam'},10:{18:'Turbatur ergo rex',33:'Cui propheta respondens',69:'et domos et uicos',107:'eo quod',109:'Interea dum hoc cognouisset',150:'Rex autem pontifices',151:'Igitur quia genus explanauimus',213:'rex dum fecisset',248:'nepus nepos'}}
GREEK={8:{59:'ἔπειθ᾽ οὕτως',110:'καὶ ὡς αὐτὸς ἐπιθείη',172:'καταδεεστέραν',245:'ταῦτα εἰπὼν πείθει',353:'ὁ δ᾽ Ἠλίας',368:'Ἄχαβος δ᾽ ἀγασθείς',409:'ὡς οὖν πλήξαντος'},10:{33:'ὁ δὲ προφήτης ὑποτυχών'}}
RETAINED_RESOLUTIONS={256:'Retain the printed clause assessment: marginal 256 shares the line with the preceding στρατείαν clause, but the adversative ἀλλ᾽ οὐκ ἔπεισαν has the secure Latin counterpart Quos tamen non ex audiuit deus. No Greek move follows from the line position.',314:'Retain Μαθεῖν / Ex his namque cognoscitur: the printed start and the Latin reflection on divine providence agree. The additional visible composite label is preserved; it does not manufacture a traditional lower division.',376:'Retain the canonical and independently controlled order of 376–377 despite the Niese printed numeral anomaly. εἶχε δ᾽ ἑτοίμην / Achab autem exercitum habuit begins the reserve army, the youths attack and release of the rest of the army; no conjectural numeral swap.',377:'Retain the canonical and independently controlled order of 376–377. ἡ δ᾽ αἰφνιδίως / qui repente syros inruentes begins the sudden victorious attack and Syrian flight. The Niese printed numeral anomaly is recorded separately and does not justify swapping starts.'}
WORD_CONTROLS={110:{'Niese_marginal_observation':'Niese p.200 puts 110 at the continuation line containing τίς μέλλοι, after the naming clause begins. It does not uniquely tag a word.','Loeb_independent_observation':'Loeb V p.630 places 110 at the earlier καὶ ὡς αὐτὸς naming clause.','Loeb_printed_page':630,'Loeb_PDF_page':638,'image':'evidence/print-collation/loeb-V-followup-638.png'},172:{'Niese_marginal_observation':'Niese p.214 puts 172 on the comparative-clause line containing καταδεεστέραν; this is not an embedded word delimiter.','Loeb_independent_observation':'Loeb V p.662 places 172 later in the same comparative clause at ἀπέφηνεν. The next explanatory clause was a considered alternative; the editor retains the earlier comparative cut.','Loeb_printed_page':662,'Loeb_PDF_page':670,'image':'evidence/print-collation/loeb-V-followup-670.png'},368:{'Niese_marginal_observation':'Niese p.256 puts 368 beside the hyphenated end of καταλείψουσιν followed by the Ahab sentence; this does not unambiguously word-tag either clause.','Loeb_independent_observation':'Loeb V Greek p.768 has a similar marginal position. English p.769 distinguishes the closing embassy quotation from the Ahab response. The editor selects the Ahab sentence.','Loeb_printed_page':768,'Loeb_PDF_page':776,'image':'evidence/print-collation/loeb-V-followup-776.png','Loeb_English_printed_page':769,'Loeb_English_PDF_page':777,'English_image':'evidence/print-collation/loeb-V-followup-777.png'}}
QUALIFICATIONS={8:{
83:'The dimensional phrase is a surviving counterpart before mirum; the whole prefix must not be classified absent. Damaged wording limits detailed equivalence.',
87:'Changed syntactic attachment of aqua plenum does not establish missing text. Locate the embedded surviving counterpart; preserve Latin syntax.',
97:'Cut before mirabilis. The connective siquidem immediately before it is uncertain; leave that wording and all punctuation unchanged.',
167:'Camels are not separately expressed in the quoted Latin. This does not establish physical loss. Retain the gifts counterpart cum auro et aromatibus.',
172:'Retain the comparative-clause cut. Niese marks a line, and Loeb places its numeral differently within the clause; the chosen word is editorial, not unambiguously word-tagged by Niese.',
187:'The visible [VII.iv.187] precedes Huc ergo, still belonging to 186. Executable 187 begins at maxima[s] res omni prouidentia; preserve the complete inherited label and paragraph.',
255:'Executable 255 starts inside paragraph num251. The visible [X.iii.255] occurs later within 255; preserve it but prevent a duplicate executable start.',
334:'The preceding praecabat enim ... morte subcumbere may incorporate the opening appeal. Commemorabatque is the elected locator for the explicit recollection; no unqualified absent-appeal claim.',
367:'PARTIAL_SURVIVAL: the main second-embassy narrative is absent, with cause undetermined. Preserve its surviving closing tail et quae displucuerint sola relinquerent. No supplied text or automatic gap.',
368:'Editorially elected start at Ahab response; the preceding quoted tail now belongs to partially surviving 367. Niese marginal position is not an unambiguous word tag.',
369:'Use the first repeated nunc inquit denuo missa legatione. Preserve both occurrences and the later recap; do not supply the missing earlier narrative.',
110:'Editorial choice supported by independent Loeb clause control. Niese marginal numeral does not uniquely tag this word; preserve that distinction.',
},10:{
18:'Before Turbatur: letter, reassurance, siege and news of Ethiopian relief. After Turbatur: Sennacherib response, then ritual/restoration material within the same paragraph, followed by the resumed Vulcan/Pelusium account. The 18 interval includes that intervening Latin material through the cut before 19; preserve it and the editorial note.',
69:'Opening Greek objects are houses and villages. Latin attaches et domos et uicos to dicarent in the preceding syntax, then begins Perscrutatus est autem ciuitatem. Preserve the changed syntactic attachment and the elected embedded cut.',
107:'Record both differences: Latin idem versus Greek μὴ ταὐτόν, and Latin non concordabant versus Greek συμφωνεῖν. No emendation; the physical eo quod locator remains elected.',
108:'UNAVAILABLE in this transcription: treaty/alliance and Egyptian narrative absent; cause undetermined. Preserve the later surviving Interea narrative and visible [VII.iii.108], which must not assert executable 108.',
109:'Executable 109 begins Interea dum hoc cognouisset although the inherited label claims 108. Preserve the visible text, ID, sameAs and chapter structure; future representation needs a data-level identity override.',
150:'Executable 150 starts Rex autem pontifices in paragraph num151. Preserve its visible inherited 151 label and prevent it asserting a false executable 151 at this location.',
151:'Executable 151 begins internally at Igitur quia genus explanauimus, independently of the visible inherited 151 label before 150.',
213:'Leave Cui etiam rea with 212; 213 begins rex dum fecisset. Preserve the broken wording and punctuation.',
248:'Use the earliest genealogical counterpart nepus nepos. Preserve both nepus and nepos, Latin order and repetition.',
102:'REVISED_PROPOSAL_ONLY: move the candidate from simulet ioachim to nomine sedechiam. simulet ioachim may preserve the concluding Joachim reference of 101. Opening imprisonment/uncle detail of Greek 102 is not explicitly recoverable; do not reconstruct words. Human approval of this revised cut is pending.'}}

def normalized(s):
 out=[];positions=[]
 for i,c in enumerate(s):
  for k in unicodedata.normalize('NFD',c).casefold():
   if k.isalpha():out.append(k);positions.append(i)
 return ''.join(out),positions
def find_phrase(book,phrase,near,first=False,greek=False):
 u=book.units[book.locate(near)['paragraph']-1]
 if greek:
  text,pos=normalized(u['text']);needle=normalized(phrase)[0];indices=[pos[m.start()] for m in re.finditer(re.escape(needle),text)]
 else:indices=[m.start() for m in re.finditer(re.escape(phrase),u['text'])]
 assert indices,(phrase,u['id'])
 assert len(indices)==1 or first,(phrase,u['id'],'ambiguous',indices)
 return book.locate(u['book_start']+indices[0])

def build(booknum,roman):
 d=W/f'review/Antiquities_Niese_Book{roman}_2026-10-08';raw=oldfile(d/'BOUNDARIES.json');old=json.loads(raw);rows=deepcopy(old)
 books={lang:Book(W/f'assets/xml/antiquities/{lang}/book-{booknum:02}.xml') for lang in ['Greek','Latin']};g=books['Greek'];l=books['Latin']
 baseline=json.loads((d/'BASELINE.json').read_text(encoding='utf8'))
 for lang in ['Greek','Latin','English']:assert sha((W/baseline['inputs'][lang]['path']).read_bytes())==baseline['inputs'][lang]['worktree_before_sha256']
 notes=json.loads((d/'LATIN_INDIVIDUAL_REVIEWS.json').read_text(encoding='utf8')) if (d/'LATIN_INDIVIDUAL_REVIEWS.json').exists() else {}
 routine=[r['niese'] for r in old if r['verification_work_state']=='GREEK_COLLATED_LATIN_CANDIDATE_AWAITING_INDIVIDUAL_VERIFICATION']
 assert set(map(int,notes)).issubset(routine)
 for r,previous in zip(rows,old):
  n=r['niese'];r['printed_checkpoint_state']={k:previous.get(k) for k in ['classification','confidence','placement','greek_locator','latin_locator','latin_anchor_phrase','verification_work_state','candidate_latin_end_book_offset']}
  r['printed_checkpoint_reassessment']=r.pop('source_collation_reassessment',None)
  r['historical_print_start_verified']=r.pop('print_start_verified',None)
  r['Greek_start_awaiting_print_verification']=False
  r['historical_verification_reason']=previous.get('verification_reason')
  r['independent_source_evidence']['historical_remaining_print_work']=r['independent_source_evidence'].get('remaining_print_work')
  r['independent_source_evidence']['remaining_print_work']=None
  r['operative_source_assessment']={'routine_print_collation_complete':True,'print_observation':'print_collation (retained accepted checkpoint evidence)','Greek_word_boundary_authority':'Retained clause locator, read with marginal line and syntax; not an embedded print word tag','Latin_confidence_independent_of_Greek_collation':True}
  r['implementation_approved']=False;r['apply_permitted']=False;r['human_decision']=None
  if n in LATIN[booknum]:
   phrase=LATIN[booknum][n];near=previous['latin_locator']['book_offset'] if previous['latin_locator'] else old[n]['latin_locator']['book_offset']
   r['latin_locator']=find_phrase(l,phrase,near,first=(booknum,n)==(8,369));r['latin_anchor_phrase']=phrase
   if n in GREEK[booknum]:r['greek_locator']=find_phrase(g,GREEK[booknum][n],previous['greek_locator']['book_offset'],greek=True)
   r['human_decision']={'authority':'Direct user editorial instruction, 2026-10-08','scope':'ADJUDICATED_CANDIDATE_ONLY','Latin_elected_phrase':phrase,'Greek_elected_phrase':GREEK[booknum].get(n),'production_application_authorized':False}
   r['verification_reason']=QUALIFICATIONS[booknum].get(n,'Paired physical starts elected by the editor after printed-collation review. Candidate only; no application authorized.')
   r['editorial_case_status']='ADJUDICATED_CANDIDATE';r['verification_work_state']='EDITORIALLY_ADJUDICATED_CANDIDATE';r['confidence']='EDITORIALLY_ADJUDICATED_WITH_RECORDED_LIMITS'
   r['latin_individual_verification_status']='EDITORIAL_DECISION_RECORDED'
   if (booknum,n) in [(8,110),(8,172),(8,368)]:
    r['Greek_word_start_authority']='EDITORIAL_CHOICE; Niese marginal line position and independent Loeb control retained separately in print_collation'
    r['Niese_unambiguous_word_tag']=False
    r['operative_source_assessment']['Greek_word_boundary_authority']=r['Greek_word_start_authority']
    r['independent_source_evidence']['historical_word_start_independently_verified']=r['independent_source_evidence'].get('word_start_independently_verified')
    r['independent_source_evidence']['word_start_independently_verified']=False
    r['operative_source_assessment']['separate_print_and_Loeb_controls']=WORD_CONTROLS[n]
  if booknum==8 and n in RETAINED_RESOLUTIONS:
   r.update(verification_reason=RETAINED_RESOLUTIONS[n],editorial_case_status='RESOLVED_SOURCE_ASSESSMENT_RETAINED',verification_work_state='GREEK_VERIFIED_WITH_SECURE_LATIN_COUNTERPART',confidence='HIGH_RETAINED_SOURCE_RESOLUTION',latin_individual_verification_status='PREVIOUS_SECURE_REVIEW_RETAINED')
   r['human_decision']={'authority':'Direct user instruction to retain resolved source assessment, 2026-10-08','scope':'RETAIN_RESOLVED_CANDIDATE_ONLY','production_application_authorized':False}
  if (booknum,n)==(10,108):
   r.update(human_decision={'authority':'Direct user editorial instruction, 2026-10-08','scope':'RETAIN_UNAVAILABLE_CANDIDATE','production_application_authorized':False},verification_reason=QUALIFICATIONS[10][108],verification_work_state='ADJUDICATED_UNAVAILABLE',editorial_case_status='ADJUDICATED_CANDIDATE')
  if (booknum,n)==(10,102):
   r['latin_locator']=find_phrase(l,'nomine sedechiam',previous['latin_locator']['book_offset']);r['latin_anchor_phrase']='nomine sedechiam';r['verification_reason']=QUALIFICATIONS[10][102];r['verification_work_state']='REVISED_CANDIDATE_AWAITING_EDITORIAL_DECISION';r['editorial_case_status']='OPEN_REVISED_CUT';r['human_decision']=None
  if str(n) in notes:
   note=notes[str(n)];r['individual_Latin_review']=note;r['verification_reason']=note['assessment']
   r['latin_individual_verification_status']='INDIVIDUALLY_REVIEWED_SECURE' if note['status']=='SECURE' else 'INDIVIDUALLY_REVIEWED_NEW_DIFFICULTY'
   r['verification_work_state']='GREEK_AND_LATIN_INDIVIDUALLY_REVIEWED_CANDIDATE' if note['status']=='SECURE' else 'NEW_LATIN_EDITORIAL_QUESTION'
   if note.get('proposed_anchor'):
    r['revised_Latin_proposal']=find_phrase(l,note['proposed_anchor'],previous['latin_locator']['book_offset'])
   if note['status']=='SECURE':r['confidence']='HIGH_INDIVIDUALLY_REVIEWED'
  if r['latin_locator']:
   loc=r['latin_locator'];r['latin_paragraph_id']=loc['stable_id'];r['latin_start']=l.stream[loc['book_offset']:loc['book_offset']+240]
   inherited=any(label['text']==r['existing_composite_label'] and label['id']==loc['stable_id'] and l.first_content(label['book_offset'])==loc['book_offset'] for label in l.labels)
   r['inherited_start_retained']=inherited;r['existing_label_is_physical_Niese_start']=inherited;r['placement']='INHERITED_START' if inherited else 'PROPOSED_INTERNAL_MILESTONE'
   if r['human_decision'] or str(n) in notes and notes[str(n)]['status']=='SECURE':r['classification']='EXACT' if inherited else 'INTERNAL-BUT-EXACT'
  if (booknum,n)==(8,367):
   r['availability']='PARTIAL_SURVIVAL';r['absence_scope_addendum']=QUALIFICATIONS[8][367];r.pop('conditional_partial_survival_candidate',None)
  elif (booknum,n)==(10,108):r['availability']='UNAVAILABLE'
  else:r['availability']='PRESENT_WITH_RECORDED_ALIGNMENT_LIMITS' if n in QUALIFICATIONS[booknum] else 'PRESENT'
  if (booknum,n)==(10,276):
   r.update(availability='PARTIAL_CORRESPONDENCE_PROPOSED',boundary_start_secure=True,editorial_case_status='OPEN_EXTENT_QUALIFICATION',confidence='SECURE_START_EXTENT_QUALIFICATION_PENDING')
   r['representation_question']='Retain Et haec and following quae omnia (277), recording the unexpressed Greek closing Roman-dominion/desolation clause as partial correspondence. Cause undetermined; no supplied text or automatic gap. Editorial qualification pending.'
  r['current_verification_category']='ESTABLISHED_UNAVAILABILITY_ADJUDICATED' if (booknum,n)==(10,108) else 'GREEK_RESOLVED_LATIN_PLACEMENT_DECISION_PENDING' if (booknum,n)==(10,102) else 'SOURCE_ANOMALY_REPRESENTATION_DECISION_PENDING' if (booknum,n)==(10,276) else 'GREEK_RESOLVED_LATIN_COUNTERPART_SECURE'
 positioned=[r for r in rows if r['latin_locator']]
 assert all(a['latin_locator']['book_offset']<b['latin_locator']['book_offset'] for a,b in zip(positioned,positioned[1:]))
 pieces=[]
 for i,r in enumerate(positioned):
  at=r['latin_locator']['book_offset'];end=positioned[i+1]['latin_locator']['book_offset'] if i+1<len(positioned) else len(l.stream)
  r['candidate_latin_end_book_offset']=end;r['candidate_latin_section']=l.stream[at:end];assert r['candidate_latin_section'].strip();pieces.append(r['candidate_latin_section'])
 prefix=l.stream[:positioned[0]['latin_locator']['book_offset']];assert prefix+''.join(pieces)==l.stream
 for i,r in enumerate(rows):
  at=r['greek_locator']['book_offset'];end=rows[i+1]['greek_locator']['book_offset'] if i+1<len(rows) else len(g.stream);assert at<end
  r['greek_section']=g.stream[at:end];r['greek_start']=r['greek_section'][:240];r['candidate_greek_end_book_offset']=end
 additions=[(r['latin_locator']['raw_byte'],f'<milestone unit="niese" n="{r["niese"]}"/>'.encode()) for r in positioned if not r['inherited_start_retained']]
 rehearsal=l.raw
 for at,tag in sorted(additions,reverse=True):rehearsal=rehearsal[:at]+tag+rehearsal[at:]
 from lxml import etree
 etree.fromstring(rehearsal);restored=rehearsal
 for at,tag in additions:assert restored.count(tag)==1;restored=restored.replace(tag,b'',1)
 assert restored==l.raw
 write(d/'BOUNDARIES.json',rows)
 columns=['book','niese','classification','confidence','placement','availability','verification_work_state','current_verification_category','Greek_start_awaiting_print_verification','latin_anchor_phrase','latin_paragraph_id','greek_locator','latin_locator','candidate_latin_end_book_offset','verification_reason','human_decision','individual_Latin_review','implementation_approved']
 with (d/'BOUNDARIES.tsv').open('w',encoding='utf8',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=columns,delimiter='\t',extrasaction='ignore');writer.writeheader()
  for r in rows:writer.writerow({k:json.dumps(r.get(k),ensure_ascii=False) if isinstance(r.get(k),(dict,list)) else r.get(k) for k in columns})
 history=[]
 for a,z in zip(old,rows):
  keys=['greek_locator','latin_locator','latin_anchor_phrase','classification','confidence','placement','verification_work_state','candidate_latin_end_book_offset','availability']
  changes={k:{'before':a.get(k),'after':z.get(k)} for k in keys if a.get(k)!=z.get(k)}
  history.append({'book':booknum,'niese':a['niese'],'accepted_printed_checkpoint_commit':CHECKPOINT,'checkpoint_register_sha256':sha(raw),'changes':changes,'human_decision':z['human_decision'],'source_XML_changed':False})
 write(d/'ADJUDICATION_HISTORY.json',history)
 summary={'book':booknum,'GO':False,'expected_sections':len(rows),'represented_candidate_starts':len(positioned),'inherited_candidate_starts':sum(r['inherited_start_retained'] for r in positioned),'proposed_milestones':len(additions),'unavailable':[r['niese'] for r in rows if r['availability']=='UNAVAILABLE'],'partial_survival':[r['niese'] for r in rows if r['availability']=='PARTIAL_SURVIVAL'],'proposed_partial_correspondence':[r['niese'] for r in rows if r['availability']=='PARTIAL_CORRESPONDENCE_PROPOSED'],'routine_review_queue':routine,'routine_reviewed':len(notes),'routine_secure':sum(n['status']=='SECURE' for n in notes.values()),'routine_new_questions':[int(n) for n,x in notes.items() if x['status']!='SECURE'],'routine_pending':[n for n in routine if str(n) not in notes],'classifications':dict(collections.Counter(r['classification'] for r in rows)),'work_states':dict(collections.Counter(r['verification_work_state'] for r in rows)),'classification_crosstab':{p:dict(collections.Counter(r['classification'] for r in rows if r['placement']==p)) for p in ['INHERITED_START','PROPOSED_INTERNAL_MILESTONE','NO_LATIN_START']},'confidence_crosstab':{p:dict(collections.Counter(r['confidence'] for r in rows if r['placement']==p)) for p in ['INHERITED_START','PROPOSED_INTERNAL_MILESTONE','NO_LATIN_START']},'Latin_source_sha256':sha(l.raw),'Latin_rehearsal_sha256':sha(rehearsal),'Latin_removed_candidate_markers_sha256':sha(restored),'byte_invariance':restored==l.raw,'candidate_partition_covers_every_narrative_character':True,'source_files_written':0,'new_milestones_applied':0,'Greek_repairs_applied':0,'implementation_approved':False}
 summary['current_verification_categories']=dict(collections.Counter(r['current_verification_category'] for r in rows))
 summary['Greek_starts_awaiting_print_verification']=sum(r['Greek_start_awaiting_print_verification'] for r in rows)
 write(d/'ADJUDICATION_QA.json',summary)
 write(d/'CANDIDATE_DRY_RUN.json',{'status':'UNAPPLIED_ADJUDICATED_AND_PENDING_CANDIDATE_REHEARSAL','candidate_markers':len(additions),'source_sha256':sha(l.raw),'candidate_bytes_sha256':sha(rehearsal),'removed_authorized_candidate_strings_recovers_original':True,'parsed_candidate_XML':True,'application_permitted':False,'source_files_written':0,'warning':'Insertion arithmetic and byte preservation only. Does not resolve executable label overrides, approve X.102 or certify unresolved Latin cuts.'})
 write(d/'EXECUTABLE_IDENTITIES.json',{'book':booknum,'status':'CANDIDATE_LOCATORS_ONLY_NO_READER_APPLICATION','identities':[{'niese':r['niese'],'availability':r['availability'],'locator':r['latin_locator'],'visible_label':r['existing_composite_label'],'visible_label_paragraph':r['existing_label_paragraph'],'label_is_executable_start':r['existing_label_is_physical_Niese_start']} for r in rows],'rule':'Preserve all visible num text, IDs, sameAs, paragraphs and traditional divisions. Future data-level overrides must suppress false/duplicate inherited claims independently of internal milestones. No code has been changed.'})
 return rows,summary,books

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--cards',type=int,choices=[8,10]);ap.add_argument('--from-section',type=int,default=1);ap.add_argument('--to-section',type=int,default=999);ap.add_argument('--full',action='store_true');args=ap.parse_args()
 summaries={}
 for b,roman in [(8,'VIII'),(10,'X')]:
  rows,summary,books=build(b,roman);summaries[b]=summary
  if args.cards==b:
   for r in rows:
    if r['niese'] not in summary['routine_review_queue'] or not args.from_section<=r['niese']<=args.to_section:continue
    go=r['greek_locator']['book_offset'];lo=r['latin_locator']['book_offset'];lim=9999 if args.full else 150
    print(f"{b}.{r['niese']} G:{books['Greek'].stream[max(0,go-35):go]} | {r['greek_section'][:lim]}\n L:{books['Latin'].stream[max(0,lo-45):lo]} | {r['candidate_latin_section'][:lim]} [end:{r['candidate_latin_section'][-45:]}]")
 if not args.cards:print(json.dumps(summaries,ensure_ascii=False,indent=2))
 fixtures()
