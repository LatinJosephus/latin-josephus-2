"""Individually reviewed XII.71–90; repetitions are retained in their section."""
from pathlib import Path
import sys,json
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parent/'Antiquities_Niese_Batch_12_13_2026-10-09'))
from record_review import save,apply
choices=json.loads((P/'LATIN_REVIEW_CHOICES.json').read_text(encoding='utf8'))
data={
71:('Super mensam autem meandrum','Table-top meander and its gem colours correspond to 71. Both repeated medio eius/tamquam stellas phrases stay in this interval; 72 starts with the next meander clause.'),
72:('Post meandrum autem completum','Rope/double-form ornament, crystal/electrum and delight comprise 72.'),
73:('Capita uero peduum','Foot capitals and lily/leaves design precede the relative clause describing their base.'),
74:('quos lapis carbunculus','Relative syntax substitutes for the Greek independent base statement; carbuncle, dimensions and support remain 74.'),
75:('sculpserunt etiam tenuissimo','Detailed carving, ivy/vine and illusion of movement comprise 75.'),
76:('Uerum etiam figuram','Tripartite table, invisible joints and thickness precede final summation of the gift.'),
77:('Talis ergo uoti ut mensa','Summary of royal munificence and comparative beauty closes table description.'),
78:('Crateras etiam aurei','Retained label start: gold mixing bowls and their scale design begin the new vessel description.'),
79:('Dehinc super eos','Meander, rods and network to the lip start after initial scale description.'),
80:('Per medium quoque','Central stone shields and decorated lips comprise 80.'),
81:('et aureos quidem crateras','Gold capacity and clearer silver reflection follow lips and precede additional bowls.'),
82:('in super fecit rex pateras','Thirty bowls and ivy/vinework start after the silver reflection.'),
83:('haec autem ideo ita fiebant','Artisans skill and still greater royal enthusiasm begin the explanatory conclusion.'),
84:('Non enim tantum','Funding, constant presence and stimulated diligence complete the workmanship account.'),
85:('Cumque haec ad hierosolimam','Retained start: receipt/dedication, messengers honours and dismissal comprise 85.'),
86:('Ergo postquam alexandriam','Arrival, royal hearing, summoning and report of messengers match 86.'),
87:('Studens autem colloqui','The kings wish to meet the elders and exceptional dismissal of other petitioners precede explanation of usual audiences.'),
88:('ut qui propter huius modi','The explanatory customary five-day audience, ambassadors and present waiting comprise 88 despite Latin sentence continuation.'),
89:('dumque seniores cum donis','Elders and gifts, gold-letter law rolls and the kings enquiry begin here.'),
90:('Cum uero reuelarent','Unwrapping, admiration of parchment/joints and thanks end before collective acclamation of 91.')}
for n,(phrase,reason) in data.items():choices[str(n)]={'phrase':phrase,'assessment':reason}
choices['71']['limits']='The repeated phrase is retained without correction and creates no additional section identity.'
choices['88']['limits']='Latin post mensam differs from Greek monthly interval; do not emend the transcription.'
save(P/'LATIN_REVIEW_CHOICES.json',choices)
obs=json.loads((P/'PRINT_OBSERVATIONS.json').read_text(encoding='utf8'))
positions={157:{70:'right margin line 1 beside ἔλασμα',71:'right margin line 6 with preceding αὐτήν and ἐπὶ δὲ',72:'right margin line 11 beside μετὰ δὲ',73:'right margin line 14 with preceding βλέπουσιν and τῶν δὲ ποδῶν',74:'right margin line 17 beside ἡ δὲ βάσις',75:'right margin line 19 with preceding ἐρήρειστο and ἀνέγλυψαν',76:'right margin line 24 with preceding μιμημάτων παρεῖχεν and ἐκαινούργησαν'},158:{77:'left margin line 2 with preceding thickness clause and τὸ μὲν οὖν',78:'left margin line 10 at lower division 10, Τῶν δὲ κρατήρων',79:'left margin line 12 with preceding ἐνδεδεμένων and εἶτα',80:'left margin line 15 with preceding χείλους and τὰ δὲ μέσα',81:'left margin line 18 with preceding περιηγμέναις and τοὺς μὲν οὖν',82:'left margin line 22 with preceding ὁρᾶσθαι and προσκατεσκεύασε',83:'left margin line 25 with preceding ἐντετορευμένων and ταῦτα'},159:{84:'right margin line 2 beside οὐ γὰρ',85:'right margin line 8 at lower division 11, Ταῦτα',86:'right margin line 11 with preceding βασιλέα and παραγενομένων',87:'right margin line 16 with preceding ἐδήλωσαν and σπεύδων',88:'right margin line 19 with preceding ἔθος and οἱ μὲν γὰρ',89:'right margin line 22 with preceding περιέμενεν and ὡς δὲ',90:'right margin line 26 with preceding βιβλίων and ὡς δ᾽'}}
for p,items in positions.items():
 for n,pos in items.items():obs[str(n)]={'edition':'Niese III, 1892','printed_page':p-72,'PDF_page':p,'image':f'evidence/Niese/page-{p}.png','observed_numeral_position':pos,'word_boundary_status':'XML_WORD_START_CONFIRMED_FROM_PRINT','editorial_word_choice':'Keep XML start after inspecting printed clauses and adjoining section context.'}
save(P/'PRINT_OBSERVATIONS.json',obs)
apply(12)
