"""Update honest checkpoint reports and manifests without promoting incomplete work."""
from prepare_review import *
import subprocess
for b in [12,13]:
 d=packet(b);baseline=json.loads((d/'BASELINE.json').read_text(encoding='utf8'));rows=json.loads((d/'CANDIDATE_REGISTER.json').read_text(encoding='utf8'));obs=json.loads((d/'PRINT_OBSERVATIONS.json').read_text(encoding='utf8'));reviewed=[r for r in rows if r['Latin']['review_status']=='INDIVIDUALLY_REVIEWED']
 unchanged={lang:digest((ROOT/f'assets/xml/antiquities/{lang}/book-{b:02}.xml').read_bytes())==x['sha256'] for lang,x in baseline['inputs'].items()}
 result={'book':b,'status':'PROVISIONAL_REVIEW_IN_PROGRESS','expected_sections':len(rows),'Greek_print_starts_visually_examined':len(obs),'Latin_individually_reviewed':len(reviewed),'validated_Latin_locators':len(reviewed),'routine_boundary_choices':sum(r['implementation_approved'] for r in rows),'review_remaining':len(rows)-len(reviewed),'Latin_milestones_applied':0,'Greek_marker_edits_applied':0,'unavailable_sections_established':[],'pending_editorial_cases':[r['niese'] for r in rows if r['editorial_status']=='PENDING_USER_DECISION'],'input_bytes_unchanged':unchanged,'reader_certification':'NOT_YET_PERFORMED','completion_certificate':False}
 save(d/'QA.json',result)
 (d/'REPORT.md').write_text(f'''# Antiquities {b}: provisional review checkpoint

This book is not certified and is not ready for integration. Expected printed/Greek span: 1–{len(rows)}. {len(obs)} Greek starts have page-image observations; {len(reviewed)} Latin candidates have individual source assessments and independently validated node/raw-byte locators. {len(rows)-len(reviewed)} Latin candidates remain to review. No corpus marker has been applied, no absence is established, and no new-book reader certificate is claimed.

Pinned base: {baseline['base_commit']}. Branch: {baseline['branch']}. Actual worktree: {ROOT}. Source preservation at this checkpoint: all three book XML inputs match their frozen worktree hashes. See SOURCE_AUTHORITY.md and BASELINE.json for absolute source paths, Git/checkout hashes and printed coverage. BOUNDARIES.md is the human view; CANDIDATE_REGISTER.json separates print, Latin review, placement, limits and editorial state. Unreviewed candidates are unapproved.

Per-book decisions remain separate. Other books, canonical and preview are untouched. Full individual review, implementation, source reversal and local reader QA remain required. Runtime baseline build succeeded; it is preparatory evidence, not implementation certification.
''',encoding='utf8',newline='\n')
 files=[{'path':str(p.relative_to(d)).replace('\\','/'),'sha256':digest(p.read_bytes()),'bytes':p.stat().st_size} for p in sorted(d.rglob('*')) if p.is_file() and p.name!='FILE_MANIFEST.json']
 save(d/'FILE_MANIFEST.json',{'status':result['status'],'files':files})
print('Checkpoint reports remain provisional; corpus inputs unchanged.')
