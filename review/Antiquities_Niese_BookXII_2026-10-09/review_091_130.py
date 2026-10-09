"""Individually examined XII.91–130, including adjacent syntax and print."""
from pathlib import Path
import sys,json
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parent/'Antiquities_Niese_Batch_12_13_2026-10-09'))
from record_review import save,apply
choices=json.loads((P/'LATIN_REVIEW_CHOICES.json').read_text(encoding='utf8'))
data={
91:('Cumque clamassent','Collective acclamation and tears follow the unwrapping and precede custody of the rolls.'),
92:('Tunc iussit codices','Custody, greeting and anniversary celebration follow the acclamation.'),
93:('Nam euenit eudem','Coincident victory date and banquet/lodging comprise 93; Latin omits the specific sea battle.'),
94:('Nicanor autem','Retained start introduces catering staff and ends with the royal arrangement.'),
95:('ut alimentis','Usual food and Dorotheus appointment belong here despite Latin syntactic continuation.'),
96:('per quem et praeparauerat','Preparation and the two halves of the seating arrangement precede the actual service.'),
97:('Post quam autem ita discubuerunt','Service according to custom and invitation to Eliseus to pray comprise 97.'),
98:('qui in medio stans','Prayer, acclamation and subsequent feasting start with Eliseus standing.'),
99:('Praeter mittens autem rex','Philosophical banquet questions and twelve days precede the Aristeus reference.'),
100:('et qui uult singula cognoscere','Aristeus reference closes the discussion of the banquets.'),
101:('Mirante uero eos','Retained start: Menedemus, providence and the ending of discussion.'),
102:('Dicebat autem maxima','Royal benefit and gifts follow the end of discussion.'),
103:('Postquam uero tres excesserunt dies','Three days, the island bridge and secluded house begin the translation setting.'),
104:('ubi eos perducens','Demetrius encouragement and work until the ninth hour precede refreshment.'),
105:('ad curam corporis uertebantur','Refreshment and Dorotheus hospitality begin at this verb phrase.'),
106:('Mane autem ad aulam','Morning audience, purification and subsequent translation comprise 106.'),
107:('itaque transcriptalege','Completion in seventy-two days and the public reading follow the working routine.'),
108:('Cumque multitudo amplexa','Popular approval and elders proposal to preserve the translation precede agreement.'),
109:('Cumque sententiam laudassent','Agreement and the provision for correction follow the elders proposal.'),
110:('gauisus ergo rex','Retained start: royal pleasure and question about historians and poets.'),
111:('Cui dimetrius respondit','Demetrius answer about divine laws and harm precedes the specific example.'),
112:('significabat uero qualiter theopompus','Theopompus disturbance, prayer and dream belong here through the attempted impure disclosure.'),
113:('cumque conscribere quieuisset','Theopompus recovery and Theodectes follow the dream.'),
114:('haec ergo rex pure suscipiens','Retained start: compressed royal reception and invitation to the interpreters.'),
115:('hoc enim eis ad honorem','Honour and voluntary future returns precede dismissal with gifts.'),
116:('Et tunc quidem transmisit eos','Dismissal and gifts to the elders follow the invitation.'),
117:('Principi autem sacerdotum eleazaro','Gifts to Eleazar begin after the gifts to the elders; Greek opening resumption has no separate Latin counterpart.'),
118:('Petiuit autem et perpistulas','Request for future returns and conclusion of the Ptolemaic narrative.'),
119:('Imperauerunt autem et regibus asiae','Retained start: Seleucus privileges and citizenship begin the Asian kings account.'),
120:('signum est quod iudaeis','Oil stipend and Mucianus provide the proof of citizenship.'),
121:('et post haec imperatoribus','Appeals of Alexandrians and Antiochenes precede the inference about Roman conduct.'),
122:('Unde potest considerare','Roman generosity including Vespasian and Titus despite resistance ends before the specific preservation of privileges.'),
123:('nihil penitus eis','No withdrawal of privileges and resistance to anger and communal requests comprise 123.'),
124:('Dum nihil neque','Beneficence over hatred and innocent peoples rights close this comparison.'),
125:('Simile uero quiddam','Retained start: Agrippa and the Ionian cities complaint.'),
126:('soli possiderent','Desired exclusive citizenship starts at this object phrase, followed by response and Agrippas judgment.'),
127:('Siquis autem certius','Nicolaus reference and judgment lead to the return from the digression.'),
128:('Uespasiani autem et titi','Magnanimity of Vespasian/Titus and return to the narrative close the digression.'),
129:('Judaeos igitur','Retained start: Antiochus and Jewish calamity in Coele-Syria.'),
130:('Nam cum antiochus pugnasset','Wars and alternating allegiances comprise 130 and precede the specific victory.')}
for n,(phrase,reason) in data.items():choices[str(n)]={'phrase':phrase,'assessment':reason}
choices['114']['limits']='Partial opening correspondence: the explicit Greek custody/bowing/keeping-clean directions are compressed or not expressed in this Latin paragraph; invitation survives. No whole-section absence or textual restoration.'
choices['117']['limits']='Greek introductory resumption of the preceding gifts lacks a distinct Latin phrase; the substantive gifts to Eleazar survive. Start at their first identifiable counterpart.'
choices['127']['limits']='Greek cites Nicolaus books 123 and 124; this Latin names only 123. Preserve the existing transcription.'
save(P/'LATIN_REVIEW_CHOICES.json',choices)
obs=json.loads((P/'PRINT_OBSERVATIONS.json').read_text(encoding='utf8'))
positions={160:{91:'left line 4, ἐκβοησάντων',92:'left line 7, preceding λυπηρῶν σύμβολα and κελεύσας',93:'left line 12, annual promise then ἔτυχεν',94:'left line 16, lower division 12, Ὁ δὲ ἐπὶ',95:'left line 19, preceding royal arrangement then κατὰ γὰρ',96:'left line 25, Dorotheus clause ending then συνέστρωσε'},161:{97:'right line 3, preceding honour ending then ἐπεὶ',98:'right line 9, preceding invitation then ὁ δὲ στὰς',99:'right line 12, preceding ἐτράπησαν then διαλιπὼν',100:'right line 17, twelve days then ὡς τῷ βουλομένῳ',101:'right line 20, lower division 13, Θαυμάζοντος',102:'right line 23, preceding discussion ending then γεγενῆσθαι'},162:{103:'left line 2, preceding lodging then διελθουσῶν',104:'left line 7, ἀγαγὼν οὖν',105:'left line 11, ἔπειτ᾽',106:'left line 14, preceding hospitality then πρωῒ',107:'left line 18, Μεταγραφέντος',108:'left line 22, τὸ δὲ πλῆθος'},163:{109:'right line 3, preceding μετακινεῖν ending then ἁπάντων',110:'right line 8, lower division 14, Ἐχάρη',111:'right line 13, preceding question then ὁ δὲ Δημήτριος',112:'right line 16, preceding harm then δηλῶν ὡς Θεόπομπος',113:'right line 22, preceding dream ending then καὶ ἀποσχόμενος'},164:{114:'left line 1, lower division 15, Παραλαβὼν',115:'left line 5, preceding invitation then τοῦτο γὰρ',116:'left line 9, preceding generosity then τότε',117:'left line 12, preceding στρωμνήν then καὶ ταῦτα',118:'left line 17, preceding bowls then παρεκάλεσεν',119:'left line 24, chapter III.1, Ἔτυχον'},165:{120:'right line 2, preceding citizenship then τεκμήριον',121:'right line 6, preceding Μουκιανός then καὶ μετὰ',122:'right line 9, preceding appeal then ἐξ οὗ',123:'right line 14, preceding resistance then οὐδενός',124:'right line 17, preceding requests then ὥστε',125:'right line 23, lower division 2, Ὅμοιον'},166:{126:'left line 1, preceding λεγόμενος then μόνοι',127:'left line 5, preceding judgment then τὸ δ᾽',128:'left line 9, preceding judgment then Οὐεσπασιανοῦ',129:'left line 13, lower division 3, Τοὺς γὰρ',130:'left line 15, preceding Coele-Syria then πολεμοῦντος'}}
for p,items in positions.items():
 for n,pos in items.items():obs[str(n)]={'edition':'Niese III, 1892','printed_page':p-72,'PDF_page':p,'image':f'evidence/Niese/page-{p}.png','observed_numeral_position':pos,'word_boundary_status':'XML_WORD_START_CONFIRMED_FROM_PRINT','editorial_word_choice':'Retain XML word start after printed clause and adjoining context inspection.'}
save(P/'PRINT_OBSERVATIONS.json',obs)
apply(12)
