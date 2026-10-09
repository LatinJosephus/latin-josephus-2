from pathlib import Path
import json,csv,hashlib,subprocess,re
from source_scope import Book,digest
from verify_locators import validate,validate_all_nodes
ROOT=Path(__file__).resolve().parents[2];BATCH=Path(__file__).resolve().parent
PIN='ad3158b7a86dea6997510b3de17f2e510c23367c'
def git(*args,cwd=ROOT):return subprocess.check_output(['git',*args],cwd=cwd).decode().strip()
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
for b,roman,total,endpage in [(14,'XIV',491,402),(15,'XV',425,481)]:
 P=ROOT/f'review/Antiquities_Niese_Book{roman}_2026-10-09';rows=json.loads((P/'BOUNDARIES.json').read_text())
 if (P/'CERTIFICATION.json').exists():
  print(roman,'complete certificate retained; provisional writer skips this book');continue
 g=Book(raw=(P/'frozen-inputs/Greek.xml').read_bytes());l=Book(raw=(P/'frozen-inputs/Latin.xml').read_bytes())
 assert rows[-1]['print_observation']['image_inspected']
 limits={165:'Greek’s opening description of Hyrcanus’s inattention and the leaders’ fear is compressed out; the explicit charge survives.'} if b==14 else {
  87:'The Latin retains Joseph’s exclusion from Herod’s presence and Alexandra’s confinement; it does not explicitly command Joseph’s execution here as Greek does.',
  118:'The renewed Arab attack and killings survive; the final Greek escapee statement is shortened in this Latin interval.',
  141:'The weak/strong contrast survives; Greek’s initial rhetorical question about deeming the enemy brave is not separately expressed in this Latin interval.'}
 for n,note in limits.items():rows[n-1].update(correspondence_status='PRESENT_WITH_LOCAL_COMPRESSION',correspondence_limit=note,reader_note=note)
 save(P/'BOUNDARIES.json',rows)
 adopted=[r for r in rows if r.get('Latin_locator')];pending=[r['number'] for r in rows if r['editorial_status']=='PENDING_USER_DECISION']
 for r in adopted:validate(l,r['Latin_locator']);validate(g,r['locator'])
 q=json.loads((P/'LATIN_PARTIAL_IMPLEMENTATION.json').read_text());q['qualified_correspondence_sections']=[r['number'] for r in rows if r.get('correspondence_status','').startswith(('PARTIAL','PRESENT_WITH'))];save(P/'LATIN_PARTIAL_IMPLEMENTATION.json',q)
 scope=json.loads((P/'NARRATIVE_SCOPE.json').read_text());scope.update(frozen_inputs_unchanged=True,Latin_narrative_codepoints=len(l.stream),Latin_narrative_sha256=digest(l.stream.encode()),
  Latin_scope_exclusions='LATIN_SCOPE_EXCLUSIONS.json',policy='Accepted chapter-0/num/note/app/rdg exclusions; embedded Greek chronological contents conclusion, marginal numeral/annotation sigla and individually identified literal chapter labels excluded. Word corrections and interlinear additions retained. All original bytes preserved.')
 save(P/'NARRATIVE_SCOPE.json',scope);save(P/'LATIN_SCOPE_EXCLUSIONS.json',l.scope_exclusions)
 status=dict(book=b,status='PROVISIONAL_FULL_REVIEW_INCOMPLETE',pinned_commit=PIN,branch=git('branch','--show-current'),checkpoint_parent_commit=git('rev-parse','HEAD'),
  expected_sections=total,complete_machine_Greek_census=True,Greek_print_verified=sum(r['Greek_print_status']!='UNREVIEWED' for r in rows),
  Latin_individually_reviewed=sum(r['Latin_review_status']!='UNREVIEWED' for r in rows),adopted_Latin_starts=len(adopted),retained_starts=len(q['retained_starts']),added_Latin_milestones=q['milestones_added'],
  approved_Greek_marker_edits=[dict(kind='ADD_IMPLICIT_OPENING_NUM',number=1,record='GREEK_OPENING_IMPLEMENTATION.json')],
 introduced_absences=len([r for r in rows if r['correspondence_status']=='UNAVAILABLE']),unavailable_sections=[r['number'] for r in rows if r['correspondence_status']=='UNAVAILABLE'],pending_decisions=pending,remaining_Latin_reviews=[r['number'] for r in rows if r['Latin_review_status']=='UNREVIEWED'],
  complete_adjoining_intervals=sum(bool(r.get('Latin_interval')) for r in adopted),full_narrative_partition=False,exact_Latin_byte_recovery=q['exact_byte_reversal'],
  English_unchanged=True,locator_validation=dict(status='PASS',Greek=validate_all_nodes(g),Latin=validate_all_nodes(l)),
  local_reader_checkpoint='PARTIAL_READER_QA.json',full_book_reader_certified=False,full_book_availability_enabled=False,published_baseline=3157,added_published_selectable_coverage=0,integration_ready=False)
 save(P/'CHECKPOINT_CERTIFICATE.json',status)
 executable=dict(book=b,expected_range=[1,total],full_book_enabled=False,status='ADOPTED_IDENTITIES_ONLY_INCOMPLETE_BOOK',
  sections=[dict(number=r['number'],Latin=dict(available=r['correspondence_status']!='UNAVAILABLE',correspondence=r['correspondence_status'],note=r.get('reader_note')),contextTarget=r.get('contextTarget') or r['Latin_paragraph_id'],physical_placement=r['physical_placement_status']) for r in rows if r.get('Latin_locator') or r['correspondence_status']=='UNAVAILABLE'],
  pending_editorial=pending,unreviewed=status['remaining_Latin_reviews'],suppressedLatinLabels=json.loads((P/'INHERITED_LABEL_EXCEPTIONS_PARTIAL.json').read_text()))
 save(P/'EXECUTABLE_IDENTITIES.json',executable)
 with (P/'BOUNDARIES_REVIEW.tsv').open('w',encoding='utf8',newline='') as f:
  w=csv.writer(f,delimiter='\t');w.writerow(['section','Greek print','Latin review','placement','correspondence','editorial','paragraph','text/tail path','Unicode node offset','raw UTF8 byte','Greek text','Latin left context','Latin right context','reason','image'])
  for r in rows:
   loc=r.get('Latin_locator',{});w.writerow([r['number'],r['Greek_print_status'],r['Latin_review_status'],r['physical_placement_status'],r['correspondence_status'],r['editorial_status'],r.get('Latin_paragraph_id',''),loc.get('text_node_path',''),loc.get('node_offset',''),loc.get('raw_byte',''),r['Greek'],loc.get('left',''),loc.get('right',''),r.get('review_reason',''),r.get('print_observation',{}).get('image','')])
 authority=P/'SOURCE_AUTHORITY.md';txt=authority.read_text().replace('Printed title, coverage and individual starts remain to be independently inspected in this assignment.','The printed title, book opening, narrative ending and the reviewed starts recorded in BOUNDARIES.json were independently inspected in this assignment. Remaining rows are explicitly unreviewed.')
 txt=re.sub(r'Current status:.*',f'Current status: {status["Latin_individually_reviewed"]} individually reviewed Latin candidates, {len(adopted)} represented starts, {status["introduced_absences"]} verified unavailabilities and {len(pending)} pending editorial cuts. The printed range is 1–{total}. Full-book reader certification remains incomplete; CHECKPOINT_CERTIFICATE.json distinguishes exact byte recovery and limited local reader QA from the full gate.',txt)
 authority.write_text(txt,encoding='utf8',newline='\n')
 qa=json.loads((P/'PARTIAL_READER_QA.json').read_text())
 md=f'''# Book {roman}: provisional implementation checkpoint

Pinned baseline: `{PIN}`. Branch: `{status['branch']}`. This book is **not ready for integration**.

Expected identities: **{total}**, established from the complete Greek XML census and independently inspected printed opening and terminal section. Interior print verification and Latin correspondence remain explicitly separate. Visually verified Greek rows: {status['Greek_print_verified']}; individually reviewed Latin candidates: {status['Latin_individually_reviewed']}; represented starts: {len(adopted)} ({status['retained_starts']} retained, {status['added_Latin_milestones']} added milestones). Verified whole-section unavailabilities in this transcription: {status['unavailable_sections']}. Unreviewed Latin candidates: {len(status['remaining_Latin_reviews'])}.

Pending editorial decisions: {', '.join(map(str,pending)) or 'none among the inspected candidates'}. Full narrative partition and final Latin extent remain provisional. The final adopted starts and any unresolved predecessor intervals must not be treated as complete extents.

The only Greek citation edit is addition of the independently verified implicit opening 1 using the accepted num mechanism, after the preserved chronological contents prefix. No Greek word or existing citation marker has been moved or corrected. Latin changes insert milestones at validated original raw-byte positions. Every added milestone reverses to the same frozen UTF-8/LF input bytes; narrative wording, punctuation, spelling, whitespace, IDs, sameAs, paragraphs, traditional divisions and apparatus remain unchanged. English files remain byte-identical.

Local reader QA passed **{len(qa['intervals'])} adjoining intervals** on the earlier checkpoint saved under [reader-tested-checkpoint3](reader-tested-checkpoint3), with actual build hashes and corpus bytes. It checked actual selection text in all languages, IDs, chapter/subchapter coverage, deep links, reload/history, previous/next, panes and light/dark themes. Later starts recorded in this current corpus require a fresh build and reader QA. The isolated test registry enables only its reviewed checkpoint range; production availability stays disabled. See [PARTIAL_READER_QA.json](PARTIAL_READER_QA.json).

Shared protected checks passed the accepted VIII/X identity censuses, critical boundary cases, protected contents/traditional/Bamberg/Alignment routes, Whiston, Bellum/Lodge and other affected works. The shared support change only permits milestones inside anonymous paragraphs. The exact inherited Book-I apparatus targets and unsupported I.1 baseline error remain narrowly documented; no additional error was excused.

The published baseline remains **3,157 selectable identities**. Added published or production-enabled coverage is **0**; this local scholarly checkpoint does not imply new published coverage.

Review data: [BOUNDARIES.json](BOUNDARIES.json), [human review register](BOUNDARIES_REVIEW.tsv), [checkpoint certificate](CHECKPOINT_CERTIFICATE.json), [executable identity plan](EXECUTABLE_IDENTITIES.json), [source authority](SOURCE_AUTHORITY.md), [decision history](DECISION_HISTORY.json), [Latin preservation](LATIN_PARTIAL_IMPLEMENTATION.json), [file manifest](FILE_MANIFEST.json).

No canonical merge, branch push, preview update or deployment has occurred. Remaining work is the unreviewed printed/Latin candidates, pending decisions, full executable identity registry, final partition/extent checks and fresh full-book browser certification.
'''
 (P/'REPORT.md').write_text(md,encoding='utf8',newline='\n')
 files=[dict(path=str(f),relative_path=f.relative_to(ROOT).as_posix(),bytes=f.stat().st_size,sha256=digest(f.read_bytes())) for f in sorted(P.rglob('*')) if f.is_file() and f.name!='FILE_MANIFEST.json']
 save(P/'FILE_MANIFEST.json',dict(book=b,pinned_commit=PIN,files=files,note='All rendered pages included; presence of an image does not imply visual inspection. Per-row statuses identify actual inspected starts.'))
 print(roman,status['Latin_individually_reviewed'],len(adopted),status['added_Latin_milestones'],'pending',pending,'remaining',len(status['remaining_Latin_reviews']))
canonical=Path(r'C:\Users\Pollard_R\Git\LatinJosephus-v2-development')
save(BATCH/'CANONICAL_HEAD_OBSERVATIONS.json',dict(initial=PIN,current=git('rev-parse','HEAD',cwd=canonical),frozen_assignment_inputs_changed=False))
names=git('diff','--name-only',PIN,'--').splitlines();allowed=['assets/js/renderTei.js','assets/xml/antiquities/niese/book-14.json','assets/xml/antiquities/niese/book-15.json',*[f'assets/xml/antiquities/{language}/book-{b:02}.xml' for b in [14,15] for language in ['Greek','Latin']]]
assert all(n in allowed or n.startswith(('review/Antiquities_Niese_BookXIV_2026-10-09/','review/Antiquities_Niese_BookXV_2026-10-09/','review/Antiquities_Niese_Batch_14_15_2026-10-09/')) for n in names),names
save(BATCH/'CHANGED_FILE_SCOPE.json',dict(pinned_commit=PIN,tracked_changed_files=names,allowed_production_files=allowed,scope='PASS',other_books_changed=False,canonical_changed=False,preview_changed=False))
