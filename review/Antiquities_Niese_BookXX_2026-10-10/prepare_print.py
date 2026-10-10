from prepare import *
def main():
    baseline=json.loads((PACK/'BASELINE.json').read_text(encoding='utf-8'))
    cache=Path(r'C:\workspace\LatinJosephus-antiquities-niese-18-19\review\Antiquities_Niese_Batch_18_19_2026-10-09')
    prior=json.loads((cache/'BASELINE.json').read_text(encoding='utf-8'))
    assert [p['sha256'] for p in baseline['PDFs']]==[p['sha256'] for p in prior['PDFs']]
    provenance=[]
    for kind,span in [('NIESE',range(288,342)),('LOEB',range(400,564))]:
        source=cache/f'{kind}_PAGE_TEXT.json';rows=json.loads(source.read_text(encoding='utf-8'))
        selected=[p for p in rows if p['PDF_page'] in span]
        save(PACK/f'{kind}_PAGE_TEXT.json',selected)
        provenance.append(dict(kind=kind,cache=info(source),PDF_sha256=baseline['PDFs'][0 if kind=='NIESE' else 1]['sha256'],note='Previously extracted OCR is a locating aid only. New physical page images govern this review.'))
    save(PACK/'OCR_PROVENANCE.json',provenance)
    jobs=[(baseline['PDFs'][0]['path'],n,PACK/f'evidence/Niese-IV-PDF{n:03}.jpg') for n in [5,*range(288,342)]]
    jobs.extend([(baseline['PDFs'][1]['path'],7,PACK/'evidence/Loeb-IX-PDF007.jpg'),(baseline['PDFs'][1]['path'],407,PACK/'evidence/Loeb-IX-PDF407.jpg')])
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        manifest=list(ex.map(lambda job:render(*job),jobs))
    save(PACK/'PRINT_EVIDENCE_MANIFEST.json',dict(images=manifest,rendering_is_not_review=True,visual_review_complete=False))
    save(PACK/'CANONICAL_OBSERVATIONS.json',dict(entry_HEAD=BASE,freeze_source=BASE,later_observed_HEAD='08f46c0fdfa4639d49c0b13559fa590b6cce314b',direct_remote_tip='08f46c0fdfa4639d49c0b13559fa590b6cce314b',direct_remote_method='git ls-remote origin refs/heads/v2-development; successful read after initial sandbox DNS failure',later_delta='XI integration plus its shared fragment reader and CSS; observed only, excluded from frozen branch',decision='Keep immutable pre-XI entry source; integration coordinator reconciles later canonical changes.',published_reference='9527578f361d48adb3094110254e627292bca2c5'))
    print('Prepared',len(manifest),'physical images; review pending.')
if __name__=='__main__':main()
