from prepare import *
import tarfile,sys
def build(mode):
    commit=BASE if mode=='baseline' else git('rev-parse','HEAD').decode().strip()
    source=RUNTIME/(mode+'-source');site=RUNTIME/(mode+'-site');assert not site.exists()
    tarpath=RUNTIME/(mode+'.tar')
    if source.exists():
        previous=json.loads((PACK/(mode.upper()+'_BUILD.json')).read_text())
        assert previous['source_commit']==commit and previous['exit_code']==3221225506
        save(PACK/(mode.upper()+'_BUILD_SANDBOX_ATTEMPT.json'),previous)
    else:
        source.mkdir();subprocess.run(['git','archive','--format=tar','-o',str(tarpath),commit],cwd=ROOT,check=True)
        with tarfile.open(tarpath) as tf:
            for m in tf:
                assert not Path(m.name).is_absolute() and '..' not in Path(m.name).parts
                p=source/m.name
                if m.isdir():p.mkdir(parents=True,exist_ok=True)
                else:assert m.isfile();p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(tf.extractfile(m).read())
    builder=ROOT/'review/Whiston_Niese_Combined_Integration_2026-10-09/build_disposable.rb'
    r=subprocess.run([r'C:\Ruby33-x64\bin\ruby.exe',str(builder),str(source),str(site)],cwd=source,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    log=RUNTIME/(mode+'-build.log');log.write_bytes(r.stdout)
    save(PACK/(mode.upper()+'_BUILD.json'),dict(source_commit=commit,source=str(source),site=str(site),archive=info(tarpath),builder=info(builder),exit_code=r.returncode,log=info(log),runtime_only=True,published=False))
    print(r.stdout.decode(errors='replace')[-1400:]);assert r.returncode==0
if __name__=='__main__':build(sys.argv[1])
