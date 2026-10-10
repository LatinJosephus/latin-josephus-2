from prepare import *
import re
def main():
    candidate=json.loads((PACK/'CANDIDATE_BUILD.json').read_text());baseline=json.loads((PACK/'BASELINE_BUILD.json').read_text())
    assert candidate['exit_code']==baseline['exit_code']==0 and baseline['source_commit']==BASE
    source='07057a284e3eb4999bd875cd05eb970e30886452'
    allowed=json.loads((PACK/'MERGE_RECEIPT.json').read_text())['production_sha256']
    for n,h in allowed.items():assert sha((ROOT/n).read_bytes())==sha((Path(candidate['source'])/n).read_bytes())==sha((Path(candidate['site'])/n).read_bytes())==sha(git('show',source+':'+n))==h
    build=dict(baseline_commit=BASE,commit=candidate['source_commit'],merge_commit='a0245745c3fd3b3a04bfb5ed8acc192cd7f01b87',certified_recovery_tip=source,baseline_site=baseline['site'],site=candidate['site'],root=str(ROOT),receipt=str(PACK/'CANDIDATE_BUILD.json'))
    save(PACK/'BUILD_CONTEXT.json',build)
    site=Path(candidate['site']);old=Path(r'C:\workspace\Antiquities-Niese-Proem-Recovery-runtime-20261010\candidate-site')
    paths=sorted([p.relative_to(site).as_posix() for p in (site/'assets').rglob('*') if p.is_file()]+['index.html',*[w+'/index.html' for w in ['antiquities','bellum-judaicum','contra-apionem','deh']]])
    manifest=[dict(path=n,bytes=(site/n).stat().st_size,sha256=sha((site/n).read_bytes())) for n in paths]
    save(PACK/'BUILD_ASSET_MANIFEST.json',manifest)
    def normalize(n,b):return re.sub(rb'(/assets/(?:css/deh-parallels\.css|js/dehParallels\.js)\?v=)[0-9]+',rb'\1BUILD_TIME',b) if n=='deh/index.html' else b
    raw=[n for n in paths if not (old/n).exists() or (site/n).read_bytes()!=(old/n).read_bytes()]
    diff=[n for n in paths if not (old/n).exists() or normalize(n,(site/n).read_bytes())!=normalize(n,(old/n).read_bytes())]
    assert len(paths)==256 and not diff and set(raw)<={'deh/index.html'},(len(paths),diff,raw)
    historical=ROOT/'review/Antiquities_Niese_Proem_Recovery_2026-10-10/CONTAINING_CROSSWORK_EQUIVALENCE.json'
    assert json.loads(historical.read_text())['status']=='PASS'
    save(PACK/'READER_INPUT_EQUIVALENCE.json',dict(status='PASS',fresh_build=build,certified_recovery_build='a3ca656151f1170a099f4f143f70feb1118dbfd1',reader_inputs=len(paths),paths=paths,manifest=info(PACK/'BUILD_ASSET_MANIFEST.json'),raw_differences=raw,normalized_DEH_cache_keys=2,differences=diff,historical_equivalence=info(historical),scope='All 251 built assets plus root and four reader entry pages; only two DEH build-time cache timestamps normalized; independent fresh browser suite still required'))
    print('PASS fresh builds bound to actual merge lineage; all 256 reader inputs equal certified recovery')
if __name__=='__main__':main()
