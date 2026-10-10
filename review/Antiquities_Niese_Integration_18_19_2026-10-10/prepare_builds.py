"""Build fresh Git-archive sources in a separate integration runtime."""
from integration_common import *
import zipfile
tip=git('rev-parse','HEAD').decode().strip()
assert subprocess.run(['git','merge-base','--is-ancestor',SOURCE,tip],cwd=ROOT).returncode==0
for label,commit in [('baseline',START),('final',tip)]:
    source=R/(label+'-source');site=R/(label+'-site');archive=R/(label+'.zip')
    assert not source.exists() and not site.exists()
    subprocess.run(['git','archive','--format=zip','--output',str(archive),commit],cwd=ROOT,check=True)
    with zipfile.ZipFile(archive) as z:z.extractall(source)
save('BUILD_CONTEXT.json',dict(source_commit=tip,canonical_start=START,baseline_source=str(R/'baseline-source'),baseline_site=str(R/'baseline-site'),source=str(R/'final-source'),site=str(R/'final-site'),runtime=str(R),fresh_git_archives=True,original_source_runtime_untouched=True))
print('Prepared immutable archives',START,tip)
