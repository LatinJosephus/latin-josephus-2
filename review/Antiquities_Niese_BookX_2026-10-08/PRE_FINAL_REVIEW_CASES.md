# Book X: adjudicated candidate decisions and remaining questions

**NO-GO. Audit only. No production application or reader enablement is approved.**

Individual routine Latin review is complete: **224/224**; **223** secure routine starts. Two questions remain: revised X.102 and the X.276 extent qualification.

The accepted print checkpoint is commit `dec5f783b1af936803150536ed5aaa031b21c479`. [Exact earlier case packet](PRINT_CHECKPOINT_REVIEW_CASES.md) preserves the original proposals, unresolved wording and decision history. Current `BOUNDARIES.json` supersedes that operative state; each record retains `printed_checkpoint_state`, `printed_checkpoint_reassessment` and an entry in `ADJUDICATION_HISTORY.json`.

All 701 routine Greek starts were already examined in print; that examination was retained, not restarted. Individual Latin review compared each incipit, proposed cut and adjoining context. It is a citation-boundary review, not a complete word-by-word textual collation. Greek verification and closed arithmetic do not establish Latin confidence.

The display symbol ⟦candidate cut⟧ is never inserted into XML. Context below omits apparatus for readability; the original paragraph including inline elements and notes remains untouched. Coordinates identify exact existing text nodes and UTF-8 bytes.

## Remaining editorial decisions

### X.101–102 — revised cut awaiting judgement

Affected Latin: `latin-book10-num99`. Niese, *Flavii Iosephi Opera* II (1885), printed p. **352**, PDF p. **360**; [accepted page image](evidence/print-collation/niese-II-pdf-360.jpg). The retained `print_collation` record separates marginal position and any independent Loeb control from the elected word cut.

**Greek 101, complete interval:**

οἷς οὐδ᾽ ἐνιαυτὸν ἡ πίστις ἔμεινεν: οὐ γὰρ ἐφύλαξεν αὐτὴν ὁ τῶν Βαβυλωνίων βασιλεύς, ἀλλὰ τοῖς στρατηγοῖς ἐπέστειλεν ἅπαντας τοὺς ἐν τῇ πόλει λαβόντας αἰχμαλώτους νέους τὴν ἡλικίαν καὶ τεχνίτας δεδεμένους ἄγειν πρὸς αὑτόν, ἦσαν δὲ οὗτοι πάντες εἰς μυρίους ὀκτακοσίους τριακονταδύο, καὶ τὸν Ἰωάκειμον μετὰ τῆς μητρὸς καὶ τῶν φίλων.  

**Greek 102, complete interval:**

τούτους δὴ κομισθέντας πρὸς αὑτὸν εἶχεν ἐν φυλακῇ: τὸν δὲ θεῖον τοῦ Ἰωακείμου Σαχχίαν ἀπέδειξε βασιλέα ὅρκους παρ᾽ αὐτοῦ λαβών, ἦ μὴν φυλάξειν αὐτῷ τὴν χώραν καὶ μηδὲν νεωτερίσειν μηδὲ τοῖς Αἰγυπτίοις εὐνοήσειν. 

**Reassessed Latin across 101–102:**

quorum fides nequaquam mansit inviolata. Non enim seruauit eam babyloniae rex sed precepit princibus suis ut omnes qui erant in ciuitate uiuenes captiuos sumerent pariter et artifices eosque ad se ligatos adducerent, qui omnis fuerunt decem milia et octingenti triginti et duo simulet ioachim  **⟦revised candidate 102⟧** nomine sedechiam constituit regem, accipiens abeo iusiurandum ut ei prouintiam custodiret et nihil ostiliter ageret nec faueret aegyptiis. 

`latin-book10-num99`; `/TEI[1]/text[1]/body[1]/div1[1]/div2[7]/p[1]/num[1]/tail()`; node character **804**, paragraph character **804**, book character **26550**, original UTF-8 byte **31889** (zero-based).

The earlier candidate before **simulet ioachim** was at original byte **31873**, node character **788**. The revised cut before **nomine sedechiam** is at original byte **31889**, node character **804**. The intervening wording remains with 101; both neighbouring extents have been recomputed.

**Difficulty and recommendation.** Greek 101 concludes with Joachim, his mother and friends. The damaged Latin **simulet ioachim** may preserve its concluding Joachim reference. Greek 102 first describes imprisonment, then appoints Joachim’s uncle; those opening details are not explicitly recoverable in this Latin wording. **nomine sedechiam constituit regem** is the first unambiguous naming/appointment phrase. Recommend this qualified first-surviving-counterpart cut, preserving every word and leaving **simulet ioachim** with 101. No reconstruction or claim of physical loss follows.

**Credible alternative.** Keep the earlier cut before **simulet ioachim** as an explicitly approximate citation location, accepting that it may assign the conclusion of 101 to 102. The previous location is retained in history, not approved.

**Decision requested:** approve or reject the revised cut before **nomine sedechiam**, with the preceding **simulet ioachim** retained in 101 and the unexpressed opening details qualified.

### X.276–277 — new partial-correspondence qualification

Niese, *Flavii Iosephi Opera* II (1885), printed p. **391**, PDF p. **399**; [accepted page image](evidence/print-collation/niese-II-pdf-399.jpg). The retained `print_collation` record separates marginal position and any independent Loeb control from the elected word cut.

Affected Latin: `latin-book10-num263`. The start **Et haec** is secure; the question concerns the extent of surviving correspondence.

**Greek 276, complete interval:**

καὶ δὴ ταῦτα ἡμῶν συνέβη παθεῖν τῷ ἔθνει ὑπὸ Ἀντιόχου τοῦ Ἐπιφανοῦς, καθὼς εἶδεν ὁ Δανίηλος καὶ πολλοῖς ἔτεσιν ἔμπροσθεν ἀνέγραψε τὰ γενησόμενα. τὸν αὐτὸν δὲ τρόπον ὁ Δανίηλος καὶ περὶ τῆς Ῥωμαίων ἡγεμονίας ἀνέγραψε, καὶ ὅτι ὑπ᾽ αὐτῶν ἐρημωθήσεται.  

**Latin 276 followed by 277:**

**⟦276⟧** Et haec utique gens nostra sustinuit per an antiocum qui appellatus est epiphoanes hoc est predarus sicut uidit danihel et ante multos conscripsit annos  **⟦277⟧** quae omnia illi deo sibi monstrante conscribens. relinquid uti legentes et quae iam prouenire considerantes credebant in honore diuino fuisse danihelem et per haecque sunt ita uerissima ita uero epicurios errare cognoscant, 

`latin-book10-num263`; `/TEI[1]/text[1]/body[1]/div1[1]/div2[11]/p[3]/cb[4]/tail()`; node character **218**, paragraph character **4050**, book character **74308**, original UTF-8 byte **85670** (zero-based).

**Evidence and limits.** The Latin expresses Antiochus and Daniel’s earlier writing, then proceeds directly to **quae omnia**, the counterpart of Greek 277 **ταῦτα πάντα**. No identifiable counterpart of the closing Greek Roman-dominion/desolation clause appears here or in the expanded book context. A whole-book case-insensitive `roman` check finds only **lingua romana** at X.244, a language description. That search supports the contextual review but is not by itself proof of absence. The cause of the unexpressed clause is undetermined; no physical loss is established.

**Recommended treatment:** retain **Et haec** for 276 and **quae omnia** for 277, qualify 276 as partial correspondence for the unexpressed closing Greek clause, and preserve the Latin order without supplementation or an automatic gap. Do not make the whole section unavailable.

**Credible alternative:** retain both secure starts while deferring the explicit partial-correspondence representation qualification pending further textual research. Moving 277 or supplying the Roman notice has no support in this transcription.

**Decision requested:** approve or defer the partial-correspondence qualification of X.276 with both candidate starts unchanged.

## Adopted editorial candidates and qualifications

| Niese | Latin candidate | Status |
|---|---|---|
| X.18 | Turbatur ergo rex | Adjudicated candidate only |
| X.33 | Cui propheta respondens | Adjudicated candidate only |
| X.69 | et domos et uicos | Adjudicated candidate only |
| X.107 | eo quod | Adjudicated candidate only |
| X.109 | Interea dum hoc cognouisset | Adjudicated candidate only |
| X.150 | Rex autem pontifices | Adjudicated candidate only |
| X.151 | Igitur quia genus explanauimus | Adjudicated candidate only |
| X.213 | rex dum fecisset | Adjudicated candidate only |
| X.248 | nepus nepos | Adjudicated candidate only |
| X.108 | No surviving counterpart | Unavailable retained; cause undetermined |

The editor’s choices are recorded independently of implementation permission. EXACT and INTERNAL-BUT-EXACT below describe physical candidate starts, including the expressly qualified editorial choices; they do not claim complete word-for-word equivalence or that a Niese marginal numeral tags a word.

### X.18 — adopted candidate

Niese, *Flavii Iosephi Opera* II (1885), printed p. **334**, PDF p. **342**; [accepted page image](evidence/print-collation/niese-II-pdf-342.jpg). The retained `print_collation` record separates marginal position and any independent Loeb control from the elected word cut.

**Greek:** Θαρσικὴν πολλὴν ἄγοντα δύναμιν ἐπὶ συμμαχίᾳ τοῖς Αἰγυπτίοις ἥκειν διεγνωκότα ποιήσασθαι τὴν πορείαν διὰ τῆς ἐρήμου καὶ ἐξαίφνης εἰς τὴν τῶν Ἀσσυρίων ἐμβαλεῖν.   **⟦candidate cut⟧** ταραχθεὶς οὖν ὑπὸ τούτων ὁ βασιλεὺς Σεναχείριμος * ἐπὶ τὸν ἱερέα τὸν Ἡφαίστου στρατεῦσαι ἔλεγεν * ὡς οὗτος ὁ βασιλεὺς ἐπὶ τὸν τῶν Αἰγυπτίων ἔλθοι βασιλέα ἱερέα ὄντα τοῦ Ἡφαίστου, πολιορκῶν δὲ τὸ Πηλούσιον ἔλυσε τὴν πολιορκίαν ἐξ αἰτίας τοιαύτης: ηὔξατο ὁ βασιλεὺς τῶν Αἰγυπτίων τῷ θεῷ, ᾧ γενόμενος ἐπήκοος ὁ θεὸς πληγὴν ἐνσκήπτει τῷ Ἄραβι:  πλανᾶται γὰρ κἀν τούτῳ οὐκ Ἀσσυρίων λέγων τὸν βασιλέα ἀλλ᾽ Ἀράβων: μυῶν γὰρ πλῆθός φησι μιᾷ νυκτὶ τὰ τόξα καὶ

**Latin:** istere, audiuit aethiopum regem tharachem cum multo exercitu ad aegyptiorum uenire solacium et per desertum iter facerent ut subito assyriorum castra inrueret.  **⟦candidate cut⟧** Turbatur ergo rex sennacherim ad sacerdotem,  suae restituebat, et potum conuiuia conuersi per septem dies summa laetitia fruebantur, ad restaurationem regenerationemque patriae festiua gratulatione celebrent postea omnis principes tribuum ad hierosilimam profecturi cum uxoribus et filii sae subiugalibus, et egerunt homines dari, quos cum eis rex usque ad hierosolimam destinauit, et cum letitia et iucunditate uel cantibus tibiisque ac sonantibus 

`latin-book10-num15`; `/TEI[1]/text[1]/body[1]/div1[1]/div2[2]/p[4]/unclear[2]/tail()`; node character **18**, paragraph character **1263**, book character **4847**, original UTF-8 byte **7415** (zero-based).

Before Turbatur: letter, reassurance, siege and news of Ethiopian relief. After Turbatur: Sennacherib response, then ritual/restoration material within the same paragraph, followed by the resumed Vulcan/Pelusium account. The 18 interval includes that intervening Latin material through the cut before 19; preserve it and the editorial note.

**Complete containing Latin paragraph, showing both sides:**

 Ipso siquidem tempore scripserat ezechias ad assyrios epistolas inquibus fatuum eum esse dicebant. Credentem quod eius seruitium posset euadere, qui multas gentes et maximas subdidisset, et inter minabatur funditus se eum disperdere dum caperet urbem. Ut nisi portas aperiens sponte in hierosololimis exercitum eius exciperet, quae dum relegisset et ezechias spreuit propter spem quam habebat in deo. Espitulam uero plicans in templo reposuit. Rursus autem cum deo uota et ora elit tiones effunderet pro ciuitate et salu non te cunctorum esaias propheta eum asseruit exauditum, et nec in praesenti tempore esse ab assyriis obsidendum et in futuro omnes qui ab illo iam captiui fuerant esse reuersuros, et tertio anno cum pace opus suum facturos et propriarum possessionum sine timore diligentiam habituros. Interea paruo tempore transeunte assyriorum rex bello quo aegyptiis intulerat frustratus ab huius modi causa sine effectu remeauit. Ab propriis enim cum multo iam tempore fuisset commoratus in obsessione peluiim peluim, et dum aggeres contra muros eleuati fuissent, quibus ciuitati nitebatur insistere, audiuit aethiopum regem tharachem cum multo exercitu ad aegyptiorum uenire solacium et per desertum iter facerent ut subito assyriorum castra inrueret.  **⟦18⟧** Turbatur ergo rex sennacherim ad sacerdotem,  suae restituebat, et potum conuiuia conuersi per septem dies summa laetitia fruebantur, ad restaurationem regenerationemque patriae festiua gratulatione celebrent postea omnis principes tribuum ad hierosilimam profecturi cum uxoribus et filii sae subiugalibus, et egerunt homines dari, quos cum eis rex usque ad hierosolimam destinauit, et cum letitia et iucunditate uel cantibus tibiisque ac sonantibus cymbalis ibant. Precedebat autem eos et reliqua multitudo iudaeorum cum laudibus atilli ad hierosolimam conscendebant ab una quaque patruum tribuum qui ulcani vucalni castra se metari dicebat quasi iste rex ad eum regem aegyptiorum uenisset qui esset ulcani sacerdos et obosessionem obsessionem pelusi huius modi causa dissoluit.  Orante numque rege aegyptiorum ad dominum et deus exaudiens maximam plagam misit in eum et multi perempti sunt. Erodotus autem errorem ideo facit quod non assyriorum dicit regem sed arabum adiciens, qui suricum multitudine una nocte arcus et arma reliqua commedit Et propterea cum non haberet rex arcus exercitum a pelusio robabit. Et haec quidem erudotus Uerosus Berosus autem qui chaldeicam conscriptis historiam meminit redig sennacherim et quia regnauit super assyrios et castra metatus est in omnem asyam asiam et aegyptum ita dicens.

**Complete candidate 18 interval:**

Turbatur ergo rex sennacherim ad sacerdotem,  suae restituebat, et potum conuiuia conuersi per septem dies summa laetitia fruebantur, ad restaurationem regenerationemque patriae festiua gratulatione celebrent postea omnis principes tribuum ad hierosilimam profecturi cum uxoribus et filii sae subiugalibus, et egerunt homines dari, quos cum eis rex usque ad hierosolimam destinauit, et cum letitia et iucunditate uel cantibus tibiisque ac sonantibus cymbalis ibant. Precedebat autem eos et reliqua multitudo iudaeorum cum laudibus atilli ad hierosolimam conscendebant ab una quaque patruum tribuum qui ulcani vucalni castra se metari dicebat quasi iste rex ad eum regem aegyptiorum uenisset qui esset ulcani sacerdos et obosessionem obsessionem pelusi huius modi causa dissoluit.  Orante numque rege aegyptiorum ad dominum et deus exaudiens maximam plagam misit in eum et multi perempti sunt. 

The complete interval includes the ritual/restoration material after the cut, its continuation across the following paragraph boundary, and the resumed Egyptian narrative before 19. It is not described as preceding Turbatur.

### X.33 — adopted candidate

Niese, *Flavii Iosephi Opera* II (1885), printed p. **338**, PDF p. **346**; [accepted page image](evidence/print-collation/niese-II-pdf-346.jpg). The retained `print_collation` record separates marginal position and any independent Loeb control from the elected word cut.

**Greek:** λῶνος ἔλεγε παρὰ τοῦ θεοῦ ἐλθεῖν αὐτούς: ἐπιδεῖξαι δὲ πάντ᾽ αὐτοῖς, ὅπως ἰδόντες τὸν πλοῦτον καὶ τὴν δύναμιν ἐκ τούτου στοχαζόμενοι σημαίνειν ἔχωσι τῷ βασιλεῖ.  **⟦candidate cut⟧** ὁ δὲ προφήτης ὑποτυχών ‘ἴσθι’  , φησίν, ‘οὐ μετ᾽ ὀλίγον χρόνον εἰς Βαβυλῶνά σου τοῦτον μετατεθησόμενον τὸν πλοῦτον καὶ τοὺς ἐκγόνους εὐνουχισθησομένους καὶ ἀπολέσαντας τὸ ἄνδρας εἶναι τῷ Βαβυλωνίῳ δουλεύσοντας βασιλεῖ: ταῦτα γὰρ προλέγειν τὸν θεόν.’  ὁ δ᾽ Ἐζεκίας λυπηθεὶς ἐπὶ τοῖς εἰρημένοις ἔφη μὲν οὐκ ἂν βούλεσθαι τοιαύταις συμφοραῖς τὸ ἔθνος αὐτοῦ περιπεσεῖν, ἐπεὶ δ᾽ οὐκ εἶναι δυνατὸν τὰ τῷ θεῷ δεδογμένα μεταβαλεῖν, ηὔχετο μέχρι τῆς αὐτοῦ ζωῆς

**Latin:** erant. Qui dixit. De babylonia eos a suo rege uenisse et ostendisse ei uniuersa ut uidentes diuitias et uirtutem regni cognoscetrent et regi suo renum tiarent.  **⟦candidate cut⟧** Cui propheta respondens. Scito in quid non post multum tempus ad babyloniam filios tuos et diuitias transmigran das, insuper et nepotes tuos eunuchos esse fa sciendos, et ammissuros uirile nomen et regi babyloniae seruituros. Haec enim praedixit deus. Ezechias autem contristatus in his quae dicta fuerant, ait. Non sequidem uelle suam gentem in talibus erumnis incurreret, sed quia inpossibile est quae apud deum deliberata sunt posse mutari rogabat

`latin-book10-num30`; `/TEI[1]/text[1]/body[1]/div1[1]/div2[3]/p[2]/expan[1]/tail()`; node character **144**, paragraph character **633**, book character **9361**, original UTF-8 byte **12662** (zero-based).

Paired physical starts elected by the editor after printed-collation review. Candidate only; no application authorized.

Elected Greek phrase: **ὁ δὲ προφήτης ὑποτυχών**. The original canonical locator, printed marginal observation and independent Loeb evidence remain distinct in the register; any relocation is an unapplied proposal.

### X.69 — adopted candidate

Niese, *Flavii Iosephi Opera* II (1885), printed p. **345**, PDF p. **353**; [accepted page image](evidence/print-collation/niese-II-pdf-353.jpg). The retained `print_collation` record separates marginal position and any independent Loeb control from the elected word cut.

**Greek:** ναι μὲν τὰς ἀσεβεῖς πράξεις καὶ τὰς τιμὰς τὰς πρὸς τοὺς ἀλλοτρίους θεοὺς ἐγκαταλιπεῖν ἔπεισε, τὸν δὲ πάτριον καὶ μέγιστον θεὸν εὐσεβεῖν καὶ τούτῳ προσανέχειν:   **⟦candidate cut⟧** τὰς οἰκίας τε καὶ τὰς κώμας ἠρεύνησε καὶ τὰς πόλεις, μή τις ἔνδον ἔχοι τι τῶν εἰδώλων ὑπονοῶν. οὐ μὴν ἀλλὰ καὶ τὰ τοῖς βασιλευομένοις ἐφεστῶτα ἅρματα, ἃ κατεσκεύασαν οἱ πρόγονοι, καὶ εἴ τι ἄλλο τοιοῦτον ἦν ᾧ προσεκύνουν ὡς θεῷ ἐβάστασε:  καὶ καθαρίσας οὕτω τὴν χώραν ἅπασαν εἰς Ἱεροσόλυμα τὸν λαὸν συνεκάλεσε κἀκεῖ τὴν ἀζύμων ἑορτὴν καὶ τὴν πάσχα λεγομένην ἤγαγεν: ἐδωρήσατό τε τῷ λαῷ τὸ πάσχα νεογνοὺς ἐρίφους καὶ ἄρνας δισμυρίους, βοῦς δ᾽ εἰς ὁλοκα

**Latin:**  seruitium assyriorum effugerant, eis que suasit et impios actos et honores deorum extraneorum relinquerent, et patrium maximumque colerent deum eique dicarent  **⟦candidate cut⟧** et domos et uicos. Perscrutatus est autem ciuitatem nequod forte idolum habentes intra sua tecta celarent, nec nos et curros qui aedificati fuerant apri oribus regibus et quae que alia huius modi erant quae uelut deos adorabant cuncta pariter amputauit. Et hoc modo purgata omni prouintia ad hierosolimam omnem populum conuocauit et ad azymorum festiuitatem quae pascha dicitur eos adduxit. Donauit que populo in pascha nouellos aedos et agnos trigin

`latin-book10-num68`; `/TEI[1]/text[1]/body[1]/div1[1]/div2[5]/p[6]/num[1]/tail()`; node character **242**, paragraph character **242**, book character **18565**, original UTF-8 byte **23088** (zero-based).

Opening Greek objects are houses and villages. Latin attaches et domos et uicos to dicarent in the preceding syntax, then begins Perscrutatus est autem ciuitatem. Preserve the changed syntactic attachment and the elected embedded cut.

### X.107 — adopted candidate

Niese, *Flavii Iosephi Opera* II (1885), printed p. **353**, PDF p. **361**; [accepted page image](evidence/print-collation/niese-II-pdf-361.jpg). The retained `print_collation` record separates marginal position and any independent Loeb control from the elected word cut.

**Greek:**  αἰχμάλωτος ἔσται, διεφώνησε δὲ Ἰεζεκίηλος εἰπὼν οὐκ ὄψεσθαι Βαβυλῶνα τὸν Σαχχίαν τοῦ Ἱερεμίου φάσκοντος αὐτῷ, ὅτι δεδεμένον αὐτὸν ὁ Βαβυλώνιος ἄξει βασιλεύς.   **⟦candidate cut⟧** καὶ διὰ τὸ μὴ ταὐτὸν αὐτοὺς ἑκατέρους λέγειν καὶ περὶ ὧν συμφωνεῖν ἐδόκουν ὡς οὐδ᾽ ἐκεῖνα ἀληθῆ λέγουσι καταγνούς: καίτοι πάντ᾽ αὐτῷ κατὰ τὰς προφητείας ἀπήντησεν, ἅπερ εὐκαιρότερον δηλώσομεν. Τὴν συμμαχίαν δὲ τὴν πρὸς τοὺς Βαβυλωνίους ἐπ᾽ ἔτη ὀκτὼ κατασχὼν διέλυσε τὰς πρὸς αὐτοὺς πίστεις καὶ τοῖς Αἰγυπτίοις προστίθεται καταλύσειν τοὺς Βαβυλωνίους ἐλπίσας, αἳ μετ᾽ ἐκείνων ἐγένοντο.  μαθὼν δὲ τοῦτο ὁ τῶν Βαβυλωνίων βασιλεὺς ἐστράτευσεν ἐπ᾽ αὐτὸν κ

**Latin:**  captiuus in babylonia. Discordabat autem ezechiel dicens. Quia sedechias babyloniam non uideret cum hieremias dixisset quia uinctum eum rex babyloniae duceret  **⟦candidate cut⟧** eo quod idem uterque dixissent etiam illi quae non concordabant non esse uera dicebat, licet ei omnia secundum eorum euenirent prophetias quae tamen oportunius declarauimus. Interea dum hoc cognouisset babyloniae rex castra mouit aduersus eum et afflicta prouincia et monitiones eius una diripiens ad ipsam hierosolimorum ciuitatem obsedendam cum magno ueniebat exericitu. Rex autem aegyptius audiens quia sedechias amicus esset sumpta uirtute maxima

`latin-book10-num103`; `/TEI[1]/text[1]/body[1]/div1[1]/div2[7]/p[2]/cb[1]/tail()`; node character **1258**, paragraph character **1289**, book character **27977**, original UTF-8 byte **33394** (zero-based).

Record both differences: Latin idem versus Greek μὴ ταὐτόν, and Latin non concordabant versus Greek συμφωνεῖν. No emendation; the physical eo quod locator remains elected.

### X.109 — adopted candidate

Niese, *Flavii Iosephi Opera* II (1885), printed p. **354**, PDF p. **362**; [accepted page image](evidence/print-collation/niese-II-pdf-362.jpg). The retained `print_collation` record separates marginal position and any independent Loeb control from the elected word cut.

**Greek:** βυλωνίους ἐπ᾽ ἔτη ὀκτὼ κατασχὼν διέλυσε τὰς πρὸς αὐτοὺς πίστεις καὶ τοῖς Αἰγυπτίοις προστίθεται καταλύσειν τοὺς Βαβυλωνίους ἐλπίσας, αἳ μετ᾽ ἐκείνων ἐγένοντο.   **⟦candidate cut⟧** μαθὼν δὲ τοῦτο ὁ τῶν Βαβυλωνίων βασιλεὺς ἐστράτευσεν ἐπ᾽ αὐτὸν καὶ τὴν χώραν κακώσας αὐτοῦ καὶ τὰ φρούρια λαβὼν ἐπ᾽ αὐτὴν ἧκε τὴν τῶν Ἱεροσολυμιτῶν πόλιν πολιορκήσων αὐτήν.  ὁ δ᾽ Αἰγύπτιος ἀκούσας ἐν οἷς ἐστιν ὁ σύμμαχος αὐτοῦ Σαχχίας ἀναλαβὼν πολλὴν δύναμιν ἧκεν εἰς τὴν Ἰουδαίαν ὡς λύσων τὴν πολιορκίαν. ὁ δὲ Βαβυλώνιος ἀφίσταται τῶν Ἱεροσολύμων, ἀπαντήσας δὲ τοῖς Αἰγυπτίοις καὶ συμβαλὼν αὐτοῖς τῇ μάχῃ νικᾷ καὶ τρεψάμενος αὐτοὺς εἰς φυγὴν ἐξ ὅλης

**Latin:** terque dixissent etiam illi quae non concordabant non esse uera dicebat, licet ei omnia secundum eorum euenirent prophetias quae tamen oportunius declarauimus.  **⟦candidate cut⟧** Interea dum hoc cognouisset babyloniae rex castra mouit aduersus eum et afflicta prouincia et monitiones eius una diripiens ad ipsam hierosolimorum ciuitatem obsedendam cum magno ueniebat exericitu. Rex autem aegyptius audiens quia sedechias amicus esset sumpta uirtute maxima bellatorum uenit ad iudeam quasi eius soluturus obscescionem. Babylonius autem recessit ab hierosolimis et occurrit aegyptiis eisque congressus proelio superauit, et eos in 

`latin-book10-num108`; `/TEI[1]/text[1]/body[1]/div1[1]/div2[8]/p[1]/num[1]/tail()`; node character **1**, paragraph character **1**, book character **28151**, original UTF-8 byte **33679** (zero-based).

Executable 109 begins Interea dum hoc cognouisset although the inherited label claims 108. Preserve the visible text, ID, sameAs and chapter structure; future representation needs a data-level identity override.

### X.150 — adopted candidate

Niese, *Flavii Iosephi Opera* II (1885), printed p. **362**, PDF p. **370**; [accepted page image](evidence/print-collation/niese-II-pdf-370.jpg). The retained `print_collation` record separates marginal position and any independent Loeb control from the elected word cut.

**Greek:**  Σαχχίου ἑπτὰ καὶ τὸν γραμματέα αὐτοῦ καὶ ἄλλους ἡγεμόνας ἑξήκοντα, οὓς ἅπαντας μεθ᾽ ὧν ἐσύλησε σκευῶν ἐκόμισε πρὸς τὸν βασιλέα εἰς Σαλάβαθα πόλιν τῆς Συρίας.   **⟦candidate cut⟧** ὁ δὲ βασιλεὺς τοῦ μὲν ἀρχιερέως καὶ τῶν ἡγεμόνων ἐκέλευσεν ἐκεῖ τὰς κεφαλὰς ἀποτεμεῖν, αὐτὸς δὲ πάντας τοὺς αἰχμαλώτους καὶ τὸν Σαχχίαν εἰς Βαβυλῶνα δέσμιον ἐπήγετο καὶ Ἰωσάδακον τὸν ἀρχιερέα ὄντα υἱὸν Σαραία τοῦ ἀρχιερέως, ὃν ἀπέκτεινεν ὁ Βαβυλώνιος ἐν Ἀριβαθᾶ πόλει τῆς Συρίας, ὡς καὶ πρότερον ἡμῖν δεδήλωται. Ἐπεὶ δὲ τὸ γένος διεξήλθομεν τὸ τῶν βασιλέων καὶ τίνες ἦσαν δεδηλώκαμεν καὶ τοὺς χρόνους αὐτῶν, ἀναγκαῖον ἡγησάμην καὶ τῶν ἀρχιερέων εἰπεῖ

**Latin:** eptem et scribam eius et alios principes saxaginta sexaginta quos omnes cum uasis quae depredatus est deduxit ad regem in arabatha prouintiae syriae ciuitatem.  **⟦candidate cut⟧** Rex autem pontifices quidem et principum ubi capita iussit abscidi. Ipse uero omnes captiuos et sedechiam deduxit in babyloniam. Uinctum uero circum egit et iosadach pontifices filium sareae pontificis quaem occidit babylonius in arabatha syriae ciuitatem sicut dudum iam designatum est. Igitur quia genus explanauimus, et qui fuerunt et eorum tempora cuncta narrauimus. Necessarium uidi caui etiam nomina reserare pontificum qui pontificatum regum t

`latin-book10-num151`; `/TEI[1]/text[1]/body[1]/div1[1]/div2[8]/p[10]/num[1]/tail()`; node character **1**, paragraph character **1**, book character **39385**, original UTF-8 byte **46130** (zero-based).

Executable 150 starts Rex autem pontifices in paragraph num151. Preserve its visible inherited 151 label and prevent it asserting a false executable 151 at this location.

### X.151 — adopted candidate

Niese, *Flavii Iosephi Opera* II (1885), printed p. **362**, PDF p. **370**; [accepted page image](evidence/print-collation/niese-II-pdf-370.jpg). The retained `print_collation` record separates marginal position and any independent Loeb control from the elected word cut.

**Greek:** μιον ἐπήγετο καὶ Ἰωσάδακον τὸν ἀρχιερέα ὄντα υἱὸν Σαραία τοῦ ἀρχιερέως, ὃν ἀπέκτεινεν ὁ Βαβυλώνιος ἐν Ἀριβαθᾶ πόλει τῆς Συρίας, ὡς καὶ πρότερον ἡμῖν δεδήλωται.  **⟦candidate cut⟧** Ἐπεὶ δὲ τὸ γένος διεξήλθομεν τὸ τῶν βασιλέων καὶ τίνες ἦσαν δεδηλώκαμεν καὶ τοὺς χρόνους αὐτῶν, ἀναγκαῖον ἡγησάμην καὶ τῶν ἀρχιερέων εἰπεῖν τὰ ὀνόματα καὶ τίνες ἦσαν οἱ τὴν ἀρχιερωσύνην καταδείξαντες ἐπὶ τοῖς βασιλεῦσι.  πρῶτος μὲν οὖν Σάδωκος ἀρχιερεὺς ἐγένετο τοῦ ναοῦ, ὃν Σολόμων ᾠκοδόμησε: μετ᾽ αὐτὸν δ᾽ ὁ υἱὸς Ἀχιμᾶς διαδέχεται τὴν τιμὴν καὶ μετὰ Ἀχιμᾶν Ἀζαρίας, τούτου δὲ Ἰώραμος, τοῦ δὲ Ἰωράμου Ἴως, μετ᾽ αὐτὸν δὲ Ἀξιώραμος,  τοῦ δὲ Ἀξιωράμου 

**Latin:**  Uinctum uero circum egit et iosadach pontifices filium sareae pontificis quaem occidit babylonius in arabatha syriae ciuitatem sicut dudum iam designatum est.  **⟦candidate cut⟧** Igitur quia genus explanauimus, et qui fuerunt et eorum tempora cuncta narrauimus. Necessarium uidi caui etiam nomina reserare pontificum qui pontificatum regum temporibus habuerunt. Primus siquidem sadoch pontifex templi quod salomon eadificauit. Post eum uero filius achimaas in eius honore successit. Post achimam zacharias. Post autem ioram, et post eum axioramus. Deinde fide as post fideam uero sudeas. Post hunc uero hilus. Hilo uero successit

`latin-book10-num151`; `/TEI[1]/text[1]/body[1]/div1[1]/div2[8]/p[10]/num[1]/tail()`; node character **289**, paragraph character **289**, book character **39673**, original UTF-8 byte **46418** (zero-based).

Executable 151 begins internally at Igitur quia genus explanauimus, independently of the visible inherited 151 label before 150.

### X.213 — adopted candidate

Niese, *Flavii Iosephi Opera* II (1885), printed p. **376**, PDF p. **384**; [accepted page image](evidence/print-collation/niese-II-pdf-384.jpg). The retained `print_collation` record separates marginal position and any independent Loeb control from the elected word cut.

**Greek:** τροπον τῆς βασιλείας ἐποίησε καὶ τοὺς συγγενεῖς αὐτοῦ, οὓς ὑπὸ φθόνου καὶ βασκανίας εἰς κίνδυνον ἐμπεσεῖν συνέβη τῷ βασιλεῖ προσκρούσαντας ἐξ αἰτίας τοιαύτης:   **⟦candidate cut⟧** ὁ βασιλεὺς κατασκευάσας χρύσεον ἀνδριάντα πηχῶν τὸ μὲν ὕψος ἑξήκοντα τὸ πλάτος δὲ ἕξ, στήσας αὐτὸν ἐν τῷ μεγάλῳ τῆς Βαβυλῶνος πεδίῳ καὶ μέλλων καθιεροῦν αὐτὸν συνεκάλεσεν ἐξ ἁπάσης ἧς ἦρχε γῆς τοὺς πρώτους πρῶτον αὐτοῖς προστάξας, ὅταν σημαινούσης ἀκούσωσι τῆς σάλπιγγος, τότε πεσόντας προσκυνεῖν τὸν ἀνδριάντα: τοὺς δὲ μὴ ποιήσαντας ἠπείλησεν εἰς τὴν τοῦ πυρὸς ἐμβληθῆναι κάμινον.  πάντων οὖν μετὰ τὸ σημαινούσης ἐπακοῦσαι τῆς σάλπιγγος προσκυνούντω

**Latin:** oscens obstipuit ingenium danihelis et procidens in faciem eo modo quo deus adoratur eum salutauit daniel ei que sacrificari quasi deo praecepit. Cui etiam rea  **⟦candidate cut⟧** rex dum fecisset statuam auream altitudine sexaginta cubitorum latitudine sex et eam statuisset in maximo babyloniae campo decicaturus eam conuocauit terrae cui praeerat preerat. Principes uniuersas eis primo praecipiens ut dum audirent tubae sonum prostrati statuam pariter adorarent. Qui uero hoc non facerent eos in igni caminum interminatus est esse mittendos. Omnibus ergo tubae sonum adorantibus simulacrum. Danihel autem et cognati eius minime

`latin-book10-num211`; `/TEI[1]/text[1]/body[1]/div1[1]/div2[10]/p[5]/num[1]/tail()`; node character **218**, paragraph character **218**, book character **56463**, original UTF-8 byte **65708** (zero-based).

Leave Cui etiam rea with 212; 213 begins rex dum fecisset. Preserve the broken wording and punctuation.

### X.248 — adopted candidate

Niese, *Flavii Iosephi Opera* II (1885), printed p. **384**, PDF p. **392**; [accepted page image](evidence/print-collation/niese-II-pdf-392.jpg). The retained `print_collation` record separates marginal position and any independent Loeb control from the elected word cut.

**Greek:** ύρου τοῦ Περσῶν βασιλέως ἐπ᾽ αὐτὸν στρατεύσαντος: Βαλτάσαρος γάρ ἐστιν, ἐφ᾽ οὗ τὴν αἵρεσιν τῆς Βαβυλῶνος συνέβη γενέσθαι, βασιλεύσαντος αὐτοῦ ἑπτακαίδεκα ἔτη.   **⟦candidate cut⟧** τῶν μὲν οὖν Ναβουχοδονοσόρου τοῦ βασιλέως ἐγγόνων τὸ τέλος τοιοῦτον παρειλήφαμεν γενόμενον: Δαρείῳ δὲ τῷ καταλύσαντι τὴν Βαβυλωνίων ἡγεμονίαν μετὰ Κύρου τοῦ συγγενοῦς ἔτος ἦν ἑξηκοστὸν καὶ δεύτερον, ὅτε τὴν Βαβυλῶνα εἷλεν, ὃς ἦν Ἀστυάγους υἱός, ἕτερον δὲ παρὰ τοῖς Ἕλλησιν ἐκαλεῖτο ὄνομα:  ὃς καὶ Δανίηλον τὸν προφήτην λαβὼν ἤγαγεν εἰς Μηδίαν πρὸς αὑτὸν καὶ πάσης αὐτῷ τιμῆς μεταδιδοὺς εἶχε σὺν αὑτῷ: τῶν τριῶν γὰρ σατραπῶν ἦν, οὓς ἐπὶ τῶν ἑξήκοντα κ

**Latin:** tus et ciuitas cyro persarum rege aduersus eum fortissime dimicantem. Balthasar enim his sub quo capi contigit babyloniam cum regnasset iam decem et octo annis  **⟦candidate cut⟧** nepus nepos nabucodonosor regis cui talem terminum fuisse percipimUs. Darius autem astiagis filius quia babyloniorum principatum destruixit cum cyro cognato suo annum habebat sexagesimum et secundum cum babylon fuisset in uasta qui tamen alio nomine uocabatur a graecis quique danihelem prophetam sumens ad se in mediam duxit et omni eum honore caelebrauit. Erat enim unus intres satraphas quos darius super trecentos sexaginta satrapas instituerat. 

`latin-book10-num245`; `/TEI[1]/text[1]/body[1]/div1[1]/div2[10]/p[10]/cb[1]/tail()`; node character **63**, paragraph character **634**, book character **66284**, original UTF-8 byte **76635** (zero-based).

Use the earliest genealogical counterpart nepus nepos. Preserve both nepus and nepos, Latin order and repetition.

## X.108 retained unavailability

Niese, *Flavii Iosephi Opera* II (1885), printed p. **353**, PDF p. **361**; [accepted page image](evidence/print-collation/niese-II-pdf-361.jpg). The retained `print_collation` record separates marginal position and any independent Loeb control from the elected word cut.

UNAVAILABLE in this transcription: treaty/alliance and Egyptian narrative absent; cause undetermined. Preserve the later surviving Interea narrative and visible [VII.iii.108], which must not assert executable 108.

The next surviving Latin narrative begins **Interea dum hoc cognouisset** at 109. Absence in this transcription is distinct from its cause, which is undetermined. The visible [VII.iii.108] and all IDs/links/divisions remain intact.

## X.281 textual discrepancy, secure start

Ego siquidem begins the final authorial statement after the providence argument. Preserve Latin crimen ... habebit despite Greek ἀνέγκλητον; the first-person cut is secure and the final extent reaches the narrative end.

The final first-person cut remains secure. The Latin **crimen prodiuersa sententia habebit** differs from Greek **ἀνέγκλητον ἐχέτω**. This is recorded without emending wording or opening a new cut decision.

## Visible inherited labels and executable identities

| Visible claim | Paragraph | Candidate section at label | Future identity action |
|---|---|---:|---|
| [VII.iii.108] | latin-book10-num108 | 109 | Preserve visible text; suppress false/duplicate executable claim |
| [VIII.vi.151] | latin-book10-num151 | 150 | Preserve visible text; suppress false/duplicate executable claim |

The separate [identity plan](EXECUTABLE_IDENTITIES.json) inventories every inherited label and its original byte. Later implementation requires certified data-level identity overrides at these displaced claims; adding internal milestones alone would be insufficient. Nothing here alters text, a label, xml:id, sameAs, chapter, paragraph or navigation.

## Current arithmetic and classifications

Expected **281** = retained inherited starts **50** + proposed internal starts **230** + unavailable **1**. Newly applied milestones: **0**.

| Placement | EXACT | INTERNAL-BUT-EXACT | REQUIRES_ADJUDICATION | UNAVAILABLE | Total |
|---|---:|---:|---:|---:|---:|
| INHERITED_START | 50 | 0 | 0 | 0 | 50 |
| PROPOSED_INTERNAL_MILESTONE | 0 | 228 | 2 | 0 | 230 |
| NO_LATIN_START | 0 | 0 | 0 | 1 | 1 |

| Placement | EDITORIALLY_ADJUDICATED_WITH_RECORDED_LIMITS | HIGH | HIGH_ABSENCE_IN_THIS_TRANSCRIPTION | HIGH_INDIVIDUALLY_REVIEWED | PENDING_EDITORIAL_VERIFICATION | SECURE_START_EXTENT_QUALIFICATION_PENDING | Total |
|---|---:|---:|---:|---:|---:|---:|---:|
| INHERITED_START | 0 | 46 | 0 | 4 | 0 | 0 | 50 |
| PROPOSED_INTERNAL_MILESTONE | 9 | 0 | 0 | 219 | 1 | 1 | 230 |
| NO_LATIN_START | 0 | 0 | 1 | 0 | 0 | 0 | 1 |

Greek starts awaiting routine print verification: **0**. Routine Latin candidates awaiting individual review: **0**. Historical confidence is preserved in each row; the operative confidence reflects individual review or an explicit editorial decision.

## Separate Greek opening proposals

The printed span is **1–281**, but the XML explicitly labels **2–281** only (280 labels). Citation **1** is implicit at the verified printed book opening. Its explicit representation is a separate unapplied proposal, not an extra section or a manufactured opening. See [Greek proposals](ADJUDICATED_GREEK_PROPOSALS.json).

## Current verification categories

| Situation | Records |
|---|---:|
| Greek start awaiting print verification | 0 |
| GREEK_RESOLVED_LATIN_COUNTERPART_SECURE | 278 |
| GREEK_RESOLVED_LATIN_PLACEMENT_DECISION_PENDING | 1 |
| ESTABLISHED_UNAVAILABILITY_ADJUDICATED | 1 |
| SOURCE_ANOMALY_REPRESENTATION_DECISION_PENDING | 1 |

RESOLVED includes expressly adjudicated word choices with retained printed qualifications; it does not mean that every marginal numeral unambiguously tags a word. Earlier `print_start_verified` flags are preserved as `historical_print_start_verified`; current category counts govern pending work.
