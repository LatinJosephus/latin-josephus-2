"""Reconcile frozen evidence without rerunning unchanged expensive browser suites."""
from pathlib import Path
import collections, csv, datetime, hashlib, json, subprocess, zipfile
ROOT=Path(__file__).resolve().parents[3]
PACK=ROOT/'review/Whiston_I_XI_Canonical_Integration_2026-10-11'
ORIGINAL=ROOT/'review/Whiston_I_XI_Renderer_2026-10-11'
PIN='663b8ce318f0aa247d304d8eeda5b8e76e7489c6'
PROTO='0c1347a5a947ae5702cf60e4162d09d7510450e5'
BOOKI='b8cf6c9d36db610ea1dc4c65d070b016048262e1'
sha=lambda b:hashlib.sha256(b).hexdigest()
git=lambda *a:subprocess.check_output(['git',*a],cwd=ROOT)
load=lambda p:json.loads(p.read_bytes())
save=lambda name,obj:(PACK/name).write_bytes((json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode())
assert git('rev-parse','v2-development').decode().strip()==PIN
prototype_files=git('ls-tree','-r','--name-only',PROTO).decode().splitlines()
original_evidence=[]
for rel in prototype_files:
    if not rel.startswith('review/Whiston_I_XI_Renderer_2026-10-11/'):continue
    body=git('show',PROTO+':'+rel)
    assert (ROOT/rel).read_bytes()==body,rel
    original_evidence.append({'path':rel,'sha256':sha(body)})
changed_runtime=[p for p in git('diff','--name-only',PIN,PROTO).decode().splitlines() if not p.startswith('review/')]
assert len(changed_runtime)==16
for rel in prototype_files:
    if rel.startswith(('assets/','_pages/','_layouts/','_includes/','_sass/')) or rel in ['_config.yml','Gemfile']:
        assert (ROOT/rel).read_bytes()==git('show',PROTO+':'+rel),rel
inventory=load(ORIGINAL/'SOURCE_INVENTORY.json')
sources=[]
for book in inventory:
    archive=Path(book['archive'])
    assert sha(archive.read_bytes())==book['archive_sha256']
    with zipfile.ZipFile(archive) as z:assert z.testzip() is None
    for output in book['outputs']:
        body=git('show',book['delivery_commit']+':'+output['path'])
        assert (ROOT/output['path']).read_bytes()==body
        assert sha(body)==output['sha256']
        sources.append({'book':book['book'],'path':output['path'],'delivery_commit':book['delivery_commit'],'sha256':sha(body),'byte_preserved':True})
oracle=load(ORIGINAL/'INTERVAL_ORACLE.json')
browser=load(ORIGINAL/'BROWSER_QA.json')
regression=load(ORIGINAL/'REGRESSION_QA.json')
aux=load(ORIGINAL/'AUXILIARY_QA.json')
assert browser['status']=='SECTIONS-PASS' and len(browser['sections'])==len(oracle)==3821
expected={(e['book'],e['number']):e for e in oracle}
assert len(expected)==3821
assert len({(r['book'],r['number']) for r in browser['sections']})==3821
for row in browser['sections']:
    e=expected[row['book'],row['number']]
    assert row['passed'] and row['allNarrativeVisible'] and row['GreekLatinPresentationUnchanged']
    assert sha(e['text'].encode())==e['sha256']==row['expectedSHA256']==row['renderedSHA256']
    assert e['opening']==row['opening'] and e['closing']==row['closing']
    assert e['nextPhysical']==row['nextPhysical']
assert regression['status']==aux['status']=='PASS'
assert len(regression['traditional'])==967 and len(regression['alignment'])==823
assert len(regression['book'])==12 and len(regression['unsegmented'])==18
assert len(regression['navigation'])==57 and len(regression['crossWork'])==105
assert not browser['errors'] and not browser['requests'] and not regression['errors'] and not regression['requests'] and not aux['errors']
assert aux['DEHConcordance']['passed'] and len(aux['DEHConcordance']['componentChecks'])==2115
for field,rel in [('rendererSHA256','assets/js/renderTei.js'),('registrySHA256','assets/xml/antiquities/niese/book-09.json'),('structureSHA256','assets/xml/antiquities/structure.xml')]:
    assert browser[field]==sha((ROOT/rel).read_bytes())
xi=[e['number'] for e in oracle if e['book']=='11']
assert xi==list(range(1,312))+list(range(326,343))+list(range(312,326))+list(range(343,348))
before=json.loads(git('show',PIN+':assets/xml/antiquities/niese/book-09.json'))
after=load(ROOT/'assets/xml/antiquities/niese/book-09.json')
for a,b in zip(before['sections'],after['sections']):
    assert a.get('Greek')==b.get('Greek') and a.get('Latin')==b.get('Latin')
    if 51<=b['number']<=109: assert b['English']['available'] and not b['Greek']['available'] and not b['Latin']['available']
zip_path=Path('C:/workspace/Whiston-I-XI-Renderer-Delivery-20261011/Whiston-I-XI-Renderer-Prototype-Certified.zip')
assert sha(zip_path.read_bytes())=='781c6909ad87d9629aa25d056635cfdd2f9d5eecc41e656469586122b25f012a'
with zipfile.ZipFile(zip_path) as z:
    assert z.testzip() is None
    for row in json.loads(z.read('CHECKSUMS.json')): assert sha(z.read(row['path']))==row['sha256']
report={'status':'PASS','verified_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'pinned_canonical_commit':PIN,'certified_prototype_commit':PROTO,'all_runtime_inputs_byte_identical_to_prototype':True,
 'original_certificate_and_evidence_unchanged':original_evidence,'source_preservation':sources,
 'exact_English_intervals_independently_reconciled':3821,'traditional_views':967,'alignment_views':823,'whole_files':12,
 'navigation':57,'fallback_XII_XX':18,'cross_work_display_checks':dict(collections.Counter(x['work'] for x in regression['crossWork'])),
 'full_DEH_component_checks':2115,'DEH_section_occurrences':8193,'restored_IX':59,'XI_physical_order_verified':True,
 'Greek_Latin_all_runtime_inputs_unchanged':True,'original_recovery_archive_reverified':True,
 'method':'Reuse complete actual displayed-content evidence only after verifying every production runtime input and original evidence byte against the certified prototype; independently reconcile every per-section hash and boundary. Candidate guard changes do not execute in the reader.'}
save('EVIDENCE_RECONCILIATION.json',report)
save('SOURCE_INVENTORY.json',inventory)
(PACK/'PER_SECTION_QA.csv').write_bytes((ORIGINAL/'PER_SECTION_QA.csv').read_bytes())
# Preserve the original scholarly evidence without rewriting its historical verdict.
evidence_dir=PACK/'BookI-original';evidence_dir.mkdir(exist_ok=True)
booki_path='review/BookI_Pilot_2026-10-10/'
records=[]
for name in ['REPORT.md','ADJUDICATION.md','ADJUDICATION_RECORDS.json','QA.json','SOURCE_DIFFERENCE_REVIEW.md','SOURCE_DIFFERENCES.json','SCHEMA_QA.json','RENDERER_QA.json']:
    body=git('show',BOOKI+':'+booki_path+name)
    (evidence_dir/name).write_bytes(body);records.append({'path':booki_path+name,'delivery_commit':BOOKI,'sha256':sha(body)})
qa=load(evidence_dir/'QA.json')
assert qa['unresolved_boundary_candidates']==0 and qa['unexplained_textual_changes']==0
assert qa['confidence']=={'HIGH':329,'MEDIUM':17}
greek=git('show',PIN+':assets/xml/antiquities/Greek/book-01.xml').decode()
assert '<num>[272]</num> τῆς τριχὸς' in greek
original_greek=git('show',BOOKI+':assets/xml/antiquities/Greek/book-01.xml')
assert original_greek==greek.encode()
save('BOOK_I_SUPERSEDING_CERTIFICATION.json',{'receipt':'Superseding scoped Book I English certification','issued_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'original_delivery_commit':BOOKI,'original_report_preserved':records,'supersedes':'The historical blanket NOT CERTIFIED / integration hold insofar as it applied to English segmentation and renderer readiness.',
 'English_DATA':'DATA-GO for exact segmentation of the preserved project transcription','English_RENDERER':'RENDERER-GO, 346/346 exact displayed intervals',
 'scope':'Proem I.1–26 and narrative I.27–346; source wording, surviving text, markup and all adopted boundaries unchanged.',
 'original_objections':[
  {'issue':'Contextual English renderer','disposition':'Resolved by independently verified 346/346 exact English interval rendering and preserved containing views.'},
  {'issue':'17 MEDIUM segmentation decisions','disposition':'All individually adjudicated in original evidence; zero unresolved candidates. MEDIUM remains MEDIUM; no new scholarly adjudication.'},
  {'issue':'Greek I.272 marker','disposition':'Inherited Greek editorial/control disagreement remains OPEN. Same Greek bytes in Book I delivery and current canonical; no later correction found in file history or canonical reports. It blocks a complete cross-language agreement claim, not faithful display of the adopted English interval.'},
  {'issue':'35 inherited English source differences, including I.260–263 losses and damaged I.271','disposition':'Acknowledged and retained. DATA-GO certifies segmentation of surviving project text; it does not certify a complete or corrected Whiston transcription.'},
  {'issue':'Inherited duplicate annotations ID and headerless TEI schema diagnostics','disposition':'Baseline conditions retained; no new source/schema diagnostic or duplicate ID introduced.'}],
 'not_certified':['Complete cross-language boundary agreement at Greek I.272','Restoration or editorial repair of inherited Book I English losses','Generic TEI All conformance','Public deployment'],
 'integration_disposition':'English integration eligible with these retained qualifications; no segmentation or Greek change required.'})
print('Verified unchanged prototype evidence, 3821 interval hashes and boundaries, all sources, original recovery archive; issued scoped Book I receipt.')
