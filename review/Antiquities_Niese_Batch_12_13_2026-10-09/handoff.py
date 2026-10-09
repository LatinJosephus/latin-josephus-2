"""Record the actual isolated branch state and independently scoped readiness."""
from prepare_review import *
import subprocess
BASE='ad3158b7a86dea6997510b3de17f2e510c23367c'
git=lambda *args:subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
head=git('rev-parse','HEAD');canonical=git('-C',r'C:\Users\Pollard_R\Git\LatinJosephus-v2-development','rev-parse','HEAD')
changed=git('diff','--name-only',BASE).splitlines()
allowed=['assets/js/renderTei.js','assets/xml/antiquities/Greek/book-12.xml','assets/xml/antiquities/Greek/book-13.xml','assets/xml/antiquities/Latin/book-12.xml','assets/xml/antiquities/Latin/book-13.xml','assets/xml/antiquities/niese/book-12.json','assets/xml/antiquities/niese/book-13.json']
assert all(p in allowed or p.startswith(str(PACK.relative_to(ROOT)).replace(chr(92),'/')+'/') or any(p.startswith(str(packet(b).relative_to(ROOT)).replace(chr(92),'/')+'/') for b in [12,13]) for p in changed)
packets={}
for b in [12,13]:
 d=packet(b);qa=json.loads((d/'QA.json').read_text(encoding='utf8'));manifest=json.loads((d/'FILE_MANIFEST.json').read_text(encoding='utf8'))
 for item in manifest['files']:
  p=(ROOT/item['path']) if item['path'].startswith('review/') else (d/item['path'])
  assert digest(p.read_bytes())==item['sha256'],p
 packets[str(b)]={'path':str(d),'QA':qa,'manifest_sha256':digest((d/'FILE_MANIFEST.json').read_bytes())}
 for lang in ['Greek','Latin','English']:
  path=ROOT/f'assets/xml/antiquities/{lang}/book-{b:02}.xml'
  packets[str(b)].setdefault('corpus_sha256',{})[lang]=digest(path.read_bytes())
cert=json.loads((packet(12)/'CERTIFICATE.json').read_text(encoding='utf8'))
for name,sha in cert['evidence_sha256'].items():
 p=packet(12)/name if (packet(12)/name).exists() else PACK/name
 assert digest(p.read_bytes())==sha
assert cert['pending_editorial_decisions']==[] and packets['13']['QA']['pending_editorial_cases']==[213,214,216]
renderer=(ROOT/'assets/js/renderTei.js').read_bytes();built=(RUNTIME/'site/assets/js/renderTei.js').read_bytes();assert renderer==built and b'13: "assets/xml/antiquities/niese/book-13.json"' not in renderer
data={'base_commit':BASE,'recorded_HEAD':head,'canonical_HEAD_at_handoff':canonical,'canonical_advance':canonical!=BASE,'branch':git('branch','--show-current'),'worktree':str(ROOT),'runtime':str(RUNTIME),'packets':packets,'published_baseline_selectable':3157,'certified_local_added_selectable':434,'certified_local_added_nonempty_Latin_intervals':433,'current_branch_selectable_total':3591,'XIII_provisional_rehearsal_selectable':433,'XIII_staged_physical_Latin_starts':430,'XIII_final_certification':False,'XIII_pending_representations':[213,214,216],'XIII_current_recommendation':'B; see updated per-book decision packet and English-context consequences','integration_readiness':{'XII':'READY through separate scoped corpus, support and certification commits','XIII':'NOT_READY; routine source stage and rehearsal passed, adjudication and final implementation/certification remain','batch':'NOT_READY as a combined integration'},'scope_verified':'Only XII/XIII corpus and review files plus documented minimal shared reader/audit support','publication_actions':{'merge':False,'push':False,'preview_changed':False,'deploy':False},'changed_files':[{'path':p,'sha256':digest((ROOT/p).read_bytes()),'bytes':(ROOT/p).stat().st_size} for p in changed if (ROOT/p).is_file()],'commits':[{'commit':line.split(' ',1)[0],'subject':line.split(' ',1)[1]} for line in git('log','--reverse','--format=%H %s',BASE+'..HEAD').splitlines()]}
save(PACK/'HANDOFF.json',data)
(PACK/'REPORT.md').write_text(f'''# XII–XIII isolated local handoff

XII is locally certified and ready for coordinated integration independently. All434 Greek starts and Latin candidates are reviewed;433 nonempty Latin intervals comprise68 retained starts and365 inserted milestones, plus one narrative end marker. Greek opening1 is explicitly marked. XII.248 has displaced correspondence in246 and no independent Latin interval; it is not a whole-section absence. The approved reciprocal246–249 notices and the other qualified correspondences are implemented. Exact source recovery, all selections and actual ranges, deep links, navigation, reload/history, pane switching, IDs and themes passed on the rebuilt branch. Certificate commit:429eb44; preceding full certification:f5483e3.

XIII remains provisional only at the genuine213–216 adjudication. All433 Greek starts and Latin candidates are individually reviewed;431 proposed physical locators are validated,430 representations are approved, and347 routine milestones plus83 retained approved starts are staged. Greek opening1 is implemented. The disputed214 cut and213/216 absence representations are excluded from repository identity data, and XIII remains disabled in the branch reader. Disposable rehearsal selection/range QA passed, including anonymous269 and exact unchanged English context. Rehearsal212,213,214,216 do not constitute certified extents. Current recommendation:B, with the dating clause within212,214 starting `Itaque iudaei feliciter`, reciprocal displaced-correspondence notices, and the existing correct English213 context. See the separate XIII decision packet for exact A/B alternatives, expanded context and recommendation history.

Protected checks compared all3,157 existing Antiquities identities, contents, traditional/Bamberg and Alignment against the frozen baseline, plus Bellum1–7 under Whiston/Lodge and the other affected works. The exact inherited Book-I apparatus hyperlink and unsupportedI.1 exceptions were reproduced separately; no additional errors were observed. The minimal anonymous-paragraph reader fix is separate commit88fb92d; all new XII certification was refreshed after it. Canonical and preview remain untouched.

Frozen base:{BASE}. Actual canonical HEAD at this handoff:{canonical}. Recorded branch HEAD before this handoff:{head}. Branch:antiquities-niese-12-13. Worktree:{ROOT}. Runtime:{RUNTIME}. Separate book packets:{packet(12)} and{packet(13)}. The published baseline stays3,157; only the certified XII addition contributes434 local selections and433 nonempty intervals, making3,591 selections in the actual branch. The provisional XIII rehearsal's433 selections are reported separately and are not certified coverage.

HANDOFF.json verifies packet manifests, bound XII evidence, exact changed-file hashes, scoped commits and actual reader availability. No merge, push, preview update or deployment was performed. The combined batch is not ready until the XIII decision and final certification are complete; XII may be integrated independently through the coordinated later process against then-current canonical code.
''',encoding='utf8')
print('Handoff scope/manifests/evidence verified; XII ready; XIII pending213,214,216; canonical',canonical)
