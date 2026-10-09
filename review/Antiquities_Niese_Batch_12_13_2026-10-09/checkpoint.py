"""Honest per-book progress records; never replace a completed certificate."""
from prepare_review import *
for b in ([int(sys.argv[1])] if len(sys.argv)>1 else [12,13]):
 d=packet(b);baseline=json.loads((d/'BASELINE.json').read_text(encoding='utf8'));rows=json.loads((d/'BOUNDARIES.json').read_text(encoding='utf8'));obs=json.loads((d/'PRINT_OBSERVATIONS.json').read_text(encoding='utf8'))
 reviewed=[r for r in rows if r['Latin']['review_status']=='INDIVIDUALLY_REVIEWED'];locators=[r for r in reviewed if r['Latin']['locator']]
 impl=json.loads((d/'IMPLEMENTATION_PRESERVATION.json').read_text(encoding='utf8')) if (d/'IMPLEMENTATION_PRESERVATION.json').exists() else {}
 applied=impl.get('status')=='APPLIED_AWAITING_READER_CERTIFICATION'
 status='PROVISIONAL_IMPLEMENTED_AWAITING_CERTIFICATION' if applied else ('PROVISIONAL_REVIEW_COMPLETE' if len(reviewed)==len(rows) else 'PROVISIONAL_REVIEW_IN_PROGRESS')
 result={'book':b,'status':status,'expected_sections':len(rows),'Greek_print_starts_visually_examined':len(obs),'Latin_individually_reviewed':len(reviewed),'validated_Latin_locators':len(locators),'approved_representations':sum(r['implementation_approved'] for r in rows),'review_remaining':len(rows)-len(reviewed),'Latin_section_milestones_applied':impl.get('Latin_section_milestones',0) if applied else 0,'Latin_end_milestones_applied':impl.get('Latin_end_milestones',0) if applied else 0,'Greek_marker_additions_applied':int(applied),'no_independent_Latin_intervals':[r['niese'] for r in reviewed if not r['Latin']['locator'] and r['implementation_approved']],'pending_editorial_cases':[r['niese'] for r in rows if r['editorial_status']=='PENDING_USER_DECISION'],'reader_certification':'NOT_YET_PERFORMED','completion_certificate':False}
 save(d/'QA.json',result)
 (d/'REPORT.md').write_text(f'''# Antiquities {b}: provisional checkpoint

Status: {status}. This book is not yet certified for integration. Printed/Greek span: 1–{len(rows)}. {len(obs)} Greek starts have individual page-image observations; {len(reviewed)} Latin candidates have individual source assessments, with {len(locators)} independently validated physical locators. Remaining Latin review: {len(rows)-len(reviewed)}. Approved sections without an independent Latin interval: {result['no_independent_Latin_intervals']}. See per-book editorial decisions for displaced or partial correspondence; these are not blanket absence claims.

Pinned base: {baseline['base_commit']}. Branch: {baseline['branch']}. Actual worktree: {ROOT}. Frozen original bytes remain in inputs; implementation changes, if applied, are limited to the exact marker operations in APPROVED_MARKER_PLAN.json, with exact inverse recovery in IMPLEMENTATION_PRESERVATION.json. English stays unchanged. No reader certification is claimed by this checkpoint.

SOURCE_AUTHORITY.md and BASELINE.json record source paths and Git/checkout provenance. BOUNDARIES.md is the human view; BOUNDARIES.json separates print observations, Latin correspondence, physical placement and editorial state. Canonical, preview and other assignments remain untouched.
''',encoding='utf8',newline='\n')
 files=[{'path':str(p.relative_to(d)).replace('\\','/'),'sha256':digest(p.read_bytes()),'bytes':p.stat().st_size} for p in sorted(d.rglob('*')) if p.is_file() and p.name!='FILE_MANIFEST.json']
 save(d/'FILE_MANIFEST.json',{'status':status,'files':files})
 print(b,status)
