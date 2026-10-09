"""Read-only integration context and final frozen-resource hash verification."""
from prepare_review import *
import subprocess

BASE = 'ad3158b7a86dea6997510b3de17f2e510c23367c'
CANONICAL = Path('C:/Users/Pollard_R/Git/LatinJosephus-v2-development')
def git_at(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args])
head = git_at(CANONICAL, 'rev-parse', 'HEAD').decode().strip()
resources = {}
corpus = []
for b in [12, 13]:
    baseline = json.loads((packet(b) / 'BASELINE.json').read_text(encoding='utf8'))
    for item in baseline['printed_sources']:
        p = Path(item['path']); actual = digest(p.read_bytes())
        assert actual == item['sha256'], p
        resources[str(p)] = {'sha256': actual, 'bytes': p.stat().st_size,
                             'status': 'UNCHANGED_FROM_FROZEN_SOURCE'}
    for lang in ['Greek', 'Latin', 'English']:
        rel = f'assets/xml/antiquities/{lang}/book-{b:02}.xml'
        frozen = (packet(b) / 'inputs' / f'{lang}-book-{b:02}.xml').read_bytes()
        base = git_at(ROOT, 'show', f'{BASE}:{rel}')
        current = git_at(CANONICAL, 'show', f'{head}:{rel}')
        assert digest(frozen) == baseline['inputs'][lang]['sha256']
        assert digest(base) == baseline['inputs'][lang]['git_blob_sha256']
        assert current == base, ('Canonical corpus advanced; reconcile independently', rel)
        corpus.append({'path': rel, 'frozen_worktree_sha256': digest(frozen),
                       'base_blob_sha256': digest(base), 'canonical_blob_sha256': digest(current),
                       'canonical_blob_equals_frozen_base_blob': True,
                       'local_implemented_sha256': digest((ROOT / rel).read_bytes())})
reference = json.loads((PACK / 'FROZEN_REFERENCE_VERIFICATION.json').read_text(encoding='utf8'))
checks = []
for item in reference['checks']:
    actual = digest(Path(item['path']).read_bytes())
    assert actual == item['expected'], item['path']
    checks.append({'path': item['path'], 'sha256': actual})
renderer_rel = 'assets/js/renderTei.js'
canonical_renderer = git_at(CANONICAL, 'show', f'{head}:{renderer_rel}')
delta = git_at(CANONICAL, 'diff', BASE, head, '--', renderer_rel).decode('utf8')
(PACK / 'CANONICAL_READER_ADVANCE.diff').write_text(delta, encoding='utf8', newline='\n')
registry9 = git_at(CANONICAL, 'show', f'{head}:assets/xml/antiquities/niese/book-09.json')
ix = json.loads(registry9)
assert b'9: "assets/xml/antiquities/niese/book-09.json"' in canonical_renderer
local_renderer = (ROOT / renderer_rel).read_bytes()
assert local_renderer == (RUNTIME / 'site' / renderer_rel).read_bytes()
controls = {}
for rel in ['_includes/display-settings.html', renderer_rel]:
    controls[rel] = {'base_blob_sha256': digest(git_at(ROOT, 'show', f'{BASE}:{rel}')),
                     'canonical_blob_sha256': digest(git_at(CANONICAL, 'show', f'{head}:{rel}')),
                     'local_worktree_sha256': digest((ROOT / rel).read_bytes())}
data = {'base_commit': BASE, 'canonical_checkout': str(CANONICAL),
        'canonical_HEAD_observed_read_only': head,
        'canonical_advance': head != BASE, 'assigned_corpus_comparison': corpus,
        'printed_resources_rechecked': list(resources.values()),
        'printed_resource_paths': list(resources), 'frozen_reference_checks': checks,
        'controls': controls, 'canonical_IX_registry_sha256': digest(registry9),
        'canonical_IX_selectable_count': len(ix['sections']),
        'shared_reader_advances': ['IX identity registry enabled',
            'registry-defined excluded narrative paragraphs removed from exact views',
            'unavailable language uses its own exact view before broader context fallback'],
        'integration_requirements': ['Retain current canonical IX corpus, identity data and enablement',
            'Retain current canonical Whiston compiled indexes and behavior',
            'Combine only the documented XII/XIII reader support with canonical advances; do not overwrite the renderer',
            'Carry per-book approved identity registries and corpus commits independently',
            'Rebuild and run coordinated integration QA against then-current canonical code'],
        'local_certification_scope': 'Actual local build from frozen ad3158b plus this isolated XII/XIII branch; canonical advances inspected read-only, not imported or certified here',
        'actions_on_canonical': 'READ_ONLY; no working files, branches or Git configuration changed',
        'frozen_inputs_replaced': False, 'result': 'PASS'}
save(PACK / 'INTEGRATION_CONTEXT.json', data)
print('PASS unchanged frozen PDFs/reference packets; assigned canonical corpus still equals pinned blobs; canonical', head)
