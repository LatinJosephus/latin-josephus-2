from prepare import *
from mixed_mapper import Book
l=Book(PACK/'frozen-inputs/Latin.xml');rows=json.loads((PACK/'IDENTITIES.json').read_text(encoding='utf-8'))
a=l.stream.index('habe inquit fiducia');b=l.stream.index('inquit fiducia')
case=dict(case='XX.058-059',status='EDITORIAL_DECISION_REQUIRED',baseline=BASE,source_sha256=sha(l.raw),Greek=[rows[n-1] for n in [58,59,60]],Latin_context=l.stream[a-230:a+400],alternatives=[dict(label='A',start=l.locate(a),effect='Keep habe inquit fiducia together at59. Greek58 reassurance verb is represented at beginning of Latin59; disclose this phrase-order overlap.',recommended=True),dict(label='B',start=l.locate(b),effect='Start59 at inquit fiducia. Latin58 ends habe; follows Greek placement of θάρσησον but splits Latin habe fiducia phrase.',recommended=False)],recommendation='A: retain a readable complete Latin reassurance phrase while noting that its initial imperative corresponds to the last Greek word of58. No source text alteration; containing views unchanged.')
save(PACK/'CASE_059.json',case)
(PACK/'CASE_059.md').write_text('''# XX.58–59: the reassurance phrase

Pending editorial choice. Pinned base: `65b3256fe202a06e33a59aa2d1dcbd7107358271`.

Niese IV printed p.286, PDF image300: §58 ends `κατεπήδησεν ἀπὸ τοῦ ἵππου καί ‘θάρσησον,`; §59 begins `εἶπεν, ὦ βασιλεῦ, μηδέ σε συγχείτω`. Its numeral is a marginal line observation, not an executable word tag.

The unchanged Latin reads `Mox exequo resiliens habe inquit fiducia o rex nec te praesentia facta confundant.` The imperative is separated from `fiducia` by the reporting verb. This is not a wording correction request.

- A (recommended): begin Latin59 before `habe inquit fiducia`. Keep the reassurance together and disclose that `habe` corresponds to the close of Greek58.
- B: begin Latin59 before `inquit fiducia`, leaving `habe` at the end of Latin58. This mirrors the Greek interruption but splits the Latin phrase.

Only the assignment of `habe ` changes between adjacent selected intervals. Book, Alignment, chapter views and all source bytes remain intact. Exact text-node/code-point/UTF-8 coordinates, source hash, both Greek extents and candidate effects are in CASE_059.json. No disputed cut is implemented or certified before adjudication.
''',encoding='utf-8',newline='\n')
print('Prepared CASE_059 with exact alternatives.')
