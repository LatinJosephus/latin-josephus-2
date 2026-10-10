"""Build the committed actual production source in a fresh local runtime."""
from reconnaissance import *
import tarfile

def main():
    commit=git('rev-parse','HEAD').decode().strip()
    destination=RUNTIME/'final-source';destination.mkdir(exist_ok=False)
    archive=RUNTIME/'final-source.tar'
    subprocess.run(['git','archive','--format=tar','-o',str(archive),commit],cwd=ROOT,check=True)
    with tarfile.open(archive) as tar:tar.extractall(destination,filter='data')
    script=ROOT/'review/Whiston_Niese_Combined_Integration_2026-10-09/build_disposable.rb'
    site=RUNTIME/'final-site'
    result=subprocess.run([r'C:\Ruby33-x64\bin\ruby.exe',str(script),str(destination),str(site)],cwd=destination,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    log=RUNTIME/'final-build.log';log.write_bytes(result.stdout)
    assert result.returncode==0,result.stdout.decode('utf8',errors='replace')
    production=git('diff','--name-only',BASE,commit,'--','assets','_includes').decode().splitlines()
    for rel in production:assert (ROOT/rel).read_bytes()==(destination/rel).read_bytes()==(site/rel).read_bytes(),rel
    save(PACK/'FINAL_BUILD.json',dict(source_commit=commit,source=str(destination),site=str(site),builder=info(script),exit_code=result.returncode,log=info(log),actual_production_files=[info(ROOT/rel) for rel in production],all_changed_production_build_bytes_equal=True,runtime_only=True,no_publication=True))
    print(result.stdout.decode('utf8',errors='replace')[-1800:])

if __name__=='__main__':main()
