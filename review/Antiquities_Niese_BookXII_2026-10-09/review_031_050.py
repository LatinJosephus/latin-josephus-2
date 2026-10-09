"""Individually read XII.31–50: manual cut observations, not inferred labels."""
from pathlib import Path
import sys,json
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parent/'Antiquities_Niese_Batch_12_13_2026-10-09'))
from record_review import save,apply
choices=json.loads((P/'LATIN_REVIEW_CHOICES.json').read_text(encoding='utf8'))
data={
31:('Dispositiones autem meas','Publication within three days, production of bodies and penalties continue the decree after the obedience provision.'),
32:('Cum haec sanctio lecta','Review of the decree and additions for earlier/later captives; advance payment arrangements precede their completion.'),
33:('quo facto intra septem','Completion within seven days and payments including infants close the release episode.'),
34:('Cum hęc secundum regiam','Retained label position. Return to Demetrius and the transcription decree precedes the documentary presentation.'),
35:('qua propter alligationes','The copies of report/letters and description of offerings and workmanship introduce the report itself.'),
36:('Maximo rege demetrius','Salutation and report about missing Hebrew legal books start here after the report introduction in 35.'),
37:('Contigit etiam minus','Prior inadequate care, need for accurate royal custody and divine legislation form 37.'),
38:('Quapropter inquid acatius','Hecataeus and reasons for avoidance by poets/historians begin after the description of divine legislation.'),
39:('Si uidetur ergo tibi','Proposal to write the high priest for elders and an accurate translation closes Demetrius report.'),
40:('Igitur tali suggestione','Retained start: royal command to write Eleazar and the gold/stone gifts begin the next episode.'),
41:('denuntians etiam custodibus','Instructions to gem keepers and additional money for sacrifices correspond to 41, within the Latin sentence.'),
42:('Narrabo igitur facturas','Authorial promise to describe the works after presenting the letter and explaining Eleazar succession.'),
43:('Defuncto principi sacerdotum','Onias death, Simon succession and explanation of Just match 43.'),
44:('Quo mortuo et filium','Simons death, child Onias, Eleazar succession and introduction to Ptolemy letter comprise 44.'),
45:('Rex ptolomeus eleazaro','Royal salutation and treatment of Jewish captives under the preceding king begin the letter.'),
46:('Cum uero ergo principatum','Ptolemy own accession, humane treatment and release of a hundred thousand captives match 46.'),
47:('Aetatibus autem uigentes','Military/court appointments and the offering to God remain between release and law translation.'),
48:('porro uel lens et istis','Desired favour to Jews worldwide and translated law in the royal library begin 48.'),
49:('Bene ergo facies','Request for qualified elders and promise of glory precede naming the messengers in 50.'),
50:('Transmisi uero qui deberent','Andreas/Aristeus, offerings, money and invitation to further requests close the king letter.')}
for n,(phrase,reason) in data.items():choices[str(n)]={'phrase':phrase,'assessment':reason}
choices['33']['limits']='The Greek sum is 460 talents; this Latin reads super sexaginta. No textual repair is authorized.'
choices['39']['limits']='The Greek specifies six elders per tribe; this transcription does not separately express the six here.'
save(P/'LATIN_REVIEW_CHOICES.json',choices)
obs=json.loads((P/'PRINT_OBSERVATIONS.json').read_text(encoding='utf8'))
positions={150:{31:'left margin line 2 with preceding κακουργεῖν and βούλομαι',32:'left margin line 7 with preceding κτῆσιν ἀνενεχθῆναι βούλομαι and τούτου',33:'left margin line 13 with preceding τραπεζίταις and γενομένου',34:'left margin line 20 at lower division 4, Ἐπειδὴ',35:'left margin line 24 at διὸ'},151:{36:'right margin line 5 with report-introduction ending and βασιλεῖ μεγάλῳ',37:'right margin line 12 at συμβέβηκε',38:'right margin line 15 after preceding θεοῦ, alongside διὸ',39:'right margin line 19 alongside ἐὰν',40:'right margin line 25 at lower division 5, Τοιαύτης'},152:{41:'left margin line 4 with preceding πολυτελῶν and προσέταξε',42:'left margin line 8 with preceding τάλαντα and διηγήσομαι',43:'left margin line 11 with preceding αἰτίας τοιαύτης and τελευτήσαντος',44:'left margin line 14 with preceding ὁμοφύλους and ἀποθανόντος',45:'left margin line 17 with preceding letter introduction and βασιλεὺς',46:'left margin line 23 with preceding φοβεροί and τὴν ἀρχὴν',47:'left margin line 26 with preceding λύτρα καταβαλών and τοὺς δὲ ἀκμάζοντας'},153:{48:'right margin line 4 after preceding ἀναθήσειν alongside βουλόμενος',49:'right margin line 7 with preceding βιβλιοθήκῃ and καλῶς',50:'right margin line 11 with preceding περιγενήσεσθαι and ἀπέσταλκα'}}
for p,items in positions.items():
 for n,pos in items.items():obs[str(n)]={'edition':'Niese III, 1892','printed_page':p-72,'PDF_page':p,'image':f'evidence/Niese/page-{p}.png','observed_numeral_position':pos,'word_boundary_status':'XML_WORD_START_CONFIRMED_FROM_PRINT','editorial_word_choice':'Retain XML start after printed clause comparison; marginal position alone is not a word tag.'}
save(P/'PRINT_OBSERVATIONS.json',obs)
apply(12)
