"""Build only in this assignment's disposable directory; no preview export."""
from reconnaissance import *
import tarfile
def main():
    destination=RUNTIME/'baseline';destination.mkdir(exist_ok=False)
    archive=RUNTIME/'baseline-source.tar'
    subprocess.run(['git','archive','--format=tar','-o',str(archive),BASE],cwd=ROOT,check=True)
    with tarfile.open(archive) as tar:
        tar.extractall(destination,filter='data')
    script=ROOT/'review/Whiston_Niese_Combined_Integration_2026-10-09/build_disposable.rb'
    result=subprocess.run([r'C:\Ruby33-x64\bin\ruby.exe',str(script),str(destination),str(RUNTIME/'baseline-site')],cwd=destination,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    log=RUNTIME/'baseline-build.log';log.write_bytes(result.stdout)
    save(PACK/'BASELINE_BUILD.json',dict(source_commit=BASE,source=str(destination),site=str(RUNTIME/'baseline-site'),builder=info(script),exit_code=result.returncode,log=info(log),runtime_only=True,no_publication=True))
    print(result.stdout.decode('utf8',errors='replace')[-1800:]);assert result.returncode==0
if __name__=='__main__':main()
