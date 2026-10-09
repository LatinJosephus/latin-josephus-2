"""Manual review of XII.51–70 and relevant printed starts."""
from pathlib import Path
import sys,json
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parent/'Antiquities_Niese_Batch_12_13_2026-10-09'))
from record_review import save,apply
choices=json.loads((P/'LATIN_REVIEW_CHOICES.json').read_text(encoding='utf8'))
data={
51:('Cum regis epistula','Retained opening: reception and reply, salutation and well-being of royal family precede acknowledgement of the letter.'),
52:('Cum uero epistolam suscepissemus','Receipt, joy, assembly and reading of the royal letter correspond to 52.'),
53:('demonstrauimus, scilicet pateras','Showings of vessels, money and messengers begin here after the assembly reading.'),
54:('Cognosce uero nos','Willingness to suffer and repay royal benefactions matches 54.'),
55:('Statim etiam prote','Sacrifices, prayers for royal peace and requested translation extend through pro tuis commodis accipere postulas, before the selected elders.'),
56:('elegi uiros seniores','The selected elders and request for safe return start here. The preceding translation-purpose clause belongs to 55 despite the Latin sentence continuing into 56.'),
57:('haec quidem princeps','Retained start: conclusion of letter and omission of elder names precede description of offerings.'),
58:('uasorum tamen magnificentiam','Purpose of describing gifts, expense and royal oversight begin after the elder-name notice.'),
59:('quorum de singulis malis','Promise to narrate individual splendour despite scope of history closes the preface.'),
60:('Prius autem de mensa','Retained start: table and royal intention to enlarge it precede the information obtained in 61.'),
61:('Cumque precepisset qualis','Existing size, proposed fivefold enlargement and functional concern comprise 61.'),
62:('qua propter arbitratus','Decision to retain size while improving variety and material beauty begins after functional rationale.'),
63:('Sagax ergo ad discernendam','The kings inventiveness and directions for novel and already described works close this passage.'),
64:('Promissa ergo complentes','Retained start: narrative undertaking, dimensions, gold and rope moulding precede explanation of triangular mouldings.'),
65:('Triangulus enim existentibus','Angles, reversible uniform appearance and inside/outside rim ornamentation comprise 65.'),
66:('Unde pro caritate partium','Two-sided sharpness, angles and precious stone pins match 66; lateral egg ornament starts 67.'),
67:('Partes autem quae per latera','Side egg ornament and dense rod forms surround the table.'),
68:('Ouorum autem dispositione','Fruit carving and colours in mounted stones start here after egg/rod description.'),
69:('Sub corona quoque','Egg/rod underside, reversible sameness and extension of the design to feet comprise 69.'),
70:('Nam ductile aurum','Gold sheet, width, supporting feet and fastening begin here before table-top meander ornament.')}
for n,(phrase,reason) in data.items():choices[str(n)]={'phrase':phrase,'assessment':reason}
choices['55']['limits']='Friends named in Greek sacrifices are not separately expressed in the Latin; substantial correspondence survives.'
choices['62']['limits']='Latin wording concerning scarcity of gold differs from Greek negated clause; retain its text and boundary.'
save(P/'LATIN_REVIEW_CHOICES.json',choices)
obs=json.loads((P/'PRINT_OBSERVATIONS.json').read_text(encoding='utf8'))
positions={153:{51:'right margin line 17 at lower division 6, Τῆς οὖν ἐπιστολῆς',52:'right margin line 21 beside τὴν δ᾽ ἐπιστολὴν',53:'right margin line 23 beside ἐπεδείξαμεν'},154:{54:'left margin line 3 with preceding messengers description and ἴσθι',55:'left margin line 6 after preceding κατατεθείσας, beside εὐθὺς',56:'left margin line 10 with preceding translation-purpose ending and ἐπελεξάμην',57:'left margin line 15 at lower division 7, Ταῦτα',58:'left margin line 18 with preceding ἐπιστολῇ and τὴν μέντοι',59:'left margin line 24 with preceding κατασκευασμάτων and ὧν',60:'left margin line 28 at lower division 8, Πρῶτον'},155:{61:'right margin line 2 with preceding size inquiry and μαθὼν',62:'right margin line 8 with preceding εὔχρηστα and καὶ διὰ',63:'right margin line 11 with preceding κατασκευάσαι and δεινὸς',64:'right margin line 17 at lower division 9, Ὑποστησάμενοι',65:'right margin line 22 with preceding moulding description and τριγώνων'},156:{66:'left margin line 3 with preceding θεωρίαν and διὸ',67:'left margin line 8 at τὰ δ᾽',68:'left margin line 11 with preceding εἴληντο and ὑπὸ',69:'left margin line 16 with preceding τράπεζαν and ὑπὸ'}}
for p,items in positions.items():
 for n,pos in items.items():obs[str(n)]={'edition':'Niese III, 1892','printed_page':p-72,'PDF_page':p,'image':f'evidence/Niese/page-{p}.png','observed_numeral_position':pos,'word_boundary_status':'XML_WORD_START_CONFIRMED_FROM_PRINT','editorial_word_choice':'Keep XML word start after inspecting printed context, separately from marginal position.'}
save(P/'PRINT_OBSERVATIONS.json',obs)
apply(12)
