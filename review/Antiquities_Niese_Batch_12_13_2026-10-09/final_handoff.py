"""Reconcile the two final certificates. handoff.py retains the historical pending audit."""
from prepare_review import *
import subprocess
BASE = 'ad3158b7a86dea6997510b3de17f2e510c23367c'
git = lambda *args: subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()
read = lambda p: json.loads(p.read_text(encoding='utf8'))
head = git('rev-parse', 'HEAD')
canonical = git('-C', 'C:/Users/Pollard_R/Git/LatinJosephus-v2-development', 'rev-parse', 'HEAD')
context = read(PACK / 'INTEGRATION_CONTEXT.json')
assert context['result'] == 'PASS' and context['canonical_HEAD_observed_read_only'] == canonical
changed = sorted(set(git('diff', '--name-only', BASE).splitlines() + git('ls-files', '--others', '--exclude-standard').splitlines()))
allowed = ['assets/js/renderTei.js'] + [f'assets/xml/antiquities/{lang}/book-{b:02}.{ext}' for b in [12,13] for lang,ext in [('Greek','xml'),('Latin','xml'),('niese','json')]]
roots = [str(p.relative_to(ROOT)).replace(chr(92), '/') + '/' for p in [PACK,packet(12),packet(13)]]
assert all(p in allowed or any(p.startswith(prefix) for prefix in roots) for p in changed)
packets = {}
for b in [12,13]:
    d = packet(b); cert = read(d/'CERTIFICATE.json'); manifest = read(d/'FILE_MANIFEST.json')
    assert cert['status'] == 'LOCAL_CERTIFIED_READY_FOR_COORDINATED_INTEGRATION' and not cert['pending_editorial_decisions']
    for item in manifest['files']:
        p = ROOT/item['path'] if item['path'].startswith('review/') else d/item['path']
        assert digest(p.read_bytes()) == item['sha256'], p
    for name,sha in cert['evidence_sha256'].items():
        p = d/name if (d/name).exists() else PACK/name
        assert digest(p.read_bytes()) == sha, p
    registry = read(ROOT/f'assets/xml/antiquities/niese/book-{b:02}.json')
    assert len(registry['sections']) == cert['local_added_selectable']
    assert sum(s['Latin']['available'] for s in registry['sections']) == cert['local_added_nonempty_Latin_intervals']
    packets[str(b)] = {'path':str(d),'certificate':cert,
        'manifest_sha256':digest((d/'FILE_MANIFEST.json').read_bytes()),
        'qualified_reader_notices':sum(bool(s['Latin'].get('note')) for s in registry['sections']),
        'corpus_sha256':{lang:digest((ROOT/f'assets/xml/antiquities/{lang}/book-{b:02}.xml').read_bytes()) for lang in ['Greek','Latin','English']}}
renderer = (ROOT/'assets/js/renderTei.js').read_bytes()
assert renderer == (RUNTIME/'site/assets/js/renderTei.js').read_bytes()
for b in [12,13]:
    assert f'{b}: "assets/xml/antiquities/niese/book-{b:02}.json"'.encode() in renderer
    assert (ROOT/f'assets/xml/antiquities/niese/book-{b:02}.json').read_bytes() == (RUNTIME/f'site/assets/xml/antiquities/niese/book-{b:02}.json').read_bytes()
counts = {key:sum(p['certificate'][key] for p in packets.values()) for key in ['local_added_selectable','local_added_nonempty_Latin_intervals','Latin_section_milestones','Latin_end_markers','retained_Latin_starts','Greek_marker_operations']}
assert counts == {'local_added_selectable':867,'local_added_nonempty_Latin_intervals':864,'Latin_section_milestones':713,'Latin_end_markers':1,'retained_Latin_starts':151,'Greek_marker_operations':2}
assert packets['12']['certificate']['no_independent_Latin_intervals'] == [248]
assert packets['12']['certificate']['whole_section_absence_claims'] == []
assert packets['13']['certificate']['no_independent_Latin_intervals'] == [213,216]
decision = read(packet(13)/'EDITORIAL_DECISIONS.json')
assert decision['adopted_alternative'] == 'B' and not decision['pending_editorial_decisions']
self_paths = [str((PACK/n).relative_to(ROOT)).replace(chr(92),'/') for n in ['HANDOFF.json','REPORT.md']]
data = {'base_commit':BASE,'recorded_HEAD_before_handoff_commit':head,'canonical_HEAD_at_handoff':canonical,
    'canonical_advance':canonical != BASE,'branch':git('branch','--show-current'),'worktree':str(ROOT),'runtime':str(RUNTIME),
    'packets':packets,'published_baseline_selectable':3157,'batch_counts':counts,
    'current_isolated_branch_selectable_total':3157+counts['local_added_selectable'],
    'count_scope':'4024 is the frozen-baseline isolated local build total, not current canonical or publication; canonical now includes IX independently',
    'XIII_213_216_statuses':decision['statuses'],'pending_editorial_decisions':[],
    'integration_readiness':{'XII':'READY','XIII':'READY','batch':'READY_FOR_COORDINATED_INTEGRATION'},
    'scope_verified':'Only assigned XII/XIII corpus and review files plus separately committed minimal shared reader/audit support',
    'integration_context_sha256':digest((PACK/'INTEGRATION_CONTEXT.json').read_bytes()),
    'publication_actions':{'merge':False,'push':False,'preview_changed_by_this_assignment':False,'deploy':False},
    'changed_files':[{'path':p,'sha256':digest((ROOT/p).read_bytes()),'bytes':(ROOT/p).stat().st_size} for p in changed if (ROOT/p).is_file() and p not in self_paths],
    'manifest_self_exclusion':'HANDOFF.json and batch REPORT.md excluded from their own hash list; final Git commit identifies exact handoff bytes',
    'commits_before_handoff':[{'commit':line.split(' ',1)[0],'subject':line.split(' ',1)[1]} for line in git('log','--reverse','--format=%H %s',BASE+'..HEAD').splitlines()]}
save(PACK/'HANDOFF.json',data)
(PACK/'REPORT.md').write_text(f'''# XII–XIII final local handoff

Both books are independently locally certified and ready for coordinated integration. All editorial decisions are closed. Each book retains its own source authority, registers, decision history, marker plan, exact-byte recovery evidence, browser results, manifest and certificate.

| Book | Selectable identities / reviewed candidates | Nonempty Latin intervals | Retained starts | Added section milestones | End markers | Greek opening additions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| XII | 434 | 433 | 68 | 365 | 1 | 1 |
| XIII | 433 | 431 | 83 | 348 | 0 | 1 |
| Batch | 867 | 864 | 151 | 713 | 1 | 2 |

XII's accepted 246–249 representation and qualifications are preserved. XII.248 has no independent Latin interval: its dating material survives earlier within XII.246. XII.249 includes partial, reordered correspondence and the resumed ending of XII.247, with reciprocal notices. It is not classified as whole-section absence.

XIII adopts approved B, immediately before `Itaque iudaei feliciter` at frozen raw UTF-8 byte 58505 in paragraph `latin-book13-num213`. XIII.212 retains the documentary dating formula corresponding to Greek 214; XIII.214 begins the prosperity-and-victories statement. Reciprocal notices explicitly describe partial correspondence distributed between two physical intervals. The inherited `[VI.vii.213]` label and paragraph remain visible and intact, with its executable 213 claim suppressed. Both alternatives and the reason for the changed recommendation remain in decision history.

| XIII section | Final Latin status |
| --- | --- |
| 213 | No independent interval; no identifiable separate liberation-account counterpart in the full reviewed transcription. The dating formula for 214 does not supply it. |
| 214 | Partial correspondence distributed with 212; approved opening `Itaque iudaei feliciter`. |
| 215 | Present; independently reviewed interval retained. |
| 216 | No independent interval; no identifiable assembly-and-warning counterpart in the full reviewed transcription. Neighbouring demolition is not reassigned. |

No cause, physical loss or claim about the entire Latin tradition is inferred. Greek and English remain independently accessible, including at 213 and 216. English wording, sequence and context are preserved. Removing inserted Latin milestones and reversing the two approved Greek opening markers recovers exactly the frozen bytes; node and UTF-8 locators, IDs, sameAs, narrative partitions, final extents and input hashes pass.

Every new identity was selected in the final local build. Exact Latin/Greek intervals, English context, unavailable states, reciprocal notices, containing ranges, actual chapter/subchapter selectors, deep links, navigation, reload/history, language panes, IDs and themes passed. XIII 212–217 containing chapter, subchapters, Alignment and Bamberg views preserve the three witnesses' source ordering and completeness. Protected checks cover all 3,157 previously selectable Antiquities identities, source contents, traditional/Bamberg/Alignment, accepted VIII/X controls, Whiston, Bellum including Lodge, and other affected works. The precise inherited Book-I apparatus-link and unsupported I.1 exceptions were reproduced separately; no additional errors were observed.

Published baseline input: 3,157 identities. This batch adds 867 local selections and 864 nonempty Latin intervals. The isolated branch has 4,024 selectable identities. That is a frozen-baseline local total; it does not include the separately integrated canonical IX addition and is not a claim about current publication.

Frozen base: {BASE}. Canonical HEAD observed read-only: {canonical}. Branch HEAD before this handoff commit: {head}. Branch: antiquities-niese-12-13. Worktree: {ROOT}. Runtime: {RUNTIME}. Separate book packets: {packet(12)} and {packet(13)}. QA records contain actual free origins and isolated profiles.

Canonical XII/XIII source blobs still equal the pinned inputs. Canonical reader advances for IX and the current Whiston indexes must be retained when combining the separately documented XII/XIII support changes. INTEGRATION_CONTEXT.json records the observed canonical commit, source hashes and integration requirements; no canonical code was silently imported. Coordinated integration must rebuild and certify against its then-current code. HANDOFF.json verifies both book manifests and bound certificates, reconciles counts, and records changed-file hashes and scoped commit history. No merge, push, preview update or deployment was performed by this assignment.
''',encoding='utf8',newline='\n')
print('PASS both certificates/manifests, exact scope, 867 identities / 864 intervals; ready; canonical',canonical)
