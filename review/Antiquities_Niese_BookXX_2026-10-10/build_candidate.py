from prepare import *
import tarfile
def main():
    commit=git('rev-parse','HEAD').decode().strip();destination=RUNTIME/f'candidate-source-{commit[:12]}'
    assert not destination.exists(),'Use a unique build source; do not overwrite runtime evidence'
    destination.mkdir();archive=RUNTIME/f'candidate-source-{commit[:12]}.tar';site=RUNTIME/f'candidate-site-{commit[:12]}'
    subprocess.run(['git','archive','--format=tar','-o',str(archive),commit],cwd=ROOT,check=True)
    with tarfile.open(archive) as tar:
        for member in tar:
            assert not Path(member.name).is_absolute() and '..' not in Path(member.name).parts
            target=destination/member.name
            if member.isdir():target.mkdir(parents=True,exist_ok=True)
            else:
                assert member.isfile();target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(tar.extractfile(member).read())
    script=ROOT/'review/Whiston_Niese_Combined_Integration_2026-10-09/build_disposable.rb'
    result=subprocess.run([r'C:\Ruby33-x64\bin\ruby.exe',str(script),str(destination),str(site)],cwd=destination,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    log=RUNTIME/f'candidate-build-{commit[:12]}.log';log.write_bytes(result.stdout)
    receipt=dict(source_commit=commit,source=str(destination),site=str(site),builder=info(script),exit_code=result.returncode,log=info(log),runtime_only=True,no_publication=True,editorial_certification=False)
    save(PACK/'CANDIDATE_BUILD.json',receipt);save(PACK/f'BUILD_{commit[:12]}.json',receipt)
    print(result.stdout.decode('utf-8',errors='replace')[-1500:]);assert result.returncode==0
if __name__=='__main__':main()
