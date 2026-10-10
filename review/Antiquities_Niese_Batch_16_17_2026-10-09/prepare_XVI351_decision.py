"""Create a concrete pending editorial packet; no production implementation."""
from pathlib import Path
import sys,json,subprocess
ROOT=Path(__file__).resolve().parents[2];BATCH=Path(__file__).resolve().parent
P=ROOT/'review/Antiquities_Niese_BookXVI_2026-10-09'
sys.path.insert(0,str(ROOT/'review/Antiquities_Niese_BookVIII_2026-10-08'))
from mixed_mapper import Book,digest,NS
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
def main():
    l=Book(P/'frozen-inputs/Latin.xml');rows=json.loads((P/'BOUNDARIES.json').read_text())
    u351=next(u for u in l.units if u['id']=='latin-book16-num351');u356=next(u for u in l.units if u['id']=='latin-book16-num356')
    prefix_end=u356['text'].index('XVIIII Herodi');rest_end=u351['text'].index('mutatus ergo caesar')
    points={key:l.locate(value) for key,value in dict(earliest_surviving_351=u351['book_start'],end_351_first_physical_fragment=u351['book_start']+rest_end,
        displaced_351_prefix=u356['book_start'],end_displaced_prefix=u356['book_start']+prefix_end,
        start_355=u351['book_start']+u351['text'].index('Quas cum caesar legisset'),start_356_semantic=u356['book_start']+u356['text'].index('Herodi uero scripsit')).items()}
    source_anchor=u356['element'].xpath('.//*[@xml:id="trad-latin-LOEB-16-Chapter-11-0"]',namespaces=NS)
    assert len(source_anchor)==1
    packet=dict(book=16,sections=[350,351,352,354,355,356],status='PENDING_EDITOR_ADJUDICATION_NO_PRODUCTION_EDITS',source_sha256=digest(l.raw),
        finding='The opening clause of Niese XVI.351 occurs after the complete Latin counterpart of XVI.355, as the prefix of coarse paragraph num356. Its syntactic completion perissent occurs at the beginning of num351, before the remainder of 351. The cause of this present transcription order is undetermined.',
        Greek={str(n):rows[n-1]['Greek_candidate_interval'] for n in [350,351,352,354,355,356]},
        literal_Latin_first_physical_fragment=u351['text'][:rest_end],literal_Latin_later_physical_fragment=u356['text'][:prefix_end],
        complete_Latin_num351=u351['text'],complete_Latin_num356=u356['text'],locators=points,
        retained_traditional_anchor='trad-latin-LOEB-16-Chapter-11-0',retained_traditional_source_offset=95,
        alternatives=[dict(id='A',name='Contiguous intervals with displaced-correspondence notes',
            behavior='351 begins at perissent and ends before mutatus ergo caesar. The displaced 351 prefix remains physically in the 355 interval; reciprocal notices explain that ownership. 356 begins at the retained chapter anchor before XVIIII Herodi.',
            tradeoff='Maintains simple contiguous partition but selection 351 omits surviving correspondence and selection 355 includes unrelated 351 material.'),
          dict(id='B',name='Two explicitly registered 351 fragments in witness order',
            behavior='351 displays perissent through the point before mutatus ergo caesar, then the later hac oratione through the point before the retained XVIIII Herodi anchor. 355 ends before the paragraph num356; 356 starts at the existing chapter anchor. The Book and Alignment-unit views preserve exactly the current XML order.',
            tradeoff='Represents all surviving 351 correspondence exactly once in physical witness order; needs a generic Niese span/end representation and exhaustive regression of the 5231 protected selections.')],
        recommendation='B: both pieces have unambiguous correspondence with the two parts of Greek 351. Explicit discontiguous ranges avoid swallowing the prefix into 355, inventing absence, moving text, or duplicating text. A source-specific note must explain that the initial clause is transmitted later; no cause is inferred.',
        print_evidence=[dict(edition='Niese IV (1890)',printed_page=58,pdf_page=72,image='evidence/Niese-IV-PDF072.jpg',inspected=True,numbers=[350,351,352]),
            dict(edition='Niese IV (1890)',printed_page=59,pdf_page=73,image='evidence/Niese-IV-PDF073.jpg',inspected=True,numbers=[354,355,356])],
        Loeb_control=[dict(pdf_page=366,printed_page=350,image='evidence/Loeb-VIII-PDF366.jpg',inspected=True),dict(pdf_page=368,printed_page=352,image='evidence/Loeb-VIII-PDF368.jpg',inspected=True)],
        implementation_approved=False,certified=False)
    sources=json.loads((BATCH/'PRINTED_SOURCES.json').read_text())
    for p in [366,367,368,369]:
        target=P/f'evidence/Loeb-VIII-PDF{p:03}.jpg'
        subprocess.run(['pdftoppm','-f',str(p),'-l',str(p),'-singlefile','-jpeg','-r','150',sources['Loeb']['path'],str(target.with_suffix(''))],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    save(P/'DECISION_XVI_351_355_356.json',packet)
    text=f'''XVI.351, 355 and 356: editorial representation decision

Pinned source: 65b3256fe202a06e33a59aa2d1dcbd7107358271.
Status: PENDING; no disputed cut or production edit applied.

Niese IV (1890), printed p. 58 / PDF p. 72, places XVI.351 at
Ταῦτα μᾶλλον ἐκίνει τὸν Καίσαρα ... ὁπόσοι τεθνήκασιν Ἀράβων.

The current Latin has its initial clause physically after the counterpart of
XVI.355, at the beginning of latin-book16-num356:
{packet['literal_Latin_later_physical_fragment']}

The syntactic completion and remainder occur earlier at latin-book16-num351:
{packet['literal_Latin_first_physical_fragment']}

Niese XVI.352 follows at καὶ πέρας εἰς τοῦτο μετέστη Καῖσαρ, corresponding to
mutatus ergo caesar. XVI.356 begins at Ἡρώδῃ δὲ γράφει, corresponding to
Herodi uero scripsit. The certified traditional/Bamberg anchor before
XVIIII Herodi remains unchanged at source offset 95.

Recommendation B: register both 351 fragments in their current physical
witness order and explicitly end 355 before the displaced prefix. Explain the
displacement in the reader. Preserve every source byte, the chapter anchor,
Book order and Alignment-unit contents. Do not infer a cause.

Alternative A: use contiguous intervals and retain the 351 prefix as the tail
of 355, with reciprocal correspondence notes. This is simpler but means that
351 does not show all its surviving correspondence, and 355 includes it.

The JSON packet records complete adjoining Latin paragraphs, exact mixed-text
and raw-byte locators with hashes, full relevant Greek intervals, image
references and the representation/testing consequences.
'''
    (P/'DECISION_XVI_351_355_356.txt').write_text(text,encoding='utf8',newline='\n')
    history=json.loads((P/'DECISION_HISTORY.json').read_text());history.append(dict(kind='EDITORIAL_REPRESENTATION_QUESTION',sections=[351,355,356],packet='DECISION_XVI_351_355_356.json',recommendation='B',status='PENDING'))
    save(P/'DECISION_HISTORY.json',history)
    print('Concrete XVI.351/355/356 decision packet prepared; production untouched.')
if __name__=='__main__':main()
