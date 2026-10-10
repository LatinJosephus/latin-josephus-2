from recover import *
import re
def main():
    candidate=json.loads((PACK/'CANDIDATE_BUILD.json').read_text());baseline=json.loads((PACK/'BASELINE_BUILD.json').read_text())
    assert candidate['exit_code']==baseline['exit_code']==0
    assert baseline['source_commit']==BASE
    for n in PRODUCTION_PATHS:
        assert (ROOT/n).read_bytes()==(Path(candidate['source'])/n).read_bytes()==(Path(candidate['site'])/n).read_bytes()==git('show',PRODUCTION+':'+n)
    build={'baseline_commit':BASE,'commit':candidate['source_commit'],'production_commit':PRODUCTION,'baseline_site':baseline['site'],'site':candidate['site'],'root':str(ROOT),'receipt':str(PACK/'CANDIDATE_BUILD.json')}
    save('BUILD_CONTEXT.json',build)
    site=Path(candidate['site']);old=Path(r'C:\workspace\Antiquities-Niese-Proem-runtime-20261010\sealed-site')
    paths=[p.relative_to(site).as_posix() for p in (site/'assets').rglob('*') if p.is_file()]
    paths+=['index.html',*[w+'/index.html' for w in ['antiquities','bellum-judaicum','contra-apionem','deh']]]
    manifest=[{'path':n,'bytes':(site/n).stat().st_size,'sha256':sha((site/n).read_bytes())} for n in sorted(paths)]
    save('BUILD_ASSET_MANIFEST.json',manifest)
    raw_differences=[n for n in paths if not (old/n).exists() or (site/n).read_bytes()!=(old/n).read_bytes()]
    def normalize(n,b):
        if n!='deh/index.html':return b
        # Only the two existing Jekyll build-time cache keys, never content or script bytes.
        return re.sub(rb'(/assets/(?:css/deh-parallels\.css|js/dehParallels\.js)\?v=)[0-9]+',rb'\1BUILD_TIME',b)
    differences=[n for n in paths if not (old/n).exists() or normalize(n,(site/n).read_bytes())!=normalize(n,(old/n).read_bytes())]
    historical=ROOT/'review/Antiquities_Niese_Proem_2026-10-10/READER_FINAL_PRIOR_RESULTS.json'
    report=json.loads(historical.read_text())
    assert report['result']=='PASS' and report['build']['commit']==PRODUCTION
    shutil.copyfile(historical,PACK/'PRESERVED_CONTAINING_CROSSWORK_PASS.json')
    save('CONTAINING_CROSSWORK_EQUIVALENCE.json',dict(status='PASS' if not differences else 'RERUN_REQUIRED',fresh_build=build,preserved_PASS=record(historical),historical_build=report['build'],compared_files=len(paths),manifest=record(PACK/'BUILD_ASSET_MANIFEST.json'),raw_differences=raw_differences,normalized_build_time_cache_keys=2 if raw_differences==['deh/index.html'] else None,differences=differences,scope='Every built asset and all five reader entry pages; same production bytes and builder. Only two DEH build-time cache keys normalized; generated feed timestamp is outside reader inputs. Fresh focused DEH and Lodge controls also required.',books=len(report['books']),cross_works=len(report['cross_works']),focused=len(report['focused']),Lodge_Whiston_switching=report['Lodge_Whiston_switching'],identity_replay_certificate=False))
    print(json.dumps({'source_build':candidate['source_commit'],'production_revision':PRODUCTION,'reader_files_compared':len(paths),'prior_containing_equivalence':'PASS' if not differences else differences}))
if __name__=='__main__':main()
