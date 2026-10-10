from prepare import *
import tarfile
def main():
    commit=git('rev-parse','HEAD').decode().strip();destination=RUNTIME/'candidate-source'
    assert not destination.exists(),'Use a unique build source; do not overwrite runtime evidence'
    destination.mkdir();archive=RUNTIME/'candidate-source.tar'
    subprocess.run(['git','archive','--format=tar','-o',str(archive),commit],cwd=ROOT,check=True)
    with tarfile.open(archive) as tar:
        for member in tar:
            assert not Path(member.name).is_absolute() and '..' not in Path(member.name).parts
            target=destination/member.name
            if member.isdir():target.mkdir(parents=True,exist_ok=True)
            else:
                assert member.isfile();target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(tar.extractfile(member).read())
    script=ROOT/'review/Whiston_Niese_Combined_Integration_2026-10-09/build_disposable.rb'
    result=subprocess.run([r'C:\Ruby33-x64\bin\ruby.exe',str(script),str(destination),str(RUNTIME/'final-site')],cwd=destination,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    log=RUNTIME/'candidate-build.log';log.write_bytes(result.stdout)
    save(PACK/'CANDIDATE_BUILD.json',dict(source_commit=commit,source=str(destination),site=str(RUNTIME/'final-site'),builder=info(script),exit_code=result.returncode,log=info(log),runtime_only=True,no_publication=True,editorial_certification=False))
    print(result.stdout.decode('utf-8',errors='replace')[-1500:]);assert result.returncode==0
if __name__=='__main__':main()
