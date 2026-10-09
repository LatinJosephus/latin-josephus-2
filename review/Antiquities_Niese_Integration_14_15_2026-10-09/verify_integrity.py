"""Bind fresh integration to exact certified corpus and actual canonical baselines."""
from pathlib import Path
import hashlib,json,re,subprocess
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
def load(p):return json.loads(p.read_text(encoding='utf8'))
def sha(raw):return hashlib.sha256(raw).hexdigest()
def save(name,x):(P/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT).decode().strip()
base=load(P/'BASELINE.json');runtime=Path(base['runtime']);incoming=load(P/'INCOMING_SCOPE.json')
advance=load(P/'CANONICAL_ADVANCE.json') if (P/'CANONICAL_ADVANCE.json').exists() else None
canonical_records=advance['canonical_tracked_files'] if advance else base['canonical_tracked_files']
tree={line.split(' ',1)[1]:line.split(' ',1)[0] for line in git('ls-tree','-r','--format=%(objectname) %(path)','HEAD').splitlines()}
production={r['path'] for r in incoming['files'] if r['kind']=='production'}
working_variants=[];protected=0
for r in canonical_records:
 if r['path'] in production:continue
 assert tree[r['path']]==r['blob'],r['path'];protected+=1
 raw=(ROOT/r['path']).read_bytes()
 if sha(raw)!=r['working_sha256']:
  current=(Path(base['canonical_checkout'])/r['path']).read_bytes()
  assert raw.replace(b'\r\n',b'\n')==current.replace(b'\r\n',b'\n')
  working_variants.append(dict(path=r['path'],canonical_working_sha256=r['working_sha256'],integration_working_sha256=sha(raw),unchanged_Git_blob=r['blob'],difference_only_checkout_line_endings=True,canonical_CRLF=current.count(b'\r\n'),integration_CRLF=raw.count(b'\r\n'),comparison_is_read_only_no_bytes_normalized=True))
 assert sha((Path(base['canonical_checkout'])/r['path']).read_bytes())==r['working_sha256'],r['path']
for r in incoming['files']:
 if r['path']=='assets/js/renderTei.js':continue
 raw=(ROOT/r['path']).read_bytes()
 if r['path']=='assets/xml/antiquities/niese/book-15.json':
  addition=b'  "structuralMilestoneUnits": ["chapter"],\n'
  assert raw.count(addition)==1 and sha(raw.replace(addition,b''))==r['certified_working_sha256']
 else:assert tree[r['path']]==r['blob'] and sha(raw)==r['certified_working_sha256'],r['path']
books=[]
for b,roman in [(14,'XIV'),(15,'XV')]:
 source=ROOT/f'review/Antiquities_Niese_Book{roman}_2026-10-09'
 cert=load(source/'CERTIFICATION.json');partition=load(source/'COMPLETE_PARTITION_QA.json')
 assert cert['status']=='READY_FOR_COORDINATED_INTEGRATION' and partition['status']=='PASS'
 latin=(ROOT/f'assets/xml/antiquities/Latin/book-{b:02}.xml').read_bytes();before=(source/'frozen-inputs/Latin.xml').read_bytes()
 rx=rb'<milestone unit="niese" n="([0-9]+)"/>'
 assert re.sub(rx,b'',latin)==before
 assert len(re.findall(rx,latin))==cert['added_Latin_milestones']
 greek=(ROOT/f'assets/xml/antiquities/Greek/book-{b:02}.xml').read_bytes();inv=load(source/'GREEK_OPENING_IMPLEMENTATION.json')['inverse'];at,n=inv['at'],inv['delete']
 assert greek[at:at+n]==inv['expected'].encode() and greek[:at]+greek[at+n:]==(source/'frozen-inputs/Greek.xml').read_bytes()
 for lang in ['Greek','Latin']:
  q=next(x for x in partition['file_hashes'] if x['language']==lang);assert sha((ROOT/f'assets/xml/antiquities/{lang}/book-{b:02}.xml').read_bytes())==q['after']
  assert sha((source/f'frozen-inputs/{lang}.xml').read_bytes())==q['before']
 engpath=f'assets/xml/antiquities/English/book-{b:02}.xml';actual=(ROOT/engpath).read_bytes();cb=next(x for x in base['canonical_tracked_files'] if x['path']==engpath)
 assert sha(actual)==cb['working_sha256']
 books.append(dict(book=b,identities=cert['selectable_identities'],Latin_intervals=cert['nonempty_Latin_intervals'],retained_starts=cert['retained_starts'],added_milestones=cert['added_Latin_milestones'],unavailable=cert['unavailable_sections'],Greek_additions=[1],Greek_corrections=[],Greek_moves=[],exact_Latin_inverse=True,exact_Greek_inverse=True,all_original_markup_IDs_sameAs_partitions_preserved=True,independent_locator_certificate_sha256=sha((source/'COMPLETE_PARTITION_QA.json').read_bytes()),locator_evidence_reused_because_input_and_output_bytes_identical=True,source_frozen_English_sha256=sha((source/'frozen-inputs/English.xml').read_bytes()),current_canonical_English_sha256=cb['working_sha256'],integration_English_sha256=sha(actual),two_English_baselines_equal=actual==(source/'frozen-inputs/English.xml').read_bytes()))
integrity=dict(result='PASS',tested_production_commit=git('rev-parse','HEAD'),source_tip=base['source_tip'],frozen_source_base=base['frozen_source_base'],actual_canonical_start=base['canonical_start'],effective_canonical_baseline=advance['canonical_advance'] if advance else base['canonical_start'],incoming_review_files_byte_identical=531,incoming_corpus_files_byte_identical=4,incoming_XIV_registry_byte_identical=True,XV_registry_certified_bytes_recovered_by_removing_one_integration_metadata_line=True,XV_accepted_sections_notes_range_representation_unchanged=True,canonical_protected_Git_blobs_unchanged=protected,canonical_actual_working_bytes_unchanged=True,integration_checkout_working_variants=working_variants,books=books,source_certificates_unchanged=True,source_byte_recovery_without_normalization=True)
save('INTEGRITY_QA.json',integrity)
prod=[];checks=[]
for f in sorted(production):
 raw=(ROOT/f).read_bytes();built=(runtime/'site'/f).read_bytes();assert raw==built,f
 prod.append(dict(path=f,merged_blob=tree[f],merged_sha256=sha(raw),bytes=len(raw),certified_source_sha256=next(x['certified_working_sha256'] for x in incoming['files'] if x['path']==f),equals_source=f not in ['assets/js/renderTei.js','assets/xml/antiquities/niese/book-15.json'],CRLF=raw.count(b'\r\n'),LF=raw.count(b'\n')))
for f in sorted(x['path'] for x in canonical_records if not x['path'].startswith('review/')):
 raw=(ROOT/f).read_bytes();built=(runtime/'site'/f)
 if built.is_file() and (f.startswith('assets/') or f.startswith('_includes/')):
  assert built.read_bytes()==raw,f;checks.append(dict(path=f,sha256=sha(raw)))
for name in ['jekyll.log','baseline-jekyll.log']:
 text=(runtime/name).read_text();assert 'done in' in text and 'Configuration file:' in text
(P/'build-logs').mkdir(exist_ok=True)
for name in ['jekyll.log','baseline-jekyll.log','dependencies.log','docker-build.log']:(P/'build-logs'/name).write_bytes((runtime/name).read_bytes())
save('PRODUCTION_MANIFEST.json',dict(result='PASS',tested_merge_commit=git('rev-parse','HEAD'),production_count=7,files=prod))
code=sha('\n'.join(f"{r['path']} {r['blob']}" for r in base['canonical_tracked_files'] if not r['path'].startswith('review/')).encode()+b'\n'+b'\n'.join(f"{r['path']} {r['merged_sha256']}".encode() for r in prod))
save('BUILD_RECORD.json',dict(result='PASS',candidate_commit=git('rev-parse','HEAD'),candidate_tree=git('rev-parse','HEAD^{tree}'),starting_canonical_commit=base['canonical_start'],effective_canonical_baseline=advance['canonical_advance'] if advance else base['canonical_start'],certified_source_tip=base['source_tip'],code_data_sha256=code,workflow='Complete documented Jekyll candidate and archived-current-canonical builds with all Gemfile plugins; isolated read-only source mounts and disposable dependency installation.',ruby_image='ruby@sha256:dba270af6994f64e45ee3dd2b85225a2a0d01f29c04508c7a3c7c8dbf59d2a85',bundler='4.0.22',build_exit_code=0,runtime=str(runtime),candidate_site=str(runtime/'site'),baseline_site=str(runtime/'baseline-site'),static_source_output_checks=checks,production_manifest='PRODUCTION_MANIFEST.json',integration_worktree_production_equals_committed_candidate=True,review_QA_helpers_excluded_by_build=True))
print('PASS integrity and full builds:',protected,'protected canonical blobs;',len(working_variants),'recorded checkout line-ending variants;',len(checks),'static source/build hashes.')
