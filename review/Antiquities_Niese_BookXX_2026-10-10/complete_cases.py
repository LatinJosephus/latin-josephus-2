"""Finish whole-witness search and preserve unresolved editorial alternatives."""
from prepare import *
from mixed_mapper import Book
from collections import Counter
l=Book(PACK/'frozen-inputs/Latin.xml')
rows=json.loads((PACK/'IDENTITIES.json').read_text(encoding='utf-8'))
assert len(rows)==268 and all(r['print_review_status']=='VISUALLY_REVIEWED' for r in rows)
def hits(term):
    return [l.locate(m.start()) for m in re.finditer(term,l.stream,re.I)]
audit=dict(source=info(PACK/'frozen-inputs/Latin.xml'),scope='Entire narrative projection, all nonexcluded paragraphs and protected excluded/header/apparatus material inspected; no recovery from another book or witness.',paragraphs=[dict(id=u['id'],sha256=u['raw_hash'],extent=[u['book_start'],u['book_start']+len(u['text'])],reviewed=True,method='Complete Latin paragraph read during the individual Greek/Latin review windows, including neighboring paragraphs; numeric ID not treated as correspondence.') for u in l.units if not u['excluded_reason']],searches={term:hits(term) for term in ['anani','helena','iaz','izati','circum','eleaz','iuda','ionath','ionathas','asamon','assamon','ioachim','tryphon','trifon','hyrcan','diadem','testi','psalm','hymn']},conclusions={
'26-37':'26 survives in Commorabatur itaque iazatis; 27-36 no defensible independent interval after entire Latin review; source annotation is not translated narrative. 37 survives only as Darta banem particum destinauit. Names elsewhere belong to later narratives, not displaced conversion/circumcision account.',
'238':'No independent Jonathan appointment and seven-year Hasmonean priesthood account found in whole witness. Joakim and neme stand in preceding vacancy account; quo per insidias moriente starts the surviving Tryphon/Simon account239.',
'218':'Only concluding judgment Omnia contraria paternis survives; no displaced opening hymn instruction identified.',
'266':'Opening intention survives; living-witness clause not independently recovered elsewhere. Later history and authorial future works remain separate268.'},status='READ_ONLY_EVIDENCE; absence representation awaits editor for26-37 and238')
save(PACK/'WHOLE_LATIN_DISPLACEMENT_AUDIT.json',audit)
annotation=l.stream.index('[Niese sections 26')
end37=rows[37]['candidate']['Latin_start']
def case(name,ns,alternatives,recommendation):
    obj=dict(case=name,status='EDITORIAL_DECISION_REQUIRED',baseline=BASE,Latin_source_sha256=sha(l.raw),Greek_records=[rows[n-1] for n in ns],whole_witness_audit='WHOLE_LATIN_DISPLACEMENT_AUDIT.json',alternatives=alternatives,recommendation=recommendation)
    save(PACK/f'CASE_{name}.json',obj)
case('026_037',list(range(25,39)),[
 dict(label='A',recommended=True,representation='26 and37 partial,27-36 unavailable with explicit notice and Whiston context; preserve literal source annotation in containing views as source-only material.',Latin26_start=rows[25]['candidate']['Latin_locator'],Latin26_end=l.locate(annotation),Latin37_start=rows[36]['candidate']['Latin_locator'],Latin37_end=l.locate(end37)),
 dict(label='B',recommended=False,representation='Keep27-36 selectable but unresolved Latin correspondence with explicit editorial-hold notice; do not certify them unavailable or give independent intervals.')],
'A. All of the BookXX Latin has been individually read and searched. Preserve annotation verbatim; isolate it from the26 interval with a registered exclusive end. No claim about how absence arose.')
(PACK/'CASE_026_037.md').write_text('''# XX.26–37: surviving clauses and source-only annotation

Greek26 begins the residence and impending succession account; Greek27–36 contain the succession, conversion and circumcision narrative. Greek37 concludes with the destination of Artabanus. Niese IV printed280–282, PDF294–296; every individual Greek extent and image hash is in the case JSON.

Latin25 ends the Ammon account. Latin26 survives only as `Commorabatur itaque iazatis apud eum usque ad mortem patris.` The following source paragraph literally contains `[Niese sections 26–37 largely missing; cf. Blatt, p. 68]` followed by `Darta banem particum destinauit.` The latter corresponds to the end of Greek37, not to34 despite its paragraph ID. Latin38 begins `Cumque legibus crederet`.

Whole-book reading/search found no defensible displaced independent counterparts for27–36. The inherited bracketed annotation is source text and remains byte-for-byte in Book, Alignment and chapter views.

- A (recommended): expose partial Latin26 and37, explicit unavailability notices for27–36, and preserve the annotation as source-only material outside individual Niese intervals. Greek and Whiston remain selectable.
- B: retain those ten identities with an unresolved Latin correspondence notice; withhold unavailability adjudication and certification.

The exact frozen-source node, code-point and byte coordinates and adjacent extents are in CASE_026_037.json. This is a representation choice, with no conjectural text or manuscript-loss claim.
''',encoding='utf-8',newline='\n')
case('238',[237,238,239,240],[dict(label='A',recommended=True,representation='238 has no independent Latin interval; explicit notice.239 begins quo per insidias moriente, qualified for missing antecedent.'),dict(label='B',recommended=False,representation='Unresolved Latin correspondence; do not assign vacancy statement237 to Jonathan or certify absence.')],'A. Whole witness has no Jonathan seven-year priesthood account. Preserve neme and the relative construction; do not emend or manufacture the antecedent.')
(PACK/'CASE_238.md').write_text('''# XX.238: Jonathan and the missing antecedent

Niese IV printed316/PDF330. Greek238 recounts Hasmonean revolt and Jonathan's appointment for seven years. Greek239 begins his murder by Tryphon and Simon's succession.

The Latin reads `Ioachim qui et alcimus cum annis III pontificatum tenuisset est mortuus, cui successit neme, sed per annos VII, ciuitas fuit sine pontifice, quo per insidias moriente triphonis, successit frater eius simon.`

The Joakim/vacancy wording belongs to237. The whole Latin witness yielded no defensible independent Jonathan account;239 survives from `quo per insidias moriente`, with its antecedent missing locally.

- A (recommended): explicit Latin unavailability for238; qualify239 for its relative opening. Preserve all source spelling and order.
- B: leave238's Latin correspondence unresolved and withhold its certification. Do not silently reassign237 or invent a reading of `neme`.

Complete Greek sections, print-image hashes, exact offsets, neighbors and whole-witness search are retained in CASE_238.json and WHOLE_LATIN_DISPLACEMENT_AUDIT.json.
''',encoding='utf-8',newline='\n')
a=l.stream.index('Is namque primus');b=l.stream.index('cum et pontificatum tenuisset et regnum')
case('241',[239,240,241,242],[dict(label='A',recommended=True,start=l.locate(a),representation='241 begins Is namque primus; preceding kingship clause remains attached to Latin240. Qualify compressed/reordered correspondence.'),dict(label='B',recommended=False,start=l.locate(b),representation='241 begins cum et pontificatum tenuisset et regnum; includes kingship clause matching Greek241 but splits its inherited Latin syntactic attachment to240.')],'A. Is namque starts the distinct diadem/succession statement. Retain inherited compressed syntax; disclose incomplete/reordered correspondence, with no historical or grammatical repair.')
(PACK/'CASE_241.md').write_text('''# XX.240–241: kingship and the diadem

Niese IV printed316/PDF330. Greek240 covers Hyrcanus and his son Judas/Aristobulus;241 states Alexander's inheritance from Judas, the latter's one-year priesthood/kingship and first use of the diadem.

The unchanged Latin reads `huic per dolum quoque generi in conuiuio morienti filius successit hyrcanus, qui cum tenuisset pontificatus annis XXXI, in senectute moriens cum et pontificatum tenuisset et regnum. Is namque primus usus est anno diademate. Heredem fratrem dereliquit alexandrum.`

- A (recommended):241 starts at `Is namque primus`. Keep the preceding kingship clause with its inherited Latin sentence; qualify240–241 for compressed/reordered correspondence.
- B:241 starts at `cum et pontificatum tenuisset et regnum`. This places the kingship clause with Greek241 but breaks the Latin construction after `moriens`.

Both alternatives preserve source bytes and containing views. CASE_241.json retains complete Greek extents, exact text-node/code-point/byte coordinates, source hash and neighbor effects. No emendation or conjectural named subject is proposed.
''',encoding='utf-8',newline='\n')
print('All268 printed identities reviewed. Remaining statuses:',dict(Counter(r['Latin_review_status'] for r in rows)))
