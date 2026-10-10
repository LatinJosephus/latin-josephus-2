from prepare import *
import tarfile
def main():
    destination=RUNTIME/'baseline';destination.mkdir(exist_ok=True)
    assert not any(destination.iterdir()),'Never overwrite an existing build source'
    archive=RUNTIME/'baseline-source.tar';subprocess.run(['git','archive','--format=tar','-o',str(archive),BASE],cwd=ROOT,check=True)
    with tarfile.open(archive) as tar:
        for member in tar:
            parts=Path(member.name).parts
            assert not Path(member.name).is_absolute() and '..' not in parts
            target=destination/member.name
            if member.isdir():target.mkdir(parents=True,exist_ok=True)
            else:
                assert member.isfile(),'Archive links are not accepted'
                target.parent.mkdir(parents=True,exist_ok=True)
                target.write_bytes(tar.extractfile(member).read())
    script=ROOT/'review/Whiston_Niese_Combined_Integration_2026-10-09/build_disposable.rb'
    result=subprocess.run([r'C:\Ruby33-x64\bin\ruby.exe',str(script),str(destination),str(RUNTIME/'baseline-site')],cwd=destination,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    log=RUNTIME/'baseline-build.log';log.write_bytes(result.stdout)
    save(PACK/'BASELINE_BUILD.json',dict(source_commit=BASE,source=str(destination),site=str(RUNTIME/'baseline-site'),builder=info(script),exit_code=result.returncode,log=info(log),runtime_only=True,no_publication=True))
    print(result.stdout.decode('utf-8',errors='replace')[-1500:]);assert result.returncode==0
if __name__=='__main__':main()
