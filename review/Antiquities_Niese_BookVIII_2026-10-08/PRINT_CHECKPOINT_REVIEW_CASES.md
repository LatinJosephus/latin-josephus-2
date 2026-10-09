# Book VIII: editorial decisions after printed collation

**NO-GO. Candidate audit only; implementation is not approved. No human decisions have been supplied.**

All 420 citation starts were checked against the supplied Niese body images. The routine page-reading queue is complete. VIII.110, VIII.172 and VIII.368 retain the specific word-precision obstacles described below.

The historical EXACT / INTERNAL-BUT-EXACT / REQUIRES_ADJUDICATION / UNAVAILABLE classifications and confidence values are unchanged. Greek print verification alone does not certify a Latin cut. Routine Latin candidates still needing individual verification are counted separately from the decisions here. The earlier register and case packet remain recoverable in checkpoint commit `cc86a1d3ef3626a04b44032b9c8fc60293a44bff`.

Human decision records: **18**, sections 59, 83, 87, 97, 110, 167, 172, 187, 224, 245, 255, 334, 353, 367, 368, 369, 408, 409. Resolved source cases: 256, 314, 376, 377. Paired sections should be decided jointly.

Every context below reproduces canonical text. The symbol ⟦candidate cut⟧ is editorial display only, never inserted into XML. Text-node offsets and UTF-8 bytes refer to the pinned LF worktree inputs; canonical CRLF hashes remain separately recorded in BASELINE.json.

## Concise decision list

| Section | Exact judgement requested |
|---|---|
| VIII.59 | Accept or reject the proposed paired relocation of 59; no source edit is authorized. |
| VIII.83 | Choose the dimensional phrase or the later admiration phrase; decide how much of the prefix is demonstrably absent. |
| VIII.87 | Choose the embedded first counterpart or an explicitly approximate larger locator. |
| VIII.97 | Approve the cut before mirabilis while preserving the broken wording. |
| VIII.110 | Choose the Greek word boundary and corresponding Latin extent for 109–110. |
| VIII.167 | Approve the first surviving gifts phrase as a partial counterpart. |
| VIII.172 | Choose the comparative or explanatory word boundary and its Latin extent. |
| VIII.187 | Choose maxima[s] res omni or omni prouidentia, and approve a data-level override of the inherited citation claim. |
| VIII.224 | Approve potius quidem narrabo despite the reordered framing. |
| VIII.245 | Accept or reject the proposed paired relocation of 245; no XML edit is authorized. |
| VIII.255 | Approve the representation policy preserving the inherited label while using the internal 255 locator. |
| VIII.334 | Approve the partial-correspondence treatment or withhold the exact citation locator. |
| VIII.353 | Accept or reject the proposed paired relocation of 353. |
| VIII.367 | Decide jointly with 368 between unavailable 367 and partial-survival 367; authorize no textual supplementation. |
| VIII.368 | Choose the section-368 word boundary and the dependent 367 representation. |
| VIII.369 | Choose the first or second repeated phrase as the physical 369 start. |
| VIII.408 | Approve the narrow accusation cut or explicitly broader context. |
| VIII.409 | Accept or reject the proposed paired relocation of 409. |

## Verification work states

| State | Records |
|---|---:|
| GREEK_VERIFIED_WITH_SECURE_LATIN_COUNTERPART | 85 |
| GREEK_COLLATED_LATIN_CANDIDATE_AWAITING_INDIVIDUAL_VERIFICATION | 317 |
| GREEK_COLLATED_LATIN_OR_REPRESENTATION_EDITORIAL_DECISION | 14 |
| GREEK_START_AWAITING_WORD_LEVEL_SOURCE_DECISION | 3 |
| ABSENCE_OR_SOURCE_ANOMALY_REQUIRES_REPRESENTATION_DECISION | 1 |

## Placement against retained confidence classifications

| Placement | EXACT | INTERNAL-BUT-EXACT | REQUIRES_ADJUDICATION | UNAVAILABLE | Total |
|---|---:|---:|---:|---:|---:|
| INHERITED_START | 81 | 0 | 2 | 0 | 83 |
| PROPOSED_INTERNAL_MILESTONE | 0 | 1 | 335 | 0 | 336 |
| NO_LATIN_START | 0 | 0 | 0 | 1 | 1 |

These are candidate placement counts, not inserted markers or certified availability. The historical unavailable record for VIII.367 is conditional on the VIII.368 decision; its surviving tail must not be discarded.

| Placement | HIGH | PENDING_EDITORIAL_VERIFICATION | HIGH_ABSENCE_IN_THIS_TRANSCRIPTION |
|---|---:|---:|---:|
| INHERITED_START | 81 | 2 | 0 |
| PROPOSED_INTERNAL_MILESTONE | 1 | 335 | 0 |
| NO_LATIN_START | 0 | 0 | 1 |

## Decisions and resolved source cases

### VIII.59 — decision required

Affected Latin: `latin-book08-num57`.

Printed authority: Niese, *Flavii Iosephi Opera* II (1885), **p. 189**, PDF **197**. [Full page image](evidence/print-collation/niese-II-pdf-197.jpg).
[Loeb V, p.600, PDF608](evidence/print-collation/loeb-V-followup-608.png) (independent control; Niese supplies numbering).

**Greek, earlier canonical cut with adjoining text:**

ετῶς: μυρίους γὰρ ἐποίησε κόπτοντας ἐπὶ μῆνα ἕνα ἐν Λιβάνῳ ὄρει δύο μῆνας ἀναπαύεσθαι παραγινομένους ἐπὶ τὰ οἰκεῖα, μέχρις οὗ πάλιν οἱ δισμύριοι τὴν   **⟦candidate cut⟧** ἐργασίαν ἀναπληρώσωσι κατὰ τὸν ὡρισμένον χρόνον ἔπειθ᾽ οὕτως συνέβαινε τοῖς πρώτοις μυρίοις διὰ τετάρτου μηνὸς ἀπαντᾶν ἐπὶ τὸ ἔργον. ἐγεγόνει δ᾽ ἐπίτροπος τοῦ φόρου τούτου Ἀδώραμος. ἦσαν δ᾽ ἐκ τῶν παροίκων οὓς Δαυίδης καταλελοίπει τῶν μὲν παρακομιζόντων τὴν λιθίαν καὶ τὴν ἄλλην ὕλην ἑπτὰ μυριάδες, τῶν δὲ λατομούντων ὀκτάκις μύριοι, τούτων

**Latin, earlier candidate with adjoining text:**

lia enim fecit incidere uno mense in libano monte: ut duobus mensibus remeantes ad propria requiescerent. Donec igitur uiginti milia definito tempore  **⟦candidate cut⟧** suum opus implerent. Ita contingebant quarto mense priores ad laborem denuo remearent. Super hos enim laboratores scrutator institutus adoram. Erant autem ex his quos reliquerat dauid ad portandos lapides aliamque materiam septuaginta milia uiri et eorum qui lapides incidebant octoaginta milia et eorum praepositi tria milia trecenti ueloc

`latin-book08-num57`; `/TEI[1]/text[1]/body[1]/div1[1]/div2[3]/p[9]/num[1]/tail()`; node offset **714**, paragraph offset **714**, UTF-8 byte **19159** (zero-based, pinned LF bytes).

**Reassessed proposal / alternative, not applied:**

 ἐν Λιβάνῳ ὄρει δύο μῆνας ἀναπαύεσθαι παραγινομένους ἐπὶ τὰ οἰκεῖα, μέχρις οὗ πάλιν οἱ δισμύριοι τὴν  ἐργασίαν ἀναπληρώσωσι κατὰ τὸν ὡρισμένον χρόνον  **⟦candidate cut⟧** ἔπειθ᾽ οὕτως συνέβαινε τοῖς πρώτοις μυρίοις διὰ τετάρτου μηνὸς ἀπαντᾶν ἐπὶ τὸ ἔργον. ἐγεγόνει δ᾽ ἐπίτροπος τοῦ φόρου τούτου Ἀδώραμος. ἦσαν δ᾽ ἐκ τῶν παροίκων οὓς Δαυίδης καταλελοίπει τῶν μὲν παρακομιζόντων τὴν λιθίαν καὶ τὴν ἄλλην ὕλην ἑπτὰ μυριάδες, τῶν δὲ λατομούντων ὀκτάκις μύριοι, τούτων δ᾽ ἐπιστάται τρισχίλιοι καὶ τριακόσιοι.  προστε

re uno mense in libano monte: ut duobus mensibus remeantes ad propria requiescerent. Donec igitur uiginti milia definito tempore suum opus implerent.  **⟦candidate cut⟧** Ita contingebant quarto mense priores ad laborem denuo remearent. Super hos enim laboratores scrutator institutus adoram. Erant autem ex his quos reliquerat dauid ad portandos lapides aliamque materiam septuaginta milia uiri et eorum qui lapides incidebant octoaginta milia et eorum praepositi tria milia trecenti uelociterque secabant lapi

`latin-book08-num57`; `/TEI[1]/text[1]/body[1]/div1[1]/div2[3]/p[9]/num[1]/tail()`; node offset **735**, paragraph offset **735**, UTF-8 byte **19180** (zero-based, pinned LF bytes).

Neighbouring extent change: 58 ends at the proposed cut instead of the old cut; 59 begins there and still ends at 60. Exact before/after offsets are in the boundary reassessment and DECISION_HISTORY.json.

**Difficulty.** Canonical Greek starts at ἐργασίαν inside the work-completion clause. Niese p.189 puts 59 on that line beside the new ἔπειθ᾽ οὕτως clause; Loeb p.600 places 59 on its line containing ὡρισμένον χρόνον and ἔπειθ᾽ οὕτως. The combined syntactic evidence supports the next rotation clause, rather than the earlier noun.

**Recommended treatment.** Propose Greek ἔπειθ᾽ οὕτως and Latin Ita contingebant. The previous work-completion words, including suum opus implerent, remain in the proposed 58 extent.

**Credible alternatives.** Retain canonical ἐργασίαν / suum opus implerent if the first word of Niese’s marked line is controlling; the old Donec igitur alternative is broader still.

**Decision requested.** Accept or reject the proposed paired relocation of 59; no source edit is authorized.

### VIII.83 — decision required

Affected Latin: `latin-book08-num81`.

Printed authority: Niese, *Flavii Iosephi Opera* II (1885), **p. 194**, PDF **202**. [Full page image](evidence/print-collation/niese-II-pdf-202.jpg).

**Greek, earlier canonical cut with adjoining text:**

ιν κατεσκευασμένος, ἐφ᾽ οἷς ἐτετόρευτο πῇ μὲν λέων πῇ δὲ ταῦρος καὶ ἀετός, ἐπὶ δὲ τῶν κιονίσκων ὁμοίως ἐξείργαστο τοῖς κατὰ τὰ πλευρὰ τετορευμένοις.   **⟦candidate cut⟧** τὸ δὲ πᾶν ἔργον ἐπὶ τεσσάρων αἰωρούμενον τροχῶν εἱστήκει. χωνευτοὶ δ᾽ ἦσαν οὗτοι πλήμνας καὶ ἄντυγας πήχεως καὶ ἡμίσους ἔχοντες τὴν διάμετρον. ἐθαύμασεν ἄν τις τὰς ἀψῖδας τῶν τροχῶν θεασάμενος, ὅπως συντετορευμέναι καὶ τοῖς πλευροῖς τῶν βάσεων προσηνωμέναι ἁρμονίως ταῖς ἄντυξιν ἐνέκειντο: ἦσαν δ᾽ ὅμως οὕτως ἔχουσαι.  τὰς δὲ γωνίας ἄνωθεν 

**Latin, earlier candidate with adjoining text:**

t in colomellis similiter per latera erant huiusmodi caelaturae quasi crispantibus peculis factae quarum altitudo fuit cubiti unius et dimidii erant:  **⟦candidate cut⟧** mirum uide orbis rotarum quem admodum erant caelate et basium iunctae lateribus. Angulos uero superiores concludebant humeris expensis utique manibus animalium super quas redebat fundus canthari reclinatus, id est incumbens super manus aquile et leonis quod erat ista sibimet coaptatum ut naturaliter insertum quod ammodo uideretur. Inter i

`latin-book08-num81`; `/TEI[1]/text[1]/body[1]/div1[1]/div2[4]/p[6]/num[1]/tail()`; node offset **559**, paragraph offset **559**, UTF-8 byte **27049** (zero-based, pinned LF bytes).

**Reassessed proposal / alternative, not applied:**

ιν κατεσκευασμένος, ἐφ᾽ οἷς ἐτετόρευτο πῇ μὲν λέων πῇ δὲ ταῦρος καὶ ἀετός, ἐπὶ δὲ τῶν κιονίσκων ὁμοίως ἐξείργαστο τοῖς κατὰ τὰ πλευρὰ τετορευμένοις.   **⟦candidate cut⟧** τὸ δὲ πᾶν ἔργον ἐπὶ τεσσάρων αἰωρούμενον τροχῶν εἱστήκει. χωνευτοὶ δ᾽ ἦσαν οὗτοι πλήμνας καὶ ἄντυγας πήχεως καὶ ἡμίσους ἔχοντες τὴν διάμετρον. ἐθαύμασεν ἄν τις τὰς ἀψῖδας τῶν τροχῶν θεασάμενος, ὅπως συντετορευμέναι καὶ τοῖς πλευροῖς τῶν βάσεων προσηνωμέναι ἁρμονίως ταῖς ἄντυξιν ἐνέκειντο: ἦσαν δ᾽ ὅμως οὕτως ἔχουσαι.  τὰς δὲ γωνίας ἄνωθεν 

s, id est alibi erat leo alibiturus, alibi aquila. Et in colomellis similiter per latera erant huiusmodi caelaturae quasi crispantibus peculis factae  **⟦candidate cut⟧** quarum altitudo fuit cubiti unius et dimidii erant: mirum uide orbis rotarum quem admodum erant caelate et basium iunctae lateribus. Angulos uero superiores concludebant humeris expensis utique manibus animalium super quas redebat fundus canthari reclinatus, id est incumbens super manus aquile et leonis quod erat ista sibimet coaptatum ut

`latin-book08-num81`; `/TEI[1]/text[1]/body[1]/div1[1]/div2[4]/p[6]/num[1]/tail()`; node offset **507**, paragraph offset **507**, UTF-8 byte **26997** (zero-based, pinned LF bytes).

Neighbouring extent change: 82 ends at the proposed cut instead of the old cut; 83 begins there and still ends at 84. Exact before/after offsets are in the boundary reassessment and DECISION_HISTORY.json.

**Difficulty.** The Greek opening describes wheels, casting, hubs and a cubit-and-a-half diameter. The earlier audit treated mirum uide orbis rotarum as the first surviving counterpart, but the preceding Latin quarum altitudo fuit cubiti unius et dimidii plausibly preserves the dimensional detail already inside 83. The surrounding quasi crispantibus peculis factae is corrupt/unclear. Thus a wholly absent prefix before mirum is not established.

**Recommended treatment.** Prefer a reassessed candidate at quarum altitudo fuit as the earliest securely recognisable dimensional counterpart, documenting the imperfect height/diameter correspondence and uncertain preceding wording. Preserve the earlier mirum proposal in history.

**Credible alternatives.** Retain mirum uide orbis rotarum as a later certain counterpart; consider quasi crispantibus peculis only after an editorial interpretation of the damaged wording.

**Decision requested.** Choose the dimensional phrase or the later admiration phrase; decide how much of the prefix is demonstrably absent.

### VIII.87 — decision required

Affected Latin: `latin-book08-num81`.

Printed authority: Niese, *Flavii Iosephi Opera* II (1885), **p. 195**, PDF **203**. [Full page image](evidence/print-collation/niese-II-pdf-203.jpg).

**Greek, earlier canonical cut with adjoining text:**

 ναοῦ, τέτραπτο δὲ τοῦτο κατὰ βορέαν ἄνεμον, καὶ τοσούτους ἐκ τοῦ δεξιοῦ πρὸς νότον ἀφορῶντας εἰς τὴν ἀνατολήν: κατὰ δ᾽ αὐτὸ καὶ τὴν θάλασσαν ἔθηκε.   **⟦candidate cut⟧** πληρώσας δὲ ὕδατος τὴν μὲν θάλασσαν ἀπέδειξεν εἰς τὸ νίπτειν τοὺς εἰς τὸν ναὸν εἰσιόντας ἱερεῖς ἐν αὐτῇ τὰς χεῖρας καὶ τοὺς πόδας μέλλοντας ἀναβαίνειν ἐπὶ τὸν βωμόν, τοὺς δὲ λουτῆρας εἰς τὸ καθαίρειν τὰ ἐντὸς τῶν ὁλοκαυτουμένων ζῴων καὶ τοὺς πόδας αὐτῶν. Κατεσκεύασε δὲ καὶ θυσιαστήριον χάλκεον εἴκοσι πηχῶν τὸ μῆκος καὶ τοσούτων τὸ εὖρος τ

**Latin, earlier candidate with adjoining text:**

ens a parte sinistre templi quae erant ad aquilonem, et totidem a latere destro ad austri partem respicientes ad orientem. Quod etiam mare constituit  **⟦candidate cut⟧** aqua plenum deseruitque mare, ut ingredientes sacerdotes templum ineo lauarent manus et pedes ascensuri scilicet ad altare. Cantharos ad animalium in terranea diluenda simul et pedes eorum quae erant holocaustis inponenda. Fecit autem et altare aereum cubitorum uiginti longitudinem, et totidem latitudinem. Altitudinem uero decem ad holoca

`latin-book08-num81`; `/TEI[1]/text[1]/body[1]/div1[1]/div2[4]/p[6]/num[1]/tail()`; node offset **1419**, paragraph offset **1419**, UTF-8 byte **27909** (zero-based, pinned LF bytes).

**Difficulty.** Greek πληρώσας δὲ ὕδατος is compressed into the embedded Latin aqua plenum before deseruitque mare. A convenient sentence cut would omit that first counterpart.

**Recommended treatment.** Retain aqua plenum as a partial syntactic cut; preserve Latin order.

**Credible alternatives.** Begin at deseruitque mare with an explicit approximation warning, or withhold exact correspondence.

**Decision requested.** Choose the embedded first counterpart or an explicitly approximate larger locator.

### VIII.97 — decision required

Affected Latin: `latin-book08-num95`.

Printed authority: Niese, *Flavii Iosephi Opera* II (1885), **p. 197**, PDF **205**. [Full page image](evidence/print-collation/niese-II-pdf-205.jpg).

**Greek, earlier canonical cut with adjoining text:**

τη πρὸς ἕκαστον τῶν ἀνέμων τέτραπτο χρυσέαις κλειομένη θύραις. εἰς τοῦτο τοῦ λαοῦ πάντες οἱ διαφέροντες ἁγνείᾳ καὶ παρατηρήσει τῶν νομίμων εἰσῄεσαν.   **⟦candidate cut⟧** θαυμαστὸν δὲ καὶ λόγου παντὸς ἀπέφηνε μεῖζον, ὡς δὲ εἰπεῖν καὶ τῆς ὄψεως, τὸ τούτων ἔξωθεν ἱερόν: μεγάλας γὰρ ἐγχώσας φάραγγας, ἃς διὰ βάθος ἄπειρον οὐδὲ ἀπόνως ἐννεύσαντας ἦν ἰδεῖν, καὶ ἀναβιβάσας εἰς τετρακοσίους πήχεις τὸ ὕψος ἰσοπέδους τῇ κορυφῇ τοῦ ὄρους ἐφ᾽ ἧς ὁ ναὸς ᾠκοδόμητο κατεσκεύασε: καὶ διὰ τοῦτο ὕπαιθρον ὂν τὸ ἔξωθεν ἱερὸν ἴ

**Latin, earlier candidate with adjoining text:**

 attendebant ubi aureas ianuas collocabit. In hoc ergo sacrario omnis populus quibus purgatio et obseruatio legitimorum in erant. Introibant siquidem  **⟦candidate cut⟧** mirabilis et omnem praecipua fuit et seditio, potest etiam contemplationem uisionis ipsius excedebat aula quae fortis erat. Magnis enim effodiens profunditates qua propter infinitam celsitudinem non poterat aliquis sine terrore conspicere. Et erigens fabricas in quadri[n]gentis cubitis earum altitudinem aequales eas uertici montis in quo 

`latin-book08-num95`; `/TEI[1]/text[1]/body[1]/div1[1]/div2[4]/p[9]/num[1]/tail()`; node offset **839**, paragraph offset **839**, UTF-8 byte **31279** (zero-based, pinned LF bytes).

**Difficulty.** The Latin Introibant belongs to the earlier entry-description; mirabilis renders the new Greek θαυμαστόν, in damaged surrounding syntax.

**Recommended treatment.** Retain mirabilis as the first corresponding word. Keep Introibant siquidem in the preceding extent.

**Credible alternatives.** Begin at Introibant siquidem with overlap in subject matter, or defer the cut because of the corrupt syntax.

**Decision requested.** Approve the cut before mirabilis while preserving the broken wording.

### VIII.110 — decision required

Affected Latin: `latin-book08-num106`.

Printed authority: Niese, *Flavii Iosephi Opera* II (1885), **p. 200**, PDF **208**. [Full page image](evidence/print-collation/niese-II-pdf-208.jpg).
[Loeb V, p.630, PDF638](evidence/print-collation/loeb-V-followup-638.png) (independent control; Niese supplies numbering).

**Greek, earlier canonical cut with adjoining text:**

πατρὶ περὶ τῶν μελλόντων ἅπαντα καθὼς ἀποβέβηκεν ἤδη τὰ πολλὰ καὶ γενήσεται τὰ λείποντα δηλώσειε, καὶ ὡς αὐτὸς ἐπιθείη τὸ ὄνομα μήπω γεγεννημένῳ καὶ   **⟦candidate cut⟧** τίς μέλλοι καλεῖσθαι προείποι καὶ ὅτι τὸν ναὸν οὗτος οἰκοδομήσει αὐτῷ βασιλεὺς μετὰ τὴν τοῦ πατρὸς τελευτὴν γενόμενος: ἃ βλέποντας κατὰ τὴν ἐκείνου προφητείαν ἐπιτελῆ τὸν θεὸν εὐλογεῖν ἠξίου καὶ περὶ μηδενὸς ἀπογινώσκειν ὧν ὑπέσχηται πρὸς εὐδαιμονίαν ὡς οὐκ ἐσομένου πιστεύοντας ἐκ τῶν ἤδη βλεπομένων. Ταῦτα διαλεχθεὶς πρὸς τὸν ὄχλον ὁ βασι

**Latin, earlier candidate with adjoining text:**

prouidentiam eius quod dauid eius patri omnia futura sicut iam multa prouenerant et forent uentura reliqua praedixisset quod ipse quoque non dum nato  **⟦candidate cut⟧** imposuit ei nomen, et quod templum ipse aedificaturus est primus post patris obitum regnaturus. Et cum omnia secundum illius fierent prophetiam supplicabat ut deo benedicerent uniuersi, et in nullo eius promissionibus disperarent quas pro eoque felicitate praedixerat, sed crederent haec implenda quae fuerant iam transacta. Cumque haec dix

`latin-book08-num106`; `/TEI[1]/text[1]/body[1]/div1[1]/div2[5]/p[2]/pb[1]/tail()`; node offset **1183**, paragraph offset **1300**, UTF-8 byte **35722** (zero-based, pinned LF bytes).

**Reassessed proposal / alternative, not applied:**

 τὴν δύναμιν αὐτοῖς καὶ τὴν πρόνοιαν, ὅτι Δαυίδῃ τῷ πατρὶ περὶ τῶν μελλόντων ἅπαντα καθὼς ἀποβέβηκεν ἤδη τὰ πολλὰ καὶ γενήσεται τὰ λείποντα δηλώσειε,  **⟦candidate cut⟧** καὶ ὡς αὐτὸς ἐπιθείη τὸ ὄνομα μήπω γεγεννημένῳ καὶ  τίς μέλλοι καλεῖσθαι προείποι καὶ ὅτι τὸν ναὸν οὗτος οἰκοδομήσει αὐτῷ βασιλεὺς μετὰ τὴν τοῦ πατρὸς τελευτὴν γενόμενος: ἃ βλέποντας κατὰ τὴν ἐκείνου προφητείαν ἐπιτελῆ τὸν θεὸν εὐλογεῖν ἠξίου καὶ περὶ μηδενὸς ἀπογινώσκειν ὧν ὑπέσχηται πρὸς εὐδαιμονίαν ὡς οὐκ ἐσομένου πιστεύοντας ἐκ τῶν ἤδ

ifestans eis dei potentiam et prouidentiam eius quod dauid eius patri omnia futura sicut iam multa prouenerant et forent uentura reliqua praedixisset  **⟦candidate cut⟧** quod ipse quoque non dum nato imposuit ei nomen, et quod templum ipse aedificaturus est primus post patris obitum regnaturus. Et cum omnia secundum illius fierent prophetiam supplicabat ut deo benedicerent uniuersi, et in nullo eius promissionibus disperarent quas pro eoque felicitate praedixerat, sed crederent haec implenda quae fuerant 

`latin-book08-num106`; `/TEI[1]/text[1]/body[1]/div1[1]/div2[5]/p[2]/pb[1]/tail()`; node offset **1153**, paragraph offset **1270**, UTF-8 byte **35692** (zero-based, pinned LF bytes).

Neighbouring extent change: 109 ends at the proposed cut instead of the old cut; 110 begins there and still ends at 111. Exact before/after offsets are in the boundary reassessment and DECISION_HISTORY.json.

**Difficulty.** Canonical Greek 110 begins at τίς μέλλοι, after the naming clause has already begun in 109. Niese p.200 puts the numeral at that continuation line; Loeb p.630 puts 110 at the earlier καὶ ὡς αὐτὸς naming clause. The marginal lines differ, and neither print supplies a word-delimiting tag.

**Recommended treatment.** Prefer the complete naming clause καὶ ὡς αὐτὸς ἐπιθείη / quod ipse quoque non dum nato, but retain it as a source-interpretation alternative pending judgement.

**Credible alternatives.** Keep canonical τίς μέλλοι and the earlier Latin imposuit ei nomen cut, admitting that Latin already began the naming counterpart in 109.

**Decision requested.** Choose the Greek word boundary and corresponding Latin extent for 109–110.

### VIII.167 — decision required

Affected Latin: `latin-book08-num165`.

Printed authority: Niese, *Flavii Iosephi Opera* II (1885), **p. 213**, PDF **221**. [Full page image](evidence/print-collation/niese-II-pdf-221.jpg).

**Greek, earlier canonical cut with adjoining text:**

ὐτοῦ βουλομένη λαβεῖν πεῖραν αὐτὴ προτείνασα καὶ λῦσαι τὸ ἄπορον τῆς διανοίας δεηθεῖσα ἧκεν εἰς Ἱεροσόλυμα μετὰ πολλῆς δόξης καὶ πλούτου παρασκευῆς:   **⟦candidate cut⟧** ἐπηγάγετο γὰρ καμήλους χρυσίου μεστὰς καὶ ἀρωμάτων ποικίλων καὶ λίθων πολυτελῶν. ὡς δ᾽ ἀφικομένην αὐτὴν ἡδέως ὁ βασιλεὺς προσεδέξατο. τά τε ἄλλα περὶ αὐτὴν φιλότιμος ἦν καὶ τὰ προβαλλόμενα σοφίσματα ῥᾳδίως τῇ συνέσει καταλαμβανόμενος θᾶττον ἢ προσεδόκα τις ἐπελύετο.  ἡ δ᾽ ἐξεπλήσσετο μὲν καὶ τὴν σοφίαν τοῦ Σολόμωνος οὕτως ὑπερβάλλουσαν αὐ

**Latin, earlier candidate with adjoining text:**

enta perciperet studuit etiam quaestiones proferre et eorum solutiones exigere. Uenit ergo hierosolima cum magna gloria et ad parato multo diuitiarum  **⟦candidate cut⟧** cum auro et aromatibus et lapidibus praeciosis eamque rex grate suscepit, et circa eam in omnibus extitit ualde largissimis et propositiones sophismatum intellectu suo cito conspitiens uelocius quam sperare poterat ex soluebat. Cum illa se sapientiam ita se transcendentem et potiorem quam audiebat agnoscens uehementer obstupescebat et max

`latin-book08-num165`; `/TEI[1]/text[1]/body[1]/div1[1]/div2[7]/p[5]/num[1]/tail()`; node offset **588**, paragraph offset **588**, UTF-8 byte **53987** (zero-based, pinned LF bytes).

**Difficulty.** The Greek introduces camels carrying gold, aromatics and gems. Latin Uenit ergo belongs to the preceding arrival material and cum auro et aromatibus supplies only part of the new clause.

**Recommended treatment.** Use cum auro et aromatibus with a documented compressed/partly absent prefix; preserve Latin order.

**Credible alternatives.** A broader Uenit ergo locator would include preceding material; exact correspondence could remain unavailable.

**Decision requested.** Approve the first surviving gifts phrase as a partial counterpart.

### VIII.172 — decision required

Affected Latin: `latin-book08-num165`.

Printed authority: Niese, *Flavii Iosephi Opera* II (1885), **p. 214**, PDF **222**. [Full page image](evidence/print-collation/niese-II-pdf-222.jpg).
[Loeb V, p.662, PDF670](evidence/print-collation/loeb-V-followup-670.png) (independent control; Niese supplies numbering).

**Greek, earlier canonical cut with adjoining text:**

 τε ἔχεις ἐν αὑτῷ, λέγω δὲ τὴν σοφίαν καὶ τὴν φρόνησιν, καὶ ὧν ἡ βασιλεία σοι δίδωσιν, οὐ ψευδὴς ἄρα ἡ φήμη πρὸς ἡμᾶς διῆλθεν, ἀλλ᾽ οὖσα ἀληθὴς πολὺ   **⟦candidate cut⟧** καταδεεστέραν τὴν εὐδαιμονίαν ἀπέφηνεν ἧς ὁρῶ νῦν παροῦσα τὰς μὲν γὰρ ἀκοὰς πείθειν ἐπεχείρει μόνον, τὸ δὲ ἀξίωμα τῶν πραγμάτων οὐχ οὕτως ἐποίει γνώριμον, ὡς ἡ ὄψις αὐτὸ καὶ τὸ παρ᾽ αὐτοῖς εἶναι συνίστησιν. ἐγὼ γοῦν οὐδὲ τοῖς ἀπαγγελλομένοις διὰ πλῆθος καὶ μέγεθος ὧν ἐπυνθανόμην πιστεύουσα πολλῷ πλείω τούτων ἱστόρηκα.  καὶ μακάριόν τε τὸν

**Latin, earlier candidate with adjoining text:**

untur. Tuorum uero bonorum et ipse inte possides. Hoc [est] sapientiam et prudentiam, et quae tibi praestantur ex regno non est mendax fama sed uera.  **⟦candidate cut⟧** Licet multorum minor quam in praesenti conspicio, nam opinio  auribus quidem aliquid suadere nititur. Dignitas uero rerum monita fieri nota sicut aspectu et ipsa praesentia conprobatur. Ego siquidem neque his quae nuntiabantur propter multitudinem et magnitudinem credens potiora multa conspexi, et beatum dico populo[um] hebraeorum seruosq

`latin-book08-num165`; `/TEI[1]/text[1]/body[1]/div1[1]/div2[7]/p[5]/num[1]/tail()`; node offset **1898**, paragraph offset **1898**, UTF-8 byte **55297** (zero-based, pinned LF bytes).

**Reassessed proposal / alternative, not applied:**

ὶ ὧν ἡ βασιλεία σοι δίδωσιν, οὐ ψευδὴς ἄρα ἡ φήμη πρὸς ἡμᾶς διῆλθεν, ἀλλ᾽ οὖσα ἀληθὴς πολὺ  καταδεεστέραν τὴν εὐδαιμονίαν ἀπέφηνεν ἧς ὁρῶ νῦν παροῦσα  **⟦candidate cut⟧** τὰς μὲν γὰρ ἀκοὰς πείθειν ἐπεχείρει μόνον, τὸ δὲ ἀξίωμα τῶν πραγμάτων οὐχ οὕτως ἐποίει γνώριμον, ὡς ἡ ὄψις αὐτὸ καὶ τὸ παρ᾽ αὐτοῖς εἶναι συνίστησιν. ἐγὼ γοῦν οὐδὲ τοῖς ἀπαγγελλομένοις διὰ πλῆθος καὶ μέγεθος ὧν ἐπυνθανόμην πιστεύουσα πολλῷ πλείω τούτων ἱστόρηκα.  καὶ μακάριόν τε τὸν Ἑβραίων λαὸν εἶναι κρίνω δούλους τε τοὺς σοὺς καὶ φίλους,

Hoc [est] sapientiam et prudentiam, et quae tibi praestantur ex regno non est mendax fama sed uera. Licet multorum minor quam in praesenti conspicio,  **⟦candidate cut⟧** nam opinio  auribus quidem aliquid suadere nititur. Dignitas uero rerum monita fieri nota sicut aspectu et ipsa praesentia conprobatur. Ego siquidem neque his quae nuntiabantur propter multitudinem et magnitudinem credens potiora multa conspexi, et beatum dico populo[um] hebraeorum seruosque tuos pariter et amicos qui cotidie tuo uultu fr

`latin-book08-num165`; `/TEI[1]/text[1]/body[1]/div1[1]/div2[7]/p[5]/num[1]/tail()`; node offset **1948**, paragraph offset **1948**, UTF-8 byte **55347** (zero-based, pinned LF bytes).

Neighbouring extent change: 171 ends at the proposed cut instead of the old cut; 172 begins there and still ends at 173. Exact before/after offsets are in the boundary reassessment and DECISION_HISTORY.json.

**Difficulty.** Canonical Greek 172 starts at καταδεεστέραν within the comparative clause. Niese p.214 places 172 at that line; Loeb p.662 places 172 later on the same comparative clause at ἀπέφηνεν. The next explanatory τὰς μὲν γὰρ clause is another credible logical cut. Latin Licet multorum minor corresponds to the comparative phrase; nam opinio begins the explanation.

**Recommended treatment.** Prefer retaining the canonical comparative cut and Latin Licet multorum minor because it directly matches Niese’s marked line, but do not claim a uniquely word-tagged physical boundary. Preserve the later explanatory alternative.

**Credible alternatives.** Start at τὰς μὲν γὰρ / nam opinio, assigning the comparative phrase to 171; or require a further independently word-delimited control.

**Decision requested.** Choose the comparative or explanatory word boundary and its Latin extent.

### VIII.187 — decision required

Affected Latin: `latin-book08-num187`.

Printed authority: Niese, *Flavii Iosephi Opera* II (1885), **p. 217**, PDF **225**. [Full page image](evidence/print-collation/niese-II-pdf-225.jpg).

**Greek, earlier canonical cut with adjoining text:**

οίνων Ἱεροσολύμων, ὃ καλεῖται μὲν Ἠτάν, παραδείσοις δὲ καὶ ναμάτων ἐπιρροαῖς ἐπιτερπὲς ὁμοῦ καὶ πλούσιον: εἰς τοῦτο τὰς ἐξόδους αἰωρούμενος ἐποιεῖτο.  **⟦candidate cut⟧** Θείᾳ τε περὶ πάντα χρώμενος ἐπινοίᾳ τε καὶ σπουδῇ καὶ λίαν ὢν φιλόκαλος οὐδὲ τῶν ὁδῶν ἠμέλησεν, ἀλλὰ καὶ τούτων τὰς ἀγούσας εἰς Ἱεροσόλυμα βασίλειον οὖσαν λίθῳ κατέστρωσε μέλανι, πρός τε τὸ ῥᾳστώνην εἶναι τοῖς βαδίζουσι, καὶ πρὸς τὸ δηλοῦν τὸ ἀξίωμα τοῦ πλούτου καὶ τῆς ἡγεμονίας.  διαμερίσας δὲ τὰ ἅρματα καὶ διατάξας, ὥστε ἐν ἑκάστῃ πόλει

**Latin, earlier candidate with adjoining text:**

 ab hierosolimis duo funiculis abest. Uocatusque ita in hortis et aquarum rigationibus  gratus et locuplex. Huc ergo causa delectationis egrediebatur  **⟦candidate cut⟧** maxima[s] res omni prouidentia et studio semper utens, et ubique cultus ac decoris et existens. Neque uiarum desidiam habuit, sed regias quae ad hierosolima ducerent. Lapide nigrostrauit ut etiam ambulantibus non possent esset difficiles et ostenderent diuitiarum et imperii dignitatem. Diuidens autem currus et disponens ut singulis ciuita

`latin-book08-num187`; `/TEI[1]/text[1]/body[1]/div1[1]/div2[8]/p[4]/num[1]/tail()`; node offset **43**, paragraph offset **43**, UTF-8 byte **59934** (zero-based, pinned LF bytes).

**Difficulty.** The inherited [VII.iv.187] stands before Huc ergo causa delectationis egrediebatur, which corresponds to 186. The following maxima[s] res omni prouidentia has damaged syntax; maxima[s] res and omni prouidentia are credible different cuts.

**Recommended treatment.** Prefer maxima[s] res omni as the earliest surviving transition. Preserve the inherited composite label and chapter structure verbatim; an eventual certified locator must override its false 187 identity.

**Credible alternatives.** Cut at omni prouidentia, leaving maxima[s] res with 186; or withhold an exact locator.

**Decision requested.** Choose maxima[s] res omni or omni prouidentia, and approve a data-level override of the inherited citation claim.

### VIII.224 — decision required

Affected Latin: `latin-book08-num219`.

Printed authority: Niese, *Flavii Iosephi Opera* II (1885), **p. 225**, PDF **233**. [Full page image](evidence/print-collation/niese-II-pdf-233.jpg).

**Greek, earlier canonical cut with adjoining text:**

 γὰρ εἶναι δίκαιον τοὺς ὁμοφύλους πολεμεῖν οὗτος ἔλεγε καὶ ταῦτα κατὰ τὴν τοῦ θεοῦ προαίρεσιν τῆς τοῦ πλήθους ἀποστάσεως γεγενημένης, οὐκέτ᾽ ἐξῆλθε.   **⟦candidate cut⟧** διηγήσομαι δὲ πρῶτον ὅσα Ἱεροβόαμος ὁ τῶν Ἰσραηλιτῶν βασιλεὺς ἔπραξεν, εἶτα δὲ τούτων ἐχόμενα τὰ ὑπὸ Ῥοβοάμου τοῦ τῶν δύο φυλῶν βασιλέως γεγενημένα δηλώσομεν: φυλαχθείη γὰρ ἂν οὕτως ἄχρι παντὸς τῆς ἱστορίας τὸ εὔτακτον. Ὁ τοίνυν Ἱεροβόαμος οἰκοδομήσας βασίλειον ἐν Σικίμῃ πόλει ἐν ταύτῃ τὴν δίαιταν εἶχε, κατεσκεύασε δὲ καὶ ἐν Φανουὴλ πόλει

**Latin, earlier candidate with adjoining text:**

stum aduersus contribulos dimicarent, eum ab eo dei uoluntate populus recessisset. Quo facto nequaquam est egressus ad praelium. Diuisos quidem regno  **⟦candidate cut⟧** potius quidem narrabo quaecumque hieroboam israhelitarum rex egit. Deinde quae ad roboam duarum tribuum rege gesta sunt explanabo. Sic et enim totius historiae ordo seruabitur. Igitur hieroboam constitus in sicimorum ciuitate: fecit non multum post scenophegiae festiuitatis immineret: cogitans hieroboam quia si promitteret populo ut domin

`latin-book08-num219`; `/TEI[1]/text[1]/body[1]/div1[1]/div2[9]/p[3]/num[1]/tail()`; node offset **1424**, paragraph offset **1424**, UTF-8 byte **70920** (zero-based, pinned LF bytes).

**Difficulty.** The Greek διηγήσομαι δὲ πρῶτον introduces the account; Latin places related framing language in a different order. Diuisos quidem regno includes the preceding division of the kingdoms.

**Recommended treatment.** Retain potius quidem narrabo as the narrower counterpart.

**Credible alternatives.** Begin at Diuisos quidem regno as broader context, or defer the exact cut.

**Decision requested.** Approve potius quidem narrabo despite the reordered framing.

### VIII.245 — decision required

Affected Latin: `latin-book08-num236`.

Printed authority: Niese, *Flavii Iosephi Opera* II (1885), **p. 229**, PDF **237**. [Full page image](evidence/print-collation/niese-II-pdf-237.jpg).
[Loeb V, p.704, PDF712](evidence/print-collation/loeb-V-followup-712.png) (independent control; Niese supplies numbering).

**Greek, earlier canonical cut with adjoining text:**

 πέσοι διὰ βάρος τῶν ἐπενηνεγμένων. ἐδήλου δ᾽ αὐτῷ καὶ τὸν θάνατον τοῦ τὰ σημεῖα ταῦτα προειρηκότος ὡς ὑπὸ λέοντος ἀπώλετο: οὕτως οὐδὲ ἓν οὔτ᾽ εἶχεν   **⟦candidate cut⟧** οὔτ᾽ ἐφθέγξατο προφήτου. ταῦτα εἰπὼν πείθει τὸν βασιλέα καὶ τὴν διάνοιαν αὐτοῦ τελέως ἀποστρέψας ἀπὸ τοῦ θεοῦ καὶ τῶν ὁσίων ἔργων καὶ δικαίων ἐπὶ τὰς ἀσεβεῖς πράξεις παρώρμησεν. οὕτως δ᾽ ἐξύβρισεν εἰς τὸ θεῖον καὶ παρηνόμησεν, ὡς οὐδὲν ἄλλο καθ᾽ ἡμέραν ζητεῖν ἢ τί καινὸν καὶ μιαρώτερον τῶν ἤδη τετολμημένων ἐργάσηται. καὶ τὰ μὲν περὶ Ἱεροβ

**Latin, earlier candidate with adjoining text:**

fuisse ruptum et cecidisse dicebat. Significauitque ei simul ita mortem eius quia haec signa praedixerat, eo quod fuisset a leone discerptus et nihil  **⟦candidate cut⟧** quod esset propheta locutus. Haec ergo dicens regi satisfecit eiusque mentem penitus auertit a deo et a sanctis operibus, et ad actos impios euocauit. Qui rex tantam deinceps contumeliam diuinati fecit et ita contra leges atrociter insiluit ut nihil aliud cotidiae quaereret quam utali quid noui super ea quae iam perpetrauerat scelera cumu

`latin-book08-num236`; `/TEI[1]/text[1]/body[1]/div1[1]/div2[10]/p[1]/pb[1]/tail()`; node offset **1408**, paragraph offset **2971**, UTF-8 byte **77863** (zero-based, pinned LF bytes).

**Reassessed proposal / alternative, not applied:**

ηνεγμένων. ἐδήλου δ᾽ αὐτῷ καὶ τὸν θάνατον τοῦ τὰ σημεῖα ταῦτα προειρηκότος ὡς ὑπὸ λέοντος ἀπώλετο: οὕτως οὐδὲ ἓν οὔτ᾽ εἶχεν  οὔτ᾽ ἐφθέγξατο προφήτου.  **⟦candidate cut⟧** ταῦτα εἰπὼν πείθει τὸν βασιλέα καὶ τὴν διάνοιαν αὐτοῦ τελέως ἀποστρέψας ἀπὸ τοῦ θεοῦ καὶ τῶν ὁσίων ἔργων καὶ δικαίων ἐπὶ τὰς ἀσεβεῖς πράξεις παρώρμησεν. οὕτως δ᾽ ἐξύβρισεν εἰς τὸ θεῖον καὶ παρηνόμησεν, ὡς οὐδὲν ἄλλο καθ᾽ ἡμέραν ζητεῖν ἢ τί καινὸν καὶ μιαρώτερον τῶν ἤδη τετολμημένων ἐργάσηται. καὶ τὰ μὲν περὶ Ἱεροβόαμον ἐπὶ τοῦ παρόντος ἐν

cebat. Significauitque ei simul ita mortem eius quia haec signa praedixerat, eo quod fuisset a leone discerptus et nihil quod esset propheta locutus.  **⟦candidate cut⟧** Haec ergo dicens regi satisfecit eiusque mentem penitus auertit a deo et a sanctis operibus, et ad actos impios euocauit. Qui rex tantam deinceps contumeliam diuinati fecit et ita contra leges atrociter insiluit ut nihil aliud cotidiae quaereret quam utali quid noui super ea quae iam perpetrauerat scelera cumularet. Igitur de hieroboam ha

`latin-book08-num236`; `/TEI[1]/text[1]/body[1]/div1[1]/div2[10]/p[1]/pb[1]/tail()`; node offset **1437**, paragraph offset **3000**, UTF-8 byte **77892** (zero-based, pinned LF bytes).

Neighbouring extent change: 244 ends at the proposed cut instead of the old cut; 245 begins there and still ends at 246. Exact before/after offsets are in the boundary reassessment and DECISION_HISTORY.json.

**Difficulty.** Canonical Greek 245 starts at οὔτ᾽ ἐφθέγξατο προφήτου, the end of the previous negative assertion. Niese p.229 places 245 beside a line containing that ending and ταῦτα εἰπών. Loeb p.704 places the new section at ταῦτ᾽ εἰπών. The combined sentence evidence supports a later Greek start.

**Recommended treatment.** Propose moving the Greek citation cut to ταῦτα εἰπὼν πείθει and the Latin candidate from quod esset propheta locutus to Haec ergo dicens. The negative assertion then remains in 244.

**Credible alternatives.** Retain the canonical cut if treating the marginal line as controlling; this preserves the earlier Latin proposal but splits the negative assertion.

**Decision requested.** Accept or reject the proposed paired relocation of 245; no XML edit is authorized.

### VIII.255 — decision required

Affected Latin: `latin-book08-num251`.

Printed authority: Niese, *Flavii Iosephi Opera* II (1885), **p. 232**, PDF **240**. [Full page image](evidence/print-collation/niese-II-pdf-240.jpg).
[Loeb V, p.710, PDF718](evidence/print-collation/loeb-V-followup-718.png) (independent control; Niese supplies numbering).

**Greek, earlier canonical cut with adjoining text:**

 χίλια καὶ διακόσια τὸν ἀριθμὸν ἠκολούθει, ἱππέων δὲ μυριάδες ἕξ, πεζῶν δὲ μυριάδες τεσσαράκοντα. τούτων τοὺς πλείστους Λίβυας ἐπήγετο καὶ Αἰθίοπας.   **⟦candidate cut⟧** ἐμβαλὼν οὖν εἰς τὴν χώραν τῶν Ἑβραίων καταλαμβάνει τε τὰς ὀχυρωτάτας τῆς Ῥοβοάμου βασιλείας πόλεις ἀμαχητὶ καὶ ταύτας ἀσφαλισάμενος ἔσχατον ἐπῆλθε τοῖς Ἱεροσολύμοιςἐγκεκλεισμένου τοῦ Ῥοβοάμου καὶ τοῦ πλήθους ἐν αὐτοῖς διὰ τὴν Ἰσώκου στρατείαν καὶ τὸν θεὸν ἱκετευόντων δοῦναι νίκην καὶ σωτηρίαν:  ἀλλ᾽ οὐκ ἔπεισαν τὸν θεὸν ταχθῆναι μετ᾽ αὐτῶ

**Latin, earlier candidate with adjoining text:**

quebantur enim eum currus mille et ducenti. Aequitum uero sexaginta milia et quadraginta milia peditum quorum plurimos habebat libeas et aethiopices.  **⟦candidate cut⟧** Inuadens itaque hebraeorum regionem munitissimas roboam ciuitates sine dimicatione detenuit et nouissimum armatus ad ierosolimam uenit ubi roboam et eius exercitus propter militiam sisoch tenebatur inclausus, dominumque rogabant ut eis uictoriam salutemque conferret. Quos tamen non ex audiuit deus nec eis pugnaturis spem uictoriae promisi

`latin-book08-num251`; `/TEI[1]/text[1]/body[1]/div1[1]/div2[11]/p[2]/pb[1]/tail()`; node offset **183**, paragraph offset **1069**, UTF-8 byte **81136** (zero-based, pinned LF bytes).

**Difficulty.** Printed 255 starts at ἐμβαλὼν οὖν, securely corresponding to Inuadens itaque hebraeorum regionem inside Latin pnum251. The inherited [X.iii.255] at pnum255 begins a later traditional subdivision within the same Niese section.

**Recommended treatment.** Retain the secure internal candidate at Inuadens itaque. Preserve pnum255, its label and traditional subdivision; eventual certified locator data must suppress the false second 255 start.

**Credible alternatives.** Keep Niese navigation unavailable until the independent citation locator can distinguish the inherited textual label from the citation identity.

**Decision requested.** Approve the representation policy preserving the inherited label while using the internal 255 locator.

### VIII.256 — resolved source check

Affected Latin: `latin-book08-num255`.

Printed authority: Niese, *Flavii Iosephi Opera* II (1885), **p. 232**, PDF **240**. [Full page image](evidence/print-collation/niese-II-pdf-240.jpg).
[Loeb V, p.710, PDF718](evidence/print-collation/loeb-V-followup-718.png) (independent control; Niese supplies numbering).

**Greek, earlier canonical cut with adjoining text:**

 τοῖς Ἱεροσολύμοιςἐγκεκλεισμένου τοῦ Ῥοβοάμου καὶ τοῦ πλήθους ἐν αὐτοῖς διὰ τὴν Ἰσώκου στρατείαν καὶ τὸν θεὸν ἱκετευόντων δοῦναι νίκην καὶ σωτηρίαν:   **⟦candidate cut⟧** ἀλλ᾽ οὐκ ἔπεισαν τὸν θεὸν ταχθῆναι μετ᾽ αὐτῶν: ὁ δὲ προφήτης Σαμαίας ἔφησεν αὐτοῖς τὸν θεὸν ἀπειλεῖν ἐγκαταλείψειν αὐτούς, ὡς καὶ αὐτοὶ τὴν θρησκείαν αὐτοῦ κατέλιπον. ταῦτ᾽ ἀκούσαντες εὐθὺς ταῖς ψυχαῖς ἀνέπεσον καὶ μηδὲν ἔτι σωτήριον ὁρῶντες ἐξομολογεῖσθαι πάντες ὥρμησαν, ὅτι δικαίως αὐτοὺς ὁ θεὸς ὑπερόψεται γενομένους περὶ αὐτὸν ἀσεβεῖς 

**Latin, earlier candidate with adjoining text:**

erosolimam uenit ubi roboam et eius exercitus propter militiam sisoch tenebatur inclausus, dominumque rogabant ut eis uictoriam salutemque conferret.  **⟦candidate cut⟧** Quos tamen non ex audiuit deus nec eis pugnaturis spem uictoriae promisit. Propheta enim semeas ait, deum eis interminari eosque relicturum sicut ipse uidebantur deseruisse culturam. Haec audientes animo sunt soluti. Et dum nullam uiderint in se salutem confitebantur omnes quod eos iuste dispexent, cum ipsi circa eum impie crudeliterque g

`latin-book08-num255`; `/TEI[1]/text[1]/body[1]/div1[1]/div2[11]/p[3]/num[1]/tail()`; node offset **134**, paragraph offset **134**, UTF-8 byte **81468** (zero-based, pinned LF bytes).

**Difficulty.** Niese p.232 prints 256 on a line beginning στρατείαν, which completes 255; ἀλλ᾽ οὐκ ἔπεισαν starts the following clause on that line. The Latin Quos tamen non exaudiuit is the corresponding refusal.

**Recommended treatment.** Retain the canonical Greek cut and current Latin candidate. Do not move the Greek marker to στρατείαν.

**Credible alternatives.** No materially preferable cut was established by the source check.

**Decision requested.** Resolved in the candidate audit; implementation remains unapproved.

### VIII.314 — resolved source check

Affected Latin: `latin-book08-num314`.

Printed authority: Niese, *Flavii Iosephi Opera* II (1885), **p. 244**, PDF **252**. [Full page image](evidence/print-collation/niese-II-pdf-252.jpg).

**Greek, earlier canonical cut with adjoining text:**

το δι᾽ ἀλλήλων αὐτοὺς ὁ θεὸς ἐποίησεν ἐλθεῖν καὶ μηδένα τοῦ γένους ὑπολιπεῖν. ἐτελεύτησε δὲ καὶ οὗτος ἐν Σαμαρείᾳ, διαδέχεται δ᾽ αὐτὸν ὁ παῖς Ἄχαβος.  **⟦candidate cut⟧** Μαθεῖν δ᾽ ἔστιν ἐκ τούτων, ὅσην τὸ θεῖον ἐπιστροφὴν ἔχει τῶν ἀνθρωπίνων πραγμάτων, καὶ πῶς μὲν ἀγαπᾷ τοὺς ἀγαθούς, μισεῖ δὲ τοὺς πονηροὺς καὶ προρρίζους ἀπόλλυσιν: οἱ μὲν γὰρ τῶν Ἰσραηλιτῶν βασιλεῖς ἄλλος ἐπ᾽ ἄλλῳ διὰ τὴν παρανομίαν καὶ τὰς ἀδικίας ἐν ὀλίγῳ χρόνῳ πολλοὶ κακῶς διαφθαρέντες ἐγνώσθησαν καὶ τὸ γένος αὐτῶν, ὁ δὲ τῶν Ἱεροσολύμω

**Latin, earlier candidate with adjoining text:**

o recedere. Et propter eam scripsit eos et nullum promisit eorum genere super esse. Et his ergo defunctus est in samana. Successitque ei filius acab.  **⟦candidate cut⟧** Ex his namque cognoscitur quantam prouidentiam humanarum rerum probat habere diuinitas et quomodo bonos quidem malos autem abhorret et a radice disperset. Israhelitarum denique reges propter suam iniquitatem et iniustiam alter super alium in ruentes multi paruo tempore perierunt et eorum genus exterminatus est. Asa autem rex hierosolimoru

`latin-book08-num314`; `/TEI[1]/text[1]/body[1]/div1[1]/div2[13]/p[6]/num[1]/tail()`; node offset **1**, paragraph offset **1**, UTF-8 byte **99376** (zero-based, pinned LF bytes).

**Difficulty.** Niese p.244 visibly prints lower division 6 and section 314 at Μαθεῖν δ᾽ ἔστιν. Latin Ex his namque cognoscitur is its counterpart. The additional composite label is real textual evidence but cannot manufacture a traditional structural division.

**Recommended treatment.** Retain the inherited Niese candidate and existing traditional structure. Record the difference from the frozen physical-start inventory.

**Credible alternatives.** No renumbering or additional traditional division is warranted.

**Decision requested.** Resolved as a candidate Niese start; no structural application approved.

### VIII.334 — decision required

Affected Latin: `latin-book08-num328`.

Printed authority: Niese, *Flavii Iosephi Opera* II (1885), **p. 249**, PDF **257**. [Full page image](evidence/print-collation/niese-II-pdf-257.jpg).

**Greek, earlier canonical cut with adjoining text:**

, μὴ τοῦ θεοῦ φανέντος αὐτῷ πάλιν εἰς ἄλλον ἀπέλθῃ τόπον, εἶτα διαμαρτὼν αὐτοῦ πέμψαντος τοῦ βασιλέως μὴ δυνάμενος εὑρεῖν ὅπου ποτ᾽ εἴη γῆς ἀποθάνῃ.   **⟦candidate cut⟧** προνοεῖν οὖν αὐτοῦ τῆς σωτηρίας παρακαλεῖ τὴν περὶ τοὺς ὁμοτέχνους αὐτοῦ σπουδὴν λέγων, ὅτι σώσειεν ἑκατὸν προφήτας Ἱεζαβέλης πάντας τοὺς ἄλλους ἀνῃρηκυίας καὶ ἔχοι κεκρυμμένους αὐτοὺς καὶ τρεφομένους ὑπ᾽ αὐτοῦ. ὁ δὲ μηδὲν δεδιότα βαδίζειν ἐκέλευε πρὸς τὸν βασιλέα δοὺς αὐτῷ πίστεις ἐνόρκους, ὅτι πάντως κατ᾽ ἐκείνην Ἀχάβῳ φανήσεται τὴν ἡμέ

**Latin, earlier candidate with adjoining text:**

od non dixerit ut te repertum ad casum necis adducat, praecabat enim ne dum regi nuntiaret, et alio alibi ducente mentire uideretur morte subcumbere.  **⟦candidate cut⟧** Commemorabatque ei quemadmodum cum zezabel prophetas occiderit centum ipse absconsos et multos alios in speleo liberasset. Cui propheta nihil metuens inquit ad regem festinus accedere praebuitque ei iure iurandi religionem quoniam illa die ad achab ipse quoque ueniret Dumque rei quod uidisset heliam et mox occurrit achab requirens cum ira

`latin-book08-num328`; `/TEI[1]/text[1]/body[1]/div1[1]/div2[14]/p[4]/num[1]/tail()`; node offset **1251**, paragraph offset **1251**, UTF-8 byte **105482** (zero-based, pinned LF bytes).

**Difficulty.** The Greek opening appeal for salvation is absent from the corresponding Latin; Commemorabatque ei renders a later part of the speech.

**Recommended treatment.** Retain Commemorabatque ei as the first surviving counterpart with an explicit partial-prefix omission record.

**Credible alternatives.** Use broader contextual display without asserting an exact start.

**Decision requested.** Approve the partial-correspondence treatment or withhold the exact citation locator.

### VIII.353 — decision required

Affected Latin: `latin-book08-num347`.

Printed authority: Niese, *Flavii Iosephi Opera* II (1885), **p. 252**, PDF **260**. [Full page image](evidence/print-collation/niese-II-pdf-260.jpg).
[Loeb V, p.760, PDF768](evidence/print-collation/loeb-V-followup-768.png) (independent control; Niese supplies numbering).
[Loeb V, p.762, PDF770](evidence/print-collation/loeb-V-followup-770.png) (independent control; Niese supplies numbering).

**Greek, earlier canonical cut with adjoining text:**

πλήθους βασιλέα Ἰηοῦν τὸν Νεμεσαίου παῖδα, ἐκ Δαμασκοῦ δὲ τῶν Σύρων Ἀζάηλον: ἀντ᾽ αὐτοῦ δὲ προφήτην Ἐλισσαῖον ὑπ᾽ αὐτοῦ γενήσεσθαι ἐκ πόλεως Ἀβέλας:   **⟦candidate cut⟧** διαφθερεῖ δὲ τοῦ ἀσεβοῦς ὄχλου τοὺς μὲν Ἀζάηλος τοὺς δὲ Ἰηοῦς. ὁ δ᾽ Ἠλίας ὑποστρέφει ταῦτ᾽ ἀκούσας εἰς τὴν Ἑβραίων χώραν καὶ τὸν Σαφάτου παῖδα Ἐλισσαῖον καταλαβὼν ἀροῦντα καὶ μετ᾽ αὐτοῦ τινας ἄλλους ἐλαύνοντας ζεύγη δώδεκα προσελθὼν ἐπέρριψεν αὐτῷ τὸ ἴδιον ἱμάτιον.  ὁ δ᾽ Ἐλισσαῖος εὐθέως προφητεύειν ἤρξατο καὶ καταλιπὼν τοὺς βόας ἠκολούθη

**Latin, earlier candidate with adjoining text:**

mi reuertens ungueret populi regem beunam esse filium, in damasco uero syriae azahel. Pro se autem prophetam constituerit helis eum de ciuitate abela  **⟦candidate cut⟧** ut totius impii populi perimeret. Alius quidem azahel alius autem heus. Haec audiens helias ad regionem reuersus est hebraeorum et in ueniens helis eum filium saphat arantem, et cum eodem alios usque ad iuga duodecim accedens proiecit super eum pallium suum. Heliseus autem coepit prophetare et relictis bubus secutus est eum, rogans ut ei 

`latin-book08-num347`; `/TEI[1]/text[1]/body[1]/div1[1]/div2[14]/p[7]/num[1]/tail()`; node offset **1543**, paragraph offset **1543**, UTF-8 byte **111238** (zero-based, pinned LF bytes).

**Reassessed proposal / alternative, not applied:**

ύρων Ἀζάηλον: ἀντ᾽ αὐτοῦ δὲ προφήτην Ἐλισσαῖον ὑπ᾽ αὐτοῦ γενήσεσθαι ἐκ πόλεως Ἀβέλας:  διαφθερεῖ δὲ τοῦ ἀσεβοῦς ὄχλου τοὺς μὲν Ἀζάηλος τοὺς δὲ Ἰηοῦς.  **⟦candidate cut⟧** ὁ δ᾽ Ἠλίας ὑποστρέφει ταῦτ᾽ ἀκούσας εἰς τὴν Ἑβραίων χώραν καὶ τὸν Σαφάτου παῖδα Ἐλισσαῖον καταλαβὼν ἀροῦντα καὶ μετ᾽ αὐτοῦ τινας ἄλλους ἐλαύνοντας ζεύγη δώδεκα προσελθὼν ἐπέρριψεν αὐτῷ τὸ ἴδιον ἱμάτιον.  ὁ δ᾽ Ἐλισσαῖος εὐθέως προφητεύειν ἤρξατο καὶ καταλιπὼν τοὺς βόας ἠκολούθησεν Ἠλίᾳ. δεηθεὶς δὲ συγχωρῆσαι αὐτῷ τοὺς γονεῖς ἀσπάσασθαι κελ

yriae azahel. Pro se autem prophetam constituerit helis eum de ciuitate abela ut totius impii populi perimeret. Alius quidem azahel alius autem heus.  **⟦candidate cut⟧** Haec audiens helias ad regionem reuersus est hebraeorum et in ueniens helis eum filium saphat arantem, et cum eodem alios usque ad iuga duodecim accedens proiecit super eum pallium suum. Heliseus autem coepit prophetare et relictis bubus secutus est eum, rogans ut ei promitteret quatenus quatenus parentes proximos salutaret, quo iubente u

`latin-book08-num347`; `/TEI[1]/text[1]/body[1]/div1[1]/div2[14]/p[7]/num[1]/tail()`; node offset **1615**, paragraph offset **1615**, UTF-8 byte **111310** (zero-based, pinned LF bytes).

Neighbouring extent change: 352 ends at the proposed cut instead of the old cut; 353 begins there and still ends at 354. Exact before/after offsets are in the boundary reassessment and DECISION_HISTORY.json.

**Difficulty.** Canonical Greek starts with διαφθερεῖ δὲ, one line above the printed 353. Niese p.252 places 353 beside the end of that sentence and ὁ δ᾽ Ἠλίας. Loeb pp.760/762 keeps the destruction sentence in 352 and prints 353 at ὁ δ᾽ Ἠλίας.

**Recommended treatment.** Propose the Greek start at ὁ δ᾽ Ἠλίας and Latin Haec audiens helias. Move the preceding destruction material back into the proposed 352 extents; preserve all Latin order and wording.

**Credible alternatives.** Retain the canonical cut and the earlier ut totius impii populi perimeret candidate, with its compressed syntax.

**Decision requested.** Accept or reject the proposed paired relocation of 353.

### VIII.367 — decision required

Affected Latin: `latin-book08-num363` (see neighbouring extents and inherited-label discussion).

Printed authority: Niese, *Flavii Iosephi Opera* II (1885), **p. 256**, PDF **264**. [Full page image](evidence/print-collation/niese-II-pdf-264.jpg).
[Loeb V, p.768, PDF776](evidence/print-collation/loeb-V-followup-776.png) (independent control; Niese supplies numbering).
[Loeb V, p.769, PDF777](evidence/print-collation/loeb-V-followup-777.png) (independent control; Niese supplies numbering).

**Greek, earlier canonical cut with adjoining text:**

ι πολιορκῶν αὐτόν.  ὁ δ᾽ Ἄχαβος τοῖς πρέσβεσιν ἐκέλευσε πορευθεῖσι λέγειν τῷ βασιλεῖ αὐτῶν, ὅτι καὶ αὐτὸς καὶ οἱ ἑκείνου πάντες κτήματά εἰσιν αὐτοῦ.   **⟦candidate cut⟧** ταῦτα δ᾽ ἀπαγγειλάντων πέμπει πάλιν πρὸς αὐτὸν ἀξιῶν ἀνωμολογηκότα πάντα εἶναι ἐκείνου δέξασθαι τοὺς πεμφθησομένους εἰς τὴν ἐπιοῦσαν ὑπ᾽ αὐτοῦ δούλους, οἷς ἐρευνήσασι τά τε βασίλεια καὶ τοὺς τῶν φίλων καὶ συγγενῶν οἴκους ἐκέλευε διδόναι πᾶν ὅ τι ἂν ἐν αὐτοῖς εὕρωσι κάλλιστον,  τὰ δ᾽ ἀπαρέσαντα σοὶ καταλείψουσιν. Ἄχαβος δ᾽ ἀγασθεὶς ἐπὶ τῇ 

**Latin, earlier candidate with adjoining text:**

astra solueret et ab obscessione cessaret. Achab autem legatis dixit ut euntes suo dicerent regi, quia et ipse et omnes illius eius possessio forent,  **⟦candidate cut⟧** et quae displucuerint sola relinquerent. Achab itaque secunda legatione syrorum regis uehementer affectus collecto populo in ecclesia a dixit. Quia ipse quidem paratus fuerit pro salute et pace cunctorum et uxores suas et filios et omnem dare possessionem, et quia haec rex syrorum prima legatione misisset, nunc inquit denuo missa legation

This displayed cut belongs to the following surviving section, not to the unavailable section. `latin-book08-num363`; `/TEI[1]/text[1]/body[1]/div1[1]/div2[15]/p[1]/num[1]/tail()`; node offset **936**, paragraph offset **936**, UTF-8 byte **115320** (zero-based, pinned LF bytes).

**Difficulty.** The main second-embassy narrative demanding a search of the palace and friends’/relatives’ houses is absent from the canonical Latin at this point. The whole-book search found no displaced copy. Latin nevertheless retains et quae displucuerint sola relinquerent, and the later 369 recap. Which section owns the surviving tail depends on the unresolved 368 cut. Absence of the narrative is evidence; a scribal, exemplar or transcription cause has not been established.

**Recommended treatment.** Preserve the historical UNAVAILABLE row as conditional, not as proof that every word of 367 is absent. Prefer a partial-survival representation if 368 begins at Ἄχαβος. Never reuse 369 as 367, supply missing text, or add a gap automatically.

**Credible alternatives.** If retaining the canonical 368 cut at τὰ δ᾽ ἀπαρέσαντα, the surviving tail remains in 368 and 367 has no Latin locator. If moving 368 to Ἄχαβος, represent 367 by its surviving tail and document the absent prefix.

**Decision requested.** Decide jointly with 368 between unavailable 367 and partial-survival 367; authorize no textual supplementation.

### VIII.368 — decision required

Affected Latin: `latin-book08-num363`.

Printed authority: Niese, *Flavii Iosephi Opera* II (1885), **p. 256**, PDF **264**. [Full page image](evidence/print-collation/niese-II-pdf-264.jpg).
[Loeb V, p.768, PDF776](evidence/print-collation/loeb-V-followup-776.png) (independent control; Niese supplies numbering).
[Loeb V, p.769, PDF777](evidence/print-collation/loeb-V-followup-777.png) (independent control; Niese supplies numbering).

**Greek, earlier canonical cut with adjoining text:**

ῦσαν ὑπ᾽ αὐτοῦ δούλους, οἷς ἐρευνήσασι τά τε βασίλεια καὶ τοὺς τῶν φίλων καὶ συγγενῶν οἴκους ἐκέλευε διδόναι πᾶν ὅ τι ἂν ἐν αὐτοῖς εὕρωσι κάλλιστον,   **⟦candidate cut⟧** τὰ δ᾽ ἀπαρέσαντα σοὶ καταλείψουσιν. Ἄχαβος δ᾽ ἀγασθεὶς ἐπὶ τῇ δευτέρᾳ πρεσβείᾳ τοῦ τῶν Σύρων βασιλέως συναγαγὼν εἰς ἐκκλησίαν τὸ πλῆθος ἔλεγεν, ὡς αὐτὸς μὲν ἑτοίμως εἶχεν ὑπὲρ σωτηρίας αὐτοῦ καὶ εἰρήνης καὶ γυναῖκας τὰς ἰδίας προέσθαι τῷ πολεμίῳ καὶ τὰ τέκνα καὶ πάσης παραχωρῆσαι κτήσεως: ταῦτα γὰρ ἐπιζητῶν ἐπρεσβεύσατο πρῶτον ὁ Σύρος.  ν

**Latin, earlier candidate with adjoining text:**

astra solueret et ab obscessione cessaret. Achab autem legatis dixit ut euntes suo dicerent regi, quia et ipse et omnes illius eius possessio forent,  **⟦candidate cut⟧** et quae displucuerint sola relinquerent. Achab itaque secunda legatione syrorum regis uehementer affectus collecto populo in ecclesia a dixit. Quia ipse quidem paratus fuerit pro salute et pace cunctorum et uxores suas et filios et omnem dare possessionem, et quia haec rex syrorum prima legatione misisset, nunc inquit denuo missa legation

`latin-book08-num363`; `/TEI[1]/text[1]/body[1]/div1[1]/div2[15]/p[1]/num[1]/tail()`; node offset **936**, paragraph offset **936**, UTF-8 byte **115320** (zero-based, pinned LF bytes).

**Reassessed proposal / alternative, not applied:**

σι τά τε βασίλεια καὶ τοὺς τῶν φίλων καὶ συγγενῶν οἴκους ἐκέλευε διδόναι πᾶν ὅ τι ἂν ἐν αὐτοῖς εὕρωσι κάλλιστον,  τὰ δ᾽ ἀπαρέσαντα σοὶ καταλείψουσιν.  **⟦candidate cut⟧** Ἄχαβος δ᾽ ἀγασθεὶς ἐπὶ τῇ δευτέρᾳ πρεσβείᾳ τοῦ τῶν Σύρων βασιλέως συναγαγὼν εἰς ἐκκλησίαν τὸ πλῆθος ἔλεγεν, ὡς αὐτὸς μὲν ἑτοίμως εἶχεν ὑπὲρ σωτηρίας αὐτοῦ καὶ εἰρήνης καὶ γυναῖκας τὰς ἰδίας προέσθαι τῷ πολεμίῳ καὶ τὰ τέκνα καὶ πάσης παραχωρῆσαι κτήσεως: ταῦτα γὰρ ἐπιζητῶν ἐπρεσβεύσατο πρῶτον ὁ Σύρος.  νῦν δ᾽ ἠξίωκε δούλους πέμψαι τάς τε π

. Achab autem legatis dixit ut euntes suo dicerent regi, quia et ipse et omnes illius eius possessio forent, et quae displucuerint sola relinquerent.  **⟦candidate cut⟧** Achab itaque secunda legatione syrorum regis uehementer affectus collecto populo in ecclesia a dixit. Quia ipse quidem paratus fuerit pro salute et pace cunctorum et uxores suas et filios et omnem dare possessionem, et quia haec rex syrorum prima legatione misisset, nunc inquit denuo missa legatione misisset, nunc inquit denuo missa legat

`latin-book08-num363`; `/TEI[1]/text[1]/body[1]/div1[1]/div2[15]/p[1]/num[1]/tail()`; node offset **977**, paragraph offset **977**, UTF-8 byte **115361** (zero-based, pinned LF bytes).

Neighbouring extent change: 367 ends at the proposed cut instead of the old cut; 368 begins there and still ends at 369. Exact before/after offsets are in the boundary reassessment and DECISION_HISTORY.json.

**Difficulty.** Both Niese p.256 and Loeb p.768 put 368 beside the hyphenated ending of καταλείψουσιν, followed by Ἄχαβος δ᾽ ἀγασθείς. Neither marginal position alone identifies whether the cut precedes the preceding τὰ δ᾽ clause or the new Ahab sentence. Loeb English p.769 distinguishes the closing embassy quotation from “But Achab”.

**Recommended treatment.** Prefer a semantic start at Ἄχαβος δ᾽ ἀγασθείς / Achab itaque secunda legatione. Keep the printed line ambiguity explicit; this assigns the surviving quoted tail to partial 367.

**Credible alternatives.** Retain canonical τὰ δ᾽ ἀπαρέσαντα / et quae displucuerint, leaving 367 unavailable. Neither choice may be presented as a physically tagged word in Niese.

**Decision requested.** Choose the section-368 word boundary and the dependent 367 representation.

### VIII.369 — decision required

Affected Latin: `latin-book08-num363`.

Printed authority: Niese, *Flavii Iosephi Opera* II (1885), **p. 256**, PDF **264**. [Full page image](evidence/print-collation/niese-II-pdf-264.jpg).
[Loeb V, p.770, PDF778](evidence/print-collation/loeb-V-followup-778.png) (independent control; Niese supplies numbering).

**Greek, earlier canonical cut with adjoining text:**

ῦ καὶ εἰρήνης καὶ γυναῖκας τὰς ἰδίας προέσθαι τῷ πολεμίῳ καὶ τὰ τέκνα καὶ πάσης παραχωρῆσαι κτήσεως: ταῦτα γὰρ ἐπιζητῶν ἐπρεσβεύσατο πρῶτον ὁ Σύρος.   **⟦candidate cut⟧** νῦν δ᾽ ἠξίωκε δούλους πέμψαι τάς τε πάντων οἰκίας ἐρευνῆσαι καὶ μηδὲν ἐν αὐταῖς καταλιπεῖν τῶν καλλίστων κτημάτων πρόφασιν βουλόμενος πολέμου λαβεῖν, εἰδὼς ὅτι τῶν μὲν ἐμαυτοῦ δι᾽ ὑμᾶς οὐκ ἂν φεισαίμην, ἀφορμὴν δ᾽ ἐκ τοῦ περὶ τῶν ὑμετέρων ἀηδοῦς πραγματευόμενος εἰς τὸ πολεμεῖν: ‘ποιήσω γε μὴν τὰ ὑμῖν δοκοῦντα.’  τὸ δὲ πλῆθος μὴ δεῖν ἀκούε

**Latin, earlier candidate with adjoining text:**

m paratus fuerit pro salute et pace cunctorum et uxores suas et filios et omnem dare possessionem, et quia haec rex syrorum prima legatione misisset,  **⟦candidate cut⟧** nunc inquit denuo missa legatione misisset, nunc inquit denuo missa legatione petit perscrutandas domum, ut quicquid in eis in eis optimum inuenire possit auferat, et occasionem hanc machinas ad pugnam, et sciens quia meis rebus non pepercissem ad uestras accessit, ego uero quod uobis placuent ex hibeo. Populus autem respondens non ei obo

`latin-book08-num363`; `/TEI[1]/text[1]/body[1]/div1[1]/div2[15]/p[1]/num[1]/tail()`; node offset **1244**, paragraph offset **1244**, UTF-8 byte **115628** (zero-based, pinned LF bytes).

**Difficulty.** The Greek νῦν δ᾽ ἠξίωκε is a later recap, not the missing embassy narrative. Latin repeats nunc inquit denuo missa legatione; choosing the second copy would allocate the first duplicate to 368.

**Recommended treatment.** Keep the candidate at the first nunc inquit denuo, preserving both copies and the later narrative. Record the duplication as transmitted.

**Credible alternatives.** Start at the second nunc inquit denuo, explicitly assigning the first to the preceding extent; no deletion is permissible.

**Decision requested.** Choose the first or second repeated phrase as the physical 369 start.

### VIII.376 — resolved source check

Affected Latin: `latin-book08-num371`.

Printed authority: Niese, *Flavii Iosephi Opera* II (1885), **p. 257**, PDF **265**. [Full page image](evidence/print-collation/niese-II-pdf-265.jpg).
[Loeb V, p.772, PDF780](evidence/print-collation/loeb-V-followup-780.png) (independent control; Niese supplies numbering).

**Greek, earlier canonical cut with adjoining text:**

 πέμπει τινὰς ὑπαντησομένους ἐντειλάμενος, ἂν μὲν εἰς μάχην ὦσι προεληλυθότες, ἵνα δήσαντες ἀγάγωσι πρὸς αὐτόν, ἂν δ᾽ εἰρηνικῶς, ὅπως ταὐτὸ ποιῶσιν.   **⟦candidate cut⟧** εἶχε δ᾽ ἑτοίμην Ἄχαβος καὶ τὴν ἄλλην στρατιὰν ἐντὸς τῶν τειχῶν. οἱ δὲ τῶν ἀρχόντων παῖδες συμβαλόντες τοῖς φύλαξι πολλοὺς αὐτῶν ἀποκτείνουσι καὶ τοὺς ἄλλους ἄχρι τοῦ στρατοπέδου διώκουσιν. ἰδὼν δὲ τούτους νικῶντας ὁ βασιλεὺς ἐξαφίησι καὶ τὴν ἄλλην στρατιὰν ἅπασαν.  ἡ δ᾽ αἰφνιδίως ἐπιπεσοῦσα τοῖς Σύροις ἐκράτησεν αὐτῶν, οὐ γὰρ προσεδόκων α

**Latin, earlier candidate with adjoining text:**

r destinauit qui eis occurrerent. Praecipiens ut siquidem ad praelium uenirent eos ad se legatos adducerent, si uero pacifice essent idem efficerent.  **⟦candidate cut⟧** Achab autem exercitum habuit alium intra murum in subsidiis. Porro filii principum congressi syrorum custodibus multos eorum interimerent. Et alios usque ad castra secuti sunt. Uidens autem o os rex israhelitarum uincentes etiam alium exerictum dimisit exire qui repente syros inruentes praeualerunt eis. Non enim syri sperabant eos super s

`latin-book08-num371`; `/TEI[1]/text[1]/body[1]/div1[1]/div2[15]/p[2]/pb[1]/tail()`; node offset **1355**, paragraph offset **1377**, UTF-8 byte **117695** (zero-based, pinned LF bytes).

**Difficulty.** Niese p.257 has no marginal 376 at εἶχε δ᾽ ἑτοίμην. It prints 376 at the later ἡ δ᾽ αἰφνιδίως, where canonical XML has 377; 378 then resumes normally. Loeb p.772 independently distinguishes 376 at εἶχε and 377 at ἡ. This is an apparent printed numbering omission/misnumber, not an extra missing XML label.

**Recommended treatment.** Retain canonical 376 and 377 and their Latin candidates; document the primary-print numeral anomaly. Do not repair canonical numbering to repeat the apparent print error.

**Credible alternatives.** Without the independent control, these starts would need source adjudication.

**Decision requested.** Source anomaly resolved for the candidate sequence by Loeb control; no XML repair proposed.

### VIII.377 — resolved source check

Affected Latin: `latin-book08-num371`.

Printed authority: Niese, *Flavii Iosephi Opera* II (1885), **p. 257**, PDF **265**. [Full page image](evidence/print-collation/niese-II-pdf-265.jpg).
[Loeb V, p.772, PDF780](evidence/print-collation/loeb-V-followup-780.png) (independent control; Niese supplies numbering).

**Greek, earlier canonical cut with adjoining text:**

λλοὺς αὐτῶν ἀποκτείνουσι καὶ τοὺς ἄλλους ἄχρι τοῦ στρατοπέδου διώκουσιν. ἰδὼν δὲ τούτους νικῶντας ὁ βασιλεὺς ἐξαφίησι καὶ τὴν ἄλλην στρατιὰν ἅπασαν.   **⟦candidate cut⟧** ἡ δ᾽ αἰφνιδίως ἐπιπεσοῦσα τοῖς Σύροις ἐκράτησεν αὐτῶν, οὐ γὰρ προσεδόκων αὐτοὺς ἐπεξελεύσεσθαι, καὶ διὰ τοῦτο γυμνοῖς καὶ μεθύουσι προσέβαλλον, ὥστε τὰς πανοπλίας ἐκ τῶν στρατοπέδων φεύγοντας καταλιπεῖν καὶ τὸν βασιλέα σωθῆναι μόλις ἐφ᾽ ἵππου ποιησάμενον τὴν φυγήν.  Ἄχαβος δὲ πολλὴν ὁδὸν διώκων τοὺς Σύρους ἤνυσεν ἀναιρῶν αὐτούς, διαρπάσας

**Latin, earlier candidate with adjoining text:**

us multos eorum interimerent. Et alios usque ad castra secuti sunt. Uidens autem o os rex israhelitarum uincentes etiam alium exerictum dimisit exire  **⟦candidate cut⟧** qui repente syros inruentes praeualerunt eis. Non enim syri sperabant eos super se sic inopinabiliter fuisse uenturos, quod propter ea inuenientes nudos et ebrios ita praesecuti sunt ut illi etiam arma relinquerent fugientes, et uix in aequo rex potuisset euadere. Achab autem multo itinere persecutus interfecit syrorum et eorum castra dir

`latin-book08-num371`; `/TEI[1]/text[1]/body[1]/div1[1]/div2[15]/p[2]/pb[1]/tail()`; node offset **1614**, paragraph offset **1636**, UTF-8 byte **117954** (zero-based, pinned LF bytes).

**Difficulty.** See 376: Niese p.257 prints 376 on the line of the canonical 377 start and has no literal 377 there. Loeb p.772 prints 377 at ἡ δ᾽ αἰφνιδίως.

**Recommended treatment.** Retain the canonical 377 candidate and the Latin qui repente syros inruentes; record the printed numeral discrepancy.

**Credible alternatives.** Do not make two canonical sections numbered 376.

**Decision requested.** Resolved at candidate level with independent control.

### VIII.408 — decision required

Affected Latin: `latin-book08-num401`.

Printed authority: Niese, *Flavii Iosephi Opera* II (1885), **p. 264**, PDF **272**. [Full page image](evidence/print-collation/niese-II-pdf-272.jpg).
[Loeb V, p.790, PDF798](evidence/print-collation/loeb-V-followup-798.png) (independent control; Niese supplies numbering).
[Loeb V, p.791, PDF799](evidence/print-collation/loeb-V-followup-799.png) (independent control; Niese supplies numbering).

**Greek, earlier canonical cut with adjoining text:**

ντα ἐν Ἱεζερήλα πόλει ἐν τῷ Ναβώθου ἀγρῷ τὸ αἷμα αὐτοῦ κύνας ἀναλιχμήσεσθαι προειπεῖν, καθὼς καὶ Ναβώθου τοῦ δι᾽ αὐτὸν καταλευσθέντος ὑπὸ τοῦ ὄχλου.   **⟦candidate cut⟧** δῆλον οὖν, ὅτι οὗτος ψεύδεται τῷ κρείττονι προφήτῃ τἀναντία λέγων ἀπὸ ἡμερῶν τριῶν φάσκων τεθνήξεσθαι. γνώσεσθε δ᾽ εἴπερ ἐστὶν ἀληθὴς καὶ τοῦ θείου πνεύματος ἔχει τὴν δύναμιν: εὐθὺς γὰρ ῥαπισθεὶς ὑπ᾽ ἐμοῦ βλαψάτω μου τὴν χεῖρα, ὥσπερ Ἰάδαος τὴν Ἱεροβοάμου τοῦ βασιλέως συλλαβεῖν θελήσαντος ἀπεξήρανε δεξιάν:  ‘ἀκήκοας γὰρ οἶμαι τοῦτο πάντως

**Latin, earlier candidate with adjoining text:**

s, et indicio simul utebatur heliae prophetasset in lazara ciuitate in agro nabuth ei per eum a populo fuisset occisus quibus ab illo sic prophetatis  **⟦candidate cut⟧** micheam dicebat esse mendacem quando meliori prophetae dicere contraria uideretur. Cognoscentes inquit repente si ueras quae dicit iste, aut si potest spiritus sancti habere uirtutem. Caesus autem palmis a me non noceat meae manui sicuti ad unam extram regis hieroboam aridam fecit dum eum conpraehendere uoluisset, hoc enim omnibus notum e

`latin-book08-num401`; `/TEI[1]/text[1]/body[1]/div1[1]/div2[16]/p[4]/pb[1]/tail()`; node offset **1010**, paragraph offset **1847**, UTF-8 byte **127575** (zero-based, pinned LF bytes).

**Difficulty.** Latin quibus ab illo sic prophetatis is connective framing, while micheam dicebat esse mendacem supplies the first clear counterpart of the accusation in δῆλον οὖν ὅτι οὗτος ψεύδεται. The translation compresses the assertion and changes the syntax.

**Recommended treatment.** Retain the narrow candidate at micheam, documenting the compressed correspondence.

**Credible alternatives.** Begin at quibus ab illo sic prophetatis for wider context, or withhold a word-exact locator.

**Decision requested.** Approve the narrow accusation cut or explicitly broader context.

### VIII.409 — decision required

Affected Latin: `latin-book08-num401`.

Printed authority: Niese, *Flavii Iosephi Opera* II (1885), **p. 264**, PDF **272**. [Full page image](evidence/print-collation/niese-II-pdf-272.jpg).
[Loeb V, p.790, PDF798](evidence/print-collation/loeb-V-followup-798.png) (independent control; Niese supplies numbering).
[Loeb V, p.791, PDF799](evidence/print-collation/loeb-V-followup-799.png) (independent control; Niese supplies numbering).

**Greek, earlier canonical cut with adjoining text:**

χει τὴν δύναμιν: εὐθὺς γὰρ ῥαπισθεὶς ὑπ᾽ ἐμοῦ βλαψάτω μου τὴν χεῖρα, ὥσπερ Ἰάδαος τὴν Ἱεροβοάμου τοῦ βασιλέως συλλαβεῖν θελήσαντος ἀπεξήρανε δεξιάν:   **⟦candidate cut⟧** ‘ἀκήκοας γὰρ οἶμαι τοῦτο πάντως γενόμενον.’ ὡς οὖν πλήξαντος αὐτοῦ τὸν Μιχαίαν μηδὲν συνέβη παθεῖν, Ἄχαβος θαρρήσας ἄγειν τὴν στρατιὰν πρόθυμος ἦν ἐπὶ τὸν Σύρον: ἐνίκα γὰρ οἶμαι τὸ χρεὼν καὶ πιθανωτέρους ἐποίει τοῦ ἀληθοῦς τοὺς ψευδοπροφήτας, ἵνα λάβῃ τὴν ἀφορμὴν τοῦ τέλους. Σεδεκίας σιδήρεα ποιήσας κέρατα λέγει πρὸς Ἄχαβον, ὡς θεὸν αὐτῷ 

**Latin, earlier candidate with adjoining text:**

 habere uirtutem. Caesus autem palmis a me non noceat meae manui sicuti ad unam extram regis hieroboam aridam fecit dum eum conpraehendere uoluisset,  **⟦candidate cut⟧** hoc enim omnibus notum est. Cumque percusisset micheam et nihil fuisset passus, confortatus est achab in semetipsum contra regem syrorum mouit exercitum uincebat arbitror illut quod inminebat, et falsi propheta uerba plus quam erat ueritas credi uiliora faciebat ut ex occasione perueniretur ad finem. Tunc ex orans sedechias et faciens cor

`latin-book08-num401`; `/TEI[1]/text[1]/body[1]/div1[1]/div2[16]/p[4]/pb[1]/tail()`; node offset **1326**, paragraph offset **2163**, UTF-8 byte **127891** (zero-based, pinned LF bytes).

**Reassessed proposal / alternative, not applied:**

ῦ βλαψάτω μου τὴν χεῖρα, ὥσπερ Ἰάδαος τὴν Ἱεροβοάμου τοῦ βασιλέως συλλαβεῖν θελήσαντος ἀπεξήρανε δεξιάν:  ‘ἀκήκοας γὰρ οἶμαι τοῦτο πάντως γενόμενον.’  **⟦candidate cut⟧** ὡς οὖν πλήξαντος αὐτοῦ τὸν Μιχαίαν μηδὲν συνέβη παθεῖν, Ἄχαβος θαρρήσας ἄγειν τὴν στρατιὰν πρόθυμος ἦν ἐπὶ τὸν Σύρον: ἐνίκα γὰρ οἶμαι τὸ χρεὼν καὶ πιθανωτέρους ἐποίει τοῦ ἀληθοῦς τοὺς ψευδοπροφήτας, ἵνα λάβῃ τὴν ἀφορμὴν τοῦ τέλους. Σεδεκίας σιδήρεα ποιήσας κέρατα λέγει πρὸς Ἄχαβον, ὡς θεὸν αὐτῷ σημαίνειν τούτοις ἅπασαν καταστρέψεσθαι τὴν 

em palmis a me non noceat meae manui sicuti ad unam extram regis hieroboam aridam fecit dum eum conpraehendere uoluisset, hoc enim omnibus notum est.  **⟦candidate cut⟧** Cumque percusisset micheam et nihil fuisset passus, confortatus est achab in semetipsum contra regem syrorum mouit exercitum uincebat arbitror illut quod inminebat, et falsi propheta uerba plus quam erat ueritas credi uiliora faciebat ut ex occasione perueniretur ad finem. Tunc ex orans sedechias et faciens cornua ferrea dixit ad achab un

`latin-book08-num401`; `/TEI[1]/text[1]/body[1]/div1[1]/div2[16]/p[4]/pb[1]/tail()`; node offset **1354**, paragraph offset **2191**, UTF-8 byte **127919** (zero-based, pinned LF bytes).

Neighbouring extent change: 408 ends at the proposed cut instead of the old cut; 409 begins there and still ends at 410. Exact before/after offsets are in the boundary reassessment and DECISION_HISTORY.json.

**Difficulty.** Canonical Greek 409 starts at ἀκήκοας, with its first syllables on the preceding line; Niese p.264 places 409 beside the line containing the end of that quotation and ὡς οὖν. Loeb p.790 places 409 at the new narrative ὡς οὖν πλήξαντος. The earlier Latin hoc enim omnibus notum est belongs to the closing quotation.

**Recommended treatment.** Propose Greek ὡς οὖν πλήξαντος and Latin Cumque percusisset micheam as the paired start. Return the closing quotation to the proposed 408 extent.

**Credible alternatives.** Retain canonical ἀκήκοας / hoc enim omnibus notum est, admitting the split quotation.

**Decision requested.** Accept or reject the proposed paired relocation of 409.

## Displaced inherited labels and future representation

An eventual implementation must preserve every visible composite `<num>` label, existing xml:id, sameAs, paragraph and traditional chapter/subchapter division. Certified citation locators would separately define executable Niese starts and suppress displaced inherited numeric claims. The current reader scans labels and milestones, so inserting a new milestone alone would leave duplicate/false identities. A future data-driven locator/override facility and full rendering QA are prerequisites. No such production change is included here.

The candidate dry-run and arithmetic in the checkpoint are mechanical evidence only. They must be recomputed if a proposed Greek/Latin cut or the VIII.367 representation is accepted. No candidate plan is authorized for application.
