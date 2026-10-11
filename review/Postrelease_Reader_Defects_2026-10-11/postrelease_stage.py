import postrelease_reader as a
import shutil,sys,json,subprocess,zipfile
def record_baseline():
    q=a.Q;T=a.T
    for name in ['FIVE_DEFECTS_baseline.json','FIVE_DEFECTS_live.json','APPARATUS_SOURCE_TRACE.json','ANNOTATIONS_ID_SOURCE_INVENTORY.json','BUILD_baseline.json']:
        shutil.copy2(T/name,q/name)
    audit=[]
    for n in ['INDEPENDENT_AUDIT_REPORT.md','AUDIT_MATRIX.csv','EVIDENCE_INDEX.md','READ_ONLY_RECEIPT.json','APPARATUS_HTTP_PROOF.json']:
        p=a.AUDIT/n;audit.append({'path':str(p),'SHA256':a.sha(p.read_bytes())})
    a.save(q/'AUDIT_REFERENCE_MANIFEST.json',audit)
    before=a.load(T/'FIVE_DEFECTS_baseline.json');live=a.load(T/'FIVE_DEFECTS_live.json');assert len(before['rows'])==len(live['rows'])==11
    for data in [before,live]:
        for route in ['/','/about/','/background/']:assert len(next(x for x in data['rows'] if x['route']==route)['errors'])==1
        for b in [11,20]:assert next(x for x in data['rows'] if x['route']=='/antiquities/?book='+str(b))['state']['duplicates'][0][0]=='annotations'
        bad=next(x for x in data['rows'] if x['route'].endswith('bamberg=5'));assert len([x for x in bad['state']['links'] if x['href'].startswith('undefinednote')])==3
        assert len(data['linkRequests'])==2 and all(x['status']==404 for x in data['linkRequests'])
        assert len(next(x for x in data['rows'] if x['route'].endswith('book=1&niese=1'))['errors'])==1
    paragraphs=['# Five current defect reproductions','',f'Canonical base {a.F}; public preview {a.V}. Both were independently observed in fresh browser profiles. Full raw before states, console stacks, exact hrefs, source targets, note/ID markup and screenshots are in FIVE_DEFECTS_baseline.json and FIVE_DEFECTS_live.json.','', '| Package | Actual before state |','|---|---|','| A | Unnamed unfocusable theme anchor; no button role, label or pressed state. |','| B | Two annotations IDs: converted Latin standOff plus UI accordion in Books XI/XX. The ID is defined only in Latin source files across all 143 XML inputs. |','| C | Three dot anchors in Latin I.34, Bamberg division 5; three absent target UUIDs; two exact malformed GET404 URLs. Source trace records all missing identifiers. No exact target mapping can be inferred from nearby notes. |','| D | Home/About/Background call reader initialization with no WORKS entry and throw on activeWork.languages. |','| E | I.1 yields null canonical selection, dereferenced by parseAnnotations. Narrative I menu starts at 27; Proem 1 is separately supported. |','', 'VII.6 was positively checked during both baselines: complete existing first Whiston paragraph exactly once. Original audit VII.1 failure is not carried forward as a current exception.','', 'A baseline capture initially stopped when Chromium displayed its native error for the deliberately failing local 404 target. That partial capture and script are preserved in runtime attempts/baseline-http-error; the narrow expected-link failure was then recorded explicitly and the whole baseline capture rerun. No production assertion was relaxed.','']
    (q/'DEFECT_REPRODUCTIONS.md').write_text('\n'.join(paragraphs),encoding='utf8',newline='\n')
    (q/'DECISIONS.md').write_text('# Reader repair decisions\n\nA: Use one native button with constant accessible name Dark mode and accurate aria-pressed state. Preserve existing icons/storage and add visible keyboard focus.\n\nB: Namespace the UI accordion as reader-annotations, updating its exact renderer, CSS and MDB parent references. Preserve all source xml:id values and converted source annotations IDs. All current source annotations IDs occur only in the canonical Latin pane, so no source-source duplicate is present.\n\nC: EDITORIAL HOLD pending the requested narrow disposition. No target UUID is defined in the current corpus. Adding a hash or stripping undefined does not recover the missing destination. Mapping these UUIDs to nearby notes would be invented evidence. No scholarly XML or fabricated note is authorized.\n\nD: Limit shared reader initialization to pages with an actual WORKS data contract and reader elements; general-site controls remain initialized by their existing scripts.\n\nE: Validate an explicitly requested Antiquities Niese identity against actual registry/menu entries before selection and annotation dereferencing. Preserve the invalid URL and show a clear notice with valid links, without substituting prose or relabelling Proem.\n',encoding='utf8',newline='\n')
    for f in ['postrelease_reader.py','postrelease_reproduce.cjs','postrelease_stage.py']:
        shutil.copy2(f,q/f)
    commit('baseline','Record independent reader-defect baselines and protected source inputs')
def checkpoint(stage):
    out=a.T/'checkpoints'/('checkpoint-'+stage+'.zip');files=[]
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
        for f in sorted(a.Q.rglob('*')):
            if f.is_file() and f.suffix in ['.md','.json','.py','.cjs','.rb','.yml'] and f.stat().st_size<2_000_000:
                n=f.relative_to(a.Q).as_posix();z.write(f,n);files.append({'path':n,'SHA256':a.sha(f.read_bytes())})
        diff=a.git('diff',a.F,'--',':(exclude)review/',repo=a.W);z.writestr('production.diff',diff)
    a.save(a.T/'checkpoints'/('checkpoint-'+stage+'.json'),{'UTC':a.now(),'stage':stage,'HEAD':a.gt('rev-parse','HEAD',repo=a.W),'ZIP_SHA256':a.sha(out.read_bytes()),'files':files,'production_diff_SHA256':a.sha(diff),'large_source_and_browser_cache_excluded':True})
def commit(stage,message):
    a.git('diff','--check',repo=a.W)
    subprocess.run(['git','add','--','review/Postrelease_Reader_Defects_2026-10-11'],cwd=a.W,check=True)
    subprocess.run(['git','commit','-m',message],cwd=a.W,check=True)
    checkpoint(stage)
    print('DURABLE CHECKPOINT',stage,a.gt('rev-parse','HEAD',repo=a.W))
if __name__=='__main__':
    if sys.argv[1]=='baseline':record_baseline()
    elif sys.argv[1]=='checkpoint':checkpoint(sys.argv[2])
