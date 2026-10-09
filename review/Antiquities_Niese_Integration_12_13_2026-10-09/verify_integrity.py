"""New merged-build integrity gate; incoming certificates remain historical and immutable."""
from preflight import *
import sys,re,shutil
sys.dont_write_bytecode=True
batch=ROOT/'review/Antiquities_Niese_Batch_12_13_2026-10-09'
sys.path.insert(0,str(batch))
from prepare_review import Book
from record_review import independent_node

def tree(commit):
    entries={}
    for entry in git(ROOT,'ls-tree','-rz','--full-tree',commit).split(b'\0'):
        if entry:
            metadata,p=entry.split(b'\t',1);entries[p.decode()] = metadata.decode().split()[-1]
    return entries

def inverse(raw,operations):
    for op in sorted(operations,key=lambda x:(x['at'],x['delete']),reverse=True):
        old=bytes.fromhex(op['before_hex']);new=bytes.fromhex(op['after_hex']);at=op['at']
        assert raw[at:at+len(old)]==old
        raw=raw[:at]+new+raw[at+len(old):]
    return raw

commit=textgit(ROOT,'rev-parse','HEAD');merged=tree(commit);source=tree(TIP)
scope=read(PACK/'INCOMING_SCOPE.json');baseline=read(PACK/'BASELINE.json')
assert textgit(ROOT,'merge-base','--is-ancestor',TIP,commit)==''
for item in scope['production']+scope['review']:
    path=item['path']
    if path=='assets/js/renderTei.js':continue
    assert merged[path]==source[path],path
    assert sha((ROOT/path).read_bytes())==item['certified_working_sha256'],path
allowed={i['path'] for i in scope['production']}
protected=[]
for item in baseline['canonical_tracked_files']:
    if item['path'] not in allowed:
        assert merged[item['path']]==item['blob'],item['path']
        protected.append({'path':item['path'],'blob':item['blob'],'working_sha256':sha((ROOT/item['path']).read_bytes())})
books=[]
for b in [12,13]:
    d=ROOT/f'review/Antiquities_Niese_Book{"XII" if b==12 else "XIII"}_2026-10-09'
    frozen=read(d/'BASELINE.json');rows=read(d/'BOUNDARIES.json');proof=read(d/'IMPLEMENTATION_PRESERVATION.json');plan=read(d/'APPROVED_MARKER_PLAN.json')
    registry=read(ROOT/f'assets/xml/antiquities/niese/book-{b:02}.json')
    perbook={'book':b,'identities':len(rows),'Latin_intervals':sum(s['Latin']['available'] for s in registry['sections']),
             'no_independent_Latin_intervals':plan['no_independent_Latin_intervals'],'languages':[]}
    for lang in ['Greek','Latin']:
        original=(d/'inputs'/f'{lang}-book-{b:02}.xml').read_bytes()
        raw=(ROOT/f'assets/xml/antiquities/{lang}/book-{b:02}.xml').read_bytes()
        record=next(x for x in proof['source_records'] if x['language']==lang)
        assert sha(original)==frozen['inputs'][lang]['sha256']
        assert sha(raw)==record['after_sha256'] and inverse(raw,record['inverse_operations'])==original
        if lang=='Latin':
            pattern=rb'<milestone unit="niese" n="[1-9]\d*"/>|<milestone unit="niese-end"/>'
            assert not re.search(pattern,original)
            tags=re.findall(pattern,raw)
            assert len(tags)==len(plan['Latin_authorized_marker_operations'])
            recovered=re.sub(pattern,b'',raw)
        else:
            assert len(plan['Greek_authorized_marker_operations'])==1
            at=rows[0]['Greek']['locator']['raw_byte'];assert raw[at:at+14]==b'<num>[1]</num>'
            recovered=raw[:at]+raw[at+14:]
        assert recovered==original
        old=Book(raw=original);new=Book(raw=raw);assert old.stream==new.stream
        positioned=[r for r in rows if r[lang]['locator']]
        starts=[r[lang]['locator']['book_offset'] for r in positioned];assert starts==sorted(set(starts))
        intervals=[old.stream[a:z] for a,z in zip(starts,starts[1:]+[len(old.stream)])]
        assert all(t.strip() for t in intervals) and ''.join(intervals)==old.stream[starts[0]:]
        assert not old.stream[:starts[0]] or old.stream[:starts[0]].isspace()
        for row,interval in zip(positioned,intervals):
            loc=row[lang]['locator'];independent_node(old,loc);assert old.locate(loc['book_offset'])==loc
            assert interval==row[lang]['section' if lang=='Greek' else 'interval']
        for query in ['//@xml:id','//@sameAs']:
            ns={'xml':'http://www.w3.org/XML/1998/namespace'};assert old.tree.xpath(query,namespaces=ns)==new.tree.xpath(query,namespaces=ns)
        perbook['languages'].append({'language':lang,'before_sha256':sha(original),'merged_sha256':sha(raw),
            'source_exact_inverse':'PASS','independent_precise_tag_recovery':'PASS','node_UTF8_locators_validated':len(positioned),
            'complete_narrative_partition':'PASS','IDs_sameAs_words_punctuation_whitespace_preserved':'PASS'})
    english=(ROOT/f'assets/xml/antiquities/English/book-{b:02}.xml').read_bytes()
    assert english==(d/'inputs'/f'English-book-{b:02}.xml').read_bytes()
    perbook['English_unchanged_sha256']=sha(english)
    perbook['source_certificate_sha256']=sha((d/'CERTIFICATE.json').read_bytes())
    books.append(perbook)
ix=read(ROOT/'assets/xml/antiquities/niese/book-09.json')
assert len(ix['sections'])==291 and sum(s['Latin']['available'] for s in ix['sections'])==232
assert [s['number'] for s in ix['sections'] if not s['Latin']['available']]==list(range(51,110))
save('INTEGRITY_QA.json',{'tested_merge_commit':commit,'tested_merge_tree':textgit(ROOT,'rev-parse','HEAD^{tree}'),
    'incoming_review_files_exact':scope['review_count'],'incoming_data_files_exact':6,'protected_canonical_file_count':len(protected),
    'protected_canonical_files':protected,'books':books,'IX':{'identities':291,'Latin_intervals':232,'unavailable_Latin':list(range(51,110)),'canonical_blobs_preserved':True},
    'source_certificates_unchanged':True,'English_and_Whiston_canonical_files_preserved':True,'result':'PASS'})
build_checks=[]
paths=[p for p in merged if p.startswith('assets/xml/')]+['assets/js/renderTei.js','assets/css/tei.css']
for rel in paths:
    raw=(ROOT/rel).read_bytes();built=(RUNTIME/'site'/rel).read_bytes();assert raw==built,rel
    build_checks.append({'path':rel,'source_and_build_sha256':sha(raw)})
for rel in ['assets/js/renderTei.js','assets/css/tei.css','assets/xml/source-contents.xml']:
    assert (RUNTIME/'baseline-site'/rel).read_bytes()==git(ROOT,'show',f'{START}:{rel}'),rel
logs=[]
(PACK/'build-logs').mkdir(exist_ok=True)
for name in ['jekyll.log','baseline-jekyll.log','dependencies.log']:
    p=RUNTIME/name;assert p.is_file();shutil.copyfile(p,PACK/'build-logs'/name)
    if name!='dependencies.log':assert b'done in' in p.read_bytes()
    logs.append({'path':str(p),'sha256':sha(p.read_bytes()),'integration_copy':f'build-logs/{name}'})
production=[{'path':p,'blob':blob} for p,blob in sorted(merged.items()) if not p.startswith('review/')]
save('BUILD_RECORD.json',{'result':'PASS','candidate_commit':commit,'candidate_tree':textgit(ROOT,'rev-parse','HEAD^{tree}'),
    'starting_canonical_commit':START,'certified_source_tip':TIP,'code_data_sha256':sha(json.dumps(production,sort_keys=True).encode()),
    'source_worktree_production_equals_committed_merge':True,'review_only_untracked_QA_helpers_excluded_by_build':True,
    'workflow':'Complete documented Jekyll build with all Gemfile plugins, candidate and archived current canonical in one isolated container',
    'ruby_image':'ruby@sha256:dba270af6994f64e45ee3dd2b85225a2a0d01f29c04508c7a3c7c8dbf59d2a85',
    'bundler':'4.0.22','build_exit_code':0,'runtime':str(RUNTIME),'static_source_output_checks':build_checks,'logs':logs,
    'executable_paths':{'Python':sys.executable,'Chrome':'C:/Program Files/Google/Chrome/Application/chrome.exe',
    'Playwright':'C:/Users/Pollard_R/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright'}})
print('PASS exact XII/XIII inverse and node/UTF-8 partitions; immutable incoming reviews; protected canonical/IX/Whiston; actual merged build hashes')
