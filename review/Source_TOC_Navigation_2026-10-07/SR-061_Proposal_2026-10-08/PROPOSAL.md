# SR-061 — proposed Book XIV capitula segmentation

Date: 2026-10-08. **Proposal only; eight boundaries await human approval. No reconstructed TOC has been implemented or registered.**

The eight proposed openings are unique, ordered and defensible as an editorial organization of the transmitted contents passage. The numerals [V]–[XII] would be supplied editorial labels, not certified manuscript numerals or recovered manuscript division marks. Approval must cover each opening and the corresponding end of its preceding segment.

Richard M. Pollard's current clarification establishes that the unusual Herodian narrative is genuinely transmitted here. This proposal preserves it in place and in full. Its presence is not treated as an error, accidental insertion or reason to relocate material. The original SR-061 history remains unchanged; this dated proposal records the later clarification separately.

## Exact segmentation for approval

Each candidate begins at the first character of its incipit. It ends after the punctuation of its explicit, immediately before the following candidate opening (apart from the preserved separator space). [XII] ends after `mereretur.` at the end of the held paragraph, before the next paragraph's literal `XIII De aristobolo`.

| Proposed supplied label | Exact candidate opening | Final words / explicit | Historical export lines | Preserved projection interval |
|---|---|---|---|---|
| [V] | `De pompeio qui cum ab armenia uenisset in damascu` | `tenus se posse decernere de inlatis inuicem criminibus quo usque ad illorum prouinciam ueniret.` | 77–80 | 208–463 |
| [VI] | `Quemadmodum aristobolus cum intellexisset pompei consilium` | `fratre altercatus est primatibus custodum uniuscuiusque castelli propria manu scribere ut pompeio castella contradere.` | 81–86 | 463–837 |
| [VII] | `Quemadmodum aristobolus cum hic timore fecisset` | `pecuniarum susceptione, hierosolimite uero aristobolum cum in custodia depositum uidissent obstructis portis romanos excluserunt.` | 87–138 | 837–4166 |
| [VIII] | `Qualiter irritatus pompeius aristobolum ligauit` | `templum confugiit quod pompeius cum inferiore parte ciuitatis suscepissent tertio mense forti ter expugnauit.` | 139–143 | 4166–4439 |
| [IX] | `De modestia eius et religiositate` | `ordinauit aristo bolum autem cum cognationem uictum roma deduxit scaurum uero curatorem syriae reliquit.` | 144–148 | 4439–4725 |
| [X] | `De scauro qui cum militiam contra petram` | `litibus antipater flectit arabium dandos scauro talenta trecen ta ut amicitias cum eo componeret.` | 149–152 | 4725–4944 |
| [XI] | `Quemadmodum aristoboli filius alexander fugiens pompeium` | `antipatrum produxit, qui cum a gauino uictus in prelio in castello alexandrae confugisset obsidebatur.` | 153–156 | 4944–5180 |
| [XII] | `Quemadmodum cum flexisset alexandrum matre sua` | `patre roma eligati fuis sent martrique mitterentur quod fidelis romanis existens hanc gratiam mereretur.` | 157–160 | 5180–5460 |

The preceding literal **IIII** remains `IIII Qualiter scaurum ... et acceptis quadringentis talentis scaurus aristobolo subuenit.` Its preserved projection interval is 0–208; the eight proposed intervals then cover 208–5460 without a gap or overlap. Supplied labels are absent from this source projection and would be separately marked additions.

The export lines are **one-based nonempty lines of the pinned RTF extraction**, as recorded in the original review packet. They are not manuscript line numbers. No manuscript image or source PDF was reopened for this proposal.

## Physical and current-source positions

Source: `assets/xml/antiquities/Latin/book-14.xml`, `latin-book14-chapter0`, fourth paragraph, historical locator `/TEI[1]/text[1]/body[1]/div1[1]/div2[1]/p[4]`. The paragraph has no existing xml:id; none has been added. Offsets and XPath are reproducible audit locators, not proposed persistent scholarly identities.

| Proposed label | XML line:column (one-based Unicode) | Raw UTF-8 file byte interval (zero-based, half-open) | Encoded folio / column span |
|---|---|---|---|
| [V] | 38:282 | 2580–2877 | 164r 1/2 → 1/2 |
| [VI] | 38:579 | 2877–3251 | 164r 1/2 → 1/2 |
| [VII] | 38:953 | 3251–6674 | 164r 1/2 → 2/2 |
| [VIII] | 38:4374 | 6674–6947 | 164r 2/2 → 2/2 |
| [IX] | 38:4647 | 6947–7233 | 164r 2/2 → 2/2 |
| [X] | 38:4933 | 7233–7452 | 164r 2/2 → 2/2 |
| [XI] | 38:5152 | 7452–7688 | 164r 2/2 → 2/2 |
| [XII] | 38:5388 | 7688–8033 | 164r 2/2 → 2/2 |

All eight openings lie on encoded image `sbb00000114_00331.jpg`, folio 164r. [V] and [VI] occupy column 1/2. [VII] starts in column 1/2 and crosses the existing column 2/2 marker after `ex ornaris`; [VIII]–[XII] are in column 2/2. The literal IIII passage starts on image 00330, encoded folio 163v, column 1/2, and crosses the existing 164r/1/2 page transition.

The [XII] raw preservation slice retains the existing terminal image-00332 / 164v / column-1/2 markers before `</p>`. Those empty markers identify the next source-page transition; they do not put any XII text on 164v. Its last textual word is still `mereretur.` on the preceding encoded column. JSON records both the content-end offset (before the separator space) and the preservation-end offset. Separating whitespace, markup and all source-position markers are retained verbatim.

`SOURCE_PARAGRAPH.xml.fragment.txt` is the exact 5,733-byte source paragraph, including its `<p>` wrapper. Its SHA-256 remains the original SR-061 hash `0284126a6164f2e4fa20deafa45af2ac8b22a394dc8366600703c0836c882725`. `SOURCE_CAPITULA.xml.fragment.txt` preserves the complete current chapter-zero block as context. These are byte copies for review, not published companion XML or newly edited transcriptions. Their namespace context is the original TEI document.

## Comparison with audited Bamberg narrative divisions

The following are **thematic comparisons**, not certified TOC-to-navigation links. Niese numbers in this table belong to the already audited narrative starts only; no Niese coordinate is assigned to a capitula entry.

| Proposed contents entry | Related frozen narrative record and label | Narrative Niese association | Frozen narrative incipit |
|---|---|---|---|
| [V] | B78-table1-row094 · V | 38 | `Cumque iussisset pompeius certantes` |
| [VI] | B78-table1-row095 · VI | 47 | `Aristobolus enim a pompeio regressus nec aliquid` |
| [VII] | B78-table1-row096 · [VII] | 52 | `Discedens autem ad ierosolimam bellum parauit` |
| [VIII] | B78-table1-row097 · [VIII] | 57 | `Qua propter pompeius iratus, aristobolum` |
| [IX] | B78-table1-row098 · VIIII | 72 | `Quas pompeius paenitus contingere noluit propter` |
| [X] | B78-table1-row099 · X | 80 | `Scaurus tamen con petram arabiae cum exercitum produxisset` |
| [XI] | B78-table1-row100 · XI | 82 | `Interiecto uero tempore cum alexander aristoboli filius` |
| [XII] | B78-table1-row101 · XII | 89 | `Quaecumque per prouinciam rediit` |

The sequence gives useful support for the editorial numbering, but the boundaries and contents do not coincide throughout:

- **[V]** starts with Pompey's arrival at Damascus, already described in current narrative `latin-book14-num34`, before the audited narrative V start at Niese 38. The contents summary covers material across that narrative edge.
- **[VI] / [VII]** do not reproduce the exact narrative VI / [VII] break. Proposed contents [VII] begins with Aristobolus' compliance and distress; audited narrative [VII] starts later at `Discedens autem ad ierosolimam bellum parauit` (Niese 52). No numeral or new division is supplied inside the Herodian passage.
- **[VII]** includes all text from `Quemadmodum aristobolus cum hic timore fecisset` to `obstructis portis romanos excluserunt.` This is a 3,329-character source projection. The Herodian material begins at `Tunc autem filiis interminatus` (historical export line 93), extends through the family dispute recorded at lines 93–136, and remains in transmitted order before `pecuniarum susceptione, hierosolimite ...`. This is intentionally a long, heterogeneous editorial contents span; its thematic irregularity is disclosed, not repaired. Approving these eight cuts does not certify that the manuscript treats that entire span as one formal capitulum.
- **[IX]** is the human editor's proposed supplied label. Narrative **VIIII** remains its recorded reading. There is no literal contents numeral here to modernize or overwrite.
- **[XII]** covers Alexander's mother and the return of the other sons. The latter is narrated at the end of current narrative XIII (`latin-book14-num92`), after the audited narrative XII start at 89. The source contents can anticipate material narrated under another division; the summary must not be shortened to force agreement.

There are **19 literal contents numerals** in current XML: I, II, III, IIII, XIII, XIIII, XV, XVI, XVII, XVIII, XVIIII, XX, XXI, XXII, XXIII, XXIIII, XXV, XXVI, XXVII. Adding eight editorial entries would give 27 contents entries. Bamberg XIV also has 27 independently audited narrative starts, but their label population differs: narrative [III], [VII], [VIII] and [XXVIII?] are supplied labels; narrative VIIII is retained; no narrative XXIII is recorded, while contents XXIII is literal. Equal totals cannot establish one-to-one identity. No Bamberg narrative record, label or start changes.

## Other uncertainty retained

The historical T-PEN excerpt has an additional `1` after `prelio in` at line 155, inside proposed [XI]. Current XML does not have it. Its function was not established by the original packet, and this proposal neither imports it as text nor interprets it as an entry numeral. The eight candidate openings are independent of that unresolved transcription difference.

All current orthography, spacing, punctuation, additions, deletions and unusual syntax remain unchanged, including the marginal `s` in `aristobo <add ...>s</add> lus`, the scraped `se`, the interlinear `non`, `falo memini`, `damascu`, and `matre sua`. Other Book XIV source-review cases, including SR-052's `corrupter`/expansion question, are outside this proposal and are not declared resolved by it.

## Proposed companion integration after approval

Use the existing generic source-contents mechanism, with a new TEI companion at `assets/xml/antiquities/paratext/bamberg78/book-14-contents.xml`. It should copy the complete existing contents, retaining every source character and inline element, and represent the approved eight editorial cuts in that companion only. The running-text file and its paragraph topology remain untouched.

Literal source numerals should remain literal labels. New labels should be explicitly supplied, with responsibility and an editorial explanation. An illustrative form is:

```xml
<item xml:id="bamberg78-ant14-contents-V">
  <label><supplied reason="not-transmitted" resp="#capitula-reconstruction">[V]</supplied></label>
  <p>De pompeio qui cum ab armenia uenisset in damascu ...</p>
</item>
```

This is a proposed TEI pattern, not a complete encoded entry or an implemented file; the ellipsis is illustrative and must not replace source text in implementation. The header would define `#capitula-reconstruction` and record human approval. `reason="not-transmitted"` describes absence without asserting physical loss or a proven scribal cause. Brackets are stored within the supplied label so that the current contents styling, which suppresses generated supplied-text brackets for the Blatt material, cannot make these numerals appear unmarked. No existing Blatt supplement encoding or styling need change.

A concise reader note could say: **“Numerals [V]–[XII] are supplied editorially; the manuscript contents proceeds from IIII to XIII. The transmitted Herodian passage is retained in its original position.”** The note should disclose that the grouping is editorial. Source contents entries remain non-clickable. New companion-local entry IDs identify contents entries only; none reuses a Bamberg division identity or asserts a narrative concordance.

After approval and validation, add Latin/Bamberg Book XIV to `assets/xml/source-contents.xml`, pointing to the companion. The existing generic `view=contents` reader can then display it without a source-specific renderer branch, a change to `structure.xml`, or a change to Chapter/Subchapter/Niese/Bamberg/Alignment-unit navigation. Until approval, XIV remains unregistered. Before publication, verify schema validity, literal-versus-supplied label rendering, full source-projection and inline-markup equality, the complete 27-entry inventory, and ordinary-view invariance. These implementation/browser checks have not been claimed as completed here.

## Provenance and integrity

Canonical and worktree branches/HEADs match the accepted base `087c0bf651037d83c5156495836510d250bdcf09`; canonical status is clean. Existing unstaged TOC implementation and all earlier review material are preserved. The original source-review checkpoint is `a70bb5060fdd7f95c9e6fc4baa3e0cc2241bebaf`. Frozen Bamberg authority remains commit `41e817680549767d36e3f80dbc825682908ea5e6`, tag `antiquities-structure-reconciliation-v1.1`; all eight entries in its manifest verify.

| Input | SHA-256 | Exact path |
|---|---|---|
| worktree_latin_xiv | `931157718997a35a84951ecebabae6813526c66250fa4f791bd338748fbf62f6` | `C:\workspace\LatinJosephus-source-toc-navigation\assets\xml\antiquities\Latin\book-14.xml` |
| canonical_latin_xiv | `931157718997a35a84951ecebabae6813526c66250fa4f791bd338748fbf62f6` | `C:\Users\Pollard_R\Git\LatinJosephus-v2-development\assets\xml\antiquities\Latin\book-14.xml` |
| original_sr061_packet | `1ece8a3236891abd60bc258154ba09d204b523f9257d8acc73fc3d1f49db5299` | `C:\Users\Pollard_R\Mon disque\Latin Josephus Project\LatinJosephus-Recovery\latinjosephus-next\review\Antiquities_source_review_reconciliation_2026-09-28\SOURCE_REVIEW_PACKET.md` |
| original_sr061_queue | `865363a0e7a6364faef42f0504227896968b507a46621592bf5f03c0028a34c8` | `C:\Users\Pollard_R\Mon disque\Latin Josephus Project\LatinJosephus-Recovery\latinjosephus-next\review\Antiquities_source_review_reconciliation_2026-09-28\source_review_queue.json` |
| bamberg_map | `146c29df6086e2dec491557a5f721726468c36dee565f4ac3ab3ac9481ecd9df` | `C:\Users\Pollard_R\Mon disque\Latin Josephus Project\LatinJosephus-Recovery\latinjosephus-next\review\Antiquities_Loeb_Bamberg_Reconciliation_2026-10-06\Antiquities_Bamberg_Niese_Map.csv` |
| frozen_manifest | `cfc898b9f051a003de7045dbf352229097855e2c39696a33213c4454be50ff11` | `C:\Users\Pollard_R\Mon disque\Latin Josephus Project\LatinJosephus-Recovery\latinjosephus-next\review\Antiquities_Loeb_Bamberg_Reconciliation_2026-10-06\Antiquities_Structure_Reconciliation_v1.1_SHA256SUMS.txt` |
| production_structure_registry | `d64c666b8f790a28cef77de88c73c489097e590a691a2bfd0d7d442c1f21ff56` | `C:\workspace\LatinJosephus-source-toc-navigation\assets\xml\antiquities\structure.xml` |

The current held paragraph is byte-identical to the original SR-061 exact variant even though the whole Book XIV file now contains later certified navigation anchors elsewhere. No paragraph, text, existing ID, sameAs, source numeral or navigation identity was edited in this task. The proposal files are separate from the original history and from the completed Phase-A/Phase-B records. `QA.json` and `FILE_MANIFEST.json` record the protected-input recheck; the latter covers all newly created proposal files except itself.

## Human approval requested

Approve or revise the eight starts and ends in the first table, especially **[VII] retaining the entire Herodian passage** and **[XII] ending only after `mereretur.`**. If approved, the next task can encode this editorial reconstruction in a source-paratext companion and make Latin XIV available in contents view. No TOC reconstruction or publication registration is authorized by this proposal alone.

## Full candidate fragments for inspection

Each fragment below is copied from current XML without any supplied numeral. Empty terminal page markers remain in the [XII] preservation slice. The JSON records these same exact fragments and their checksums.

### [V] — proposed text, without the supplied label

```xml
De pompeio qui cum ab armenia uenisset in damascu apud eum aristobo <add hand="post" place="marginleft">s</add> lus et hyrcanus de regno altercati sunt et pompeius dilatione pro nun tiata dixit, nulla tenus se posse decernere de inlatis inuicem criminibus quo usque ad illorum prouinciam ueniret. 
```

The contents starts with Pompey arriving at Damascus; current narrative num34 already describes that arrival, before audited Bamberg V (Niese 38). The related topic is broader than the narrative division edge.

### [VI] — proposed text, without the supplied label

```xml
Quemadmodum aristobolus cum intellexisset pompei consilium ad sua discessit aduersus quem indignatus pompeius exercitum producens aristobolum in alexandria castello fugauit, qui cum descenderet ad pompeium promittentem regnum se etiam tradere saepius cum fratre altercatus est primatibus custodum uniuscuiusque castelli propria manu scribere ut pompeio castella contradere. 
```

Narrative VI opens with Aristobolus leaving Pompey (Niese 47); this contents summary also includes the ensuing pursuit and castle instructions. Thematic correspondence does not certify identical boundaries.

### [VII] — proposed text, without the supplied label

```xml
Quemadmodum aristobolus cum hic timore fecisset grauiter ferebat quod per spem sibi a pompeio uenisset. Qui cum ad ierosolimam discessisset statim pompeio cum exercitu secuto paenitentia ductus est, et processit ad hierichuntem, occurrere ei, quatinus ueniam pro peccatis petens ciuitate cum pecuniis tradereret, tunc pompeius gauimum destinauit cum electis militibus pro ciuitatis. Tunc autem filiis interminatus satis factionibus corum adpresens molliter in posterum atrocius exarsit. Nam ferora cum alexandrum uenis set et filiam archelai glafiram sicut prediximus habentem salomon inquit dicentem. Audiuit quod herodes in amore glafyrae suae nurus incidisset, et minime desiderii <del hand="?" rend="scraping">se</del> salai cum posset inuenire. Quod ille audieris adulescentia uel emulatione commotus quę honoris causa circa puellam ad herode fiebant. Propter amorem haec eadem facere suspicabatur. Dolorem ergo minus tolerans patri nunti auit cum lacrimis quae ferora dixisset, herodes autem multo magis feruens et mendacium inpudicae criminationis non ferens turbabatur et pius exclamans maliuolentiam familiarum qualis ipse erga eos conuocauit feroram quem huius modi adgressus pessime omnium inquit ad tam inmensam uel infandam in deuotionem peruenis ut ta lia de nobis existimes aut loquaris. Nonne uideo tuam uolun tatem quia non in meam iniuriam talia uerba producere, sed insidias et uenena inmittere filio pro mea proditione festinasti, quis enim alter nisi dei bonitate retentus quam hic puer in se habet, portare potuisset in patrem <add hand="orig" place="interlinear">non</add> uindicare tam crudele opinionem Prius enim gladium in dextra quam hoc uerbum in animo eius debebas inmittere compatrem. Quid autem conaris male loquendo de me nisi ut eorum fauorem fraudibus tibi concilies. Nam talia di xisti quae tuae tantum impietatis fuissent cogitanda abscede iam pessime circa fratrem atque benefactorem, et tecum quidem haec militia conscientiae conuiuat ego uero uindico sicut soleo meo nec uindicans merito in eis sed magis ueneficus ex ornaris <cb n="2/2"/> quibus indignis esse nascuntur. Talia quidem rex ferora sue cruro statim mestitia plenus. Salom inquit hęc persuasit et ab illa sermones audiui, quae mox ut audiuit nam praesens erat exclamauit quod nihil ab ipsa tale dictum fuisset, et quod festinarent omnes ad odium regis eam perducere cunctisque modis occidere propter fidem quam erga eum semper habere cognoscerent. In presenti uero plus sibi insidiari quod sola reflecteret fratrem, ne uxorem quam nunc haberet repudiaret regisque familiam in matrimonio sibi coniungeret. Qua propter me falsis inquit accusationibus est agressus. Cum haec dixis set crines suos dilacerans et pectora manibus tundens ueris similis ad negationem esse constabat, maliuolentiam uero morum dissi mulationem redarguebat, feroras autem in medio restitit nullam habens satisfactionem. Nam alexandro se dixisse confessus est, audisse uero a falo memini me comprobabit, unde diu confessione sermonum inter eos facta. Rex fratrem uel sororem uersatus, filium pro constantia laudabit, quod sibi sermones ferore nuntiasset. Hac lite facta saloniae ut accusationis commotae caput omnium odio tenebatur quam uxores regis ut maliuolam abhorrebant et quod natura maligna eam cognoscerent, pecuniarum susceptione, hierosolimite uero aristobolum cum in custodia depositum uidissent obstructis portis romanos excluserunt. 
```

The contents opens with compliance with the castle instructions and distress; audited narrative [VII] begins later at Discedens autem (Niese 52). Preserve the entire Herodian passage and the return to the siege account inside this proposed contents span.

### [VIII] — proposed text, without the supplied label

```xml
Qualiter irritatus pompeius aristobolum ligauit et ad ciuitatem obsidendam accessit, quem dum hyrcani socii ad superiora ciuitatis suscepissent, aristoboli pars a templum confugiit quod pompeius cum inferiore parte ciuitatis suscepissent tertio mense forti ter expugnauit. 
```

Related narrative [VIII] opens with Pompey imprisoning Aristobolus (Niese 57). The summary is thematically parallel; the frozen narrative label is supplied [VIII], not evidence of a contents numeral.

### [IX] — proposed text, without the supplied label

```xml
De modestia eius et religiositate qui nullatenus passus est tangere templi pecunias licet multa fugissent quae cum regisset et fecisset iudaeam tributariam hyrcanum genti principem ordinauit aristo bolum autem cum cognationem uictum roma deduxit scaurum uero curatorem syriae reliquit. 
```

Narrative label is VIIII, not IX; its start is Quas pompeius (Niese 72). [IX] is the requested editorial contents label only, with no alteration of the literal narrative numeral.

### [X] — proposed text, without the supplied label

```xml
De scauro qui cum militiam contra petram produxisse urbem tunc regnum arabum habentem obsedit. Sed inopia tentis eius mi litibus antipater flectit arabium dandos scauro talenta trecen ta ut amicitias cum eo componeret. 
```

Narrative X opens with Scaurus against Petra (Niese 80). This supports the topic sequence, not a source-authorized TOC-to-navigation link.

### [XI] — proposed text, without the supplied label

```xml
Quemadmodum aristoboli filius alexander fugiens pompeium ad iudaeam peruenit ubi multo exercitu congregato bellum contra hyrcanum et antipatrum produxit, qui cum a gauino uictus in prelio in castello alexandrae confugisset obsidebatur. 
```

Narrative XI opens with Alexander, son of Aristobolus (Niese 82). The contents preserves its own summary wording and boundaries. Export line 155 has an extra 1 after prelio in. It remains a separately recorded transcription question; this proposal preserves current XML without importing that character.

### [XII] — proposed text, without the supplied label

```xml
Quemadmodum cum flexisset alexandrum matre sua tradere secum castello gauinius alexandrum quidem dimisit, scripsit uero senatui ut fratris eius soluerentur qui cum aristobolo patre roma eligati fuis sent martrique mitterentur quod fidelis romanis existens hanc gratiam mereretur. <milestone n="sbb00000114_00332.jpg"/><pb n="164v"/><cb n="1/2"/>
```

Narrative XII (Niese 89) concerns the siege, surrender and Alexanders mother; the release of the other sons by the senate is narrated at the end of current narrative XIII (num92). Thus the proposed contents XII summary anticipates material in narrative XIII; do not truncate or relocate it.
