from pathlib import Path
import postrelease_reader as u
import subprocess,json,shutil,sys,os,gzip,zipfile

R=u.R;S=u.W;ST=u.T;SQ=u.Q
SOURCE='e4005026370a2ff6ca0cf135ea5718f348db814c'
REPORTED=u.F;PREVIEW=u.V
W=Path('C:/workspace/LatinJosephus-postrelease-reader-repairs-integration-20261011')
T=Path('C:/workspace/Postrelease-Reader-Repairs-Integration-runtime-20261011')
Q=W/'review/Postrelease_Reader_Repairs_Integration_2026-10-11'
BR='integration/postrelease-reader-repairs-20261011'
PROMPT=Path('C:/Users/Pollard_R/Mon disque/Downloads from Chrome (11-08-2026 onward)/01_WORKBOT_Integrate_Postrelease_Reader_Repairs_ABDE_2026-10-11.txt')
PRODUCTION=['_includes/annotations-bar.html','_includes/header.html','_sass/_antiquities.scss','_sass/_branding.scss','_sass/_reader-ui.scss','assets/js/dark_mode.js','assets/js/renderTei.js','assets/js/theme.js']

def saved():
    global W,T,Q,BR
    p=Path('reader_integration_context.json');d=u.load(p)
    W=Path(d['worktree']);T=Path(d['runtime']);Q=W/'review/Postrelease_Reader_Repairs_Integration_2026-10-11';BR=d['branch'];return d
def run(*args,repo=R):subprocess.run(['git',*args],cwd=repo,check=True)
def fetch():run('fetch','origin','v2-development')
def ancestor(old,new,repo=R):return subprocess.run(['git','merge-base','--is-ancestor',old,new],cwd=repo,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0

def initial():
    global W,T,Q,BR
    source=u.state(S);assert source['HEAD']==SOURCE and not source['status'];assert u.gt('rev-parse','fix/postrelease-reader-a11y-ids-links-startup-20261011')==SOURCE
    canonical=u.state();remote=u.gt('rev-parse','origin/v2-development');direct=u.gt('ls-remote','origin','refs/heads/v2-development').split()[0]
    assert canonical['branch']=='v2-development' and not canonical['status'];assert remote==direct
    assert ancestor(REPORTED,canonical['HEAD']) and ancestor(REPORTED,remote),'Unexpected canonical divergence from reported historical source'
    if ancestor(canonical['HEAD'],remote):base=remote
    elif ancestor(remote,canonical['HEAD']):base=canonical['HEAD']
    else:raise RuntimeError('Local and remote canonical histories diverged; reconcile in isolation before promotion')
    pv=u.gt('ls-remote','https://github.com/LatinJosephus/LatinJosephus.github.io.git','refs/heads/main').split()[0]
    certificate=u.load(SQ/'CERTIFICATE.json');manifest=u.load(SQ/'CHANGED_FILES.json');handoff=u.load(ST/'HANDOFF_RECEIPT.json');unresolved=u.load(SQ/'UNRESOLVED_REFERENCES.json')
    assert handoff['final_commit']==SOURCE and certificate['implementation_tip']=='951555f41c4fda1e21f7615b4a125f7036b3b55f'
    assert all(certificate['packages'][p]['status']=='PASS' for p in ['A','B','D','E']) and 'HOLD' in certificate['packages']['C']['status']
    assert sorted(r['path'] for r in manifest['production'])==PRODUCTION
    assert all(u.sha((S/r['path']).read_bytes())==r['final_SHA256'] for r in manifest['production'])
    assert all(u.sha((S/r['path']).read_bytes())==r['SHA256'] for r in manifest['evidence'])
    assert u.sha((S/'assets/js/renderTei.js').read_bytes())=='e75244c444771c733ca8ddb0d130b8f32463f59fd9460c26a5048b3669727322'
    for c in ['b48e8778b6ece616775d59a8e8949199c3ee84ef','0f006764c36b36bc0cf856f6c3b11f2e4a03660c',certificate['implementation_tip']]:assert ancestor(c,SOURCE)
    n=1
    while W.exists() or T.exists() or subprocess.run(['git','show-ref','--verify','--quiet','refs/heads/'+BR],cwd=R).returncode==0:
        n+=1;W=Path('C:/workspace/LatinJosephus-postrelease-reader-repairs-integration-20261011-'+str(n));T=Path('C:/workspace/Postrelease-Reader-Repairs-Integration-runtime-20261011-'+str(n));BR='integration/postrelease-reader-repairs-20261011-'+str(n)
    Q=W/'review/Postrelease_Reader_Repairs_Integration_2026-10-11'
    T.mkdir();(T/'logs').mkdir();(T/'checkpoints').mkdir();(T/'screenshots').mkdir();(T/'qa').mkdir()
    context={'worktree':str(W),'runtime':str(T),'branch':BR,'baseline':base,'source':SOURCE,'preview':pv};u.save('reader_integration_context.json',context)
    instructions=[]
    for p in [Path('C:/AGENTS.md'),Path('C:/workspace/AGENTS.md'),Path('C:/Users/AGENTS.md'),Path('C:/Users/Pollard_R/AGENTS.md'),Path('C:/Users/Pollard_R/Git/AGENTS.md'),R/'AGENTS.md']:
        if p.exists():instructions.append({'path':str(p),'text':p.read_text(encoding='utf8'),'SHA256':u.sha(p.read_bytes())})
    frozen=u.blobs(base)
    start={'UTC':u.now(),**context,'canonical':canonical,'fetched_remote':remote,'direct_remote':direct,'merge_base':u.gt('merge-base',canonical['HEAD'],remote),'drift_from_reported':u.gt('log','--format=%H %s',REPORTED+'..'+base),'baseline_manifest':frozen,'source_state':source,'source_certificate':certificate,'source_handoff':handoff,'source_production_manifest':manifest['production'],'source_complete_history':u.gt('log','--reverse','--format=%H %P %s',REPORTED+'..'+SOURCE),'unresolved_reference_packet_SHA256':u.sha((SQ/'UNRESOLVED_REFERENCES.json').read_bytes()),'governing_prompt':{'path':str(PROMPT),'SHA256':u.sha(PROMPT.read_bytes())},'instructions':instructions,'other_worktrees':u.protected(),'preview_original':u.state(Path('C:/workspace/LatinJosephus-Antiquities-Final-Preview-Publication-20261010')),'preview_publication':u.state(Path('C:/workspace/LatinJosephus-Antiquities-VII1-6-Preview-Publication-20261011'))}
    u.save(T/'START.json',start)
    run('-c','core.autocrlf=false','worktree','add','-b',BR,str(W),base)
    Q.mkdir(parents=True);u.save(Q/'BASELINE.json',start)
    protected=[r for r in frozen if r['path'].startswith('assets/xml/') or (r['path'].startswith('assets/data/') and r['path'].endswith('.json'))]
    assert sum(r['path'].endswith('.xml') for r in protected)==143 and len(protected)==159
    for r in protected:assert u.sha((W/r['path']).read_bytes())==r['SHA256']
    u.save(T/'PROTECTED_INPUTS.json',{'XML_count':143,'protected_count':159,'files':protected})
    # Independent native build input; no old generated build copied.
    for f in (SQ/'qa').iterdir():
        if f.is_file() and f.suffix in ['.cjs','.rb','.yml','.json']:
            if f.name=='READER_FINAL_PRIOR_RESULTS.json':continue
            text=f.read_text(encoding='utf8').replace(ST.as_posix(),T.as_posix()).replace(S.as_posix(),W.as_posix());(T/'qa'/f.name).write_text(text,encoding='utf8',newline='\n')
    for f in SQ.glob('postrelease_*.cjs'):
        text=f.read_text(encoding='utf8').replace(ST.as_posix(),T.as_posix()).replace(S.as_posix(),W.as_posix());(T/'qa'/f.name).write_text(text,encoding='utf8',newline='\n')
    u.save(T/'qa/BUILD_CONTEXT.json',{'baseline_commit':base,'source':W.as_posix(),'baseline_site':(T/'baseline-site').as_posix(),'site':(T/'candidate-final-site').as_posix()})
    shutil.copy2(ST/'BASELINE_VII1.json',T/'BASELINE_VII1.json')
    shutil.copy2(SQ/'UNRESOLVED_REFERENCES.json',Q/'UNRESOLVED_REFERENCES.json');shutil.copy2(SQ/'UNRESOLVED_REFERENCES.md',Q/'UNRESOLVED_REFERENCES.md')
    print(json.dumps({'status':'VERIFIED ISOLATED BASELINE','canonical_local':canonical['HEAD'],'canonical_fetched_remote':remote,'baseline':base,'preview':pv,'source':SOURCE,'source_history_preserved':True,'worktree':str(W),'branch':BR,'instructions':instructions}))

def build(mode):
    ctx=saved();dst=T/(mode+'-site')
    with (T/'logs'/('BUILD-'+mode+'.log')).open('wb') as f:r=subprocess.run(['C:/Ruby33-x64/bin/ruby.exe',str(T/'qa/build.rb'),str(W),str(dst),str(T/'qa/local.yml')],cwd=W,stdout=f,stderr=subprocess.STDOUT)
    assert r.returncode==0,(T/'logs'/('BUILD-'+mode+'.log')).read_text(errors='replace')[-1800:]
    for row in u.load(T/'PROTECTED_INPUTS.json')['files']:assert u.sha((W/row['path']).read_bytes())==row['SHA256']==u.sha((dst/row['path']).read_bytes())
    assets=[{'path':p.relative_to(dst).as_posix(),'SHA256':u.sha(p.read_bytes()),'bytes':p.stat().st_size} for p in sorted((dst/'assets').rglob('*')) if p.is_file()]
    u.save(T/('BUILD_'+mode+'.json'),{'UTC':u.now(),'status':'PASS','source_commit':u.gt('rev-parse','HEAD',repo=W),'source_status':u.state(W)['status'],'site':str(dst),'assets':assets,'builder_SHA256':u.sha((T/'qa/build.rb').read_bytes()),'protected_143_XML_159_inputs_exact':True})
    print('PASS fresh native build',mode,len(assets),'assets',flush=True)

def merge():
    ctx=saved();before=u.gt('rev-parse','HEAD',repo=W)
    # BASELINE and the hold-copy files are new integration evidence, not production.
    run('add','--','review/Postrelease_Reader_Repairs_Integration_2026-10-11',repo=W)
    run('commit','-m','Freeze verified canonical baseline and certified reader integration inputs',repo=W)
    pre_merge=u.gt('rev-parse','HEAD',repo=W)
    result=subprocess.run(['git','merge','--no-ff',SOURCE,'-m','Merge certified reader repairs A B D E; retain apparatus editorial hold'],cwd=W,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    conflicts=u.gt('diff','--name-only','--diff-filter=U',repo=W).splitlines()
    u.save(T/'MERGE.json',{'UTC':u.now(),'baseline':ctx['baseline'],'integration_start':before,'pre_merge':pre_merge,'source':SOURCE,'exit':result.returncode,'output':result.stdout.decode(errors='replace'),'conflicts':conflicts,'HEAD':u.gt('rev-parse','HEAD',repo=W),'merge_parents':u.gt('rev-list','--parents','-n','1','HEAD',repo=W).split()[1:]})
    print(result.stdout.decode(errors='replace')[-1400:])
    assert result.returncode==0 and not conflicts,'Specific unresolved merge conflict; preserve worktree for scoped reconciliation'
    assert ancestor(SOURCE,'HEAD',W)
    for row in u.load(T/'START.json')['source_production_manifest']:
        assert u.sha((W/row['path']).read_bytes())==row['final_SHA256'],'Investigate reconciliation production digest '+row['path']
    assert sorted(u.gt('diff','--name-only',ctx['baseline'],'HEAD','--',':(exclude)review/',repo=W).splitlines())==PRODUCTION
    for row in u.load(T/'PROTECTED_INPUTS.json')['files']:assert u.sha((W/row['path']).read_bytes())==row['SHA256']
    u.save(Q/'MERGE.json',u.load(T/'MERGE.json'))
    print('PASS history-preserving merge; no conflicts; exact eight production hashes; scholarly inputs frozen',flush=True)

if __name__=='__main__':
    op=sys.argv[1]
    if op=='initial':initial()
    elif op=='build':build(sys.argv[2])
    elif op=='merge':merge()
