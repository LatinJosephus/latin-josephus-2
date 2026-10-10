"""Refresh certificate references and evidence hashes after review-only wording edits."""
from finalize_certification import ROOT,BATCH,read,save,reference,manifest
def main():
    certificate=read(BATCH/'CERTIFICATION.json')
    assert certificate['status']=='BOTH_BOOKS_INDEPENDENTLY_LOCALLY_CERTIFIED'
    for b,roman in [(16,'XVI'),(17,'XVII')]:
        p=ROOT/f'review/Antiquities_Niese_Book{roman}_2026-10-09/CERTIFICATION.json'
        assert read(p)['status']=='INDEPENDENTLY_LOCALLY_CERTIFIED'
        certificate['books'][str(b)]=reference(p)
    save(BATCH/'CERTIFICATION.json',certificate)
    for p in [BATCH/'BATCH_HANDOFF.txt',*[(ROOT/f'review/Antiquities_Niese_Book{r}_2026-10-09/BOOK_HANDOFF.txt') for r in ['XVI','XVII']]]:
        text=p.read_text(encoding='utf8')
        for old,new in [('All132','All 132'),('all759','all 759'),('all311','all 311'),('and35','and 35'),('all5231','all 5,231'),('All20','All 20'),('all20','all 20'),('total5990','total 5,990'),('frozen5231','frozen 5,231'),('+759','+ 759'),('section1','section 1'),('XVII31','XVII.31')]:text=text.replace(old,new)
        p.write_text(text,encoding='utf8',newline='\n')
    manifest([x['path'] for x in certificate['production_paths']])
    print('PASS refreshed independent certificate references and complete review manifest; production unchanged.')
if __name__=='__main__':main()
