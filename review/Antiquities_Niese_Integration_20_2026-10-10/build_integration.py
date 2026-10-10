from integration_common import *
def main():
    mode=sys.argv[1];commit=START if mode=='baseline' else git('rev-parse','HEAD').decode().strip()
    source=RUNTIME/(mode+'-source');site=RUNTIME/(mode+'-site')
    assert not site.exists()
    ar=archive(commit,source)
    builder=ROOT/'review/Whiston_Niese_Combined_Integration_2026-10-09/build_disposable.rb'
    result=subprocess.run([r'C:\Ruby33-x64\bin\ruby.exe',str(builder),str(source),str(site)],cwd=source,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    log=RUNTIME/(mode+'-build.log');log.write_bytes(result.stdout)
    record=dict(source_commit=commit,source=str(source),site=str(site),archive=ar,builder=info(builder),exit_code=result.returncode,log=info(log),runtime_only=True,no_publication=True)
    save(PACK/('BASELINE_BUILD.json' if mode=='baseline' else 'CANDIDATE_BUILD.json'),record)
    print(result.stdout.decode('utf-8',errors='replace')[-1600:]);assert result.returncode==0
    if mode!='baseline':save(PACK/'BUILD_CONTEXT.json',dict(baseline_commit=START,commit=commit,baseline_site=str(RUNTIME/'baseline-site'),site=str(site),root=str(ROOT)))
if __name__=='__main__':main()
