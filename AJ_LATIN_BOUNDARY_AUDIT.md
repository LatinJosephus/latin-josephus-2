# AJ Latin boundary audit — 25 October 2026

**Disposition: GO for the local derived-layer repair.** All 31 DEH records and 44 AJ correspondence components were checked against the approved current Latin XML. All 140 Latin section occurrences are accounted for (139 available, one inherited unavailable occurrence). No new boundary needs editorial adjudication.

Current source base: `5bb301c1b41d63c89c33a79826fc62892ac3890f`. Historical derivation base: `38af60ff42ea733d3494d713c1f6f4450f624205`.

## Method and scholarly scope

This is an agent textual boundary review of the established project correspondence, followed by automated coordinate and extraction validation. It is not a new manuscript collation or an independent adjudication of the printed Ussani/Mras citations. The frozen references, order, annotations and prior approvals remain authoritative. Related narrative material is not recast as exact verbal equivalence.

The eight historical XML files were recovered from the historical Git revision and matched to their original SHA-256 pins. Every old selected interval independently matches the October 14 XML expectations (oracle SHA-256 `e03fc59b1b0d6c85a2c47c0eb17d3d996ebe4b12c0c6a3340d9cf1da36a07fb9`). Each current XML body has exactly the same ordered elements and attributes as its historical counterpart. Current boundary node identities, surrounding text and full selected passages were then checked, with current positions recomputed independently using an ElementTree text walk. Actual browser DOM Ranges subsequently verified all available Latin endpoints and excerpts.

## Results

- 43 components retain both their boundary definitions and selected text; one retains its boundaries and incorporates an already approved textual correction.
- No child path or boundary side changes are required. Absolute body-text offsets change at 164 of the 278 available span endpoints, despite the unchanged paths.
- AJ IX.216 / DEH II.12.3 loses the embedded ` Hoc ergo tibi`, as already authorized by candidate `S27-B09-216-HOC-ERGO-TIBI` in `review/Bamberg_Substantive_Closeout_v3_4/approved_correction_manifest.json` and integrated by commit `123d82f631602ccad174daea38e99d6a64d3e69f`. The range remains after milestone 216 and before milestone 217 in `latin-book09-num215`. The repair adopts the current source; it does not perform that deletion.
- Preserve `latin-book09-num51` exclusions, the Latin XX.238 unavailable interval, all witness qualifications, component order and the open XV.38 et sqq. citation. Its displayed XV.38–56 remains the prior P4-D07 approved excerpt; no endpoint is inferred here.

Offsets below are half-open positions in XML-parser-normalized **body text**, including whitespace and annotation text. CP means Unicode codepoints; U16 means UTF-16 code units. These are recalculated audit coordinates, not serialized XML byte positions and not a new runtime offset model. The runtime continues to resolve element-child paths and sides. JSON evidence additionally records exact raw selected text, endpoint attributes, nearest XML IDs, and 70-character contexts on each side.

## Authority hashes

| Source | Historical SHA-256 | Current SHA-256 |
| --- | --- | --- |
| `assets/xml/antiquities/Latin/book-14.xml` | `beeaa404131ffeb8a29aec12b9ac9a67270223e72638c9169d85a9e2d7f1f9a3` | `211f49930eef6fa3a93836b8d18e32a3afa05656307e75d91e3d59d428485a76` |
| `assets/xml/antiquities/Latin/book-15.xml` | `39115de0689b35ad0185f5e21a81127637cd2dfb94cac49cb6bda49eee5d7149` | `6b563b6bfa0ddd96c52030377043440e88aa90dd83913c67b5c940f4fcb02485` |
| `assets/xml/antiquities/Latin/book-16.xml` | `8fb15391bafc87b7fc251269c6cbe78b9b2f3d782156d413b7b2317649420e7c` | `25151895a46d2c8d9d6fba53bdcf92afadc689ab834a7fd4d152f1df6acc12fa` |
| `assets/xml/antiquities/Latin/book-17.xml` | `859a12f93a7f42478a796420c9b22db449b94fcadeb55255be4324f8ef5a186d` | `efdcd622593626a3b9740745c1b1e23755b07d59c3423a02e76c453ed7df8c2b` |
| `assets/xml/antiquities/Latin/book-18.xml` | `0afb40d0a03c42520fafe4357ae13c9ac9447c25d4f2d7736121ccd57ad917ec` | `dec6665c846a7f90227502fffbc949bd0c571ed0e958ed0be1b95047a0b3be50` |
| `assets/xml/antiquities/Latin/book-20.xml` | `60040f2fecc074f37ca03dddc5f66d438246d60ec9e85319623b3a6124f5f877` | `84308f674a71fdb50a44f17097d48a1d57a79ae8b260cb69fa0afad0c187caa7` |
| `assets/xml/antiquities/Latin/book-09.xml` | `206ca5bed674f7ebaa750dd8357c82d90510cb71162477a8214c5b8ccbd284c0` | `a018cf1fce87300451a6988c002e3a95be991ea6a685b443cceb27e387084640` |
| `assets/js/renderTei.js` | `03bfb9b0de5e13e6b07bd638413b2b82a9ed2f7b0cc7c33eb6c09dabde3c9294` | `39ded95fc3b7fdf39d9827cf513e6fc6c88922bb039435446b48b22ec4192848` |
| `assets/xml/antiquities/Latin/book-03.xml` | `8750c56152f750fbc1bd7c5d28e07cc73972bf1a86ed3221f79824e1c0573c97` | `4e2f268e05cd88a5cedccab1b0c9e8fd3315f013d89516eb17ca7c4c49ce6e59` |

The current renderer retains the complete previously recovered numbering helper and call. Its relevant extraction behaviour is tested against all AJ witnesses in the actual browser. The exact current renderer pin is retained; no dependency or integrity check was removed.

## Every affected correspondence

The following sections give the DEH passage and every ordered AJ component. For each section, old/new boundary definitions and CP/U16 coordinates are explicit. When selected text is identical, one passage is labelled Old = current; changed text is printed twice. Raw, unnormalized old/new selections are preserved in `_docs/aj-latin-reconciliation/certified-boundaries.json`.

### DEH I.15.3 — `deh-1-15-3`

Canonical source ID: `latin-deh1-num45`.

**DEH Latin passage:**

> [I.15.3] Pompeius quoque fugientem insequi, clausum urguere neque parandis belli usibus tempus ullum dare. Direxit Magni intentionem de Mitridate nuntius quod morte bellum finisset; urbs Hiericho in finitimis suis Pompeium tenebat, cum rei memoratae indicia uenere, locus prope urbem in quo balsamum gignitur uirgultisque innascitur, quae acutis lapidibus incidunt pueri agricolarum, perque eas incisiones distillat humor lacrimis pulcher rorantibus. Inde uir militiae uetus conpositis ordinibus ad uesperum castra mouit et primo diluculo Hierosolymitanis moenibus adstitit atque improuisus armatas acies infudit.

#### `deh-1-15-3-aj-2` — AJ 14.54–54

Classification: **BOUNDARIES_AND_SELECTED_TEXT_RETAINED**. Old and current child paths/sides are retained. Intended passage: the existing frozen AJ target, in its recorded order.

Same ordered XML elements and attributes as the certified historical witness; each old interval matches independent October 14 XML expectations; current start/end identities, complete selected text and recomputed offsets checked. Frozen reference retained without expanding the passage.

| Section | Old boundary → current boundary | CP old → current | U16 old → current |
| --- | --- | --- | --- |
| 54 | `1.1.1.0.0.0.13.0:before → 1.1.1.0.0.0.13.1:before` → same | `20634:20793` → `20634:20793` | `20634:20793` → `20634:20793` |

**AJ 14.54**

Old = current selected passage:

> [IV.i.54] Cumque in hiericho castra posuisset ubi maxime nascitur opobalsamum cuius cum flos acuto lapide incisus fuerit destillat, mane ierosolimis ascendit,

### DEH I.16.3 — `deh-1-16-3`

Canonical source ID: `latin-deh1-num48`.

**DEH Latin passage:**

> [I.16.3] Sed pluribus quos terror potentiae Romanae auxerat, cessere inferiores atque in templum se recepere soluto ponte, qui transitu peruio urbem ac templum medius coniunxerat. Receptus itaque in urbem est exercitus Romanus, et suis manibus Iudaei aperuere portas non multo post urbis ac templi expugnatoribus futuris conpletumque est illud Dauiticum: deus, uenerunt gentes in hereditatem tuam, polluerunt templum sanctum tuum. Sponte itaque tradidere regalia sua, cessere aulicis. Pisoni claro inter suos uiro et militiae stipendiis exercitato id negotii commissum, ut manu ualida aulam regiam ceteraque urbis tuenda existimaret. Quod ab eo sollicite curatum, quasi ad ea defendenda potius quam occupanda Romanum exercitum ductauerit.

#### `deh-1-16-3-aj-2` — AJ 14.59–59

Classification: **BOUNDARIES_AND_SELECTED_TEXT_RETAINED**. Old and current child paths/sides are retained. Intended passage: the existing frozen AJ target, in its recorded order.

Same ordered XML elements and attributes as the certified historical witness; each old interval matches independent October 14 XML expectations; current start/end identities, complete selected text and recomputed offsets checked. Frozen reference retained without expanding the passage.

| Section | Old boundary → current boundary | CP old → current | U16 old → current |
| --- | --- | --- | --- |
| 59 | `1.1.1.0.0.0.14.1:after → 1.1.1.0.0.0.14.5:before` → same | `21775:21947` → `21775:21947` | `21775:21947` → `21775:21947` |

**AJ 14.59**

Old = current selected passage:

> Alii autem exercitum pompei susceperunt, et aulam ei tradireunt. Pompeius autem pisonem legatum cum exercitu destinauit palatium custodire et domus uel templum obseruare,

### DEH I.24.3 — `deh-1-24-3`

Canonical source ID: `latin-deh1-num71`.

**DEH Latin passage:**

> [I.24.3] Quibus egregie Caesar delectatus in honore Antipatrum, ut oportebat, inter amicos recepit. Deinde ubi ea quae in Aegypto constituenda forent disposuit atque in Syriam processit, Romanae eum rei publicae honoribus adfectat, ateliam quoque contulit ceteraque ut probato sibi uiro gratiae suae pignora impertiuit. Hyrcano etiam summum sacerdotium de sententia Antipatri uolens firmauit.

#### `deh-1-24-3-aj-2` — AJ 14.137–137

Classification: **BOUNDARIES_AND_SELECTED_TEXT_RETAINED**. Old and current child paths/sides are retained. Intended passage: the existing frozen AJ target, in its recorded order.

Same ordered XML elements and attributes as the certified historical witness; each old interval matches independent October 14 XML expectations; current start/end identities, complete selected text and recomputed offsets checked. Frozen reference retained without expanding the passage.

| Section | Old boundary → current boundary | CP old → current | U16 old → current |
| --- | --- | --- | --- |
| 137 | `1.1.1.0.0.0.33.0:before → 1.1.1.0.0.0.33.1:before` → same | `40672:40850` → `40672:40850` | `40672:40850` → `40672:40850` |

**AJ 14.137**

Old = current selected passage:

> [VIII.iii.137] ergo bello finito caesar cum in syriam nauigasset, hyrcano quidem principatum sacerdotii firmum indulsit. Antipatrum uero uicem romanum et sine censum constituit.

### DEH I.36.2 — `deh-1-36-2`

Canonical source ID: `latin-deh1-num136`.

**DEH Latin passage:**

> [I.36.2] Diligebat interea Mariammen inpenso amore nec offensam uolebat. Cumulauerat mulieri gratiam numerosior partus. Nam quinque ei generauerat filios, sed ex tribus maribus iunior Romae obierat, dum litteris inbuitur liberalibus. Reliqui duo ultra priuatorum modum regio cultu celebrabantur. Suffragio erat iuuenibus matris nobilitas et suus in regno ortus, quod imperante iam patre geniti forent, sed amor maxime Mariammes, quo rex magis magisque cotidie accendebatur, ut cum ipsi nulla uicissitudo amoris a coniuge rependeretur, caueret tamen ne in aliquo mulieris animum maestificaret. Aequa lance odium mulieris et amor uiri aduersum se certabant. Iustius tamen Mariamme amantem sibi uirum oderat, quam Herodes Mariammen non amantem amabat, suppetebat mulieri odium de flagitio, fiducia de amore, quia alterum, dolore neptis, auersabatur, altero per obsequium amantis extollebatur. Et ideo ne a conuicio quidem obiciendorum criminum temperauit, quod auum sibi Hyrcanum et fratrem Ionathen per scelus eripuisset, cum alius prosocer, alius adfinis, ille propter senectutis infirmum reseruari debuerit, hic saltem propter aetatem adulescentulam. Facinus indignum, cui septemdecim annorum adulescenti summum commiserat sacerdotium, huic continuo honorem contulit et mortem intulit nulla alia causa, ut accepimus, nisi quod sacerdotali amictu indutus, ubi primum accessit ad altaria sacrato et celebri die, subito populus inlacrimauit. Quod suspectum adeo Herodi fuit, ut prae gaudio populum crederet inlacrimasse atque eo erga ephebum prodidisse affectum suum, lacrimas illas uoti indices, studium populi sibi periculosum, qui intimis uisceribus significauerit quod studium erga cultum adulescentis haberet, nobilem illum regium nepotem, inpotentis mulieris filium, fratrem reginae proteruioris, quae regem uirum dedignaretur, prorupturum ad imperandum, nisi maturius sublatus e medio foret, cui forma, cui decoris gratia suppeteret, ut iure praeferendus omnibus aestimaretur. Proposuit itaque adulescentem occidere. Exagitabat eum mater adulescentis, quae et ad inuestigandum acrior et ad ulciscendum uehementior nihil occultum nihilque inultum patiebatur, eoque reuocare sese ac reprimere deliberabat: rursus exagitabat eum cumulatior in dies erga adulescentem amor uniuersorum et regni periculum. Vnde praerupto furore excitus statuit quouis modo sibi consulere.

#### `deh-1-36-2-aj-2` — AJ 15.52–52

Classification: **BOUNDARIES_AND_SELECTED_TEXT_RETAINED**. Old and current child paths/sides are retained. Intended passage: the existing frozen AJ target, in its recorded order.

Same ordered XML elements and attributes as the certified historical witness; each old interval matches independent October 14 XML expectations; current start/end identities, complete selected text and recomputed offsets checked. Frozen reference retained without expanding the passage.

| Section | Old boundary → current boundary | CP old → current | U16 old → current |
| --- | --- | --- | --- |
| 52 | `1.2.9.2:after → 1.2.9.3:before` → same | `12213:12568` → `12213:12568` | `12213:12568` → `12213:12568` |

**AJ 15.52**

Old = current selected passage:

> populi sui excitauit fauorem, et aristoboli aui sui praesens memoriam ei reduxit. Qui paulatim irritati uoluntates suas iam demonstrabant gaudentes simul et laetitia perfusi, uocesque laudabiles in eum orationibus mixtas emittebant. Ut manifestus fieret populi fauor et temerarius, sub regno itaque constituti cum aliorum praeterita beneficia memorarent.

#### `deh-1-36-2-aj-3` — AJ 15.49–49

Classification: **BOUNDARIES_AND_SELECTED_TEXT_RETAINED**. Old and current child paths/sides are retained. Intended passage: the existing frozen AJ target, in its recorded order.

Same ordered XML elements and attributes as the certified historical witness; each old interval matches independent October 14 XML expectations; current start/end identities, complete selected text and recomputed offsets checked. Frozen reference retained without expanding the passage.

| Section | Old boundary → current boundary | CP old → current | U16 old → current |
| --- | --- | --- | --- |
| 49 | `1.2.8.11:after → 1.2.9.0:before` → same | `11615:11721` → `11615:11721` | `11615:11721` → `11615:11721` |

**AJ 15.49**

Old = current selected passage:

> Proposuit tamen omnibus modis adulescentem perimere, sed tacito propter uerisimilem dissimulationem.

### DEH I.37.1 — `deh-1-37-1`

Canonical source ID: `latin-deh1-num137`.

**DEH Latin passage:**

> [I.37.1] Mittitur adulescens nocturnis temporibus ad urbem Hiericho atque ibi solitus delectari studio natandi, plurimis quasi in ludum coeuntibus, dum sine modo mergitur, in piscina necatur.

#### `deh-1-37-1-aj-2` — AJ 15.55–55

Classification: **BOUNDARIES_AND_SELECTED_TEXT_RETAINED**. Old and current child paths/sides are retained. Intended passage: the existing frozen AJ target, in its recorded order.

Same ordered XML elements and attributes as the certified historical witness; each old interval matches independent October 14 XML expectations; current start/end identities, complete selected text and recomputed offsets checked. Frozen reference retained without expanding the passage.

| Section | Old boundary → current boundary | CP old → current | U16 old → current |
| --- | --- | --- | --- |
| 55 | `1.2.9.5:after → 1.2.9.7:before` → same | `13018:13275` → `13018:13275` | `13018:13275` → `13018:13275` |

**AJ 15.55**

Old = current selected passage:

> prius quidem natantes seruos et amicos prospiciebant. Post autem adulescens cum irritaretur, herodis amici quibus hoc praeceptum fuerat tenebris iam tenentibus saepe eum mergentes tamquam eludentes non emiserunt usque quo eum pressum fontibus suffocarent.

### DEH I.37.2 — `deh-1-37-2`

Canonical source ID: `latin-deh1-num138`.

**DEH Latin passage:**

> [I.37.2] Id tacitum soror non tulit, sed affectu germanitatis per conuicium prodidit atque obiectauit marito iussu eius sibi fratrem ereptum. Destitutam se omnibus, funestam sibi domum coniugis, qui primo sibi auum ademerit, postea germanum interemerit, miseram se exitio suis fuisse. Inprecari dira uiro socrui et regis sorori; commune omnium flagitium, ultorem deum poscere, ne tantum facinus inpunitum relinqueretur. Ferebat ista Herodes quasi amore captus et nutibus deditus, sed furebant mulieres et ferre non poterant maledicta exsecrantis et indignantis adrogantiam, maxime quia uictus miraculo eius Herodes insurgere aduersus dilectam nequibat. Et ideo quo magis excitari quasi amans posset, scena adulterii contexitur atque in mulierem istiusmodi crimen conponitur, quod imaginem suam Antonio in Aegypto destinauisset. Quantae istud intemperantiae fuisse, ut absenti et promto in libidines uiro, tum praeterea potenti, qui potestate pro iure uteretur, formam suam uenalem offerret, ut pulchritudinem licitaretur! Nouae auctionis commercio se mulierem prostituisse uine amoris an odio mariti, cuius periculum pro mercede adulterii postulauisset. Hoc itaque commento mulierum apud Herodem Mariamme quo magis amabatur eo grauius adpetebatur, nec tamen insimulatio ipsa quamuis indignantium feminarum aliena ueri penitus fuit. Matrem enim Alexandriam furentem, quod alius filio suo Aristobolo in sacerdotio praeferebatur — hoc enim nomine Ionathan filium suum, quo auum sibi regem fuisse in memoriam reduceret, appellari malebat —, ab Antonio per musurgam quendam litterarum sequestrem petisse filio sacerdotium fides uero propior erat. Deinde adueniente in Iudaeam Gellio Antoni amico cognitum adulescentem miraculo fuisse propter excellentissimi decoris gratiam, non minus etiam Mariammen, cuius quo dignitas clarior, eo fama inlustrior, et forte conpertam more quodam humani ingenii, quo uiri quoque eo se interioribus amicis cariores cupiant declarare, si praesentibus quoque necessitudinibus suis mensae hospitalis societatem indulgeant.

#### `deh-1-37-2-aj-2` — AJ 15.23–25

Classification: **BOUNDARIES_AND_SELECTED_TEXT_RETAINED**. Old and current child paths/sides are retained. Intended passage: the existing frozen AJ target, in its recorded order.

Same ordered XML elements and attributes as the certified historical witness; each old interval matches independent October 14 XML expectations; current start/end identities, complete selected text and recomputed offsets checked. Frozen reference retained without expanding the passage.

| Section | Old boundary → current boundary | CP old → current | U16 old → current |
| --- | --- | --- | --- |
| 23 | `1.2.4.0:after → 1.2.4.1:before` → same | `6374:6570` → `6374:6570` | `6374:6570` → `6374:6570` |
| 24 | `1.2.4.1:after → 1.2.5.0:before` → same | `6570:6815` → `6570:6815` | `6570:6815` → `6570:6815` |
| 25 | `1.2.5.0:after → 1.2.5.1:before` → same | `6815:7110` → `6815:7110` | `6815:7110` → `6815:7110` |

**AJ 15.23**

Old = current selected passage:

> quod non pertulit alexandra filia hyrcani uxor alexandri filii aristoboli regis ex quo filios habuit. Unum quidem pulcherrimum aristobolum nomine et herodis iugalem, mariamnem forma nobilissimam,

**AJ 15.24**

Old = current selected passage:

> turbata ergo et moleste ferens infamiam filii, quod illo superstite, alter aduena principatum sacerdotii meruisset, scripsit cleopatrae, sodale quodam suo litteras deportante, ut peteret antonium principatum sacerdotii filio suo praestare,

**AJ 15.25**

Old = current selected passage:

> sed et antonio neglegente petitionem, amicus eius gellius ad iudaeam cum propter aliquas, causas peruenisset et uidisset aristoboli pulchritudinem et magnitudinem uel iuuentutem mirabatur, non minus etiam mariamen regi cohabitantem stupebat, unde alexandram bonorum liberorum matrem existimans,

### DEH I.37.3 — `deh-1-37-3`

Canonical source ID: `latin-deh1-num139`.

**DEH Latin passage:**

> [I.37.3] Ibi quoque Alexandriae datam cum Sossio conloquendi copiam, licet liberiori uiduae alia quoque cognoscendi hospitis deesse copia non potuerit, cum praesertim huiusmodi et causas et personas requireret. Deinde conlato utrimque consilio id sedisse sententiae, uti utriusque imagines Antonio dirigerentur. Praestrictum illum splendore imaginum et Sossi praecipue testimonio, qui nihil tale se umquam uidisse in terris adseueraret et gratiam illis non hominum sed diuinam inesse, lenocinanter ut excitaret uiri minime sobrias cupiditates, scripsisse Herodi ut Aristobolum ad se sine mora mitteret, de Mariamme quod ei coniuncta foret praetermisisse, non quo operire libidines suas uel in his quae nuptae essent apud maritos soleret, cui sine periculo usus foret, flagitium sine pudore, sed quo Cleopatrae caueret indignationem, quae utriusque quidem sexus riuali offenderetur, sed amplius si sociatam uiro mulierem deprehendisset, quia se decore super omnes excellere mulieres arbitrabatur. Perlectis itaque litteris Herodem excusauisse, quod sine seditione populi et perturbatione totius gentis auellere a suis nobilem non posset adulescentem atque ut satisfaceret Alexandriae, spopondisse Aristobolo sacerdotium, sed cum moram fieri promissis et arte se ludi putaret, Alexandriam parasse nauigium atque in ipso fugae apparatu cognito per Sabbionem consilio reuocatam esse cum filio. His motum Herodem dissimulasse ad tempus iniuriam et adcelerasse Aristobolo sacerdotii conlationem, ut honoris specie paratae necis inuidiam uelaret.

#### `deh-1-37-3-aj-2` — AJ 15.26–34

Classification: **BOUNDARIES_AND_SELECTED_TEXT_RETAINED**. Old and current child paths/sides are retained. Intended passage: the existing frozen AJ target, in its recorded order.

Same ordered XML elements and attributes as the certified historical witness; each old interval matches independent October 14 XML expectations; current start/end identities, complete selected text and recomputed offsets checked. Frozen reference retained without expanding the passage.

| Section | Old boundary → current boundary | CP old → current | U16 old → current |
| --- | --- | --- | --- |
| 26 | `1.2.5.1:after → 1.2.5.2:before` → same | `7110:7229` → `7110:7229` | `7110:7229` → `7110:7229` |
| 27 | `1.2.5.2:after → 1.2.5.3:before` → same | `7229:7415` → `7229:7415` | `7229:7415` → `7229:7415` |
| 28 | `1.2.5.3:after → 1.2.5.4:before` → same | `7415:7585` → `7415:7585` | `7415:7585` → `7415:7585` |
| 29 | `1.2.5.4:after → 1.2.5.6:before` → same | `7585:7867` → `7585:7867` | `7585:7867` → `7585:7867` |
| 30 | `1.2.5.6:after → 1.2.6.0:before` → same | `7867:8025` → `7867:8025` | `7867:8025` → `7867:8025` |
| 31 | `1.2.6.0:after → 1.2.6.1:before` → same | `8025:8380` → `8025:8380` | `8025:8380` → `8025:8380` |
| 32 | `1.2.6.1:after → 1.2.6.2:before` → same | `8380:8557` → `8380:8557` | `8380:8557` → `8380:8557` |
| 33 | `1.2.6.2:after → 1.2.6.3:before` → same | `8557:8760` → `8557:8760` | `8557:8760` → `8557:8760` |
| 34 | `1.2.6.3:after → 1.2.6.4:before` → same | `8760:8966` → `8760:8966` | `8760:8966` → `8760:8966` |

**AJ 15.26**

Old = current selected passage:

> et ad sermonem eius ueniens, flectit eam pingere amborum imagines, ea quidem petitiones eius modis omnibus adimpleuit.

**AJ 15.27**

Old = current selected passage:

> His elata uerbis alexandra imagines antonio direxit. Cui gellius ferebat dicens, non ab homine putari sed a quodam esse deo liberos alexandrae dum uellet ad libidines antonium emollire.

**AJ 15.28**

Old = current selected passage:

> Qui puellam quidem erubuit herodi nuptam accersire uerum etiam cleopatram metuens contristari. Scripsit ergo puerum transmitti cum honore, addens nisi graue uisum foret,

**AJ 15.29**

Old = current selected passage:

> his deportatis ad herodem litteris non cautum existimauit iuuenem excellentem aristobolum, et tunc iam sedecim annos ducentem genere nobilissimo, ad antonium destinare potentissimum romanorum et paratum suae luxuriae subponere puerum, qui etiam libidinosus per potentiam existebat.

**AJ 15.30**

Old = current selected passage:

> Rescripsit ergo dicens, si puer exierit a prouincia, statim omnia bello uel seditionibus, complebuntur, iudaeis sperantibus posterum nouarum mutationem.

**AJ 15.31**

Old = current selected passage:

> Quibus rescriptis cum antonio excusasset, iudicauit non ultra puerum uel alexandram humiliare, sed etiam uxore sua mariamne ualde petente quatinus fratri suo principatum sacerdotii redderet quod prodesse arbitratus est, dum nec ad antonium proficisci posset tali praeditus adulescens honore. Conuentum itaque faciens amicorum, multum alexandram accusabat

**AJ 15.32**

Old = current selected passage:

> dicendo latenter insidias egisse pro principatu, dum per cleopatram ageret, quatinus ipse quidem regno priuaretur. Puer autem pro ipso rerum gubernatione ab antonio susciperet,

**AJ 15.33**

Old = current selected passage:

> et haec quidem illam non iuste postulasset quod et filiam suam a possesso iam honore priuaret, et seditiones in regno moueret, cum multum ipse laborasset ut possideret multis et non fortuitis periculis,

**AJ 15.34**

Old = current selected passage:

> uerum etiam millatenus memor ipse malorum illius, sed beniuolus circa eos esset, et nunc puero principatum sacerdotii praeberet. Ideoque olim ordinasse dicebat ananelogum, quod ualde puer esset aristobolus

#### `deh-1-37-3-aj-3` — AJ 15.44–49

Classification: **BOUNDARIES_AND_SELECTED_TEXT_RETAINED**. Old and current child paths/sides are retained. Intended passage: the existing frozen AJ target, in its recorded order.

Same ordered XML elements and attributes as the certified historical witness; each old interval matches independent October 14 XML expectations; current start/end identities, complete selected text and recomputed offsets checked. Frozen reference retained without expanding the passage.

| Section | Old boundary → current boundary | CP old → current | U16 old → current |
| --- | --- | --- | --- |
| 44 | `1.2.8.3:after → 1.2.8.4:before` → same | `10414:10646` → `10414:10646` | `10414:10646` → `10414:10646` |
| 45 | `1.2.8.4:after → 1.2.8.5:before` → same | `10646:10819` → `10646:10819` | `10646:10819` → `10646:10819` |
| 46 | `1.2.8.5:after → 1.2.8.6:before` → same | `10819:11104` → `10819:11104` | `10819:11104` → `10819:11104` |
| 47 | `1.2.8.6:after → 1.2.8.7:before` → same | `11104:11359` → `11104:11359` | `11104:11359` → `11104:11359` |
| 48 | `1.2.8.7:after → 1.2.8.11:before` → same | `11359:11615` → `11359:11615` | `11359:11615` → `11359:11615` |
| 49 | `1.2.8.11:after → 1.2.9.0:before` → same | `11615:11721` → `11615:11721` | `11615:11721` → `11615:11721` |

**AJ 15.44**

Old = current selected passage:

> quae paulatim magis illam exacerbabant et inodio suscitabant. Nam superbia mulieris, diligentiam custodiae indignabatur habere, dum omnia uellet potius pati quam fiducia priuari, et fucosum honorem cum seruitute uel metu possidere.

**AJ 15.45**

Old = current selected passage:

> Ad cleopatram igitur in quibus existeret, frequener se lamentando destinabat, postulans auxilium sibi praeberi, quae iussit ei furtim cum filio in aegyptum ad se confugere.

**AJ 15.46**

Old = current selected passage:

> Cumque hoc ei placuisset tale aliquid excogitauit, duo locula tamquam pro mortuorum exequiis parauit, in quibus se ipsam et filium mitti dixit, praecipiens consciis famulis ea noctu deferre, et exinde uiam ad mare facere, ubi nauem in qua nauigarent ad aegyptum praeparatam habuisset.

**AJ 15.47**

Old = current selected passage:

> Haec sabbioni amico alexandro esopus seruus eius edixit. Quod cum sabbio audisset et inimicus herodis esset, quod inter insidiatores antipatri de ueneno conscius putaretur, odium lenire per indicationis fauorem sperauit, et renuntiat insidias alexandrae.

**AJ 15.48**

Old = current selected passage:

> Qui cum eam usque ad conatum procedere demisisset, in ipso facinoris opere detinuit, sed inuitus concessit culpam, dum putaret et nullatenus cleopatram cessare si contra se causam inuenisset. Palam ergo magnanimitate uel modestia, ueniam ei largitus est.

**AJ 15.49**

Old = current selected passage:

> Proposuit tamen omnibus modis adulescentem perimere, sed tacito propter uerisimilem dissimulationem.

### DEH I.37.4 — `deh-1-37-4`

Canonical source ID: `latin-deh1-num140`.

**DEH Latin passage:**

> [I.37.4] Qua peracta, ut diximus, quasi fulmine ictus, exagitatus est simul et affectati adulteri adficto a suis crimine, quod sciret Antonium promtum ad libidines, et inuelatas, ex eo quod plurimum poterat, inflammantem in omne genus amatorium cupiditates; Cleopatrae quoque inexpiabilem riualitatis praecipue dolorem immanitatemque plurimos uirorum quos segniores circa uxorum reprimendam intemperantiam conpererat interemisse. Imminere sibi periculum non solum amittendae coniugis sed etiam subeundae mortis perhorrescebat. Proposuit itaque ipse contendere in Aegyptum ut Antonium uel Cleopatram quam maxime metuebat flecteret. Euocatum alii ferunt Antoni litteris eo tetendisse ut necati adulescentis causas praestaret.

#### `deh-1-37-4-aj-2` — AJ 15.64–64

Classification: **BOUNDARIES_AND_SELECTED_TEXT_RETAINED**. Old and current child paths/sides are retained. Intended passage: the existing frozen AJ target, in its recorded order.

Same ordered XML elements and attributes as the certified historical witness; each old interval matches independent October 14 XML expectations; current start/end identities, complete selected text and recomputed offsets checked. Frozen reference retained without expanding the passage.

**Retained annotations:** `[{"segment_order": 3, "raw_token": "(= alii)", "expression_offset": 25, "content": "= alii", "type": "alternative_tradition", "raw_value": "alii", "target_orders": [2, 3], "interpretation": "alii identifies the AJ material as an alternative tradition corresponding to DEH’s alii ferunt. Associate it with AJ XV.64 and XV.67, without a stronger source-critical claim.", "editorial_status": "human_approved_annotation", "editorial_decision": "P4-D10", "adjudication_date": "2026-10-02"}]`

| Section | Old boundary → current boundary | CP old → current | U16 old → current |
| --- | --- | --- | --- |
| 64 | `1.2.11.5:after → 1.2.11.6:before` → same | `15174:15375` → `15174:15375` | `15174:15375` → `15174:15375` |

**AJ 15.64**

Old = current selected passage:

> Quibus cum flexus esset antonius ad lauditiam perueniens, mittit praecipiens herodem ad se proficisci sibique pro morte aristoboli satisfacere, nam non recte insidiae confectae si per eum extitissent.

#### `deh-1-37-4-aj-3` — AJ 15.67–67

Classification: **BOUNDARIES_AND_SELECTED_TEXT_RETAINED**. Old and current child paths/sides are retained. Intended passage: the existing frozen AJ target, in its recorded order.

Same ordered XML elements and attributes as the certified historical witness; each old interval matches independent October 14 XML expectations; current start/end identities, complete selected text and recomputed offsets checked. Frozen reference retained without expanding the passage.

**Retained annotations:** `[{"segment_order": 3, "raw_token": "(= alii)", "expression_offset": 25, "content": "= alii", "type": "alternative_tradition", "raw_value": "alii", "target_orders": [2, 3], "interpretation": "alii identifies the AJ material as an alternative tradition corresponding to DEH’s alii ferunt. Associate it with AJ XV.64 and XV.67, without a stronger source-critical claim.", "editorial_status": "human_approved_annotation", "editorial_decision": "P4-D10", "adjudication_date": "2026-10-02"}]`

| Section | Old boundary → current boundary | CP old → current | U16 old → current |
| --- | --- | --- | --- |
| 67 | `1.2.11.9:after → 1.2.12.0:before` → same | `15852:16028` → `15852:16028` | `15852:16028` → `15852:16028` |

**AJ 15.67**

Old = current selected passage:

> per quae demonstrabat impetum antonii quem in eam habuisset, cum olim de pulchritudine illius audisset. Herodes quidem haec praecipiens, spe incerta ad antonium perrexit.

### DEH I.37.5 — `deh-1-37-5`

Canonical source ID: `latin-deh1-num141`.

**DEH Latin passage:**

> [I.37.5] Profecturus tamen adfini suo Iosepho, cui Salome germana regis in coniugium conuenerat, secreto aperit suspectam sibi necem propter coniugalis formae adpetentiam, quam missa sui decoris specie prodidisse mulier argueretur. Id se quasi adfini negotii committere, ut si ipse ab Antonio extinctus foret, Mariammen necaret, ne merces flagitii superesset. Iosephus hautquaquam, ut arbitror, studio proditionis sed quo mulieris erga uirum sopiret querellas, quibus se adflictam diceret ardere odiis uiri, mandatum expromit atque ad affectum amantis interpretatur, quod ne mortuus quidem pateretur Herodes seiungi se ab uxoris societate. Sed mulier longe aliter quam Iosephus aestimauerat ad argumentum traxit inplacatae adhuc in se crudelitatis, cuius exercendae post mortem quoque suam exsecutionem adfini proprio mandauisset. Infestum illum sibi iniuria, qui suspectiones suas non argumento aliquo ueritatis examinaret sed praeruptae mortis exitio urgueret, nullum odiis finem fore quae ultra ipsum uitae ac salutis defectum extenderentur. Sed Iosephus domestici mali immemor, dum alienam coniugem uiro reconciliare expetit, suae coniugis aduersum se inflammauit suspiciones, quae conloquia uiri proprii cum Mariamme, moras in aula regis haut perfunctorie ferendas arbitrabatur. Denique ubi frater reuertit, insimulationem non distulit, iniuriam suam addens regalibus contumeliis, quod sibi quoque Mariamme ademisset maritum. Sed Herodes, praestrictus licet, tamen hautquaquam grauius primo commotus est, nec infensum se uxori praebuit, quin etiam ui amoris infractus quodam die iurare mulieri coepit, quod tanto eam diligeret affectu, ut numquam alterius mulieris flagrauerit cupiditate, ita omnes ex animo abiecerit, ut uxori fidem seruaret. At illa: ‘Satis’ inquit ‘amorem erga me tuum mandatis quae Iosepho dederas declarasti, praecipiens ut me occideret. Quomodo potest amare qui occidere potest?’

#### `deh-1-37-5-aj-2` — AJ 15.67–67

Classification: **BOUNDARIES_AND_SELECTED_TEXT_RETAINED**. Old and current child paths/sides are retained. Intended passage: the existing frozen AJ target, in its recorded order.

Same ordered XML elements and attributes as the certified historical witness; each old interval matches independent October 14 XML expectations; current start/end identities, complete selected text and recomputed offsets checked. Frozen reference retained without expanding the passage.

| Section | Old boundary → current boundary | CP old → current | U16 old → current |
| --- | --- | --- | --- |
| 67 | `1.2.11.9:after → 1.2.12.0:before` → same | `15852:16028` → `15852:16028` | `15852:16028` → `15852:16028` |

**AJ 15.67**

Old = current selected passage:

> per quae demonstrabat impetum antonii quem in eam habuisset, cum olim de pulchritudine illius audisset. Herodes quidem haec praecipiens, spe incerta ad antonium perrexit.

#### `deh-1-37-5-aj-3` — AJ 15.68–70

Classification: **BOUNDARIES_AND_SELECTED_TEXT_RETAINED**. Old and current child paths/sides are retained. Intended passage: the existing frozen AJ target, in its recorded order.

Same ordered XML elements and attributes as the certified historical witness; each old interval matches independent October 14 XML expectations; current start/end identities, complete selected text and recomputed offsets checked. Frozen reference retained without expanding the passage.

| Section | Old boundary → current boundary | CP old → current | U16 old → current |
| --- | --- | --- | --- |
| 68 | `1.2.12.0:after → 1.2.12.1:before` → same | `16028:16234` → `16028:16234` | `16028:16234` → `16028:16234` |
| 69 | `1.2.12.1:after → 1.2.12.2:before` → same | `16234:16558` → `16234:16558` | `16234:16558` → `16234:16558` |
| 70 | `1.2.12.2:after → 1.2.13.0:before` → same | `16558:16767` → `16558:16767` | `16558:16767` → `16558:16767` |

**AJ 15.68**

Old = current selected passage:

> Iosippus autem cum in dispensatione rerum magistratus esset, et propter hoc frequenter mariamnen conueniret, et de negotiis honoris causa reginam percontaret, fauorem uel amorem circa eam herodis inseruit,

**AJ 15.69**

Old = current selected passage:

> mulieres autem cum illum adulationibus, emolis sent, plus autem ab alexandra seductus iosippus, sententiam regis demonstrauit, et mandatum explanauit, dum fides illis uellet facere quod post mortem sine ipsa posset uiuere, dum diceret, ut siquid acerbum ab antonio pateretur non sufferret ab ea nec post interitum separari.

**AJ 15.70**

Old = current selected passage:

> Haec quidem iosippus, mulieres autem non hoc amorem affectus herodis putauerunt, sed timuerunt ne reuersus tyrannica crudelitate sibi mortem inferret. Ideoque de uerbo suspicionem non paruam perceperunt.

#### `deh-1-37-5-aj-4` — AJ 15.80–86

Classification: **BOUNDARIES_AND_SELECTED_TEXT_RETAINED**. Old and current child paths/sides are retained. Intended passage: the existing frozen AJ target, in its recorded order.

Same ordered XML elements and attributes as the certified historical witness; each old interval matches independent October 14 XML expectations; current start/end identities, complete selected text and recomputed offsets checked. Frozen reference retained without expanding the passage.

| Section | Old boundary → current boundary | CP old → current | U16 old → current |
| --- | --- | --- | --- |
| 80 | `1.2.15.0:after → 1.2.15.4:before` → same | `18549:18868` → `18549:18868` | `18549:18868` → `18549:18868` |
| 81 | `1.2.15.4:after → 1.2.15.5:before` → same | `18868:19081` → `18868:19081` | `18868:19081` → `18868:19081` |
| 82 | `1.2.15.5:after → 1.2.15.6:before` → same | `19081:19335` → `19081:19335` | `19081:19335` → `19081:19335` |
| 83 | `1.2.15.6:after → 1.2.15.9:before` → same | `19335:19596` → `19335:19596` | `19335:19596` → `19335:19596` |
| 84 | `1.2.15.9:after → 1.2.15.10:before` → same | `19596:19760` → `19596:19760` | `19596:19760` → `19596:19760` |
| 85 | `1.2.15.10:after → 1.2.15.11:before` → same | `19760:19963` → `19760:19963` | `19760:19963` → `19760:19963` |
| 86 | `1.2.15.11:after → 1.2.15.12:before` → same | `19963:20159` → `19963:20159` | `19963:20159` → `19963:20159` |

**AJ 15.80**

Old = current selected passage:

> Cum hae litterę peruenissent desierunt ab impetu quem tamquam de mortuo habuissent, ut ad romana signa confugerent. Non tamen earum latuit uoluntas. Nam praecessit antonium rex ad parthos euntem et ad iudaeam reuertitur, statimque soror eius salomi materque eorum consilium quod habuisset alexandra cum suis aperiunt.

**AJ 15.81**

Old = current selected passage:

> Salomi uero et contra maritum iosippum accusationem protulit dicens. Quod cum mariamne frequenter conuenisset haec uero dicebat inimicitiarum causa quod frequenter ignobilitatem generis eius in iurgio deprauaret.

**AJ 15.82**

Old = current selected passage:

> Herodes autem callidus semper et nimis marianne amans, licet statim conturbatus fuisset, non tamen patitur amore marianne aliquid temerarium in ea conficere, sed in utroque anxius, secrete eam inquirit utrum uera esset de iosippo quod audierat an falsa.

**AJ 15.83**

Old = current selected passage:

> Illa uero cum iuramento adfirmante in et satis faciente, quod in nullo peccato fuisset ei commixta, paulatim rex deflectitur et ira deleta coniuris I amore superatur. Ut etiam satisfactum sibi de his crederet quae audisset, honestati eius multas ageret gratias

**AJ 15.84**

Old = current selected passage:

> fauorem quoque quem erga ipsam uel amorem haberet pandebat, uel qualia saepe amantibus contingunt conlacri mabant inuicem magno suo studio sese pariter diligentes.

**AJ 15.85**

Old = current selected passage:

> Cum uero rex suum affectum iam pretermissa aemulatione firmasset, non amantis est inquit mariamne quod mandaueras iosippo ut siquid patereris ab antonio molestum me perimeret, quae nihil tibi peccassem.

**AJ 15.86**

Old = current selected passage:

> Quod uerbum ut audiuit herodes exardescens in furorem, statim eam ab amplexu demisit. Clamans ut suos capillos delacerent, dicendo manifestum signum coepisse iosippum cum ea habuisse communionem.

### DEH I.37.7 — `deh-1-37-7`

Canonical source ID: `latin-deh1-num143`.

**DEH Latin passage:**

> [I.37.7] Nec multo post secuta est factorum paenitentia, et ubi ira cecidit, amor successit, et passio resuscitata est tantusque incanduit feruor cupiditatis, ut defunctam non crederet atque in excessu mentis positus quasi uiuentem alloqueretur. Et sicut ad eam quae uiueret pueros dirigebat, rogans ut depositis simultatibus ad sese ueniret et redderet se coniugali gratiae. Vix denique multo edoctus interuallo temporis obisse credidit, quam pro amore tamquam immortalis feminam decoris mori non potuisse arbitrabatur. Tantus erat affectus circa defunctam. Denique efferasse postea atque in multorum necem praesentium odio fertur exasperatus, nec solum morbo animi laborasse sed etiam graui corporis aegritudine, quam ex pestilentia quoque aeris contractam aiebant. Nam tractus caeli corruptior plurimis pestem creauit. Vnde consultis medicinae peritis siluarum secretis sese abdit et refuso paulatim uigore uenatibus salubritatem corporis pariter ac mentis sobrietatem recepit.

#### `deh-1-37-7-aj-2` — AJ 15.240–246

Classification: **BOUNDARIES_AND_SELECTED_TEXT_RETAINED**. Old and current child paths/sides are retained. Intended passage: the existing frozen AJ target, in its recorded order.

Same ordered XML elements and attributes as the certified historical witness; each old interval matches independent October 14 XML expectations; current start/end identities, complete selected text and recomputed offsets checked. Frozen reference retained without expanding the passage.

| Section | Old boundary → current boundary | CP old → current | U16 old → current |
| --- | --- | --- | --- |
| 240 | `1.5.7.0:after → 1.5.7.1:before` → same | `53416:53468` → `53414:53466` | `53416:53468` → `53414:53466` |
| 241 | `1.5.7.1:after → 1.5.7.2:before` → same | `53468:53611` → `53466:53609` | `53468:53611` → `53466:53609` |
| 242 | `1.5.7.2:after → 1.5.7.3:before` → same | `53611:53762` → `53609:53760` | `53611:53762` → `53609:53760` |
| 243 | `1.5.7.3:after → 1.5.7.4:before` → same | `53762:53970` → `53760:53968` | `53762:53970` → `53760:53968` |
| 244 | `1.5.7.4:after → 1.5.7.5:before` → same | `53970:54162` → `53968:54160` | `53970:54162` → `53968:54160` |
| 245 | `1.5.7.5:after → 1.5.7.6:before` → same | `54162:54358` → `54160:54356` | `54162:54358` → `54160:54356` |
| 246 | `1.5.7.6:after → 1.5.8.0:before` → same | `54358:54610` → `54356:54608` | `54358:54610` → `54356:54608` |

**AJ 15.240**

Old = current selected passage:

> Post quam interiit regis potius desiderium exarsit,

**Retained witness note:** The intensified desire after Mariamne’s death survives; the Greek retrospective account of the earlier passion is compressed.

**AJ 15.241**

Old = current selected passage:

> ut saepius nomen illius inuocaret. Moliebatur autem omnia facere quae potuissent solacium afferre. Conuiuia colloquia quae nihil ei profuerunt

**Retained witness note:** The repeated calling and attempted distractions survive; the Greek interpretation of divine retribution is not separately expressed.

**AJ 15.242**

Old = current selected passage:

> gubernationes etiam regales recusabat, et tantum doloribus tenebatur, ut aliquando mariamme uocare ministris tamquam uiuentem ualentemque praeciperet.

**AJ 15.243**

Old = current selected passage:

> Cum sic haberetur superuenit aegritudo pestifera quae plures populi uel amicorum eius honestissimos extinxit, et omnibus praebuit suspicari per iram dei haec contigisse pro iniquitate erga mariamme confecta.

**AJ 15.244**

Old = current selected passage:

> Ideoque ad peiora rex peruenit, in ultimo solitudines eligeret sub occasione uenationis his confectus cogitationibus non potuit multos dies protahere sed incidit in difficillimam ualitudinem.

**AJ 15.245**

Old = current selected passage:

> Nam inflammatione uel astrictione gutturis mentisque mutatione tenebatur, et quae potuissent curam exhibere nihil paenitus profuerunt. Sed contraria inueniebantur. Unde postea desperatione facta,

**AJ 15.246**

Old = current selected passage:

> medici dum nequaquam medicaminibus adlatis aegritudo decresceret et rex nihil potuisset accipere, omnia quae ille uellet iusserunt ei praebere desperationem salutis casui deuouoentes, et ille quidem in samaria sebasti nominata inualidus iacebat.

### DEH I.38.1 — `deh-1-38-1`

Canonical source ID: `latin-deh1-num144`.

**DEH Latin passage:**

> [I.38.1] Haec quoque addebat miraculis suis, quibus defunctae suspiciebat gratiam, luisse se iniusti poenas flagitii et elementorum aegritudine expiatum interitum tanti decoris, excidio mundi, populorum lue unius mortem, sorte tamen inpari uindicatam, cum fructus terra abnegaret, fames augeret pestilentiam.

#### `deh-1-38-1-aj-1` — AJ 15.243–243

Classification: **BOUNDARIES_AND_SELECTED_TEXT_RETAINED**. Old and current child paths/sides are retained. Intended passage: the existing frozen AJ target, in its recorded order.

Same ordered XML elements and attributes as the certified historical witness; each old interval matches independent October 14 XML expectations; current start/end identities, complete selected text and recomputed offsets checked. Frozen reference retained without expanding the passage.

| Section | Old boundary → current boundary | CP old → current | U16 old → current |
| --- | --- | --- | --- |
| 243 | `1.5.7.3:after → 1.5.7.4:before` → same | `53762:53970` → `53760:53968` | `53762:53970` → `53760:53968` |

**AJ 15.243**

Old = current selected passage:

> Cum sic haberetur superuenit aegritudo pestifera quae plures populi uel amicorum eius honestissimos extinxit, et omnibus praebuit suspicari per iram dei haec contigisse pro iniquitate erga mariamme confecta.

#### `deh-1-38-1-aj-2` — AJ 15.299–300

Classification: **BOUNDARIES_AND_SELECTED_TEXT_RETAINED**. Old and current child paths/sides are retained. Intended passage: the existing frozen AJ target, in its recorded order.

Same ordered XML elements and attributes as the certified historical witness; each old interval matches independent October 14 XML expectations; current start/end identities, complete selected text and recomputed offsets checked. Frozen reference retained without expanding the passage.

| Section | Old boundary → current boundary | CP old → current | U16 old → current |
| --- | --- | --- | --- |
| 299 | `1.6.0.2:after → 1.6.0.3:before` → same | `65883:66024` → `65881:66022` | `65883:66024` → `65881:66022` |
| 300 | `1.6.0.3:after → 1.6.0.4:before` → same | `66024:66214` → `66022:66212` | `66024:66214` → `66022:66212` |

**AJ 15.299**

Old = current selected passage:

> Eodem tempore tertiodecimo anno regis herodis instante, magnae calamitates prouinciam occupauerunt, siue de ultione seu casu sic occurrente,

**AJ 15.300**

Old = current selected passage:

> siquidem prius gelu percussa terra fructus nullatenus inferebat. Praeterea et ciues per inopiam frumenti morbus et passio pestifera possidebat. Qui continue malorum diuersitate conprehensi,

### DEH I.38.2 — `deh-1-38-2`

Canonical source ID: `latin-deh1-num145`.

**DEH Latin passage:**

> [I.38.2] Hunc Mariamme exitum tulit sobrie uiro pudica sed insolens formae conscientia. Cui magnanimitas superfluebat, sedulitas deerat, ut blanditias dedignaretur mariti, secura quod nihil ab eo qui supra modum diligeret exitii perpeti posset.

#### `deh-1-38-2-aj-1` — AJ 15.237–238

Classification: **BOUNDARIES_AND_SELECTED_TEXT_RETAINED**. Old and current child paths/sides are retained. Intended passage: the existing frozen AJ target, in its recorded order.

Same ordered XML elements and attributes as the certified historical witness; each old interval matches independent October 14 XML expectations; current start/end identities, complete selected text and recomputed offsets checked. Frozen reference retained without expanding the passage.

| Section | Old boundary → current boundary | CP old → current | U16 old → current |
| --- | --- | --- | --- |
| 237 | `1.5.6.0:after → 1.5.6.1:before` → same | `52765:52993` → `52763:52991` | `52765:52993` → `52763:52991` |
| 238 | `1.5.6.1:after → 1.5.6.2:before` → same | `52993:53170` → `52991:53168` | `52993:53170` → `52991:53168` |

**AJ 15.237**

Old = current selected passage:

> et illa quidem sic interiit, femina ad continentiam et magnitudinem anni optima erat modestia uero ei defuit, pulchritudinem namque corporis et affabilitatis dignitate mauis quam si quis extimare posset omnes mulieres anteibat.

**AJ 15.238**

Old = current selected passage:

> Occasio tamen exinde maior prouenit, cum nec gratia regis uellet uiuere. Nam dum semper potiretur illius amore et nihil difficile ab illo speraret, fiduciam inmoderatam habuit.

### DEH I.40.1 — `deh-1-40-1`

Canonical source ID: `latin-deh1-num152`.

**DEH Latin passage:**

> [I.40.1] Discessere plerique laeti, quibus placebat concordia germanitatis, sed cum fratribus reuertit dissensio eoque grauior, quo dignitas potior cui amplius inuideretur et nocendi suppeteret maior potestas. Dolebant filii Mariammes aequatum sibi priuatae filium mulieris, quae regni nesciret prosapiam. Contra Antipater distinctam sibi ac fratribus regni spem dedignabatur et inuidebat germanis, quibus posteriora pro primis uix reseruarentur. Sed hic sese tegebat et uelabat, odio praetendens gratiam, illis consilium omne in sermone obuium etiam non quaerentibus, promtiore lingua et secretorum prodiga. Quicquid locuti fuerant, apud Antipatrum continuo erat, multa etiam quae non dixerant simulabantur. Pleraque internuntius cum incremento adiciebat. Architectus omnium quibus adpeterentur fratres Antipater erat, cuius uita nihil aliud erat nisi quoddam uersutiarum conciliabulum, scena inprobitatis, argumentum scelerum, flagitiorum mysterium. Subiciebat indices, subornabat testes, simulabat defensionem quasi in theatro personam fratris circumferens, ut leuiora excuteret obiecta, grauioribus cederet, quo magis patrem falleret et uehementius in fratres moueret, maximeque aceruabat arte inuidiam paternae necis paratae ut regnum eriperetur, quae regibus metu periculi suspectiora. Sed ne sine repulsore minus uerisimilia regi uiderentur, ipse primo temtabat refellere, dein constringi se manifestis rerum indiciis uolebat uideri, ut perorata utrimque causa, quasi nihil iudicio defuisset, amplius pater tamquam in conuictos filios excitaretur. Nulla enim res maiorem fidem adsertis dabat, quam quod Antipater fratrum defensor aestimabatur. Hac fraude plurimorum captabat gratiam, ipsius quoque patris in se mentem inclinabat.

#### `deh-1-40-1-aj-1` — AJ 16.135–135

Classification: **BOUNDARIES_AND_SELECTED_TEXT_RETAINED**. Old and current child paths/sides are retained. Intended passage: the existing frozen AJ target, in its recorded order.

Same ordered XML elements and attributes as the certified historical witness; each old interval matches independent October 14 XML expectations; current start/end identities, complete selected text and recomputed offsets checked. Frozen reference retained without expanding the passage.

| Section | Old boundary → current boundary | CP old → current | U16 old → current |
| --- | --- | --- | --- |
| 135 | `1.6.7.6:before → 1.7.0.1:before` → same | `26849:26963` → `26849:26963` | `26849:26963` → `26849:26963` |

**AJ 16.135**

Old = current selected passage:

> Cum haec dixisset contentione demissa multi sub expectatione filiorum eius, nouis rebus studebant.

### DEH I.45.12 — `deh-1-45-12`

Canonical source ID: `latin-deh1-num213`.

**DEH Latin passage:**

> [I.45.12] V itaque diebus Antipatro superstes defecit, XXXVII annis, ex quo a Romanis imperitare iussus est, regno potitus; ex quo autem Antigonum sustulit regni aemulum, annos XXXIIII in imperio exegit, utinam tam domestico usu quam publicis laetus successibus. Namque ita foris secundae ei res adspirauerunt, ut priuatus in regnum adscisceretur, eoque permulta usus annorum curricula, quod difficile, saluo potestatis usu decederet relinquens liberis imperii successionem, quam ipse a suis non acceperat, sed intra domum infelicissimus, quam acerbo suorum sanguine et luctu repleuit. Nec tamen exsecutionem inuenit ultimae crudelitatis, hoc uno Salome obliterante criminum suorum ludibria superiora, quod eos quos percuti rex iusserat omnes dimisit, dicens regem praecepti feralis postea paenituisse reuocatisque mandatis superioribus praecepisse ut ad sua omnes dimitterentur.

#### `deh-1-45-12-aj-2` — AJ 17.193–193

Classification: **BOUNDARIES_AND_SELECTED_TEXT_RETAINED**. Old and current child paths/sides are retained. Intended passage: the existing frozen AJ target, in its recorded order.

Same ordered XML elements and attributes as the certified historical witness; each old interval matches independent October 14 XML expectations; current start/end identities, complete selected text and recomputed offsets checked. Frozen reference retained without expanding the passage.

| Section | Old boundary → current boundary | CP old → current | U16 old → current |
| --- | --- | --- | --- |
| 193 | `1.8.1.0:before → 1.8.1.1:before` → same | `63437:63686` → `63453:63702` | `63437:63686` → `63453:63702` |

**AJ 17.193**

Old = current selected passage:

> At salome et alexias ante antequam mors regis diuulgata foret, exipodromo iudaeos abire permittunt ad proprias domos dicentes, regem iussisse ut unus quisque in suas regiones abscederent. Hoc autem fecerunt beneficium illi genti praestare cupientes

### DEH II.3.4 — `deh-2-3-4`

Canonical source ID: `latin-deh2-num12`.

**DEH Latin passage:**

> [II.3.4] Dum haec in Iudaea geruntur, Agrippa Aristoboli filius Romam aduenit cupiens aduersum Herodem tetrarchen apud Tiberium iudicio decernere, sed despectus a Tiberio, cum Romae degeret, plurimos sibi adsciuit ad amicitiam et maxime Germanici filium Gaium, quem siue paterni nominis gratia amabilem populo, seu regii generis propinquitate proximum imperio ratus an quodam praesagio studiosius excolebat, quam uel aetatis uel honoris eius ratio patiebatur, ita ut quodam die manus eleuans deprecaretur, ut maturius Tiberio mortuo Gaium uideret imperatorem. Quo prodito per Eutychum, libertum suum, Agrippa iussu Tiberi in uincla ducitur et grauibus modis excruciatur, non ante dimissus quam Tiberius diem clauderet. Cuius tempora foeda ludibriis Caprearumque secessus — ignauia intolerabilis — nullum tamen efficacis uirum operis in necem eius excitauerunt, recentis, ut arbitror, Romani imperii reuerentia siue terrore saeuissimae crudelitatis, quia plerumque asperitas quo grauior eo tutior est.

#### `deh-2-3-4-aj-2` — AJ 18.168–168

Classification: **BOUNDARIES_AND_SELECTED_TEXT_RETAINED**. Old and current child paths/sides are retained. Intended passage: the existing frozen AJ target, in its recorded order.

Same ordered XML elements and attributes as the certified historical witness; each old interval matches independent October 14 XML expectations; current start/end identities, complete selected text and recomputed offsets checked. Frozen reference retained without expanding the passage.

| Section | Old boundary → current boundary | CP old → current | U16 old → current |
| --- | --- | --- | --- |
| 168 | `1.10.9:start → 1.10.9.0:before` → same | `50480:50860` → `50470:50850` | `50480:50860` → `50470:50850` |

**AJ 18.168**

Old = current selected passage:

> Per dies igitur agrippa circa gaium in melius procedente quodam die sermo fit de tiberio. Cumque agrippa ex affectu uota profunderet, ut caeleriter defuncto tiberio gaio daretur imperium. Quem meliorem dignioremque in omnibus esse firmabat. Inter auditores horum uerborum forte fuit quidam etiam eutichius agrippae libertus auriga et tunc quidem silentio quid audiuerat tradidit.

**Retained witness note:** The Latin gives the wish as defuncto tiberio; its wording remains unchanged.

### DEH II.4.1 — `deh-2-4-1`

Canonical source ID: `latin-deh2-num13`.

**DEH Latin passage:**

> [II.4.1] Eo imperante famosum ludibrium Paulinae spectatissimi generis feminae Romae percelebratum est. Quae cum egregiam castitatis apud omnes famam haberet, esset autem praestantissimi decoris et eminentis gratiae, temtata Mundi equestris militiae ducis interpellationibus nec inflexa, uitio nimiae superstitionis patuit errori, namque subornatis Isidis sacerdotibus qui uelut Anubis ad eam mandata perferrent, quod eam ad templum inuitaret, delectatum se eius sedulitate et pudicitia noctem poscere, habere se quod eidem secreto uellet committere. Quod illa accipiens laeta ad maritum detulit, deum suis adesse uotis, a deo suam posci praesentiam, negare se non posse oboedientiam. Itaque et ex sua et ex mariti sententia pergit ad templum Isidis, noctem exegit remotisque procul arbitris quasi sacri cognitionem mysterii perceptura sese stratis conposuit suis, aestimans quod ad eam deus suus in somnis ueniret et per uisionem sese eidem demonstraret. Verum ubi aliquid noctis processit, quo facilius mulier plena somni deciperetur, Mundus assumto uultu Anubis habituque aduenit, uestimenta ableuat, in oscula ruit. Expergefactae mulieri Anubem se esse dicit, uultum Anubis praetendit. Illa deum credidit, beatam se adserit quod eam dignatus sit uisitare dominus deus suus. Amplexum petenti non negat, refert tamen utrum deus possit homini misceri. Ille promit exempla quod et Iouem summum deorum Alcmena susceperit et Leda eiusdem concubitu potita et plurimae aliae, quae ediderint deos partu. De se quoque et illa deum esse generandum persuadet mulieri, concubitu miscetur. Redit ad maritum laetior, dicens quod mixta deo sit mulier et eius promissu deum esset generatura. Fit ingens in stupro mulieris mariti gaudium. Postea occurrit Mundus mulieri et ait: ‘Beata Paulina concubitu dei, magnus deus Anubis, cuius tu accepisti mysteria. Sed disce te sicut diis ita et hominibus non negare, quibus tribuunt quod tu negaueris, quia nec formas suas dare nobis nec nomina dedignantur. Ecce ad sacra sua deus Anubis uocauit et Mundum ut tibi iungeret. Quid tibi profuit duritia tua, nisi ut te XX milium quae obtuleram conpendio defraudaret? Imitare deos indulgentiores, qui nobis sine pretio tribuunt quod abs te magno pretio impetrari nequitum. Quodsi te humana offendunt uocabula, Anubem me uocari placuit et nominis huius gratia effectum iuuit.’ Praestricta sermone mulier inlusum sibi intellexit et dolens iniuriam pudicitiae confessa est fraudem marito. Ille nihil habens quod uxori indignaretur, cui ipse cubandi in templo potestatem permiserat, et conscius coniugalis castimoniae principi querellam detulit. Qui motus potentis uiri contumelia atque atrocis flagitii commento sacerdotes templo rapuit, quaestioni subicit, confessos necat, simulacrum Isidis Tiberi demergit. Mundo fugiendi potestas permissa, eo quod ui amoris et formae superatus gratia leuioribus commissorum suorum pretiis multandus aestimaretur.

#### `deh-2-4-1-aj-1` — AJ 18.65–80

Classification: **BOUNDARIES_AND_SELECTED_TEXT_RETAINED**. Old and current child paths/sides are retained. Intended passage: the existing frozen AJ target, in its recorded order.

Same ordered XML elements and attributes as the certified historical witness; each old interval matches independent October 14 XML expectations; current start/end identities, complete selected text and recomputed offsets checked. Frozen reference retained without expanding the passage.

| Section | Old boundary → current boundary | CP old → current | U16 old → current |
| --- | --- | --- | --- |
| 65 | `1.6.0:start → 1.6.0.3:before` → same | `20793:21040` → `20791:21038` | `20793:21040` → `20791:21038` |
| 66 | `1.6.0.3:after → 1.6.0.5:before` → same | `21040:21369` → `21038:21367` | `21040:21369` → `21038:21367` |
| 67 | `1.6.0.5:after → 1.6.0.6:before` → same | `21369:21765` → `21367:21763` | `21369:21765` → `21367:21763` |
| 68 | `1.6.0.6:after → 1.6.0.10:before` → same | `21765:22054` → `21763:22052` | `21765:22054` → `21763:22052` |
| 69 | `1.6.0.10:after → 1.6.0.12:before` → same | `22054:22330` → `22052:22328` | `22054:22330` → `22052:22328` |
| 70 | `1.6.0.12:after → 1.6.0.13:before` → same | `22330:22725` → `22328:22723` | `22330:22725` → `22328:22723` |
| 71 | `1.6.0.13:after → 1.6.0.14:before` → same | `22725:23040` → `22723:23038` | `22725:23040` → `22723:23038` |
| 72 | `1.6.0.14:after → 1.6.0.15:before` → same | `23040:23418` → `23038:23416` | `23040:23418` → `23038:23416` |
| 73 | `1.6.0.15:after → 1.6.0.17:before` → same | `23418:23676` → `23416:23674` | `23418:23676` → `23416:23674` |
| 74 | `1.6.0.17:after → 1.6.0.19:before` → same | `23676:24009` → `23674:24007` | `23676:24009` → `23674:24007` |
| 75 | `1.6.0.19:after → 1.6.0.21:before` → same | `24009:24285` → `24007:24283` | `24009:24285` → `24007:24283` |
| 76 | `1.6.0.21:after → 1.6.0.22:before` → same | `24285:24461` → `24283:24459` | `24285:24461` → `24283:24459` |
| 77 | `1.6.0.22:after → 1.6.0.23:before` → same | `24461:24853` → `24459:24851` | `24461:24853` → `24459:24851` |
| 78 | `1.6.0.23:after → 1.6.0.24:before` → same | `24853:25101` → `24851:25099` | `24853:25101` → `24851:25099` |
| 79 | `1.6.0.24:after → 1.6.0.25:before` → same | `25101:25425` → `25099:25423` | `25101:25425` → `25099:25423` |
| 80 | `1.6.0.25:after → 1.6.1:start` → same | `25425:25673` → `25423:25671` | `25425:25673` → `25423:25671` |

**AJ 18.65**

Old = current selected passage:

> X Eisdem temporibus alia iudaeos seui ora perturbant. Nam etiam in templo isidis quod romae fuerat constitutum, factum quoddam turbi dine plenum obprobrioque contingit, quod primum explanabo tum demum ad illa quae S apud iudaeos euenere transibo.

**AJ 18.66**

Old = current selected passage:

> Paulina quaedam mulier erat romae, maiorum dignitate preclara, studio castitatis intenta, honestatis opinione perspicua. Erat etiam opum magnitudine locuplex, et uultus pulchritudine decorosa, aetate autem quando maxime mulieres pudicitia decorantur. Haec nup taerat saturnino etiam ipso genere opibus ceteroque cultu consimili.

**AJ 18.67**

Old = current selected passage:

> Huius itaque amore detinetur iuuenis quidam nomine mundus ex numero equestri sed in gradu iam emerito constitutus et dignitate magna sublimis. Idoneus etiam ad munera largienda sump tusque faciendos. Nam memoratae quoque mulieri maiora dona promiserat, quae illa contempnente maximo fuerat amore succensus. Ut etiam uiginti miriadas dragmarum atticarum sed aturum pro uno concubitu spopondisset,

**AJ 18.68**

Old = current selected passage:

> sed neque sic illa deflexa est. Tum illae nimiam infelicitatem morbi sustinens siquidem neque cibum ualeat accipere morti se addixerat. Hoc unum sibi uindicans tanti mali fore remedium, et ille quidem tale decretum animo in fingens per dies singulos hoc agebat ut celeri morte raperetur.

**AJ 18.69**

Old = current selected passage:

> Erat autem mundo liberta quaedam ex parentibus nomine ida omnium malorum iniquitatum quoagulum, e grauiter ferens quod ille iuuenis se damnaret in mortem. Nam clarebat omnino periturus. Accedens erexit eum et coepit cum eo talia fabulari quae animum eius bonae spei facerent.

**AJ 18.70**

Old = current selected passage:

> Promittebat se namque acturam apud paulinam ut quinque miriadas accipiens concederet iuueni quod uolebat. His itaque dictis iuuenem de morte reuocans super sit ab eo pecuniae quantum placuerat, sed non eadem uia paulinam aggreditur qua fuerat ante temptata, cernens animum mulieris nullo modo capi pęcuniis, sciens illam quod ammodum esset illa cultura hisdis occupata, tale aliquid machinatur.

**Retained witness note:** The Latin condenses and orders the proposal differently; the complete price-and-Isis scheme remains in this interval.

**AJ 18.71**

Old = current selected passage:

> Accedit ad quosdam ex templo isidis sacerdotes, quibus interpositione iurandi fidem seruare persuasit. Dans etiam in presenti duas miriadas et dimidiam, promittens etiam aliud, tantum siquod uellet habuisset effectum. Tunc causam aperit, amorem iuuenis indicat, orat ut et mulierem quibus possent modis inducerent.

**AJ 18.72**

Old = current selected passage:

> Illi autem pecuniarum cupidine capti promittunt, quicquit imperaret protinus impleturos. Praesertim autem ipse maximus sacerdotum ut paulinam conueniret ac suis uerbis inpelleret pollicetur. Finxit itaque se ex aegypto uenisse ab anubio destinatum quod is grandi circa paulinam amore teneretur eumque deum sibi iussisse ut romam ueniret. Mulierique precepta nominis apportaret.

**AJ 18.73**

Old = current selected passage:

> Libenter illa exobtabiliter suscipit atque ad amicas gloriando denunciat ciat, quod ab anubio tali merito digna iudicetur hoc etiam intimaret marito, quod ab ea corum et cenam anubius concupiscat. Ille autem grate concessit pudicitiam coniugis non ignorans.

**AJ 18.74**

Old = current selected passage:

> Illa igitur pergit ad templum et cum caenasset tempusque quiescendi uenisset, uniuersae ianuae a sacerdote clauduntur. Cuncta quoque lumina subtrahuntur, mundum autem intro latebat occultus, qui postquam silentium factum est ad mulierem deuenit. Illa autem existimans deum esse, reuerenter accipit atque ita cum ea mundus pernoctans

**AJ 18.75**

Old = current selected passage:

> circa uicinam lucis abscessit. Illa autem mane facto consurgens atque ad suum uirum ueniens aduentum ad se numinis enarrauit. Similiter etiam loquitur ad amicas, magnam sibi ex hoc gloriationes m reputans prouenisse , et quia uerba quoque ad illam fecisset anubius indicabat.

**AJ 18.76**

Old = current selected passage:

> Sed ex audientibus, alii non credebant naturam inspicientes reipubli pars autem credebant, qui dum uerum ad miraculum dicebant pudicitiam adtendentes dignitatemque referentes.

**AJ 18.77**

Old = current selected passage:

> Tertia uero die post quam factum est, occurrens eam mundu. O paulina inquit saluasti mihi inquit XX miriadas quas posses familiaribus tuis rebus adicere. Nunc autem nec meis postulationibus defuisti et dampnificatione liberasti. Nam in templo tota nox tecum mundo peracta est nec mei nominis interest uoluptate percepta. Nihil enim ad perficiendum negotium offuit quod anubius uocitatus sum.

**AJ 18.78**

Old = current selected passage:

> Et ille quidem talia, locutus abscessit. Illa uero in mentem suam rediens, tunc primum illud facinus intellexit, et scis scis protinus uestimentis ad uirum occurrit factionemque aperuit. Tum magni facinoris de precata ne suam iniuriam neglexisset.

**AJ 18.79**

Old = current selected passage:

> At ille imperatori cuncta denuntiat. Tunc tiberius causam diligenter examinans, uniuersum sacerdotum scelus inuenit, et ipsos quidem cum ida quae causa totius iniquitatis extiterat adegit in cruces. Templum autem ipsum fundit euertit, statuamque isidis in tiberim fluuium iactari precepit. Mundum autem exilio condemp nauit

**AJ 18.80**

Old = current selected passage:

> dignum eum maiore paena non iudicans, quod amoris uehementia deliquisset, et ea quidem in templo isidis prouenere tali fine conclusa sunt. Nunc ad rem redeo ut explicem quae iudaeis romae eodem tempore contingerunt sicut etiam ante prestuxi.

### DEH II.5.1 — `deh-2-5-1`

Canonical source ID: `latin-deh2-num14`.

**DEH Latin passage:**

> [II.5.1] Quod igitur ludibrium imperitante Tiberio acciderit non putaui praetereundum, ut ex eo deformitas colligatur imperatoris. Sicut enim boni principis uita probitatis quaedam praescriptio et per uniuersos uiuendi forma est, ita imperatoris conluuio lex flagitiorum est. Ab eo missus Pilatus in Iudaeam, uir inprobus atque in exiguo ponens mendacium, circumuenit Samaritanos, ut montem cui nomen Gadir peterent — erat enim illis sacratus — eo quod uellet eorum mysteria cognoscere. Et ascendens populum praeuenit equitatu pedestrique exercitu, strauit adficto crimine, quod a Romanis discedere et conciliabulum sibi quaerere praeparauissent.

#### `deh-2-5-1-aj-1` — AJ 18.85–87

Classification: **BOUNDARIES_AND_SELECTED_TEXT_RETAINED**. Old and current child paths/sides are retained. Intended passage: the existing frozen AJ target, in its recorded order.

Same ordered XML elements and attributes as the certified historical witness; each old interval matches independent October 14 XML expectations; current start/end identities, complete selected text and recomputed offsets checked. Frozen reference retained without expanding the passage.

| Section | Old boundary → current boundary | CP old → current | U16 old → current |
| --- | --- | --- | --- |
| 85 | `1.6.2:start → 1.6.2.0:before` → same | `26636:27013` → `26634:27011` | `26636:27013` → `26634:27011` |
| 86 | `1.6.2.0:after → 1.6.2.1:before` → same | `27013:27187` → `27011:27185` | `27013:27187` → `27011:27185` |
| 87 | `1.6.2.1:after → 1.7.0:start` → same | `27187:27511` → `27185:27509` | `27187:27511` → `27185:27509` |

**AJ 18.85**

Old = current selected passage:

> Sed neque samara eorum gens turbis fuit expers uel tumultibus aliena. Hos enim peruertit uir quidam mentiri pro nihilo iudicans caphe don nomine, qui omnem plebem suasionibus artificiosis induxerat, ut in montem garizin omnes accurrerent quod eum sanctum haberent ac uenerabilem, pollicebatur enim se ascendentibus ostensurum uniuersa uasa quae ibidem a moseo fuissent obruta.

**AJ 18.86**

Old = current selected passage:

> At illi persuasi uerbis illius armantur et conscidunt in quodam uico cuius nomen tyrithua atque hinc inde plurimos congregabant ut cum maxima multitudine montem ascenderent.

**AJ 18.87**

Old = current selected passage:

> Sed hos in ipso ascensu pilatus occupat omnem equitatum precedere iubens, et dictu uelocissimos, atque ibi circa memoratum uicum pugna committitur, et alios obtruncant pluresque in fugam uertunt. Maximam partem capiunt, quorum seditionis principes uel eos quin fugiendo plurimum ualuerant pilatus interfecit.

### DEH II.5.2 — `deh-2-5-2`

Canonical source ID: `latin-deh2-num15`.

**DEH Latin passage:**

> [II.5.2] Quid enim non auderet, qui etiam Christum dominum ad salutem humani generis aduenientem, multis et diuinis operibus profundentem in homines misericordiae suae gratiam nihilque aliud docentem, nisi quod primum deo, deinde imperatoribus faceret populos oboedientes, cruci suffixerit? Demens qui minister esset sacrilegi furoris et interficeret auctorem salutis. Ex illo itaque Iudaeorum res perditae, ex illo exitium genti temploque maturatum excidium. Nam si Herodes, qui Iohannem neci tradidit, perfidiae et crudelitatis suae pretium luit deiectus regno atque exilio datus, quanto magis praecipitibus furiis actum intellegi datur eum qui Christum occiderit?

#### `deh-2-5-2-aj-1` — AJ 18.63–64

Classification: **BOUNDARIES_AND_SELECTED_TEXT_RETAINED**. Old and current child paths/sides are retained. Intended passage: the existing frozen AJ target, in its recorded order.

Same ordered XML elements and attributes as the certified historical witness; each old interval matches independent October 14 XML expectations; current start/end identities, complete selected text and recomputed offsets checked. Frozen reference retained without expanding the passage.

| Section | Old boundary → current boundary | CP old → current | U16 old → current |
| --- | --- | --- | --- |
| 63 | `1.5.2:start → 1.5.2.0:before` → same | `20121:20390` → `20119:20388` | `20121:20390` → `20119:20388` |
| 64 | `1.5.2.0:after → 1.6.0:start` → same | `20390:20793` → `20388:20791` | `20390:20793` → `20388:20791` |

**AJ 18.63**

Old = current selected passage:

> fuit autem hisdem temporibus ihesus sapiens uir si tamen uirum eum nominare fas est. Erat enim mirabilium operum effector et doctor hominum eorum qui libenter audiunt quae uera sunt. Et multos quidem iudaeorum multos etiam ex gentibus sibi adiunxit. Christus hic erat.

**AJ 18.64**

Old = current selected passage:

> Hunc accusatione primorum nostrae gentis uirorum cum pilatus in crucem agendum esse decreuisset. Non deseruerunt hii qui ab initio eum dilexerit. Apparuit enim eis tertio die iterum uiuus secundum quod diuinitus inspirati prophetae uel haec uel alia de eo innumera miracula futura esse predixerant. Sed et in odiernum cristianorum qui ab ipso nuncupati sunt et nomen perseuerat et genus.

#### `deh-2-5-2-aj-2` — AJ 18.116–116

Classification: **BOUNDARIES_AND_SELECTED_TEXT_RETAINED**. Old and current child paths/sides are retained. Intended passage: the existing frozen AJ target, in its recorded order.

Same ordered XML elements and attributes as the certified historical witness; each old interval matches independent October 14 XML expectations; current start/end identities, complete selected text and recomputed offsets checked. Frozen reference retained without expanding the passage.

| Section | Old boundary → current boundary | CP old → current | U16 old → current |
| --- | --- | --- | --- |
| 116 | `1.10.2:start → 1.10.2.2:before` → same | `36570:36764` → `36568:36762` | `36570:36764` → `36568:36762` |

**AJ 18.116**

Old = current selected passage:

> A quibusdam autem iudaeorum uidebatur ideoque perisse herodis exercitum, quod in eum satis de iohanne baptiza iuste indignatio diuina commota sit. Pro uindicta iohannis qui uocabatur baptistet.

### DEH II.12.1 — `deh-2-12-1`

Canonical source ID: `latin-deh2-num45`.

**DEH Latin passage:**

> [II.12.1] Luebant enim scelerum suorum supplicia, qui postquam Iesum crucifixerant diuinorum arbitrum, postea etiam discipulos eius persequebantur. Plerique tamen Iudaeorum, gentilium plurimi crediderunt in eum, cum praeceptis moralibus, operibus ultra humanam possibilitatem profluentibus inuitarentur. Quibus ne mors quidem eius uel fidei uel gratiae finem inposuit, immo etiam cumulauit deuotionem. Intulerunt itaque parricidales manus atque auctorem uitae interficiendum ad Pilatum deduxere, reluctantem coeperunt perurguere iudicem. In quo tamen non excusatur Pilatus sed Iudaeorum amentia coaceruatur, quia nec ille adiudicare debuit, quem reum minime deprehenderat, nec isti sacrilegium parricidio geminare, ut ab his qui ad redimendos et sanandos eos sese optulerat, obtruncaretur. De quo ipsi Iudaei quoque testantur dicente Iosepho historiarum scriptore, quod fuerat illo in tempore uir sapiens, si tamen oportet, inquit, uirum dici mirabilium creatorem operum, qui apparuerit discipulis suis post triduum mortis suae uiuens secundum prophetarum scripta, qui et haec et alia innumerabilia de eo plena miraculi prophetauerunt. Ex quo coepit congregatio Christianorum et in omne hominum penetrauit genus, nec ulla natio Romani orbis remansit, quae cultus eius expers relinqueretur. Si nobis non credunt Iudaei, uel suis credant. Hoc dixit Iosephus, quem ipsi maximum putant, et tamen ita in eo ipso quod uerum locutus est mente deuius fuit, ut nec sermonibus suis crederet. Sed locutus est propter historiae fidem, quia fallere nefas putabat, non credidit propter duritiam cordis et perfidiae intentionem. Non tamen ueritati praeiudicat, quia non credidit sed plus addidit testimonio, quia nec incredulus et inuitus negauit. In quo Christi Iesu claruit aeterna potentia, quod eum etiam principes synagogae quem ad mortem conprehenderant deum fatebantur. Et uere quasi deus sine exceptione personarum aut ulla mortis formidine locutus excidium quoque templi futurum adnuntiauit. Sed non eos templi iniuria commouit, sed quia in flagitiis ab eo et sacrilegiis corripiebantur, hinc ira exarsit ut interficerent eum, quem nulla habuissent tempora. Nam cum alii precando meruerint facere quae fecerunt, hic in potestate habebat ut omnia quae fieri uellet imperaret.

#### `deh-2-12-1-aj-1` — AJ 18.63–64

Classification: **BOUNDARIES_AND_SELECTED_TEXT_RETAINED**. Old and current child paths/sides are retained. Intended passage: the existing frozen AJ target, in its recorded order.

Same ordered XML elements and attributes as the certified historical witness; each old interval matches independent October 14 XML expectations; current start/end identities, complete selected text and recomputed offsets checked. Frozen reference retained without expanding the passage.

| Section | Old boundary → current boundary | CP old → current | U16 old → current |
| --- | --- | --- | --- |
| 63 | `1.5.2:start → 1.5.2.0:before` → same | `20121:20390` → `20119:20388` | `20121:20390` → `20119:20388` |
| 64 | `1.5.2.0:after → 1.6.0:start` → same | `20390:20793` → `20388:20791` | `20390:20793` → `20388:20791` |

**AJ 18.63**

Old = current selected passage:

> fuit autem hisdem temporibus ihesus sapiens uir si tamen uirum eum nominare fas est. Erat enim mirabilium operum effector et doctor hominum eorum qui libenter audiunt quae uera sunt. Et multos quidem iudaeorum multos etiam ex gentibus sibi adiunxit. Christus hic erat.

**AJ 18.64**

Old = current selected passage:

> Hunc accusatione primorum nostrae gentis uirorum cum pilatus in crucem agendum esse decreuisset. Non deseruerunt hii qui ab initio eum dilexerit. Apparuit enim eis tertio die iterum uiuus secundum quod diuinitus inspirati prophetae uel haec uel alia de eo innumera miracula futura esse predixerant. Sed et in odiernum cristianorum qui ab ipso nuncupati sunt et nomen perseuerat et genus.

### DEH II.12.2 — `deh-2-12-2`

Canonical source ID: `latin-deh2-num46`.

**DEH Latin passage:**

> [II.12.2] Occisus erat ante mortem Iesu Baptista Iohannes uir sanctus, qui numquam in secundis salutis ueritatem posuerit. Denique ad omnia, quae plena iustitiae docebat, quibus ad cultum dei inuitabat Iudaeos, etiam baptismum propter purificationem animae et corporis instituerat. Cui causa necis libertas, quod perpeti nequiuit ab Herode fraterni uiolata conubii iura germanoque abductam coniugem. Nam cum idem Herodes Romam pergeret, hospitii causa fratris ingressus domum, cui erat uxor Herodias Aristoboli filia, regis Agrippae soror, ausus est eam naturae immemor sollicitare, ut relicto fratre sibi nuberet, cum de urbe Roma reuertisset, et consensu mulieris inita incesti pactio. cuius indicium rei peruenit ad Aretae regis filiam in coniugio adhuc Herodis manentem. Ea riualem indignata redeunti marito insinuauit ut ad Macherunta oppidum dirigeretur, quod erat in confinio Petrei regis et Herodis. Ille qui nihil suspicaretur, simul quia omnem iam circa eandem inminuerat affectum, quo facilius Herodiadi pactionis fidem praestaret si ablegaret coniugem, adquieuit eius secessioni. At illa ubi patrio regno adpropinquauit, cognita patri Aretae prodidit, qui per insidias omnem exercitum Herodis bello lacessitum deleuit proditione facta per eos, qui ex Philippi tetrarchae populo Herodi se adsociauerant. Vnde Herodes querellam Caesari detulit, sed uindictam imperatam a Caesare indignatio dei sustulit. Nam in ipso apparatu belli Caesaris mors nuntiata. Idque Iudaeis aestimatum conperimus et creditum, auctore Iosepho aduersum se idoneo, quod non fraude hominum sed dei commotione Herodes exercitum amiserit et iuste quidem propter uindictam Iohannis Baptistae uiri iusti qui dixerat ei: non tibi licet illam uxorem habere.

#### `deh-2-12-2-aj-1` — AJ 18.117–117

Classification: **BOUNDARIES_AND_SELECTED_TEXT_RETAINED**. Old and current child paths/sides are retained. Intended passage: the existing frozen AJ target, in its recorded order.

Same ordered XML elements and attributes as the certified historical witness; each old interval matches independent October 14 XML expectations; current start/end identities, complete selected text and recomputed offsets checked. Frozen reference retained without expanding the passage.

| Section | Old boundary → current boundary | CP old → current | U16 old → current |
| --- | --- | --- | --- |
| 117 | `1.10.2.2:after → 1.10.2.6:before` → same | `36764:37231` → `36762:37229` | `36764:37231` → `36762:37229` |

**AJ 18.117**

Old = current selected passage:

> Hunc enim herodes occidit uirum ualde bonum qui precipiebat iudaeis uirtuti operam dare. Iustitiam coloere, in deum seruare pietatem et per baptismum in unum coire. Tum demum enim baptismum acceptabile fore si non solum ad abluenda peccata sumatur. Uerum etiam ad castimoniam corporis atque ad animae iustitiam purificationemque seruetur. Omniumque pariter uirtutum uelut signaculum et custodia quaedam fidelis habeatur, quae cum ab eo precepta huiusmodi doceretur.

**Retained witness note:** The Latin baptism account includes its own amplifications and qualifications; these remain literal.

#### `deh-2-12-2-aj-2` — AJ 18.109–115

Classification: **BOUNDARIES_AND_SELECTED_TEXT_RETAINED**. Old and current child paths/sides are retained. Intended passage: the existing frozen AJ target, in its recorded order.

Same ordered XML elements and attributes as the certified historical witness; each old interval matches independent October 14 XML expectations; current start/end identities, complete selected text and recomputed offsets checked. Frozen reference retained without expanding the passage.

| Section | Old boundary → current boundary | CP old → current | U16 old → current |
| --- | --- | --- | --- |
| 109 | `1.10.1:start → 1.10.1.0:before` → same | `34424:34801` → `34422:34799` | `34424:34801` → `34422:34799` |
| 110 | `1.10.1.0:after → 1.10.1.2:before` → same | `34801:35146` → `34799:35144` | `34801:35146` → `34799:35144` |
| 111 | `1.10.1.2:after → 1.10.1.4:before` → same | `35146:35524` → `35144:35522` | `35146:35524` → `35144:35522` |
| 112 | `1.10.1.4:after → 1.10.1.5:before` → same | `35524:35951` → `35522:35949` | `35524:35951` → `35522:35949` |
| 113 | `1.10.1.5:after → 1.10.1.6:before` → same | `35951:36150` → `35949:36148` | `35951:36150` → `35949:36148` |
| 114 | `1.10.1.6:after → 1.10.1.7:before` → same | `36150:36296` → `36148:36294` | `36150:36296` → `36148:36294` |
| 115 | `1.10.1.7:after → 1.10.2:start` → same | `36296:36570` → `36294:36568` | `36296:36570` → `36294:36568` |

**AJ 18.109**

Old = current selected passage:

> His quoque temporibus inter aretam petraeum et herodem regem simulatio magna contingit, propter huiusmodi causam. Herodes tetrarches uxorem habuit aretae filiam cum qua non paruum tempus aduixerat. Sed cum romam euocaretur transiens in domo herodis exceptus est, frater eius erat etiam ipse sed non ex una progenitus. Herodes enim ex filia simonis sacerdotis fuerat proceatus.

**AJ 18.110**

Old = current selected passage:

> Cumque ibi esset herodiadis amore captus est uxoris alterius herodis, filia enim erat ista aristoboli. Soror autem agrippae maioris, audet igitur cum muliere de nuptiis ineundis miscere sermonem. Illa uero suscipiente pacta firmantur ut cum roma reuersus fuisset illa conubiaira susciperet. Erat enim in pactis ut filiam aretae regis excluderet

**AJ 18.111**

Old = current selected passage:

> et herodes quidem romam talibus pactis firmatis aduehitur. Sed cum reuersus fuisset peragens rome propter quae fuerat euocatus uxor eius fideliter cuncta cognoscens quae inter eum fuerant herodiademque composita antequam eam ille cuncta cognouisse sentiret rogat uirum ut in macherunta ubi limes erat aretae herodisque regionis ab eo mitteretur. Nihil suae uoluntatis aperiens.

**AJ 18.112**

Old = current selected passage:

> Hoc herodes libenter accipiens mittit uxorem nihil eam sensisse penitus arbitratus. Illa uero premiserat enim ante multum tempus ad patrem ut ei apud macherunta omnia pararentur, quae itineris usus exposcerent a ductoribus aretae suscipitur. Confestimque intra arabiam atque ibi ab illis ductoribus ad alios ab illisque rursus ad alteros transmisset cum summa cęleritate patri perducitur, cui cuncta herodis aperit uoluntatem.

**AJ 18.113**

Old = current selected passage:

> Ille uero ex hinc inimicitiarum sumpsit initium, atque ab utroque exercitu congregato in regione gamalica bello confligitur. Non quidem ipsis presentibus sed ductoribus ab utraque parte transmissis.

**AJ 18.114**

Old = current selected passage:

> Pugna itaque fa cia et exercitu herodis afflicto proditione pro fugarum qui ex philippi tetrarchia ad herodem quasi auxiliandi causa conuenerant.

**AJ 18.115**

Old = current selected passage:

> Haec herodes scribit ad tyberium, ille autem indignatus quod aretas talia perpetrauerit, scribit uitellio ut ei bellum incunctanter inferret, et aut uiuum eum uinctum adduceret aut certe mortui caput auferret. Tiberius quidem ut haec ageret rectori syriae demandabait.

#### `deh-2-12-2-aj-3` — AJ 18.124–124

Classification: **BOUNDARIES_AND_SELECTED_TEXT_RETAINED**. Old and current child paths/sides are retained. Intended passage: the existing frozen AJ target, in its recorded order.

Same ordered XML elements and attributes as the certified historical witness; each old interval matches independent October 14 XML expectations; current start/end identities, complete selected text and recomputed offsets checked. Frozen reference retained without expanding the passage.

| Section | Old boundary → current boundary | CP old → current | U16 old → current |
| --- | --- | --- | --- |
| 124 | `1.10.3.3:after → 1.10.3.4:before` → same | `38697:39019` → `38695:39017` | `38697:39019` → `38695:39017` |

**AJ 18.124**

Old = current selected passage:

> Quarto autem die adlatae sunt illi litterae in quibus significabatur mors tyberii, et ut omnem multitudinem congregans ad deuotionem gai iurare conpelleret. Milites quoque et auxilia cuncta ad loca propria demittebat. Quod bellum iam gerere non ualeret, nesciens gai propositum in quem potestas rerum translata constaret.

#### `deh-2-12-2-aj-4` — AJ 18.116–116

Classification: **BOUNDARIES_AND_SELECTED_TEXT_RETAINED**. Old and current child paths/sides are retained. Intended passage: the existing frozen AJ target, in its recorded order.

Same ordered XML elements and attributes as the certified historical witness; each old interval matches independent October 14 XML expectations; current start/end identities, complete selected text and recomputed offsets checked. Frozen reference retained without expanding the passage.

| Section | Old boundary → current boundary | CP old → current | U16 old → current |
| --- | --- | --- | --- |
| 116 | `1.10.2:start → 1.10.2.2:before` → same | `36570:36764` → `36568:36762` | `36570:36764` → `36568:36762` |

**AJ 18.116**

Old = current selected passage:

> A quibusdam autem iudaeorum uidebatur ideoque perisse herodis exercitum, quod in eum satis de iohanne baptiza iuste indignatio diuina commota sit. Pro uindicta iohannis qui uocabatur baptistet.

### DEH II.12.3 — `deh-2-12-3`

Canonical source ID: `latin-deh2-num47`.

**DEH Latin passage:**

> [II.12.3] Sed ita haec conteximus quasi uel in suis Iudaei legitima custodierint, apud quos interierat summi ius sacerdotii aut auaritia interemtum aut potiorum insolentia, qui licere quod uellent ius putabant. Namque a principio Aaron summus sacerdos fuit, qui ad filios suos ex uoluntate dei unctione legitima transmisit sacerdotii praerogatiuam, a quibus per ordinem successionis constituti sunt sacerdotii principatum gerentes. Vnde patrio more conualuit neminem fieri principem sacerdotum, nisi qui esset ex sanguine Aaron, cui primum ius istius modi delatum est sacerdotii, alterius autem generis uiro ne regi quidem licere succedere. Denique Ozias, quia usurpauit sacerdotii munus, perfusus lepra temploque eiectus reliquam aetatem sine imperio exegit. Et certe rex optimus fuit, sed usurpare ei non licuit officium religionis.

#### `deh-2-12-3-aj-1` — AJ 20.224–226

Classification: **BOUNDARIES_AND_SELECTED_TEXT_RETAINED**. Old and current child paths/sides are retained. Intended passage: the existing frozen AJ target, in its recorded order.

Same ordered XML elements and attributes as the certified historical witness; each old interval matches independent October 14 XML expectations; current start/end identities, complete selected text and recomputed offsets checked. Frozen reference retained without expanding the passage.

| Section | Old boundary → current boundary | CP old → current | U16 old → current |
| --- | --- | --- | --- |
| 224 | `1.12.3.0:after → 1.12.3.1:before` → same | `50971:51164` → `50964:51157` | `50971:51164` → `50964:51157` |
| 225 | `1.12.3.1:after → 1.12.3.2:before` → same | `51164:51343` → `51157:51336` | `51164:51343` → `51157:51336` |
| 226 | `1.12.3.2:after → 1.12.3.3:before` → same | `51343:51514` → `51336:51507` | `51343:51514` → `51336:51507` |

**AJ 20.224**

Old = current selected passage:

> Necessarium itaque credo et historiae praesenti esse conueniens, narrare de pontificibus quomodo inchoauerunt, et quibus fungi hoc honore permissum est, et quanti fuerunt usque ad belli finem.

**AJ 20.225**

Old = current selected passage:

> Primum itaque omnium dicunt aaron fratrem moyseos pontificatum sumpsisse diuinum, quo moriente, successisse mox filios, et ab aliis eorum denuo liberis honorem unius distributum,

**AJ 20.226**

Old = current selected passage:

> unde legitimum est nullum posse pontificatum percipere nisi de sanguine fuerit aaron ex alio namque genere neque si in regno constitutus sit pontificatum potest adipsici,

#### `deh-2-12-3-aj-2` — AJ 9.216–216

Classification: **BOUNDARIES_RETAINED_APPROVED_TEXT_CHANGE**. Old and current child paths/sides are retained. Intended passage: the existing frozen AJ target, in its recorded order.

Same ordered XML elements and attributes as the certified historical witness; each old interval matches independent October 14 XML expectations; current start/end identities, complete selected text and recomputed offsets checked. Frozen reference retained without expanding the passage.

| Section | Old boundary → current boundary | CP old → current | U16 old → current |
| --- | --- | --- | --- |
| 216 | `1.3.27.1:after → 1.3.27.5:before` → same | `43928:44223` → `43930:44211` | `43928:44223` → `43930:44211` |

**AJ 9.216**

Old selected passage:

> Eodem uero modo et ozias amasiae filius, quarto Hoc ergo tibiiam et decimo anno regni hieroboam duabus tribus in hierosolimis imperauit, cuius mater fuit athelamas nomine, genere uero ciuis. Erat autem hic bonus et naturaliter iustus atque magnanimus et ad rerum prouidentiam nimis industrius.

Current verified passage:

> Eodem uero modo et ozias amasiae filius, quarto iam et decimo anno regni hieroboam duabus tribus in hierosolimis imperauit, cuius mater fuit athelamas nomine, genere uero ciuis. Erat autem hic bonus et naturaliter iustus atque magnanimus et ad rerum prouidentiam nimis industrius.

Justification: the approved IX.216 internal deletion recorded above; section markers, narrative endpoints and the exclusion policy are unchanged.

**Retained exclusions:** `latin-book09-num51`.

#### `deh-2-12-3-aj-3` — AJ 9.222–227

Classification: **BOUNDARIES_AND_SELECTED_TEXT_RETAINED**. Old and current child paths/sides are retained. Intended passage: the existing frozen AJ target, in its recorded order.

Same ordered XML elements and attributes as the certified historical witness; each old interval matches independent October 14 XML expectations; current start/end identities, complete selected text and recomputed offsets checked. Frozen reference retained without expanding the passage.

| Section | Old boundary → current boundary | CP old → current | U16 old → current |
| --- | --- | --- | --- |
| 222 | `1.3.28.0:before → 1.3.28.2:before` → same | `45755:45974` → `45742:45961` | `45755:45974` → `45742:45961` |
| 223 | `1.3.28.2:after → 1.3.28.3:before` → same | `45974:46283` → `45961:46270` | `45974:46283` → `45961:46270` |
| 224 | `1.3.28.3:after → 1.3.28.4:before` → same | `46283:46541` → `46270:46528` | `46283:46541` → `46270:46528` |
| 225 | `1.3.28.4:after → 1.3.28.6:before` → same | `46541:46938` → `46528:46925` | `46541:46938` → `46528:46925` |
| 226 | `1.3.28.6:after → 1.3.28.7:before` → same | `46938:47319` → `46925:47306` | `46938:47319` → `46925:47306` |
| 227 | `1.3.28.7:after → 1.3.29.0:before` → same | `47319:47584` → `47306:47571` | `47319:47584` → `47306:47571` |

**AJ 9.222**

Old = current selected passage:

> [X.iv.222] Dumque haec ita constituisset mittens elatione corruptus et substancia mortali ditatus contra inmortale omni tempore agere nitebatur. Est autem inmortalis substantia pietas circa deum et custodia mandatorum.

**Retained exclusions:** `latin-book09-num51`.

**AJ 9.223**

Old = current selected passage:

> Lapsus est itaque felicitatis euentu, et ad paterna peccata descendit, quae etiam illum post quam claritatem bonorum et rerum magnitudinem de reliquid adprehenderunt. Hic enim in stante insigne die et generali festiuitate, indutus stola sacerdotali intrauit in templum oblaturus incensum in aureo altare deo.

**Retained exclusions:** `latin-book09-num51`.

**AJ 9.224**

Old = current selected passage:

> Pontifice uero azaria eum aliis octuaginta sacerdotibus eum prohibentem ne faceret, quoniam haec solummodo his adiacerent qui ex genere aaron erant et clamantibus ei ut exiret et non ageret contra dei leges, iratus interminatus est eis mortem nisi tacerent,

**Retained exclusions:** `latin-book09-num51`.

**AJ 9.225**

Old = current selected passage:

> inter haec autem terrae motus factus est magnus et stupes cente populo claritas sols nimis effulsit, et incidit in faciem regis, et illi quidem lepra continuo prouenit. Ante ciuitatem uero in loco quae dicitur eroge scissa est media pars montem ad occidentem et sua uolubilitate per quattuor stadia procedens ad orientalem restitit montem ita ut et uiasuiras clauderet et regios urbes obprimeret.

**Retained exclusions:** `latin-book09-num51`.

**AJ 9.226**

Old = current selected passage:

> Cumque sacerdotes regis faciem lepram adprehendisse, conspiciunt, pandebant ei calamitatem suam hortantes ut tamquam pollutus exiret a ciuitate, ille uero confusione huius euentus, et dum illi iam esset nulla fiducia quod iuuebat impleuit, qui licet fuisset ultra humanos mentes de uatus, et propter hoc impie gressisset in deo miserabilem tantum hanc et uilem protulit passionem,

**Retained exclusions:** `latin-book09-num51`.

**AJ 9.227**

Old = current selected passage:

> et tempus quidem aliquod extra ciuitatem commoratus in uita priuata de gens filio licet eius suspiciente regnum. Deinde mestitia faciente defunctus est qui uixit quidem annis octo et sexaginta, regnauit quinquaginta et duo, supultus est autem solus in hortis,

**Retained exclusions:** `latin-book09-num51`.

### DEH II.13.1 — `deh-2-13-1`

Canonical source ID: `latin-deh2-num48`.

**DEH Latin passage:**

> [II.13.1] Fuerunt itaque ex quo egressi sunt ex Aegypto patres usque ad aedificationem templi quod Solomon condidit principes sacerdotum XIII qui fiunt anni DCXII, quoniam primum qui erat princeps sacerdotum usque ad mortem perseuerabat, nec quisquam in locum uiuentium substituebatur. Postea etiam uiuentibus subrogabantur. Ergo isti XIII per successionem adepti sunt sacerdotium, quibus temporibus et aristocratia fuit et monarchia iudicum et regum potestas. Rursus a Solomone usque ad tempora captiuitatis, quando in Syriam populus demigrauit urbe capta temploque exusto, fuerunt sacerdotum principes XVIII per annos CCCCLX et menses VI et dies X. LXX autem annis in captiuitate populus fuit. Postea Cyrus cum dimitteret populum de regione Assyriorum et templi aedificandi potestatem daret, etiam sacerdotum principem Iosedec qui simul abductus erat redire permisit, ut ritus ueteris sollemnitas per adsueti sacerdotis scientiam reformaretur. Ipse igitur et posteri sui XV numero uiri a reditu populi usque ad Antiochum Eupatorem officio functi sunt per ordinem successionis et principatum sacerdotii repraesentarunt annis CCCCXIIII. Primus Antiochus, quem supra memorauimus, et dux eius Lysias occiso Onia sacerdotum principe in locum eius substituerunt Iacimum in sacerdotium. Qui licet fuerit de Aaron genere, non tamen fuit de ipsa domo. Vnde Ananias frater Oniae pergens in Aegyptum petit a Ptolomaeo Filometore et Cleopatra coniuge Filometoris, qui ritus obseruationis ad Hierosolymitanae sollemnitatis similitudinem in Alexandrinae urbis cultibus inseruerat, ut illic princeps sacerdotum subrogaretur, eo quod Iacimus legitimam non haberet sacerdotii successionem. Atque idem tamen exacto triennio defunctus; nec successorem habere meruit, qui abrogauerat legitimae successionis sollemnitatem. Fuit itaque VII annis ciuitas sine principe sacerdotii. Vsque ad hoc tempus regressionis patrum de terra Assyriorum democratiam tenuit, eo quod per iniquitates regum in captiuitatem se esse deductum Iudaeorum populus recognosceret. Asamonaei postea nancti potestatem populo praesidendi Ionathen sacerdotum principem constituere, qui per annos VII functus suscepto munere per insidias Tryphonis finem uitae inuenit. In cuius locum Simon frater germanus tamquam iure hereditario per electionem tamen successit, quem generi insidiis inter epulas extinctum accepimus. A quo ad filium eius Hyrcanum, quem fuga periculo exemerat, praerogatiua sacerdotii demigrauit. Hyrcano autem Aristobolus, qui etiam regnum memorato adiunxit muneri ut utriusque esset particeps, et Aristobolo Alexander substituti sunt. Penes Alexandrum et regnum et sacerdotium usque ad diem uitae eius mansit supremum, per VII scilicet et XX annos, sed plerumque dubio statu, nam et anceps inter ipsum et Demetrium uictoria fuit et odium immane a ciuibus.

#### `deh-2-13-1-aj-1` — AJ 20.230–242

Classification: **BOUNDARIES_AND_SELECTED_TEXT_RETAINED**. Old and current child paths/sides are retained. Intended passage: the existing frozen AJ target, in its recorded order.

Same ordered XML elements and attributes as the certified historical witness; each old interval matches independent October 14 XML expectations; current start/end identities, complete selected text and recomputed offsets checked. Frozen reference retained without expanding the passage.

| Section | Old boundary → current boundary | CP old → current | U16 old → current |
| --- | --- | --- | --- |
| 230 | `1.12.3.8:after → 1.12.4.0:before` → same | `52213:52437` → `52206:52430` | `52213:52437` → `52206:52430` |
| 231 | `1.12.4.0:after → 1.12.4.1:before` → same | `52437:52761` → `52430:52754` | `52437:52761` → `52430:52754` |
| 232 | `1.12.4.1:after → 1.12.4.2:before` → same | `52761:52903` → `52754:52896` | `52761:52903` → `52754:52896` |
| 233 | `1.12.4.2:after → 1.12.4.3:before` → same | `52903:53090` → `52896:53083` | `52903:53090` → `52896:53083` |
| 234 | `1.12.4.3:after → 1.12.5.0:before` → same | `53090:53321` → `53083:53314` | `53090:53321` → `53083:53314` |
| 235 | `1.12.5.0:after → 1.12.5.1:before` → same | `53321:53566` → `53314:53559` | `53321:53566` → `53314:53559` |
| 236 | `1.12.5.1:after → 1.12.5.2:before` → same | `53566:53839` → `53559:53832` | `53566:53839` → `53559:53832` |
| 237 | `1.12.5.2:after → 1.12.5.6:before` → same | `53839:54042` → `53832:54035` | `53839:54042` → `53832:54035` |
| 238 | Unavailable → unavailable; no substitute | — | — |
| 239 | `1.12.5.6:after → 1.12.5.7:before` → same | `54042:54165` → `54035:54158` | `54042:54165` → `54035:54158` |
| 240 | `1.12.5.7:after → 1.12.5.8:before` → same | `54165:54347` → `54158:54340` | `54165:54347` → `54158:54340` |
| 241 | `1.12.5.8:after → 1.12.6.0:before` → same | `54347:54433` → `54340:54426` | `54347:54433` → `54340:54426` |
| 242 | `1.12.6.0:after → 1.12.6.1:before` → same | `54433:54742` → `54426:54735` | `54433:54742` → `54426:54735` |

**AJ 20.230**

Old = current selected passage:

> Tempus igitur quo isti XIII, habuere principatum a die qua aegyptum patres nostri moyse duce reliquerunt usque ad aedificationem templi quod salomon rex ierosolimorum urbe construxit, fuit annorum XII, et sex centorum,

**AJ 20.231**

Old = current selected passage:

> post illos itaque XIII pontifices XVIII, alii hanc tenuere potestatem a salomonis regis temporibus ierosolimis sibimet succedentes, usque ad aduentum nabucodonosor babiloniorum regis qui castra metatus aduersus urbem templum quidem concremauit gentem uero nostram in babiloniam migrauit, et pontificem iosad captiuum duxit.

**AJ 20.232**

Old = current selected passage:

> Tempus enim pontificatus horum quadringentorum LXVI, fuit annorum, mensium sex dierumque XX, Cum utique iudaei essent sub regibus constituti.

**AJ 20.233**

Old = current selected passage:

> Post tempus autem annorum LXX, captiuitatis gestae per babilo nios syrus persarum rex dimisit ex babilonia iudaeos ad propriam remeare terram atque concessit templum aedificari captiuis.

**AJ 20.234**

Old = current selected passage:

> His itaque remeantibus, sison pontificatus sumpsit, et ex eius genere alii quindecim usque ad tempus regit antiochi qui uocabatur euphator hunc habuere praesulatum. Conuersabantur autem popularia potestate annis quadringentis

**AJ 20.235**

Old = current selected passage:

> XIIII. Primusque antiochus quem prędiximus et princeps militiae eius lisias oniam cui erat menelaus cognomentum pontificatu deposuerunt perimentes eum in bero ea, et constituerunt pontificem ioachim ex genere quidem aarom non autem exista domu.

**AJ 20.236**

Old = current selected passage:

> Propterea et ananias defuncti fratruhelis et nomen referens patris, ueniens in aegyptum ptolomei filometoris amicus effectus et cleopatrę eius uxoris suasit eis ut secundum helio politicam legem deo constituerent templum ierosolimitano simile et eum pontificem ordinarent.

**AJ 20.237**

Old = current selected passage:

> Sed de templo quidem apud aegyptum aedificato saepius declarauimus. Ioachim uero cum tribus annis habuisset ponfificatum defunctus est, cui successit neme, sed per annos VII, ciuitas fuit sine pontifice

**AJ 20.238**

No independent Latin interval is available for Jonathan’s appointment in XX.238 in the present transcription; the neighboring vacancy and Tryphon/Simon wording remains in XX.237 and XX.239. The cause of the absence is undetermined.

**AJ 20.239**

Old = current selected passage:

> quo per insidias moriente dolo trifonis sicut superius iam quodam loco narrauimus accepit honorem hunc symon germanus eius

**Retained witness note:** The surviving Latin opens with a relative clause whose Jonathan antecedent has no independent interval in XX.238.

**AJ 20.240**

Old = current selected passage:

> huic per dolum quoque generi in conuiuio morienti filius successit hyrcanus, qui cum tenuisset pontificatus annis XXXI, in senectute moriens cum et pontificatum tenuisset et regnum.

**Retained witness note:** The Latin compresses and attaches kingship wording to this sentence; the adjacent XX.241 correspondence is reordered.

**AJ 20.241**

Old = current selected passage:

> Is namque primus usus est anno diademate. Heredem fratrem dereliquit alexandrum.

**Retained witness note:** The Latin diadem and Alexander succession statements are compressed and reordered relative to Greek XX.241.

**AJ 20.242**

Old = current selected passage:

> Alexander autem cum et regnasset et sacerdotium tenuisset, annis XXVII, uita priuatus est. Alexandrae coniugi praecipiens ut ipsa pontificem ordinaret, quae pontificatum quidem hyrcano suo filio dedit, regnum uero ipsa retinens anni VIIII, defuncta est. Cuius filius hyrcanus pertempus pontificatum optinuit.

### DEH II.13.2 — `deh-2-13-2`

Canonical source ID: `latin-deh2-num49`.

**DEH Latin passage:**

> [II.13.2] Moriens Alexander, qui periculosam filiis suis cerneret odiorum suorum hereditatem, Alexandriam coniugem suam exercitam usu imperii et communium adsuetudine consiliorum, gratiorem tamen populo, quod et aduersum uiri saeuitiam periclitantibus frequenter praesidio fuerit et coniugi temperamento, regni praeesse uoluit gubernaculo, arbitram simul statuens, cuinam potissimum filiorum summum sacerdotium committeretur. Illa Hyrcanum patri substituit in sacerdotium, uel propter senioris aetatis praerogatiuam, uel quod leniore quam frater ingenio nullas super regni negotiis matri uideretur molestias excitaturus. Aristobolo nihil publicorum commisit officiorum, sed ille etiam uiuente matre, aegritudinis tamen eius occasione, in remotis et munitioribus locis regem agebat. Quo offensa mater et Hyrcani querellis anxia uim morbi aluit, nec ultra VIIII annos imperii progressa omnium heredem Hyrcanum reliquit, non quo seruaturum praesumeret, sed ne indignum iuuaret aut usurpatoris insolentiam iudicio prosperiore accenderet.

#### `deh-2-13-2-aj-1` — AJ 20.242–242

Classification: **BOUNDARIES_AND_SELECTED_TEXT_RETAINED**. Old and current child paths/sides are retained. Intended passage: the existing frozen AJ target, in its recorded order.

Same ordered XML elements and attributes as the certified historical witness; each old interval matches independent October 14 XML expectations; current start/end identities, complete selected text and recomputed offsets checked. Frozen reference retained without expanding the passage.

| Section | Old boundary → current boundary | CP old → current | U16 old → current |
| --- | --- | --- | --- |
| 242 | `1.12.6.0:after → 1.12.6.1:before` → same | `54433:54742` → `54426:54735` | `54433:54742` → `54426:54735` |

**AJ 20.242**

Old = current selected passage:

> Alexander autem cum et regnasset et sacerdotium tenuisset, annis XXVII, uita priuatus est. Alexandrae coniugi praecipiens ut ipsa pontificem ordinaret, quae pontificatum quidem hyrcano suo filio dedit, regnum uero ipsa retinens anni VIIII, defuncta est. Cuius filius hyrcanus pertempus pontificatum optinuit.

### DEH II.13.3 — `deh-2-13-3`

Canonical source ID: `latin-deh2-num50`.

**DEH Latin passage:**

> [II.13.3] Verum Alexandriae mors etiam Hyrcano sacerdotium regnumque ademit. Nam bello uictus ad munitiora se contulit retentisque coniuge et filiis Aristoboli, quos in castro inuenerat, amplexatus est mutare condicionem ut ad Aristobolum potestas omnis transiret et sacerdotium, ipse priuatus in domum Aristoboli concederet.

#### `deh-2-13-3-aj-1` — AJ 20.243–243

Classification: **BOUNDARIES_AND_SELECTED_TEXT_RETAINED**. Old and current child paths/sides are retained. Intended passage: the existing frozen AJ target, in its recorded order.

Same ordered XML elements and attributes as the certified historical witness; each old interval matches independent October 14 XML expectations; current start/end identities, complete selected text and recomputed offsets checked. Frozen reference retained without expanding the passage.

| Section | Old boundary → current boundary | CP old → current | U16 old → current |
| --- | --- | --- | --- |
| 243 | `1.12.6.1:after → 1.12.6.2:before` → same | `54742:54922` → `54735:54915` | `54742:54922` → `54735:54915` |

**AJ 20.243**

Old = current selected passage:

> Post mortem namque alexandrae dimicauit aduersus eum, frater aristobolus, et dum uicisset illum. Illum quidem pontificatu remouit. Ipse uero et regnum tenuit et dei pontifex fuit.

### DEH II.13.5 — `deh-2-13-5`

Canonical source ID: `latin-deh2-num52`.

**DEH Latin passage:**

> [II.13.5] Qui eludentem Aristobolum anno iam tertio imperitantem bello perculit, auctoritate cepit atque ante uictoriam custodiae dedit superatoque eius populo et capta urbe, captiuum ipsum cum filiis Romam dirigi praecipiens, Hyrcano sacerdotii dignitatem refudit atque eum praesidere ciuibus absque diademate tamen regnique infulis statuit, largus quidem honoris sed consultor quietis, ne fraternae insolentiae spiritu pax turbaretur. Ita Aristobolus, captus licet, Hyrcanum tamen regno exuit, qui XXIIII annos postea maiore usu quam nomine in potestate exegit.

#### `deh-2-13-5-aj-2` — AJ 20.245–245

Classification: **BOUNDARIES_AND_SELECTED_TEXT_RETAINED**. Old and current child paths/sides are retained. Intended passage: the existing frozen AJ target, in its recorded order.

Same ordered XML elements and attributes as the certified historical witness; each old interval matches independent October 14 XML expectations; current start/end identities, complete selected text and recomputed offsets checked. Frozen reference retained without expanding the passage.

| Section | Old boundary → current boundary | CP old → current | U16 old → current |
| --- | --- | --- | --- |
| 245 | `1.12.6.3:after → 1.12.6.4:before` → same | `55210:55470` → `55203:55463` | `55210:55470` → `55203:55463` |

**AJ 20.245**

Old = current selected passage:

> Habuit autem hyrcanus hanc potestatem super nouem priores alios annos uiginti et tres. Barzanis autem et pacorus parthiene potentes transeuntes eufraten et pugnantes aduersus hyrcanum ipsum quidem coeperunt, aristoboli uero filium antigonum constituere regem,

### DEH II.13.6 — `deh-2-13-6`

Canonical source ID: `latin-deh2-num53`.

**DEH Latin passage:**

> [II.13.6] Nec tamen is uitae finis Hyrcano qui potestatis fuit. Nam reliquum tempus dedecori cessit, ut supra memorauimus, siquidem superatus proelio Parthis Euphraten transgredientibus captus et Antigono Aristoboli filio in potestatem datus truncatis quoque auribus nec sic quidem aerumnae miserabilis inpleuit acerbitatem. Nam post illa in Parthiam quoque abductus exul, debilis senex ludibrium de se barbaris praebuit, et cognito postea quod Herodes imperitaret, cuius coniugio Mariamme neptis sua potiebatur, in Iudaeam reuertit. Vbi primo summa honoris specie susceptus, quo insidiarum uelamen obtenderetur, haut multo post adficto crimine quod potestatem repetere uellet interemtus est.

#### `deh-2-13-6-aj-1` — AJ 20.245–245

Classification: **BOUNDARIES_AND_SELECTED_TEXT_RETAINED**. Old and current child paths/sides are retained. Intended passage: the existing frozen AJ target, in its recorded order.

Same ordered XML elements and attributes as the certified historical witness; each old interval matches independent October 14 XML expectations; current start/end identities, complete selected text and recomputed offsets checked. Frozen reference retained without expanding the passage.

| Section | Old boundary → current boundary | CP old → current | U16 old → current |
| --- | --- | --- | --- |
| 245 | `1.12.6.3:after → 1.12.6.4:before` → same | `55210:55470` → `55203:55463` | `55210:55470` → `55203:55463` |

**AJ 20.245**

Old = current selected passage:

> Habuit autem hyrcanus hanc potestatem super nouem priores alios annos uiginti et tres. Barzanis autem et pacorus parthiene potentes transeuntes eufraten et pugnantes aduersus hyrcanum ipsum quidem coeperunt, aristoboli uero filium antigonum constituere regem,

### DEH II.13.7 — `deh-2-13-7`

Canonical source ID: `latin-deh2-num54`.

**DEH Latin passage:**

> [II.13.7] Nactus igitur Herodes regnum, quod a Romanis pro obpugnatae uel proditae patriae mercede acceperat, in locum Antigoni, qui triennio et tribus mensibus tenuerat imperium, substituit successores in sacerdotium non Asamonaei generis, quos clarioris fuisse prosapiae accepimus, sed ignobiles quosque quos aut libido aut casus dedisset, tamen fatigatus Alexandriae precibus socrus uel insimulationibus territus Ionathen coniugis suae fratrem XVII annos agentem sacerdotem creauit. Quem mox ipse exitio dedit suspectum imperii, quod circa eum ingentem populi totius gratiam in dies uideret adolescere. Posthabito itaque Anhelo, quem iam ex ignobilibus ante Ionathen in sacerdotium subrogauerat, reliquos per ordinem huiusmodi elegit, de quibus nihil suspectum haberet. Nam quod in adfine perpeti non potuerat, quemadmodum non caueret in alienis? Similia in huiusmodi ordinationibus Archelaus secutus, paternae specie consuetudinis angustioris animi tenuit sententiam more quodam insito mortalibus, ut apud eos minus suspecta sit ignauia hebetiorum quam gratia bonorum, cum infirmus animus insolentior sit in rebus secundis, prudentior autem nouerit uicem referre beneficiis.

#### `deh-2-13-7-aj-1` — AJ 20.247–249

Classification: **BOUNDARIES_AND_SELECTED_TEXT_RETAINED**. Old and current child paths/sides are retained. Intended passage: the existing frozen AJ target, in its recorded order.

Same ordered XML elements and attributes as the certified historical witness; each old interval matches independent October 14 XML expectations; current start/end identities, complete selected text and recomputed offsets checked. Frozen reference retained without expanding the passage.

| Section | Old boundary → current boundary | CP old → current | U16 old → current |
| --- | --- | --- | --- |
| 247 | `1.12.7.0:after → 1.12.7.2:before` → same | `55613:55822` → `55606:55815` | `55613:55822` → `55606:55815` |
| 248 | `1.12.7.2:after → 1.12.7.3:before` → same | `55822:56147` → `55815:56140` | `55822:56147` → `55815:56140` |
| 249 | `1.12.7.3:after → 1.12.7.4:before` → same | `56147:56367` → `56140:56360` | `56147:56367` → `56140:56360` |

**AJ 20.247**

Old = current selected passage:

> Herodes uero commisso regno sibimet a romanis, nequaquam constituit ex genere asamonei pontifices, sed quibusdam ignobilibus, et qui solum modo de sacerdotibus essent praeter aristobolum tribuit hunc honorem.

**AJ 20.248**

Old = current selected passage:

> Aristobolum namque filium hyrcani qui parthis captus fuerat pontificem constituens, sororem eius mariam dixit uxorem. Obquam rem fauorem populi sibimet collocauit propter hyrcani memoriam. Deinde metuens ne cuncti ad aristobulum declinarent, eum in iericho suffocari dolo machinatus est, cum nataret sicuti iam declarauimus.

**AJ 20.249**

Old = current selected passage:

> Post hunc autem naquaquam alicui ex genere asamonei pontificatus tribuit potestatem similia quoque gessit in constitutione sacerdotum archelaus herodis filius, pariter et romani postea super iudaeos optinentes imperium.

#### `deh-2-13-7-aj-2` — AJ 15.38–56

Classification: **BOUNDARIES_AND_SELECTED_TEXT_RETAINED**. Old and current child paths/sides are retained. Intended passage: the existing frozen AJ target, in its recorded order.

Same ordered XML elements and attributes as the certified historical witness; each old interval matches independent October 14 XML expectations; current start/end identities, complete selected text and recomputed offsets checked. Frozen reference retained without expanding the passage.

**Retained display qualification:** Original citation: AJ XV.38 et sqq. (endpoint unspecified). The displayed XV.38–56 excerpt was separately approved on 2 October 2026 (P4-D07).

| Section | Old boundary → current boundary | CP old → current | U16 old → current |
| --- | --- | --- | --- |
| 38 | `1.2.6.7:after → 1.2.7.2:before` → same | `9544:9633` → `9544:9633` | `9544:9633` → `9544:9633` |
| 39 | `1.2.7.2:after → 1.2.7.3:before` → same | `9633:9710` → `9633:9710` | `9633:9710` → `9633:9710` |
| 40 | `1.2.7.3:after → 1.2.7.4:before` → same | `9710:9796` → `9710:9796` | `9710:9796` → `9710:9796` |
| 41 | `1.2.7.4:after → 1.2.8.0:before` → same | `9796:10040` → `9796:10040` | `9796:10040` → `9796:10040` |
| 42 | `1.2.8.0:after → 1.2.8.2:before` → same | `10040:10234` → `10040:10234` | `10040:10234` → `10040:10234` |
| 43 | `1.2.8.2:after → 1.2.8.3:before` → same | `10234:10414` → `10234:10414` | `10234:10414` → `10234:10414` |
| 44 | `1.2.8.3:after → 1.2.8.4:before` → same | `10414:10646` → `10414:10646` | `10414:10646` → `10414:10646` |
| 45 | `1.2.8.4:after → 1.2.8.5:before` → same | `10646:10819` → `10646:10819` | `10646:10819` → `10646:10819` |
| 46 | `1.2.8.5:after → 1.2.8.6:before` → same | `10819:11104` → `10819:11104` | `10819:11104` → `10819:11104` |
| 47 | `1.2.8.6:after → 1.2.8.7:before` → same | `11104:11359` → `11104:11359` | `11104:11359` → `11104:11359` |
| 48 | `1.2.8.7:after → 1.2.8.11:before` → same | `11359:11615` → `11359:11615` | `11359:11615` → `11359:11615` |
| 49 | `1.2.8.11:after → 1.2.9.0:before` → same | `11615:11721` → `11615:11721` | `11615:11721` → `11615:11721` |
| 50 | `1.2.9.0:after → 1.2.9.1:before` → same | `11721:11946` → `11721:11946` | `11721:11946` → `11721:11946` |
| 51 | `1.2.9.1:after → 1.2.9.2:before` → same | `11946:12213` → `11946:12213` | `11946:12213` → `11946:12213` |
| 52 | `1.2.9.2:after → 1.2.9.3:before` → same | `12213:12568` → `12213:12568` | `12213:12568` → `12213:12568` |
| 53 | `1.2.9.3:after → 1.2.9.4:before` → same | `12568:12878` → `12568:12878` | `12568:12878` → `12568:12878` |
| 54 | `1.2.9.4:after → 1.2.9.5:before` → same | `12878:13018` → `12878:13018` | `12878:13018` → `12878:13018` |
| 55 | `1.2.9.5:after → 1.2.9.7:before` → same | `13018:13275` → `13018:13275` | `13018:13275` → `13018:13275` |
| 56 | `1.2.9.7:after → 1.2.10.0:before` → same | `13275:13439` → `13275:13439` | `13275:13439` → `13275:13439` |

**AJ 15.38**

Old = current selected passage:

> post quam autem locuti sunt dextris datis, reconciliantur omni suspicione sublata.

**AJ 15.39**

Old = current selected passage:

> Itaque rex herodes statim principatu sacerdotii anandum praeter legem exuit,

**Retained witness note:** The Latin compresses material from Greek XV.39–40 into one removal statement. The phrase praeter legem, corresponding to the statement in Greek §40 that Herod acted unlawfully, occurs earlier and remains in this Latin interval. See the reciprocal note at XV.40.

**AJ 15.40**

Old = current selected passage:

> seditiones domesticas pacando, nam non licebat aliquem honore semel accepto fraudari,

**Retained witness note:** Partial correspondence: the Latin compresses material from Greek XV.39–40 into one removal statement. Seditiones domesticas pacando corresponds to the household-disturbance phrase within Greek §40. Praeter legem, corresponding to the statement in Greek §40 that Herod acted unlawfully, occurs earlier and remains in the Latin interval assigned to XV.39. This displayed Latin interval supplies only part of the Greek section.

**AJ 15.41**

Old = current selected passage:

> quod prius antiochus epifanis destruxit, dum auferret ab hiesu sacerdotium et ordinaret fratrem eius oniam. Secundus autem aristobolus hyrcanum fratrem suum priuauit. Tertius herodes principatum sacerdotii adulescenti tradidit aristobolo.

**AJ 15.42**

Old = current selected passage:

> Tunc quidem putabat putabat sedasse contentionem, et licet reconciliati fuissent non tamen securus degebat, dum alexandram expraeteritis conatibus ne tempus nouarum rerum caperet ualde timeret.

**AJ 15.43**

Old = current selected passage:

> Qua propter praecepit eam ita in aula conuersari, ut nihil sub potestatem suam haberet, diligenter etiam custodiebatur occulte nequid praeter cottidianam conuersationem niteretur,

**AJ 15.44**

Old = current selected passage:

> quae paulatim magis illam exacerbabant et inodio suscitabant. Nam superbia mulieris, diligentiam custodiae indignabatur habere, dum omnia uellet potius pati quam fiducia priuari, et fucosum honorem cum seruitute uel metu possidere.

**AJ 15.45**

Old = current selected passage:

> Ad cleopatram igitur in quibus existeret, frequener se lamentando destinabat, postulans auxilium sibi praeberi, quae iussit ei furtim cum filio in aegyptum ad se confugere.

**AJ 15.46**

Old = current selected passage:

> Cumque hoc ei placuisset tale aliquid excogitauit, duo locula tamquam pro mortuorum exequiis parauit, in quibus se ipsam et filium mitti dixit, praecipiens consciis famulis ea noctu deferre, et exinde uiam ad mare facere, ubi nauem in qua nauigarent ad aegyptum praeparatam habuisset.

**AJ 15.47**

Old = current selected passage:

> Haec sabbioni amico alexandro esopus seruus eius edixit. Quod cum sabbio audisset et inimicus herodis esset, quod inter insidiatores antipatri de ueneno conscius putaretur, odium lenire per indicationis fauorem sperauit, et renuntiat insidias alexandrae.

**AJ 15.48**

Old = current selected passage:

> Qui cum eam usque ad conatum procedere demisisset, in ipso facinoris opere detinuit, sed inuitus concessit culpam, dum putaret et nullatenus cleopatram cessare si contra se causam inuenisset. Palam ergo magnanimitate uel modestia, ueniam ei largitus est.

**AJ 15.49**

Old = current selected passage:

> Proposuit tamen omnibus modis adulescentem perimere, sed tacito propter uerisimilem dissimulationem.

**AJ 15.50**

Old = current selected passage:

> Cum ergo tabernaculorum festiuitas uenisset, quae apud nos cum summa ueneratione celebratur, tunc quidem distulit et in de liiis ipse et reliqua multitudo degebat, mouit tamen eum festinare uoluntatem suam conficere inuidia.

**AJ 15.51**

Old = current selected passage:

> Nam dum adulescens, aristobolus septimum et undecimum annum ducens secundum legem super aram ascenderet uictimas immolaturus, et ornatu sacerdotali circumdatus celebraret religionis consequentia magnitudinem superare aetatis ostendens, nec non et generis dignitatem,

**AJ 15.52**

Old = current selected passage:

> populi sui excitauit fauorem, et aristoboli aui sui praesens memoriam ei reduxit. Qui paulatim irritati uoluntates suas iam demonstrabant gaudentes simul et laetitia perfusi, uocesque laudabiles in eum orationibus mixtas emittebant. Ut manifestus fieret populi fauor et temerarius, sub regno itaque constituti cum aliorum praeterita beneficia memorarent.

**AJ 15.53**

Old = current selected passage:

> Inter haec omnia statuit herodes uoluntatem quam in adulescentem habuisset implere. Celebratione autem transacta, dum in hierichunte maneret, et in conuiuio eos alexandra peteret, herodes adulabatur adulescenti et inliciebat ad affluentiam potionis, paratus colludere uel iuueniliter ad gratiam illius iocari,

**AJ 15.54**

Old = current selected passage:

> et loco aestiuo illic existente collecti simul exierunt refrigerium captantes. Cumque fontibus assistent calorem meridianum aula temperare,

**AJ 15.55**

Old = current selected passage:

> prius quidem natantes seruos et amicos prospiciebant. Post autem adulescens cum irritaretur, herodis amici quibus hoc praeceptum fuerat tenebris iam tenentibus saepe eum mergentes tamquam eludentes non emiserunt usque quo eum pressum fontibus suffocarent.

**AJ 15.56**

Old = current selected passage:

> Aristobolus quidem ita extinctus est, decimum et octauum annum agens aetatis cum principatum sacerdotii annon amplius tenuisset quem rursus ananelus suscepit.

### DEH II.13.8 — `deh-2-13-8`

Canonical source ID: `latin-deh2-num55`.

**DEH Latin passage:**

> [II.13.8] Igitur a regno Herodis usque ad Romanorum imperium, quod Archelao deiecto Iudaeam reliquis prouinciis adsociauerat, atque inde usque ad templi excidium et triumphum Titi fuerunt sacerdotum principes XXVIII per annos CLXX. Sane apud plerosque eorum dignitatis sola functio, penes paucos etiam ius potestatis fuit. Liquet igitur in sacerdotum principibus non perseuerasse legitimi generis successionem, quia non omnes ex Aaron neque ex filiis eius, qui in eius subrogati locum formam praescriptae successionis ceteris dereliquere. Itaque cum auaritia aut perfidia suorum corrupta essent maiorum instituta, uiolata iura religionis, conuulsa antiquitatis praesidia, non immerito eos diuina deseruit opitulatio. Eoque tamquam in uacuum populum omni iniuriarum genere processum, ut seditionibus domesticis in se ipsos manus uerterent, latrociniis grauibus adflictarentur, taeterrimos sortirentur iudices, ut inprobis nequiores succederent.

#### `deh-2-13-8-aj-1` — AJ 20.250–251

Classification: **BOUNDARIES_AND_SELECTED_TEXT_RETAINED**. Old and current child paths/sides are retained. Intended passage: the existing frozen AJ target, in its recorded order.

Same ordered XML elements and attributes as the certified historical witness; each old interval matches independent October 14 XML expectations; current start/end identities, complete selected text and recomputed offsets checked. Frozen reference retained without expanding the passage.

| Section | Old boundary → current boundary | CP old → current | U16 old → current |
| --- | --- | --- | --- |
| 250 | `1.12.7.4:after → 1.12.7.5:before` → same | `56367:56565` → `56360:56558` | `56367:56565` → `56360:56558` |
| 251 | `1.12.7.5:after → 1.12.8.0:before` → same | `56565:56800` → `56558:56793` | `56565:56800` → `56558:56793` |

**AJ 20.250**

Old = current selected passage:

> Sunt ergo uiri qui ab herodis temporibus pontiticatum habuerunt usque ad diem quatitus templum et ciuitatem capiens conere mauit cuncti simul XXVIIII. Tempus autem horum anni sunt centum et septem.

**AJ 20.251**

Old = current selected passage:

> Quorum quidam conuersati sunt sub herodis regno et filli eius archelai, post horum uero mortem populi quidem potestate cuncta regnabantur. Praesulatum tamen gentis pontifices optinebant haec ergo de pontificibus dicta sufficiant.

### DEH III.5.2 — `deh-3-5-2`

Canonical source ID: `latin-deh3-num17`.

**DEH Latin passage:**

> [III.5.2] Vrbs ea Syriae sine retractatione prima ideoque metropolis habetur, condita ab his qui Alexandro Magno bellanti adhaesere, conditoris sui nuncupata uocabulo. Situs urbis, porrecta in inmensum longitudine, in lato angustior, quia praerupto montis a laeua artatur, ut extendi ulterius metandae urbis spatia nequirent. Necessitas locum signauit, quia per occulta et deuia inrumpentibus Parthis mons celsior latibulum daret, ex quo se inopinato aduentu et promtiore impetu in imparatam Syriam effunderent, nisi ciuitas monti uelut claustrum obiaceret exitusque obstrueret aduenientibus, ut si quis barbarorum ascenderet, statim e medio urbis sinu prospectaretur. Denique ferunt, cum ludi scenici in ea urbe celebrarentur, quendam actorem mimorum eleuatis oculis ad montem Persas uidisse aduenientes et dixisse continuo: ‘Aut somnium uideo aut magnum periculum. Ecce Persae’. Ita mons urbi praeminet, ut nec theatri altitudo ad prospiciendum montem impedimento sit. Fluuius eam medius intersecat, qui a solis ortu oriens non longe ab urbe in mare conditur, quem de originis suae tractu Orientem ueteres appellauerunt, ut uulgo putetur locis nomen dedisse, cum inde acceperit. Cuius fluentis ipso impetu frigidioribus et zephyris assiduo per ea locorum spirantibus tota ciuitas momentis prope omnibus refrigeratur, ut Orientis in partibus Orientem absconderit. Intus dulces aquae, foris finitimum nemus intextum cupressis crebris fontes atque uberes. Daphnen uocant, quod numquam deponat uiriditatem. Frequens et laetior populus ut pleraque Orientis facetiorque prope omnibus sed propior lasciuiae. Vrbs tertio loco ante ex omnibus, quae in orbe Romano sunt ciuitatibus aestimata, nunc quarto, postquam Constantinopolim excreuit ciuitas Byzantiorum, Persarum quondam caput, nunc repulsorium. De situ urbis satis dictum puto. Neque enim describendis eius aedificiis immorandum uidetur. Cuius a tergo cum orientem dixerim, satis liquet a laeua meridiem iacere, a fronte Europam occurrere, in dexteram septentrionales gentes degere Caspiaque regna haberi, quae ante promtissima ad incursandam Syriam erant. Sed postquam Alexander Magnus Caspiam portam Tauri montis praerupto inposuit atque omne interioribus gentibus interclusit iter, memoratam urbem quietam reddidit, nisi forte motus Persicos suspectantem.

#### `deh-3-5-2-aj-3` — AJ 18.97–97

Classification: **BOUNDARIES_AND_SELECTED_TEXT_RETAINED**. Old and current child paths/sides are retained. Intended passage: the existing frozen AJ target, in its recorded order.

Same ordered XML elements and attributes as the certified historical witness; each old interval matches independent October 14 XML expectations; current start/end identities, complete selected text and recomputed offsets checked. Frozen reference retained without expanding the passage.

| Section | Old boundary → current boundary | CP old → current | U16 old → current |
| --- | --- | --- | --- |
| 97 | `1.9.0.3:after → 1.9.0.5:before` → same | `30876:31152` → `30874:31150` | `30876:31152` → `30874:31150` |

**AJ 18.97**

Old = current selected passage:

> Haec itaque ad uitellium scribente tyberio ille magnis muneribus persuadet ibe rorum et labanorum regi ut tcum artabano sine ulla dilatione pugnarent. At illi a pugna quidem abstinent, uerum scitas concesso ei transitu aperientes caspias pilas in artabani regiones inmittunt,

**Retained witness note:** The invasion account differs in naming and wording; Latin scitas remains literal.

### DEH V.9.3 — `deh-5-9-3`

Canonical source ID: `latin-deh5-num24`.

**DEH Latin passage:**

> [V.9.3] Denique princeps sacerdotum haec quattuor indumento suo exprimere consueuerat, quando maxima celebritas erat festorum dierum, quasi totum mundum indueret pro populo supplicaturus, in eius figuram qui uenturus erat, princeps sacerdotum Iesus, ut tolleret peccatum mundi. Femora princeps sacerdotum lineo interius operimento tegebat eo quod prae ceteris in sacerdote fides mentis quaeritur et corporis castimonia, quae succingere debeat carnis intemperantiam. Duo erant tabernacula sacra, unum interius alterum exterius. In hoc semper introibant sacerdotes, in illud interius quod secundum appellabatur semel introibat princeps tantummodo sacerdotum non sine sanguine, ut offerret pro se et pro populi delicto, hoc significante spiritu sancto uenturum Iesum qui uere solus intraret interiora diuinorum penetralia sacramentorum et, arcana substantiae caelestis quia nosset omnia, solus quoque patri sanguine suo totum mundum reconciliaret ut et caelestium et terrestrium misereretur. Denique posteaquam uenit, pacificauit omnia per sanguinem crucis suae, quae uel in terra uel in caelo sunt.

#### `deh-5-9-3-aj-1` — AJ 3.184–184

Classification: **BOUNDARIES_AND_SELECTED_TEXT_RETAINED**. Old and current child paths/sides are retained. Intended passage: the existing frozen AJ target, in its recorded order.

Same ordered XML elements and attributes as the certified historical witness; each old interval matches independent October 14 XML expectations; current start/end identities, complete selected text and recomputed offsets checked. Frozen reference retained without expanding the passage.

| Section | Old boundary → current boundary | CP old → current | U16 old → current |
| --- | --- | --- | --- |
| 184 | `1.7.6.7:after → 1.7.6.8:before` → same | `51148:51512` → `51142:51506` | `51148:51512` → `51142:51506` |

**AJ 3.184**

Old = current selected passage:

> Significat autem et pontificis linea tonica totam terram. Iacinctina uero ueste[i]s polum quae per malo granata corruscationes, per tinn[t]inabulum sonitum tonitrua indicare dinosce[i]tur. Super humerale[i]s etiam ad similitudinem naturae totius est quando eum deo placuit, et quattuor coloribus, fieret auro contexi propter splendorem reor qui mundo diffunditur.

### DEH V.50.1 — `deh-5-50-1`

Canonical source ID: `latin-deh5-num114`.

**DEH Latin passage:**

> [V.50.1] Per idem tempus Alani, gens fera et diu ignota nostris, quod interiorum locorum difficultate et claustro portae ferratae, quam Magnus Alexander praerupti montis imposuit iugo, cum ceteris feris et indomitis introrsum gentibus cohibebantur, incolebant Scythicum Tanain finitimaque eius et Meotis paludes uelut quodam clausi carcere memorati ingenio regis, ut suas terras exercerent, alienas non incursarent. Sed siue ob sterilitatem locorum, quod auari uotis agricolae sperata culturae non responderet fecunditas, siue praedandi cupidine regem Hyrcanorum, qui locis praeerat, sollicitarunt, pretione an dissensione inter se gentium incertum, ut reserata porta eruptionis sibi copiam daret. Quo inpetrato infudere se genti Medorum et inparatam breui uelocibus equis et aliis pariter ad dexteram nexis, in quos per uices cum foret libitum desilirent, totam propemodum regionem percursauere, ut primo perturbarent omnia maiorisque multitudinis speciem darent, aduersus quam nullus fugae locus uacaret, deinde circumuentis omnibus, quanta uellent strage edita, praedam abducerent. Erat enim regio populis frequens et pecoris abundans, quae nullo resistente facile patuit direptioni. Siquidem ipse Pacorus, Medorum rex, in abstrusa loca se contulit saluti potius quam regno consulens, ita ut uxor eius ac liberi uel concubinae captae ab Alanis centum talentis postea redimerentur. Nec Tiridates, Armeniae rex, immunis periculi fuit, sed alieno malo cautior pestem prouidit et uiriliter quidem uoluit occurrere, ut a finibus suis hostem auerteret. Dum proeliatur tamen laqueolo insertus in potestatem hostium uiuus concesserat, ni praeacuto gladio nodum informem uelociter intercidisset. Namque insolentia quadam propriae fortitudinis et in ceteros despectu superbo, simul ut familiarem sibi eminus decernendi consuetudinem refugiendique facultatem tali fraude praetexerent, laqueos iacere atque hostem innectere ars Alanis bellandique mos est.

#### `deh-5-50-1-aj-2` — AJ 18.97–97

Classification: **BOUNDARIES_AND_SELECTED_TEXT_RETAINED**. Old and current child paths/sides are retained. Intended passage: the existing frozen AJ target, in its recorded order.

Same ordered XML elements and attributes as the certified historical witness; each old interval matches independent October 14 XML expectations; current start/end identities, complete selected text and recomputed offsets checked. Frozen reference retained without expanding the passage.

| Section | Old boundary → current boundary | CP old → current | U16 old → current |
| --- | --- | --- | --- |
| 97 | `1.9.0.3:after → 1.9.0.5:before` → same | `30876:31152` → `30874:31150` | `30876:31152` → `30874:31150` |

**AJ 18.97**

Old = current selected passage:

> Haec itaque ad uitellium scribente tyberio ille magnis muneribus persuadet ibe rorum et labanorum regi ut tcum artabano sine ulla dilatione pugnarent. At illi a pugna quidem abstinent, uerum scitas concesso ei transitu aperientes caspias pilas in artabani regiones inmittunt,

**Retained witness note:** The invasion account differs in naming and wording; Latin scitas remains literal.

## Editorial questions

No new unresolved boundary question arose. The inherited absence at Latin AJ XX.238 and the historical open reference are preserved explicitly; neither is silently filled or reinterpreted. The original printed reference loci and the cause of the XX.238 absence remain outside this repair.
