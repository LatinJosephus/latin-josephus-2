from print_locations import *
def main():
    baseline=json.loads((PACK/'BASELINE.json').read_text(encoding='utf8'))
    niese=baseline['PDFs'][0]['path'];loeb=baseline['PDFs'][1]['path'];jobs=[]
    for b,span in [(18,range(152,224)),(19,range(224,291))]:
        for n in span:jobs.append((niese,n,packet(b)/f'evidence/Niese-IV-PDF{n:03}.jpg'))
    jobs.extend([(niese,5,PACK/'evidence/Niese-IV-title-PDF005.jpg'),(loeb,7,PACK/'evidence/Loeb-IX-title-PDF007.jpg')])
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        result=list(ex.map(lambda args:render(*args),jobs))
    save(PACK/'PRINT_EVIDENCE_MANIFEST.json',dict(pages=result,visual_inspection_complete=False,source_sha256=baseline['PDFs'][0]['sha256'],warning='Rendering is not examination; only explicit review records count as reviewed.'))
    print('Rendered',len(result),'pages. Visual review still pending.')
if __name__=='__main__':main()
