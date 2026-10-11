from pathlib import Path
import subprocess,json,hashlib,datetime,shutil,sys,zipfile,xml.etree.ElementTree as ET
R=Path('C:/Users/Pollard_R/Git/LatinJosephus-v2-development')
W=Path('C:/workspace/LatinJosephus-postrelease-reader-repairs-20261011')
T=Path('C:/workspace/LatinJosephus-postrelease-reader-repairs-runtime-20261011')
Q=W/'review/Postrelease_Reader_Defects_2026-10-11'
F='4ffbc79b84806d180e9d713f9605255e7dfed73e';V='afea19c25456c4476c37e4ce7164a2b8ed3b61c8'
BR='fix/postrelease-reader-a11y-ids-links-startup-20261011'
I=Path('C:/workspace/Antiquities-VII2-6-Whiston-Integration-runtime-20261010')
P=Path('C:/workspace/Antiquities-VII1-6-Preview-Publication-runtime-20261011')
AUDIT=Path('C:/workspace/LatinJosephus-Antiquities-Final-Independent-Audit-20261010')
PY=sys.executable
NODE='C:/Program Files/WindowsApps/OpenAI.CodexPrimaryRuntime.v26-1007-641-0_26.1007.641.0_x64__3k8sg7r9htsxt/dependencies/node/bin/node.exe'
PW='C:/Program Files/WindowsApps/OpenAI.CodexPrimaryRuntime.v26-1007-641-0_26.1007.641.0_x64__3k8sg7r9htsxt/dependencies/node/node_modules/playwright'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(b):return hashlib.sha256(b).hexdigest()
def save(p,x):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n',encoding='utf8',newline='\n')
def load(p):return json.loads(Path(p).read_text(encoding='utf8'))
def git(*a,repo=R):return subprocess.check_output(['git',*a],cwd=repo)
def gt(*a,repo=R):return git(*a,repo=repo).decode().strip()
def blobs(ref):
    rows=[dict(zip(['blob','path'],s.split(' ',1))) for s in gt('ls-tree','-r','--format=%(objectname) %(path)',ref).splitlines()]
    out=subprocess.check_output(['git','cat-file','--batch'],input=('\n'.join(x['blob'] for x in rows)+'\n').encode(),cwd=R);pos=0
    for x in rows:
        end=out.index(b'\n',pos);n=int(out[pos:end].split()[2]);b=out[end+1:end+1+n];pos=end+n+2;x.update(bytes=n,SHA256=sha(b))
    assert pos==len(out);return rows
def state(repo=R):return {'HEAD':gt('rev-parse','HEAD',repo=repo),'branch':gt('branch','--show-current',repo=repo),'status':gt('--no-optional-locks','status','--porcelain',repo=repo)}
def protected():
    rows=[]
    for block in gt('worktree','list','--porcelain').split('\n\n'):
        d=dict(s.split(' ',1) if ' ' in s else (s,True) for s in block.splitlines());d['status']=state(Path(d['worktree']))['status'];rows.append(d)
    return rows
def initial():
    assert not W.exists() and not T.exists(),'Suggested isolated paths occupied'
    assert state()['HEAD']==F and not state()['status']
    assert gt('ls-remote','origin','refs/heads/v2-development').split()[0]==F
    assert gt('merge-base','HEAD','origin/v2-development')==F
    assert gt('ls-remote','https://github.com/LatinJosephus/LatinJosephus.github.io.git','refs/heads/main').split()[0]==V
    T.mkdir();(T/'logs').mkdir();manifest=blobs(F)
    start={'UTC':now(),'canonical':state(),'source_remote':F,'source_merge_base':F,'remote_default_HEAD':gt('ls-remote','--symref','origin','HEAD'),'preview_remote':V,'preview_original':state(Path('C:/workspace/LatinJosephus-Antiquities-Final-Preview-Publication-20261010')),'preview_publication':state(Path('C:/workspace/LatinJosephus-Antiquities-VII1-6-Preview-Publication-20261011')),'other_worktrees':protected(),'branch':BR,'worktree':str(W),'runtime':str(T),'source_manifest':manifest,'governing_prompt':{'path':'C:/Users/Pollard_R/Mon disque/Downloads from Chrome (11-08-2026 onward)/WORKBOT_Postrelease_Reader_Defects_2026-10-11.txt','SHA256':sha(Path('C:/Users/Pollard_R/Mon disque/Downloads from Chrome (11-08-2026 onward)/WORKBOT_Postrelease_Reader_Defects_2026-10-11.txt').read_bytes())}}
    save(T/'START.json',start)
    subprocess.run(['git','-c','core.autocrlf=false','worktree','add','-b',BR,str(W),F],cwd=R,check=True)
    Q.mkdir(parents=True);save(Q/'BASELINE.json',start)
    for x in manifest:
        if x['path'].startswith('assets/') or x['path'].startswith(('_includes/','_sass/','_layouts/')):assert sha((W/x['path']).read_bytes())==x['SHA256'],x['path']
    xml=[x for x in manifest if x['path'].startswith('assets/xml/') and x['path'].endswith('.xml')];assert len(xml)==143
    protected_inputs=[x for x in manifest if x['path'].startswith('assets/xml/') or (x['path'].startswith('assets/data/') and x['path'].endswith('.json'))]
    save(T/'PROTECTED_SOURCE_INPUTS.json',{'XML_count':143,'files':protected_inputs})
    for folder in ['qa','checkpoints','screenshots']:(T/folder).mkdir()
    for f in (I/'qa').iterdir():
        if f.is_file() and (f.suffix in ['.cjs','.rb'] or f.name in ['EXPECTED_SELECTIONS.json','AUTHORIZED_ADDITIONS.json','TRADITIONAL_EXPECTATIONS.json','EXPECTED_INTERVALS.json','local.yml']):shutil.copy2(f,T/'qa'/f.name)
    for f in (T/'qa').glob('*.cjs'):
        text=f.read_text(encoding='utf8').replace(I.as_posix(),T.as_posix()).replace('C:/workspace/LatinJosephus-antiquities-vii2-6-whiston-context-integration',W.as_posix());f.write_text(text,encoding='utf8',newline='\n')
    (T/'qa/BUILD_CONTEXT.json').write_text(json.dumps({'baseline_commit':F,'source':W.as_posix(),'baseline_site':(T/'baseline-site').as_posix(),'site':(T/'candidate-final-site').as_posix()}),encoding='utf8')
    shutil.copy2(P/'BASELINE_VII1.json',T/'BASELINE_VII1.json')
    save(T/'checkpoint-initial.json',{'UTC':now(),'canonical':F,'preview':V,'source_XML':143,'state':'Isolated checkout created from verified canonical; no production changes yet'})
    print('PASS verified F/AF baseline; isolated branch',BR,'143 XML protected; other worktrees excluded')
def build(mode):
    dst=T/(mode+'-site');src=W
    with (T/'logs'/('BUILD-'+mode+'.log')).open('wb') as f:
        r=subprocess.run(['C:/Ruby33-x64/bin/ruby.exe',str(T/'qa/build.rb'),str(src),str(dst),str(T/'qa/local.yml')],cwd=W,stdout=f,stderr=subprocess.STDOUT)
    assert r.returncode==0,(T/'logs'/('BUILD-'+mode+'.log')).read_text(errors='replace')[-1500:]
    for row in load(T/'PROTECTED_SOURCE_INPUTS.json')['files']:
        assert sha((W/row['path']).read_bytes())==row['SHA256']==sha((dst/row['path']).read_bytes()),row['path']
    assets=[{'path':p.relative_to(dst).as_posix(),'SHA256':sha(p.read_bytes()),'bytes':p.stat().st_size} for p in sorted((dst/'assets').rglob('*')) if p.is_file()]
    save(T/('BUILD_'+mode+'.json'),{'UTC':now(),'status':'PASS','source_HEAD':gt('rev-parse','HEAD',repo=W),'source_status':gt('status','--porcelain',repo=W),'destination':str(dst),'assets':assets,'builder_SHA256':sha((T/'qa/build.rb').read_bytes()),'protected_XML_and_registries_exact':True})
    print('PASS native Jekyll',mode,len(assets),'assets; XML/registries exact')
def source_links():
    targets=set();results=[];definitions={};xml_inputs=load(T/'PROTECTED_SOURCE_INPUTS.json')['files']
    for x in xml_inputs:
        if not x['path'].endswith('.xml'):continue
        tree=ET.fromstring((W/x['path']).read_bytes())
        for e in tree.iter():
            id=e.attrib.get('{http://www.w3.org/XML/1998/namespace}id') or e.attrib.get('id')
            if id:definitions.setdefault(id,[]).append({'file':x['path'],'tag':e.tag,'text':''.join(e.itertext())})
            if e.tag.endswith('}ref') and 'note_' in e.attrib.get('target',''):
                ids=e.attrib['target'].split();targets.update(ids);results.append({'file':x['path'],'target':e.attrib['target'],'label':''.join(e.itertext()),'defined_targets':[]})
    for x in results:x['defined_targets']=[{'id':t,'definitions':definitions.get(t,[])} for t in x['target'].split()]
    save(T/'APPARATUS_SOURCE_TRACE.json',{'UTC':now(),'XML_files_searched':143,'target_ids':sorted(targets),'references':results,'definitions':{t:definitions.get(t,[]) for t in sorted(targets)},'CETEI_mechanism':'default ref interpolates rw(target); missing CETEI base concatenates undefined with the complete unparsed multi-target string. The three source target UUIDs have no XML ID definitions in the current corpus.','scope':'Source-only diagnosis; no source edits or invented reference mapping'})
    print('Source target definitions',[(t,len(definitions.get(t,[]))) for t in sorted(targets)])
if __name__=='__main__':
    op=sys.argv[1]
    if op=='build':build(sys.argv[2])
    else:globals()[op]()
