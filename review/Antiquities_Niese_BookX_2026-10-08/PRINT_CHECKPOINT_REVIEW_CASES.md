# Book X: editorial decisions after printed collation

**NO-GO. Candidate audit only; implementation is not approved. No human decisions have been supplied.**

All 281 citation starts were checked against the supplied Niese body images. The routine page-reading queue is complete. No unread or inaccessible Niese start remains.

The historical EXACT / INTERNAL-BUT-EXACT / REQUIRES_ADJUDICATION / UNAVAILABLE classifications and confidence values are unchanged. Greek print verification alone does not certify a Latin cut. Routine Latin candidates still needing individual verification are counted separately from the decisions here. The earlier register and case packet remain recoverable in checkpoint commit `da28ec5abd7084fe5199549e2e38488171505c0e`.

Human decision records: **11**, sections 18, 33, 69, 102, 107, 108, 109, 150, 151, 213, 248. Resolved source cases: none. Paired sections should be decided jointly.

Every context below reproduces canonical text. The symbol ⟦candidate cut⟧ is editorial display only, never inserted into XML. Text-node offsets and UTF-8 bytes refer to the pinned LF worktree inputs; canonical CRLF hashes remain separately recorded in BASELINE.json.

## Concise decision list

| Section | Exact judgement requested |
|---|---|
| X.18 | Approve the contextual extent policy around 17–18 and the cut at Turbatur ergo rex. |
| X.33 | Accept or reject the proposed paired relocation of 33. |
| X.69 | Choose the embedded first counterpart or an explicitly approximate later locator. |
| X.102 | Approve the partial-survival citation treatment. |
| X.107 | Approve citation representation despite the recorded semantic difference. |
| X.108 | Approve an unavailable 108 state and an independent 109 locator while retaining the inherited label. |
| X.109 | Approve the displaced-label representation jointly with 108. |
| X.150 | Approve the 150 locator and suppression of the false inherited 151 start jointly with 151. |
| X.151 | Approve the non-textual override and internal locator jointly with 150. |
| X.213 | Choose which side of the cut retains Cui etiam rea. |
| X.248 | Choose the earliest genealogical counterpart or an explicitly approximate later cut. |

## Verification work states

| State | Records |
|---|---:|
| GREEK_VERIFIED_WITH_SECURE_LATIN_COUNTERPART | 46 |
| GREEK_COLLATED_LATIN_CANDIDATE_AWAITING_INDIVIDUAL_VERIFICATION | 224 |
| GREEK_COLLATED_LATIN_OR_REPRESENTATION_EDITORIAL_DECISION | 10 |
| ABSENCE_OR_SOURCE_ANOMALY_REQUIRES_REPRESENTATION_DECISION | 1 |

## Placement against retained confidence classifications

| Placement | EXACT | INTERNAL-BUT-EXACT | REQUIRES_ADJUDICATION | UNAVAILABLE | Total |
|---|---:|---:|---:|---:|---:|
| INHERITED_START | 46 | 0 | 4 | 0 | 50 |
| PROPOSED_INTERNAL_MILESTONE | 0 | 1 | 229 | 0 | 230 |
| NO_LATIN_START | 0 | 0 | 0 | 1 | 1 |

These are candidate placement counts, not inserted markers or certified availability.

| Placement | HIGH | PENDING_EDITORIAL_VERIFICATION | HIGH_ABSENCE_IN_THIS_TRANSCRIPTION |
|---|---:|---:|---:|
| INHERITED_START | 46 | 4 | 0 |
| PROPOSED_INTERNAL_MILESTONE | 1 | 229 | 0 |
| NO_LATIN_START | 0 | 0 | 1 |

## Decisions and resolved source cases

### X.18 — decision required

Affected Latin: `latin-book10-num15`.

Printed authority: Niese, *Flavii Iosephi Opera* II (1885), **p. 334**, PDF **342**. [Full page image](evidence/print-collation/niese-II-pdf-342.jpg).

**Greek, earlier canonical cut with adjoining text:**

ολλὴν ἄγοντα δύναμιν ἐπὶ συμμαχίᾳ τοῖς Αἰγυπτίοις ἥκειν διεγνωκότα ποιήσασθαι τὴν πορείαν διὰ τῆς ἐρήμου καὶ ἐξαίφνης εἰς τὴν τῶν Ἀσσυρίων ἐμβαλεῖν.   **⟦candidate cut⟧** ταραχθεὶς οὖν ὑπὸ τούτων ὁ βασιλεὺς Σεναχείριμος * ἐπὶ τὸν ἱερέα τὸν Ἡφαίστου στρατεῦσαι ἔλεγεν * ὡς οὗτος ὁ βασιλεὺς ἐπὶ τὸν τῶν Αἰγυπτίων ἔλθοι βασιλέα ἱερέα ὄντα τοῦ Ἡφαίστου, πολιορκῶν δὲ τὸ Πηλούσιον ἔλυσε τὴν πολιορκίαν ἐξ αἰτίας τοιαύτης: ηὔξατο ὁ βασιλεὺς τῶν Αἰγυπτίων τῷ θεῷ, ᾧ γενόμενος ἐπήκοος ὁ θεὸς πληγὴν ἐνσκήπτει τῷ Ἄραβι: 

**Latin, earlier candidate with adjoining text:**

diuit aethiopum regem tharachem cum multo exercitu ad aegyptiorum uenire solacium et per desertum iter facerent ut subito assyriorum castra inrueret.  **⟦candidate cut⟧** Turbatur ergo rex sennacherim ad sacerdotem,  suae restituebat, et potum conuiuia conuersi per septem dies summa laetitia fruebantur, ad restaurationem regenerationemque patriae festiua gratulatione celebrent postea omnis principes tribuum ad hierosilimam profecturi cum uxoribus et filii sae subiugalibus, et egerunt homines dari, quos cum

`latin-book10-num15`; `/TEI[1]/text[1]/body[1]/div1[1]/div2[2]/p[4]/unclear[2]/tail()`; node offset **18**, paragraph offset **1263**, UTF-8 byte **7415** (zero-based, pinned LF bytes).

**Difficulty.** Niese pp.334–335 confirms Greek 18 and editorial lacuna signals. Latin pnum15 has an extended ritual procession before Turbatur ergo rex which is not in the corresponding Greek; the existing “chapter 2 starts here” note is markup, not narrative. Greek verification does not settle how that additional Latin material belongs to the citation extents.

**Recommended treatment.** Preserve the procession and note in their present order; retain Turbatur ergo rex as the first corresponding candidate for 18 and document the broader preceding Latin extent.

**Credible alternatives.** An explicitly contextual locator may include the procession; do not manufacture Greek counterparts or relocate the chapter.

**Decision requested.** Approve the contextual extent policy around 17–18 and the cut at Turbatur ergo rex.

### X.33 — decision required

Affected Latin: `latin-book10-num30`.

Printed authority: Niese, *Flavii Iosephi Opera* II (1885), **p. 338**, PDF **346**. [Full page image](evidence/print-collation/niese-II-pdf-346.jpg).
[Loeb VI, p.174, PDF190](evidence/print-collation/loeb-VI-followup-190.png) (independent control; Niese supplies numbering).

**Greek, earlier canonical cut with adjoining text:**

ἐπιδεῖξαι δὲ πάντ᾽ αὐτοῖς, ὅπως ἰδόντες τὸν πλοῦτον καὶ τὴν δύναμιν ἐκ τούτου στοχαζόμενοι σημαίνειν ἔχωσι τῷ βασιλεῖ. ὁ δὲ προφήτης ὑποτυχών ‘ἴσθι’   **⟦candidate cut⟧** , φησίν, ‘οὐ μετ᾽ ὀλίγον χρόνον εἰς Βαβυλῶνά σου τοῦτον μετατεθησόμενον τὸν πλοῦτον καὶ τοὺς ἐκγόνους εὐνουχισθησομένους καὶ ἀπολέσαντας τὸ ἄνδρας εἶναι τῷ Βαβυλωνίῳ δουλεύσοντας βασιλεῖ: ταῦτα γὰρ προλέγειν τὸν θεόν.’  ὁ δ᾽ Ἐζεκίας λυπηθεὶς ἐπὶ τοῖς εἰρημένοις ἔφη μὲν οὐκ ἂν βούλεσθαι τοιαύταις συμφοραῖς τὸ ἔθνος αὐτοῦ περιπεσεῖν, ἐπεὶ δ

**Latin, earlier candidate with adjoining text:**

rege uenisse et ostendisse ei uniuersa ut uidentes diuitias et uirtutem regni cognoscetrent et regi suo renum tiarent. Cui propheta respondens. Scito  **⟦candidate cut⟧** in quid non post multum tempus ad babyloniam filios tuos et diuitias transmigran das, insuper et nepotes tuos eunuchos esse fa sciendos, et ammissuros uirile nomen et regi babyloniae seruituros. Haec enim praedixit deus. Ezechias autem contristatus in his quae dicta fuerant, ait. Non sequidem uelle suam gentem in talibus erumnis incurrere

`latin-book10-num30`; `/TEI[1]/text[1]/body[1]/div1[1]/div2[3]/p[2]/expan[1]/tail()`; node offset **175**, paragraph offset **664**, UTF-8 byte **12693** (zero-based, pinned LF bytes).

**Reassessed proposal / alternative, not applied:**

ε παρὰ τοῦ θεοῦ ἐλθεῖν αὐτούς: ἐπιδεῖξαι δὲ πάντ᾽ αὐτοῖς, ὅπως ἰδόντες τὸν πλοῦτον καὶ τὴν δύναμιν ἐκ τούτου στοχαζόμενοι σημαίνειν ἔχωσι τῷ βασιλεῖ.  **⟦candidate cut⟧** ὁ δὲ προφήτης ὑποτυχών ‘ἴσθι’  , φησίν, ‘οὐ μετ᾽ ὀλίγον χρόνον εἰς Βαβυλῶνά σου τοῦτον μετατεθησόμενον τὸν πλοῦτον καὶ τοὺς ἐκγόνους εὐνουχισθησομένους καὶ ἀπολέσαντας τὸ ἄνδρας εἶναι τῷ Βαβυλωνίῳ δουλεύσοντας βασιλεῖ: ταῦτα γὰρ προλέγειν τὸν θεόν.’  ὁ δ᾽ Ἐζεκίας λυπηθεὶς ἐπὶ τοῖς εἰρημένοις ἔφη μὲν οὐκ ἂν βούλεσθαι τοιαύταις συμφοραῖς τὸ

 dixit. De babylonia eos a suo rege uenisse et ostendisse ei uniuersa ut uidentes diuitias et uirtutem regni cognoscetrent et regi suo renum tiarent.  **⟦candidate cut⟧** Cui propheta respondens. Scito in quid non post multum tempus ad babyloniam filios tuos et diuitias transmigran das, insuper et nepotes tuos eunuchos esse fa sciendos, et ammissuros uirile nomen et regi babyloniae seruituros. Haec enim praedixit deus. Ezechias autem contristatus in his quae dicta fuerant, ait. Non sequidem uelle suam gent

`latin-book10-num30`; `/TEI[1]/text[1]/body[1]/div1[1]/div2[3]/p[2]/expan[1]/tail()`; node offset **144**, paragraph offset **633**, UTF-8 byte **12662** (zero-based, pinned LF bytes).

Neighbouring extent change: 32 ends at the proposed cut instead of the old cut; 33 begins there and still ends at 34. Exact before/after offsets are in the boundary reassessment and DECISION_HISTORY.json.

**Difficulty.** Canonical Greek 33 follows ἴσθι and precedes φησίν, splitting the speech opening. Niese p.338 prints 33 at the line beginning ὁ δὲ προφήτης ὑποτυχών; Loeb p.174 supports the response clause as the section transition.

**Recommended treatment.** Propose moving the Greek start to ὁ δὲ προφήτης ὑποτυχών and Latin to Cui propheta respondens. Keep Scito in quid and the following speech together in 33; adjust proposed 32 extent accordingly.

**Credible alternatives.** Retain the old cut at φησίν / in quid non post multum, or at Scito with an explicit speech-order approximation.

**Decision requested.** Accept or reject the proposed paired relocation of 33.

### X.69 — decision required

Affected Latin: `latin-book10-num68`.

Printed authority: Niese, *Flavii Iosephi Opera* II (1885), **p. 345**, PDF **353**. [Full page image](evidence/print-collation/niese-II-pdf-353.jpg).

**Greek, earlier canonical cut with adjoining text:**

ς ἀσεβεῖς πράξεις καὶ τὰς τιμὰς τὰς πρὸς τοὺς ἀλλοτρίους θεοὺς ἐγκαταλιπεῖν ἔπεισε, τὸν δὲ πάτριον καὶ μέγιστον θεὸν εὐσεβεῖν καὶ τούτῳ προσανέχειν:   **⟦candidate cut⟧** τὰς οἰκίας τε καὶ τὰς κώμας ἠρεύνησε καὶ τὰς πόλεις, μή τις ἔνδον ἔχοι τι τῶν εἰδώλων ὑπονοῶν. οὐ μὴν ἀλλὰ καὶ τὰ τοῖς βασιλευομένοις ἐφεστῶτα ἅρματα, ἃ κατεσκεύασαν οἱ πρόγονοι, καὶ εἴ τι ἄλλο τοιοῦτον ἦν ᾧ προσεκύνουν ὡς θεῷ ἐβάστασε:  καὶ καθαρίσας οὕτω τὴν χώραν ἅπασαν εἰς Ἱεροσόλυμα τὸν λαὸν συνεκάλεσε κἀκεῖ τὴν ἀζύμων ἑορτὴν καὶ τὴν

**Latin, earlier candidate with adjoining text:**

 assyriorum effugerant, eis que suasit et impios actos et honores deorum extraneorum relinquerent, et patrium maximumque colerent deum eique dicarent  **⟦candidate cut⟧** et domos et uicos. Perscrutatus est autem ciuitatem nequod forte idolum habentes intra sua tecta celarent, nec nos et curros qui aedificati fuerant apri oribus regibus et quae que alia huius modi erant quae uelut deos adorabant cuncta pariter amputauit. Et hoc modo purgata omni prouintia ad hierosolimam omnem populum conuocauit et ad azym

`latin-book10-num68`; `/TEI[1]/text[1]/body[1]/div1[1]/div2[5]/p[6]/num[1]/tail()`; node offset **242**, paragraph offset **242**, UTF-8 byte **23088** (zero-based, pinned LF bytes).

**Difficulty.** Greek and Latin distribute the search of houses and streets differently; et domos et uicos is embedded before the later summary Perscrutatus est autem ciuitatem.

**Recommended treatment.** Prefer the earliest surviving counterpart et domos et uicos, preserving Latin order and documenting the reordered scope.

**Credible alternatives.** Begin at Perscrutatus est autem ciuitatem as a convenient larger cut but acknowledge the earlier counterpart.

**Decision requested.** Choose the embedded first counterpart or an explicitly approximate later locator.

### X.102 — decision required

Affected Latin: `latin-book10-num99`.

Printed authority: Niese, *Flavii Iosephi Opera* II (1885), **p. 352**, PDF **360**. [Full page image](evidence/print-collation/niese-II-pdf-360.jpg).

**Greek, earlier canonical cut with adjoining text:**

αὶ τεχνίτας δεδεμένους ἄγειν πρὸς αὑτόν, ἦσαν δὲ οὗτοι πάντες εἰς μυρίους ὀκτακοσίους τριακονταδύο, καὶ τὸν Ἰωάκειμον μετὰ τῆς μητρὸς καὶ τῶν φίλων.   **⟦candidate cut⟧** τούτους δὴ κομισθέντας πρὸς αὑτὸν εἶχεν ἐν φυλακῇ: τὸν δὲ θεῖον τοῦ Ἰωακείμου Σαχχίαν ἀπέδειξε βασιλέα ὅρκους παρ᾽ αὐτοῦ λαβών, ἦ μὴν φυλάξειν αὐτῷ τὴν χώραν καὶ μηδὲν νεωτερίσειν μηδὲ τοῖς Αἰγυπτίοις εὐνοήσειν. Σαχχίας δ᾽ ἦν ἐτῶν μὲν εἴκοσι καὶ ἑνός, ὅτε τὴν ἀρχὴν παρέλαβεν, ὁμομήτριος μὲν Ἰωακείμου τοῦ ἀδελφοῦ αὐτοῦ, τῶν δὲ δικαίων καὶ 

**Latin, earlier candidate with adjoining text:**

 ciuitate uiuenes captiuos sumerent pariter et artifices eosque ad se ligatos adducerent, qui omnis fuerunt decem milia et octingenti triginti et duo  **⟦candidate cut⟧** simulet ioachim nomine sedechiam constituit regem, accipiens abeo iusiurandum ut ei prouintiam custodiret et nihil ostiliter ageret nec faueret aegyptiis. Sedechias autem quidem annorumviginti et unum quando accepit regnum et nomen matris eius amias. Fuit contra iustitiam superbus circa quem impii locum maximam habere uidebantur qua propt

`latin-book10-num99`; `/TEI[1]/text[1]/body[1]/div1[1]/div2[7]/p[1]/num[1]/tail()`; node offset **788**, paragraph offset **788**, UTF-8 byte **31873** (zero-based, pinned LF bytes).

**Difficulty.** Greek opens with bringing captives to imprisonment. The immediate Latin first securely corresponds at simulet ioachim nomine sedechiam, compressing the appointment of the uncle.

**Recommended treatment.** Retain the surviving appointment counterpart and record a partial-prefix omission; do not mark all of 102 unavailable.

**Credible alternatives.** Display broader context without exact start; no supplied narrative.

**Decision requested.** Approve the partial-survival citation treatment.

### X.107 — decision required

Affected Latin: `latin-book10-num103`.

Printed authority: Niese, *Flavii Iosephi Opera* II (1885), **p. 353**, PDF **361**. [Full page image](evidence/print-collation/niese-II-pdf-361.jpg).
[Loeb VI, p.216, PDF232](evidence/print-collation/loeb-VI-followup-232.png) (independent control; Niese supplies numbering).

**Greek, earlier canonical cut with adjoining text:**

ς ἔσται, διεφώνησε δὲ Ἰεζεκίηλος εἰπὼν οὐκ ὄψεσθαι Βαβυλῶνα τὸν Σαχχίαν τοῦ Ἱερεμίου φάσκοντος αὐτῷ, ὅτι δεδεμένον αὐτὸν ὁ Βαβυλώνιος ἄξει βασιλεύς.   **⟦candidate cut⟧** καὶ διὰ τὸ μὴ ταὐτὸν αὐτοὺς ἑκατέρους λέγειν καὶ περὶ ὧν συμφωνεῖν ἐδόκουν ὡς οὐδ᾽ ἐκεῖνα ἀληθῆ λέγουσι καταγνούς: καίτοι πάντ᾽ αὐτῷ κατὰ τὰς προφητείας ἀπήντησεν, ἅπερ εὐκαιρότερον δηλώσομεν. Τὴν συμμαχίαν δὲ τὴν πρὸς τοὺς Βαβυλωνίους ἐπ᾽ ἔτη ὀκτὼ κατασχὼν διέλυσε τὰς πρὸς αὐτοὺς πίστεις καὶ τοῖς Αἰγυπτίοις προστίθεται καταλύσειν τοὺς Βα

**Latin, earlier candidate with adjoining text:**

in babylonia. Discordabat autem ezechiel dicens. Quia sedechias babyloniam non uideret cum hieremias dixisset quia uinctum eum rex babyloniae duceret  **⟦candidate cut⟧** eo quod idem uterque dixissent etiam illi quae non concordabant non esse uera dicebat, licet ei omnia secundum eorum euenirent prophetias quae tamen oportunius declarauimus. Interea dum hoc cognouisset babyloniae rex castra mouit aduersus eum et afflicta prouincia et monitiones eius una diripiens ad ipsam hierosolimorum ciuitatem obsedend

`latin-book10-num103`; `/TEI[1]/text[1]/body[1]/div1[1]/div2[7]/p[2]/cb[1]/tail()`; node offset **1258**, paragraph offset **1289**, UTF-8 byte **33394** (zero-based, pinned LF bytes).

**Difficulty.** Greek μὴ ταὐτόν says that the prophets did not agree; canonical Latin eo quod idem uterque lacks the corresponding negation. This is a textual difference, not permission to repair the transcription.

**Recommended treatment.** Retain the physical candidate and record the negation difference; preserve idem verbatim.

**Credible alternatives.** Withhold exact semantic equivalence while still providing a contextual citation locator.

**Decision requested.** Approve citation representation despite the recorded semantic difference.

### X.108 — decision required

Affected Latin: `latin-book10-num108` (see neighbouring extents and inherited-label discussion).

Printed authority: Niese, *Flavii Iosephi Opera* II (1885), **p. 353**, PDF **361**. [Full page image](evidence/print-collation/niese-II-pdf-361.jpg).
[Following page, p.354/PDF362](evidence/print-collation/niese-II-pdf-362.jpg).
[Loeb VI, p.216, PDF232](evidence/print-collation/loeb-VI-followup-232.png) (independent control; Niese supplies numbering).

**Greek, earlier canonical cut with adjoining text:**

ν καὶ περὶ ὧν συμφωνεῖν ἐδόκουν ὡς οὐδ᾽ ἐκεῖνα ἀληθῆ λέγουσι καταγνούς: καίτοι πάντ᾽ αὐτῷ κατὰ τὰς προφητείας ἀπήντησεν, ἅπερ εὐκαιρότερον δηλώσομεν.  **⟦candidate cut⟧** Τὴν συμμαχίαν δὲ τὴν πρὸς τοὺς Βαβυλωνίους ἐπ᾽ ἔτη ὀκτὼ κατασχὼν διέλυσε τὰς πρὸς αὐτοὺς πίστεις καὶ τοῖς Αἰγυπτίοις προστίθεται καταλύσειν τοὺς Βαβυλωνίους ἐλπίσας, αἳ μετ᾽ ἐκείνων ἐγένοντο.  μαθὼν δὲ τοῦτο ὁ τῶν Βαβυλωνίων βασιλεὺς ἐστράτευσεν ἐπ᾽ αὐτὸν καὶ τὴν χώραν κακώσας αὐτοῦ καὶ τὰ φρούρια λαβὼν ἐπ᾽ αὐτὴν ἧκε τὴν τῶν Ἱεροσολυμιτῶν

**Latin, earlier candidate with adjoining text:**

issent etiam illi quae non concordabant non esse uera dicebat, licet ei omnia secundum eorum euenirent prophetias quae tamen oportunius declarauimus.  **⟦candidate cut⟧** Interea dum hoc cognouisset babyloniae rex castra mouit aduersus eum et afflicta prouincia et monitiones eius una diripiens ad ipsam hierosolimorum ciuitatem obsedendam cum magno ueniebat exericitu. Rex autem aegyptius audiens quia sedechias amicus esset sumpta uirtute maxima bellatorum uenit ad iudeam quasi eius soluturus obscescionem. B

This displayed cut belongs to the following surviving section, not to the unavailable section. `latin-book10-num108`; `/TEI[1]/text[1]/body[1]/div1[1]/div2[8]/p[1]/num[1]/tail()`; node offset **1**, paragraph offset **1**, UTF-8 byte **33679** (zero-based, pinned LF bytes).

**Difficulty.** Niese pp.353–354 and Loeb p.216 attest the eight-year alliance, breach and transfer to the Egyptians. No counterpart was found in the canonical Latin passage or the whole-book search. The inherited [VII.iii.108] precedes the surviving siege narrative corresponding to 109. The missing counterpart is established for this transcription; its cause is not established by these printed witnesses or by a physical manuscript inspection.

**Recommended treatment.** Keep 108 unavailable with no supplied text or automatic gap. Preserve the later siege narrative and inherited label; a future data locator must prevent the textual label from creating a false 108 identity.

**Credible alternatives.** Hold the whole citation unavailable until a non-textual absence display is approved; do not label 109 as 108 or infer an omission cause.

**Decision requested.** Approve an unavailable 108 state and an independent 109 locator while retaining the inherited label.

### X.109 — decision required

Affected Latin: `latin-book10-num108`.

Printed authority: Niese, *Flavii Iosephi Opera* II (1885), **p. 354**, PDF **362**. [Full page image](evidence/print-collation/niese-II-pdf-362.jpg).
[Loeb VI, p.216, PDF232](evidence/print-collation/loeb-VI-followup-232.png) (independent control; Niese supplies numbering).

**Greek, earlier canonical cut with adjoining text:**

ἐπ᾽ ἔτη ὀκτὼ κατασχὼν διέλυσε τὰς πρὸς αὐτοὺς πίστεις καὶ τοῖς Αἰγυπτίοις προστίθεται καταλύσειν τοὺς Βαβυλωνίους ἐλπίσας, αἳ μετ᾽ ἐκείνων ἐγένοντο.   **⟦candidate cut⟧** μαθὼν δὲ τοῦτο ὁ τῶν Βαβυλωνίων βασιλεὺς ἐστράτευσεν ἐπ᾽ αὐτὸν καὶ τὴν χώραν κακώσας αὐτοῦ καὶ τὰ φρούρια λαβὼν ἐπ᾽ αὐτὴν ἧκε τὴν τῶν Ἱεροσολυμιτῶν πόλιν πολιορκήσων αὐτήν.  ὁ δ᾽ Αἰγύπτιος ἀκούσας ἐν οἷς ἐστιν ὁ σύμμαχος αὐτοῦ Σαχχίας ἀναλαβὼν πολλὴν δύναμιν ἧκεν εἰς τὴν Ἰουδαίαν ὡς λύσων τὴν πολιορκίαν. ὁ δὲ Βαβυλώνιος ἀφίσταται τῶν Ἱερο

**Latin, earlier candidate with adjoining text:**

issent etiam illi quae non concordabant non esse uera dicebat, licet ei omnia secundum eorum euenirent prophetias quae tamen oportunius declarauimus.  **⟦candidate cut⟧** Interea dum hoc cognouisset babyloniae rex castra mouit aduersus eum et afflicta prouincia et monitiones eius una diripiens ad ipsam hierosolimorum ciuitatem obsedendam cum magno ueniebat exericitu. Rex autem aegyptius audiens quia sedechias amicus esset sumpta uirtute maxima bellatorum uenit ad iudeam quasi eius soluturus obscescionem. B

`latin-book10-num108`; `/TEI[1]/text[1]/body[1]/div1[1]/div2[8]/p[1]/num[1]/tail()`; node offset **1**, paragraph offset **1**, UTF-8 byte **33679** (zero-based, pinned LF bytes).

**Difficulty.** Interea dum hoc cognouisset opens Latin pnum108 and securely corresponds to Greek 109, not 108. The printed 109 line contains the end of the absent alliance paragraph followed by μαθὼν δὲ τοῦτο, the new siege narrative.

**Recommended treatment.** Retain the 109 candidate at the existing narrative start. Preserve [VII.iii.108] and paragraph identity; an eventual citation registry override must replace its executable citation claim without changing its visible text.

**Credible alternatives.** Keep Niese disabled until the reader supports this data distinction.

**Decision requested.** Approve the displaced-label representation jointly with 108.

### X.150 — decision required

Affected Latin: `latin-book10-num151`.

Printed authority: Niese, *Flavii Iosephi Opera* II (1885), **p. 362**, PDF **370**. [Full page image](evidence/print-collation/niese-II-pdf-370.jpg).
[Loeb VI, p.240, PDF256](evidence/print-collation/loeb-VI-followup-256.png) (independent control; Niese supplies numbering).

**Greek, earlier canonical cut with adjoining text:**

πτὰ καὶ τὸν γραμματέα αὐτοῦ καὶ ἄλλους ἡγεμόνας ἑξήκοντα, οὓς ἅπαντας μεθ᾽ ὧν ἐσύλησε σκευῶν ἐκόμισε πρὸς τὸν βασιλέα εἰς Σαλάβαθα πόλιν τῆς Συρίας.   **⟦candidate cut⟧** ὁ δὲ βασιλεὺς τοῦ μὲν ἀρχιερέως καὶ τῶν ἡγεμόνων ἐκέλευσεν ἐκεῖ τὰς κεφαλὰς ἀποτεμεῖν, αὐτὸς δὲ πάντας τοὺς αἰχμαλώτους καὶ τὸν Σαχχίαν εἰς Βαβυλῶνα δέσμιον ἐπήγετο καὶ Ἰωσάδακον τὸν ἀρχιερέα ὄντα υἱὸν Σαραία τοῦ ἀρχιερέως, ὃν ἀπέκτεινεν ὁ Βαβυλώνιος ἐν Ἀριβαθᾶ πόλει τῆς Συρίας, ὡς καὶ πρότερον ἡμῖν δεδήλωται. Ἐπεὶ δὲ τὸ γένος διεξήλθομεν

**Latin, earlier candidate with adjoining text:**

cribam eius et alios principes saxaginta sexaginta quos omnes cum uasis quae depredatus est deduxit ad regem in arabatha prouintiae syriae ciuitatem.  **⟦candidate cut⟧** Rex autem pontifices quidem et principum ubi capita iussit abscidi. Ipse uero omnes captiuos et sedechiam deduxit in babyloniam. Uinctum uero circum egit et iosadach pontifices filium sareae pontificis quaem occidit babylonius in arabatha syriae ciuitatem sicut dudum iam designatum est. Igitur quia genus explanauimus, et qui fuerunt et eo

`latin-book10-num151`; `/TEI[1]/text[1]/body[1]/div1[1]/div2[8]/p[10]/num[1]/tail()`; node offset **1**, paragraph offset **1**, UTF-8 byte **46130** (zero-based, pinned LF bytes).

**Difficulty.** Greek 150 starts in the final portion of Greek pnum144, but Rex autem pontifices opens Latin pnum151 under [VIII.vi.151]. A paragraph-number or sameAs-only window would lose the real counterpart.

**Recommended treatment.** Use Rex autem pontifices as the 150 locator across the existing paragraph boundary; preserve all IDs, sameAs and chapter structure.

**Credible alternatives.** Keep Niese unavailable until certified locators handle the displacement.

**Decision requested.** Approve the 150 locator and suppression of the false inherited 151 start jointly with 151.

### X.151 — decision required

Affected Latin: `latin-book10-num151`.

Printed authority: Niese, *Flavii Iosephi Opera* II (1885), **p. 362**, PDF **370**. [Full page image](evidence/print-collation/niese-II-pdf-370.jpg).
[Loeb VI, p.240, PDF256](evidence/print-collation/loeb-VI-followup-256.png) (independent control; Niese supplies numbering).

**Greek, earlier canonical cut with adjoining text:**

το καὶ Ἰωσάδακον τὸν ἀρχιερέα ὄντα υἱὸν Σαραία τοῦ ἀρχιερέως, ὃν ἀπέκτεινεν ὁ Βαβυλώνιος ἐν Ἀριβαθᾶ πόλει τῆς Συρίας, ὡς καὶ πρότερον ἡμῖν δεδήλωται.  **⟦candidate cut⟧** Ἐπεὶ δὲ τὸ γένος διεξήλθομεν τὸ τῶν βασιλέων καὶ τίνες ἦσαν δεδηλώκαμεν καὶ τοὺς χρόνους αὐτῶν, ἀναγκαῖον ἡγησάμην καὶ τῶν ἀρχιερέων εἰπεῖν τὰ ὀνόματα καὶ τίνες ἦσαν οἱ τὴν ἀρχιερωσύνην καταδείξαντες ἐπὶ τοῖς βασιλεῦσι.  πρῶτος μὲν οὖν Σάδωκος ἀρχιερεὺς ἐγένετο τοῦ ναοῦ, ὃν Σολόμων ᾠκοδόμησε: μετ᾽ αὐτὸν δ᾽ ὁ υἱὸς Ἀχιμᾶς διαδέχεται τὴν τιμ

**Latin, earlier candidate with adjoining text:**

ero circum egit et iosadach pontifices filium sareae pontificis quaem occidit babylonius in arabatha syriae ciuitatem sicut dudum iam designatum est.  **⟦candidate cut⟧** Igitur quia genus explanauimus, et qui fuerunt et eorum tempora cuncta narrauimus. Necessarium uidi caui etiam nomina reserare pontificum qui pontificatum regum temporibus habuerunt. Primus siquidem sadoch pontifex templi quod salomon eadificauit. Post eum uero filius achimaas in eius honore successit. Post achimam zacharias. Post autem i

`latin-book10-num151`; `/TEI[1]/text[1]/body[1]/div1[1]/div2[8]/p[10]/num[1]/tail()`; node offset **289**, paragraph offset **289**, UTF-8 byte **46418** (zero-based, pinned LF bytes).

**Difficulty.** Niese p.362 and Loeb p.240 start 151 at Ἐπεὶ δὲ τὸ γένος, securely corresponding to Igitur quia genus explanauimus inside Latin pnum151. The inherited label at the beginning of that paragraph belongs physically to 150.

**Recommended treatment.** Retain the secure internal 151 candidate and the literal inherited label. A data-level override must keep the label from creating an earlier false 151 identity.

**Credible alternatives.** Keep Niese disabled until independently certified locators are supported.

**Decision requested.** Approve the non-textual override and internal locator jointly with 150.

### X.213 — decision required

Affected Latin: `latin-book10-num211`.

Printed authority: Niese, *Flavii Iosephi Opera* II (1885), **p. 376**, PDF **384**. [Full page image](evidence/print-collation/niese-II-pdf-384.jpg).

**Greek, earlier canonical cut with adjoining text:**

 βασιλείας ἐποίησε καὶ τοὺς συγγενεῖς αὐτοῦ, οὓς ὑπὸ φθόνου καὶ βασκανίας εἰς κίνδυνον ἐμπεσεῖν συνέβη τῷ βασιλεῖ προσκρούσαντας ἐξ αἰτίας τοιαύτης:   **⟦candidate cut⟧** ὁ βασιλεὺς κατασκευάσας χρύσεον ἀνδριάντα πηχῶν τὸ μὲν ὕψος ἑξήκοντα τὸ πλάτος δὲ ἕξ, στήσας αὐτὸν ἐν τῷ μεγάλῳ τῆς Βαβυλῶνος πεδίῳ καὶ μέλλων καθιεροῦν αὐτὸν συνεκάλεσεν ἐξ ἁπάσης ἧς ἦρχε γῆς τοὺς πρώτους πρῶτον αὐτοῖς προστάξας, ὅταν σημαινούσης ἀκούσωσι τῆς σάλπιγγος, τότε πεσόντας προσκυνεῖν τὸν ἀνδριάντα: τοὺς δὲ μὴ ποιήσαντας ἠπείλη

**Latin, earlier candidate with adjoining text:**

tipuit ingenium danihelis et procidens in faciem eo modo quo deus adoratur eum salutauit daniel ei que sacrificari quasi deo praecepit. Cui etiam rea  **⟦candidate cut⟧** rex dum fecisset statuam auream altitudine sexaginta cubitorum latitudine sex et eam statuisset in maximo babyloniae campo decicaturus eam conuocauit terrae cui praeerat preerat. Principes uniuersas eis primo praecipiens ut dum audirent tubae sonum prostrati statuam pariter adorarent. Qui uero hoc non facerent eos in igni caminum intermin

`latin-book10-num211`; `/TEI[1]/text[1]/body[1]/div1[1]/div2[10]/p[5]/num[1]/tail()`; node offset **218**, paragraph offset **218**, UTF-8 byte **65708** (zero-based, pinned LF bytes).

**Difficulty.** Between 212’s instruction to sacrifice and the statue narrative, Latin retains the broken transition Cui etiam rea. Greek 213 begins the king’s construction of the golden statue; rex dum fecisset is secure narrative correspondence but allocation of the broken words is uncertain.

**Recommended treatment.** Prefer rex dum fecisset as the cut, leaving Cui etiam rea in the preceding extent and documenting the damaged transition.

**Credible alternatives.** Begin at Cui etiam rea and explicitly mark uncertain scope; do not complete or delete the words.

**Decision requested.** Choose which side of the cut retains Cui etiam rea.

### X.248 — decision required

Affected Latin: `latin-book10-num245`.

Printed authority: Niese, *Flavii Iosephi Opera* II (1885), **p. 384**, PDF **392**. [Full page image](evidence/print-collation/niese-II-pdf-392.jpg).

**Greek, earlier canonical cut with adjoining text:**

ερσῶν βασιλέως ἐπ᾽ αὐτὸν στρατεύσαντος: Βαλτάσαρος γάρ ἐστιν, ἐφ᾽ οὗ τὴν αἵρεσιν τῆς Βαβυλῶνος συνέβη γενέσθαι, βασιλεύσαντος αὐτοῦ ἑπτακαίδεκα ἔτη.   **⟦candidate cut⟧** τῶν μὲν οὖν Ναβουχοδονοσόρου τοῦ βασιλέως ἐγγόνων τὸ τέλος τοιοῦτον παρειλήφαμεν γενόμενον: Δαρείῳ δὲ τῷ καταλύσαντι τὴν Βαβυλωνίων ἡγεμονίαν μετὰ Κύρου τοῦ συγγενοῦς ἔτος ἦν ἑξηκοστὸν καὶ δεύτερον, ὅτε τὴν Βαβυλῶνα εἷλεν, ὃς ἦν Ἀστυάγους υἱός, ἕτερον δὲ παρὰ τοῖς Ἕλλησιν ἐκαλεῖτο ὄνομα:  ὃς καὶ Δανίηλον τὸν προφήτην λαβὼν ἤγαγεν εἰς Μηδί

**Latin, earlier candidate with adjoining text:**

itas cyro persarum rege aduersus eum fortissime dimicantem. Balthasar enim his sub quo capi contigit babyloniam cum regnasset iam decem et octo annis  **⟦candidate cut⟧** nepus nepos nabucodonosor regis cui talem terminum fuisse percipimUs. Darius autem astiagis filius quia babyloniorum principatum destruixit cum cyro cognato suo annum habebat sexagesimum et secundum cum babylon fuisset in uasta qui tamen alio nomine uocabatur a graecis quique danihelem prophetam sumens ad se in mediam duxit et omni eum ho

`latin-book10-num245`; `/TEI[1]/text[1]/body[1]/div1[1]/div2[10]/p[10]/cb[1]/tail()`; node offset **63**, paragraph offset **634**, UTF-8 byte **76635** (zero-based, pinned LF bytes).

**Difficulty.** Greek 248 starts the summary of Nebuchadnezzar’s descendants. Latin nepus nepos nabucodonosor regis is attached to the preceding regnal sentence, before cui talem terminum; the first counterpart therefore crosses the sentence logic.

**Recommended treatment.** Prefer nepus nepos as the first counterpart, preserving the repeated forms and Latin order. Document that this is not a shared syntactic sentence boundary.

**Credible alternatives.** Begin at cui talem terminum, explicitly assigning the earlier genealogical counterpart to 247; or withhold an exact locator.

**Decision requested.** Choose the earliest genealogical counterpart or an explicitly approximate later cut.

## Displaced inherited labels and future representation

An eventual implementation must preserve every visible composite `<num>` label, existing xml:id, sameAs, paragraph and traditional chapter/subchapter division. Certified citation locators would separately define executable Niese starts and suppress displaced inherited numeric claims. The current reader scans labels and milestones, so inserting a new milestone alone would leave duplicate/false identities. A future data-driven locator/override facility and full rendering QA are prerequisites. No such production change is included here.

The candidate dry-run and arithmetic in the checkpoint are mechanical evidence only. They must be recomputed if a proposed Greek/Latin cut or the VIII.367 representation is accepted. No candidate plan is authorized for application.
