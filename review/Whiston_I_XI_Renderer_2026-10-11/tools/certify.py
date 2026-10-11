from pathlib import Path
import json,hashlib,subprocess,collections,csv,datetime
ROOT=Path(__file__).resolve().parents[3];PACK=ROOT/'review/Whiston_I_XI_Renderer_2026-10-11'
PIN='663b8ce318f0aa247d304d8eeda5b8e76e7489c6'
sha=lambda b:hashlib.sha256(b).hexdigest()
load=lambda name:json.loads((PACK/name).read_bytes())
sections=load('BROWSER_QA.json');reg=load('REGRESSION_QA.json');aux=load('AUXILIARY_QA.json');preserve=load('SOURCE_PRESERVATION_QA.json');inventory=load('SOURCE_INVENTORY.json')
assert sections['status']=='SECTIONS-PASS' and len(sections['sections'])==3821
assert reg['status']==aux['status']==preserve['status']=='PASS'
assert len(reg['traditional'])==967 and len(reg['alignment'])==823 and len(reg['book'])==12
assert all(r['passed'] and r['expectedSHA256']==r['renderedSHA256'] and r['GreekLatinPresentationUnchanged'] for r in sections['sections'])
assert sections['rendererSHA256']==sha((ROOT/'assets/js/renderTei.js').read_bytes())
assert sections['registrySHA256']==sha((ROOT/'assets/xml/antiquities/niese/book-09.json').read_bytes())
assert sections['structureSHA256']==sha((ROOT/'assets/xml/antiquities/structure.xml').read_bytes())
assert not sections['errors'] and not reg['errors'] and not aux['errors']
assert len(aux['DEHConcordance']['componentChecks'])==2115 and aux['DEHConcordance']['passed']
assert len(aux['markup'])==16 and sum(x['elements'] for x in aux['markup'])==18
perbook=collections.Counter(x['book'] for x in sections['sections'])
restored=[x for x in sections['sections'] if x['book']=='9' and 51<=x['number']<=109]
assert len(restored)==59 and all(x['passed'] for x in restored)
cross=collections.Counter(x['work'] for x in reg['crossWork'])
assert cross['Bellum']==70 and cross['contra-apionem']==10 and cross['deh']==25
qa_receipts=PACK/'source-receipts'
for book in inventory:
    raw=(qa_receipts/f"Book{book['book']}-QA.json").read_bytes();book['QA_sha256']=sha(raw)
    parsed=json.loads(raw);book['QA_data_checks']=parsed.get('data_checks');book['QA_unresolved']=parsed.get('unresolved_boundary_candidates',parsed.get('unresolved',0))
(PACK/'SOURCE_INVENTORY.json').write_bytes((json.dumps(inventory,ensure_ascii=False,indent=2)+'\n').encode())
ixroot='review/BookIX_Restored_Segmentation_2026-10-11/'
for relative in ['PROVENANCE.md','restoration-authority/PROVENANCE_AND_LICENSING.md','restoration-authority/NOTICE.md']:
    blob=subprocess.check_output(['git','show','2ce18b40ea8652e5e0d5046f10b1c39935fcdc54:'+ixroot+relative],cwd=ROOT)
    target=qa_receipts/'BookIX'/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(blob)
certificate={'status':'RENDERER-GO for the isolated I-XI prototype','canonical_integration_authorized':False,'public_deployment_authorized':False,
    'pinned_canonical_commit':PIN,'source_assembly_commit':'c7525d559d7ac672d6f6e9f1e5e00a77fca5755b','renderer_implementation_commit':'33d1b7210671b33b4ebe006bd194bfcca5abe8e6',
    'certification_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'source_intervals':3821,'rendered_intervals':3821,'perbook_counts':dict(perbook),'restored_IX_sections':59,
    'traditional_views':len(reg['traditional']),'alignment_views':len(reg['alignment']),'whole_files':12,'navigation_checks':len(reg['navigation']),
    'cross_work_display_checks':dict(cross),'unsegmented_fallback_checks':18,'DEH_component_checks':2115,'DEH_section_occurrences':8193,
    'owned_notes_checked':sum(x['notes'] for x in sections['sections']),'inline_markup_elements':18,
    'script_errors':0,'failed_browser_requests':len(sections['requests'])+len(reg['requests']),
    'renderer_sha256':sections['rendererSHA256'],'registry_sha256':sections['registrySHA256'],'structure_sha256':sections['structureSHA256'],
    'source_preservation':'All twelve assembled XML files byte-identical to pinned delivery Git blobs; archive trees identical, with recorded EOL differences for VI-XI.',
    'protected_canonical_and_XII_XIII':'UNCHANGED',
    'data_status_qualification':'The mission supplies DATA-GO for I-XI. The Book I local delivery packet retains NOT CERTIFIED metadata despite all 346 data checks passing. That historical metadata is preserved, not overwritten.',
    'historical_test_launchers':'Three old corpus-wide launcher guards are stale; current displayed-content, publication-input and full concordance gates passed. See HISTORICAL_GUARD_AUDIT.json.',
    'publication_build_qualification':'Preserve reviewed CRLF DEH/Bellum publication bytes; their frozen authority hashes do not match a fresh LF Git checkout. Generated preview assets retain the original reviewed bytes. No repository witness source is edited.'}
(PACK/'CERTIFICATE.json').write_bytes((json.dumps(certificate,indent=2)+'\n').encode())
fields=['book','number','nextPhysical','passed','expectedSHA256','renderedSHA256','opening','closing','allNarrativeVisible','notes','inline','GreekLatinPresentationUnchanged','latinSHA256','greekSHA256','URL']
with (PACK/'PER_SECTION_QA.csv').open('w',encoding='utf-8',newline='') as file:
    w=csv.DictWriter(file,fieldnames=fields);w.writeheader();w.writerows(sections['sections'])
table='\n'.join(f"| {x['book']} | {sum(o['sections'] for o in x['outputs'])} | `{x['delivery_commit']}` | {'PASS; archived NOT CERTIFIED label' if x['book']=='I' else 'DATA-GO'} |" for x in inventory)
sourcehashes='\n'.join(f"| {Path(o['path']).name} | `{o['sha256']}` |" for x in inventory for o in x['outputs'])
report=f'''# Whiston Antiquities I to XI renderer certification

The isolated prototype displays all **3,821 certified English Niese intervals correctly**. Its essential displayed-content and regression gates pass: **RENDERER-GO for this prototype**. Canonical development remains clean at `{PIN}`. Books XII and XIII remain untouched. No merge, push or public deployment has occurred.

DATA-GO concerns the supplied segmentation and wording. RENDERER-GO here concerns faithful display of those supplied intervals. It does not certify new translation correspondences, a generic TEI schema, or public publication rights. Book I’s archived delivery still says NOT CERTIFIED; its 346 data checks pass and the mission supplies DATA-GO. This metadata discrepancy is preserved for reconciliation without reopening boundaries.

## Original limitation and implemented behavior

The reader loads each language independently through `fetchTei` and CETEI. Antiquities then always routed English Niese requests to `antiquitiesNieseContextView`, using Latin starts, stable alignment IDs, `sameAs`, and contextual paragraph targets. Adding English milestones could not change that route. The Antiquities exact extractor indexed Latin milestones and Greek labels or registered fragments; it did not use the new English milestones. Bellum already had a separate English milestone extractor.

Whiston’s Antiquities source configuration now explicitly enables exact extraction for the Proem and Books I–XI. The prototype reuses Bellum’s physical milestone interval extraction, with Antiquities-only handling for inline ancestor retention, inherited contextual citation labels and an exact-English notice. Each interval starts after its own marker and ends before the **next physical English marker**, or at the book’s end. Book XI therefore correctly follows physical order 1–311, 326–342, 312–325, 343–347. Numeric navigation remains governed by the canonical identity registry, independently of witness order.

Latin and Greek retain their original exact/fragment paths and qualifications. Traditional Chapters, Subchapters, Book views and Alignment units remain separate selections. English XII–XX retains the original contextual-English notice and paragraph behavior; no segmentation from the ongoing XII–XIII work is assembled.

## Book IX independent witness availability

The source is the restored-and-segmented delivery `{inventory[8]['delivery_commit']}`. All 59 English intervals IX.51–109 display their certified restored text. Only the English availability flags and English paragraph exclusion are changed in the Niese registry. Every Greek and Latin field remains identical.

Ten inherited English Chapter/Subchapter locators now resolve to the certified English milestones at their already registered Niese starts. Alignment unit 51 binds the complete English IX.51–109 interval, ending at the English IX.110 marker. Greek and Latin omission placeholders and direct-selection notices remain unchanged; the prototype supplies no missing text in either language.

All seven restored Whiston footnotes display with their original text, identifiers and interval ownership. The English notice distinguishes the elected Alden & Beardsley 1856 printing, printed pp. 251–255, from the project’s Greek and Latin omissions. The restoration’s source and licensing qualifications are preserved in [the source receipts](source-receipts/BookIX/PROVENANCE.md).

## Implementation files and commits

The renderer changes are limited to:

- `assets/js/renderTei.js`: explicitly enabled English extraction, physical interval slicing, exact/context distinction and a Niese milestone structural locator.
- `assets/css/tei.css`: visibility of the seven restored Whiston footnotes.
- `assets/xml/antiquities/niese/book-09.json`: 59 independent English availability corrections and its English exclusion list.
- `assets/xml/antiquities/structure.xml`: ten English locators and one English alignment binding.

The twelve English XML files under `assets/xml/antiquities/English/` are assembled directly from delivery commits. Their wording and structure are not edited.

Source assembly commit: `c7525d559d7ac672d6f6e9f1e5e00a77fca5755b`.

Renderer and registry implementation commit: `33d1b7210671b33b4ebe006bd194bfcca5abe8e6`.

The final QA/report commit and reviewable binary Git patch are recorded in the recovery delivery receipt. All implementation commits are confined to `prototype/whiston-i-xi-exact-20261011` in `C:/workspace/LatinJosephus-Whiston-I-XI-Renderer-Prototype-20261011`.

## Sources and preservation

| Book | English sections | Pinned delivery commit | Archived data status |
| --- | ---: | --- | --- |
{table}

Book I’s total comprises 26 Proem sections and 320 narrative sections I.27–346. [SOURCE_INVENTORY.json](SOURCE_INVENTORY.json) records every exact branch, Git blob, delivery QA hash, archive path, archive SHA-256, CRC result and verified manifest entry. All eleven recovery packages have verified sidecar checksums and contents.

| Assembled file | Exact delivery Git blob SHA-256 |
| --- | --- |
{sourcehashes}

All twelve assembled files are byte-identical to their pinned delivery Git blobs, both in the worktree and source assembly commit. Recovery outputs VI–XI use CRLF where Git stores LF; both hashes are recorded, and their complete parsed XML trees are identical. [SOURCE_PRESERVATION_QA.json](SOURCE_PRESERVATION_QA.json) verifies the restricted production diff, unchanged other witness/source blobs, unchanged Greek/Latin registry fields, and the unchanged canonical and XII–XIII worktrees.

## Actual displayed content QA

An independent Python XML-event traversal produces the expected intervals without using production JavaScript or DOM Range. Chrome drives the real Niese selector and observes completion of the real renderer. Every selection is compared for complete prose and punctuation, opening and closing boundaries, visible narrative, citation identity, footnote ownership, and unchanged canonical Greek/Latin DOM. Whitespace is normalized according to browser display; raw boundary text is retained for containing-range concatenation. Inherited contextual citation labels and UI notices are excluded from prose comparison and checked separately.

| Gate | Result |
| --- | --- |
| Every English Niese selection | **3,821 / 3,821 PASS** |
| Greek and Latin presentation for those selections | **3,821 / 3,821 unchanged** |
| Restored IX.51–109 | **59 / 59 PASS** |
| Complete English files | **12 / 12 PASS** |
| Traditional Chapter and Subchapter views | **967 / 967 PASS** |
| Alignment views | **823 / 823 PASS** |
| Direct URL and Previous/Next checks, including Proem transition | **{len(reg['navigation'])} PASS** |
| Contextual fallback checks for XII–XX | **18 PASS** |
| Bellum displayed-content regressions, Whiston and Lodge, all seven books | **70 PASS** |
| Contra Apionem displayed-content regressions, both books | **10 PASS** |
| DEH displayed-content regressions, all five books | **25 PASS** |
| All certified anchors, line breaks and emphasis elements, including notes | **18 elements in 16 selections PASS** |
| Browser script errors and failed requests | **0** |

The boundary fixtures include Proem 1 and 26, I.27, VII.1, IX.49–52 and IX.108–111, and XI.311/312/325/326/342/343/347. All literal quotation punctuation is covered by the complete interval comparisons. [PER_SECTION_QA.csv](PER_SECTION_QA.csv) and [BROWSER_QA.json](BROWSER_QA.json) retain every section’s expected and displayed hash, opening/closing text and witness comparison. [REGRESSION_QA.json](REGRESSION_QA.json) retains every structural and cross-work result. Screenshots under `evidence/` supplement the content checks.

The existing DEH concordance extraction harness also passes **2,115 component checks**, **8,193 section occurrences**, **1,110 DEH source checks**, 21 final-boundary checks and eight eligibility guards. Lodge source switching passes all seven books at four levels, with back/forward history, note visibility and the VI.3 omission notice intact. These results are in [AUXILIARY_QA.json](AUXILIARY_QA.json).

## Remaining technical and source record issues

Three historical launchers stop at obsolete corpus-wide guards before their browser tests. One still requires 107 tracked XML files, whereas the pinned canonical commit already contains 286; the others assume a historical inventory or hashes that include subsequently changed Antiquities. Their code remains unchanged. The replacement gates compare current displayed content to the pinned canonical reader, protect unchanged source inputs, and execute the full DEH extraction harness and Lodge controls. [HISTORICAL_GUARD_AUDIT.json](HISTORICAL_GUARD_AUDIT.json) preserves the original launcher failures. Update these launchers’ scope before relying on them for future integration CI; do not weaken the production concordance guard.

DEH/Bellum’s reviewed authority hashes bind CRLF publication bytes. A fresh LF Git checkout fails that byte guard despite identical XML text and structure. The generated local preview preserves the existing reviewed byte representation for 44 unchanged cross-work XML files; no repository witness source or frozen hash is altered. [PUBLICATION_BYTE_REPRESENTATION.json](PUBLICATION_BYTE_REPRESENTATION.json) records the exact input/output hashes. Canonical integration needs a reproducible build policy for these existing hash-bound inputs.

Reconcile Book I’s historical NOT CERTIFIED packet label with the mission’s DATA-GO record. The pre-existing Greek I.272 control qualification and other scholarly qualifications remain preserved; no new scholarly boundary decision is requested. Book IX’s mixed source/licensing notices also remain applicable to any later publication.

## Controlled canonical integration

The isolated implementation is technically ready for review. Review the two implementation commits and source inventory, reconcile the Book I delivery-status record, and preserve the reviewed publication byte representation. Then, under separate authorization, integrate into a new worktree pinned to the actual canonical HEAD and rerun these gates against that state. Enable only the books whose certified sources are assembled; coordinate any later XII–XIII expansion with their independent deliveries. Review source notices and publication qualifications before any separately authorized public deployment.

## Recovery and local review

The recovery archive is `C:/workspace/Whiston-I-XI-Renderer-Delivery-20261011/Whiston-I-XI-Renderer-Prototype-Certified.zip`, with a separate SHA-256 sidecar and verification receipt. It contains the exact changed files, certification evidence, per-entry checksums, an implementation bundle with the pinned canonical prerequisite, a binary Git patch, and a runnable local reader preview. The recovery verifier checks archive CRC, every entry checksum, source identities and a local Git recovery checkout. It does not merge, push or deploy.

The generated preview is at `C:/workspace/Whiston-I-XI-Renderer-runtime-20261011/site`. `tools/preview.cjs` serves it on loopback for local review. `RECOVERY.md` supplies rebuilding and recovery instructions.
'''
(PACK/'REPORT.md').write_bytes(report.encode())
print('RENDERER-GO certificate and complete per-section report generated.')
