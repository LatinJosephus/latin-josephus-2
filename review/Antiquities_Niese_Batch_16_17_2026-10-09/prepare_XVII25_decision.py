"""Prepare the XVII.24/25 word-cut alternatives; no disputed cut applied."""
from pathlib import Path
import sys,json,subprocess
ROOT=Path(__file__).resolve().parents[2];BATCH=Path(__file__).resolve().parent
P=ROOT/'review/Antiquities_Niese_BookXVII_2026-10-09'
sys.path.insert(0,str(ROOT/'review/Antiquities_Niese_BookVIII_2026-10-08'))
from mixed_mapper import Book,digest
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
def main():
    l=Book(P/'frozen-inputs/Latin.xml');rows=json.loads((P/'BOUNDARIES.json').read_text())
    u=next(u for u in l.units if u['id']=='latin-book17-num23')
    a=u['book_start']+u['text'].index('cui balatha nomen erat');b=u['book_start']+u['text'].index('Euocabat ergo eum')
    packet=dict(book=17,sections=[24,25,26],status='PENDING_EDITOR_ADJUDICATION_NO_DISPUTED_CUT_APPLIED',source_sha256=digest(l.raw),
        Greek={str(n):rows[n-1]['Greek_candidate_interval'] for n in [24,25,26]},complete_Latin_paragraph=u['text'],
        finding='Greek 25 begins with the name Οὐλαθά, referring to the Babylonian, then Herod summons him. Latin embeds balatha in the preceding clause about the grant of a place: Illum ei locum ad habitandum benigna largitate cui balatha nomen erat caedere compromisit. The following Euocabat ergo eum corresponds to Herod summoning him. The name survives, but its local syntax and attribution differ; the cause is undetermined.',
        alternatives=[dict(id='A',incipit='cui balatha nomen erat',locator=l.locate(a),
            consequence='Earliest literal name correspondence opens 25 inside the preceding grant clause. The tail caedere compromisit, corresponding to the preceding grant in Greek 24, is thereby included in 25.'),
          dict(id='B',incipit='Euocabat ergo eum',locator=l.locate(b),
            consequence='The whole preceding grant clause, including balatha, stays in 24. 25 begins at the summoning clause; qualify 25 as partial correspondence with the name surviving in the preceding interval, and add a reciprocal note at 24.')],
        recommended='B',recommendation_reason='Preserves the complete transmitted grant clause and starts 25 at its clear narrative counterpart. Explicit reciprocal qualification prevents the surviving name from being classified as absent and prevents the interval from being represented as exact complete correspondence.',
        printed_evidence=dict(edition='Niese IV (1890)',printed_page=74,pdf_page=88,image='evidence/Niese-IV-PDF088.jpg',inspected=True,
            observation='25 is printed beside the line opening χωρίον. Οὐλαθὰ ὄνομα αὐτῷ, μετεπέμπετο; the marginal line is not itself an exact word delimiter. The current Greek 25 begins at Οὐλαθά and is supported by the complete name/summoning clause.'),
        neighbours=dict(previous_start=l.locate(u['book_start']+u['text'].index('Et cognoscens uirum')),next_start=l.locate(next(v for v in l.units if v['id']=='latin-book17-num26')['book_start'])),
        implementation_approved=False,certified=False)
    save(P/'DECISION_XVII_024_025.json',packet)
    (P/'DECISION_XVII_024_025.txt').write_text('''XVII.24/25: word-cut decision

Pinned source: 65b3256fe202a06e33a59aa2d1dcbd7107358271.
Status: PENDING; neither disputed cut is applied.

Greek 25 opens with Οὐλαθὰ ὄνομα αὐτῷ, μετεπέμπετο: the Babylonian's
name, followed by Herod summoning him. Niese IV (1890), printed p. 74 /
PDF p. 88, has been visually inspected.

Latin: Illum ei locum ad habitandum benigna largitate cui balatha nomen erat
caedere compromisit. Euocabat ergo eum cum tota multitudine omnium qui eum
fuerant consecuti, spondens daturum se terram in regionem quaedicitur bathanea.

A: begin 25 before cui balatha nomen erat. This retains the earliest literal
name correspondence in 25 but splits the preceding grant clause and includes
caedere compromisit from Greek 24 in the following Latin interval.

B (recommended): begin 25 before Euocabat ergo eum. Keep the complete grant
clause, including balatha, in 24. Mark 25 as partial correspondence because
the name survives in the preceding interval; add a reciprocal note at 24.
Do not classify the name as absent or infer a cause for the local difference.

The JSON packet contains complete Greek intervals 24-26, the whole Latin
paragraph, both exact text/tail and byte locators, source hash and adjoining
extents. All wording, punctuation, whitespace, IDs and source markers remain.
''',encoding='utf8',newline='\n')
    history=json.loads((P/'DECISION_HISTORY.json').read_text());history.append(dict(kind='EDITORIAL_WORD_CUT_QUESTION',sections=[24,25],packet='DECISION_XVII_024_025.json',recommendation='B',status='PENDING'))
    save(P/'DECISION_HISTORY.json',history)
    print('Concrete XVII.24/25 cut packet prepared; no disputed cut applied.')
if __name__=='__main__':main()
