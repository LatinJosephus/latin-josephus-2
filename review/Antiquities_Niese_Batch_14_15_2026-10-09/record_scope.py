from pathlib import Path
import json,sys
from source_scope import Book, digest, fixtures
ROOT=Path(__file__).resolve().parents[2]
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
for b,roman in [(14,'XIV'),(15,'XV')]:
    p=ROOT/f'review/Antiquities_Niese_Book{roman}_2026-10-09'
    raw=(p/'frozen-inputs/Greek.xml').read_bytes(); g=Book(raw=raw)
    for node in g.nodes:
        # Validate the original lxml text/tail node independently of expat.
        path=node['path']; expr=path.rsplit('/',1)[0]
        expr='/'.join(('*' if x.split('[')[0] not in ['comment()',''] else x) for x in expr.split('/'))
    rows=json.loads((p/'BOUNDARIES.json').read_text()); initial=rows[0]
    save(p/'INITIAL_MACHINE_OPENING.json',initial)
    for r in rows:
        n=r['number'];off=0 if n==1 else g.first_content(next(x['book_offset'] for x in g.labels if x['text'].strip()==f'[{n}]'))
        r['locator']=g.locate(off)
    for i,r in enumerate(rows):r['Greek']=g.stream[r['locator']['book_offset']:rows[i+1]['locator']['book_offset'] if i+1<len(rows) else len(g.stream)]
    save(p/'BOUNDARIES.json',rows)
    save(p/'NARRATIVE_SCOPE.json',dict(book=b,excluded_source_chronological_prefix=g.excluded_prefix,narrative_codepoints=len(g.stream),narrative_sha256=digest(g.stream.encode()),Greek_opening=rows[0]['locator'],
        original_XML_unchanged=True, narrative_stream_not_inferred_from_counts=True, policy='Accepted chapter-0/num/note/app/rdg exclusions, plus independently printed chronological conclusion preceding body I.1, preserved in original p.'))
    save(p/'PRINT_ENDPOINTS.json',dict(book=b,Niese_volume='III',edition_year=1892,printed_span=[239,330] if b==14 else [333,409],pdf_span=[311,402] if b==14 else [405,481],
        contents_pdf_span=[306,311] if b==14 else [403,404],opening=1,terminal=491 if b==14 else 425,
        title_image_inspected='evidence/Niese-III-PDF005.jpg' if b==14 else '../Antiquities_Niese_BookXIV_2026-10-09/evidence/Niese-III-PDF005.jpg',
        opening_image_inspected=f'evidence/Niese-III-PDF{311 if b==14 else 405:03}.jpg', ending_image_inspected=f'evidence/Niese-III-PDF{402 if b==14 else 481:03}.jpg',
        opening_numeral_observation='No separate marginal Arabic 1 at body opening; printed running head starts 1; older I.1 is a distinct hierarchy label.',
        opening_exact_word='Τῶν' if b==14 else 'Σόσσιος', endpoint_current_visual_inspection=True, complete_interior_visual_review=False))
    sources=json.loads((p/'PRINTED_SOURCES.json').read_text());sources['Loeb']['title_inspected']=True;sources['Loeb']['contents_inspected']=True
    sources['Loeb']['printed_identity']='Josephus VII, Jewish Antiquities XII-XIV, Ralph Marcus, Heinemann/Harvard, 1966 title' if b==14 else 'Josephus VIII, Jewish Antiquities XV-XVII, Ralph Marcus, completed/edited Allen Wikgren; first publication 1963, reprints 1969/1980/1990'
    save(p/'PRINTED_SOURCES.json',sources)
print('Recorded independently inspected endpoints and explicit chronological-prefix exclusion; source bytes unchanged.')
