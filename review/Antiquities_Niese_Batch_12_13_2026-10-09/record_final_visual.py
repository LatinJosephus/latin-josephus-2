"""Record only the final screenshots actually opened and visually examined by the agent."""
from prepare_review import *
import subprocess, shutil
from datetime import datetime, timezone
observations = {
    12: {'READER_248_dark.png': 'No independent Latin interval notice explicitly identifies dating material in XII.246; Greek 248 and unchanged English context are visible. Notice wraps within the Latin pane in dark theme.',
         'READER_249_light.png': 'The full surviving nec non etiam eos clause and resumed 247 ending appear in transmitted order, with partial/reordered qualification. Greek 249 and unchanged English context are visible in light theme.'},
    13: {'READER_212_light.png': 'The notice identifies the appended dating formula in latin-book13-num208 and points to continuation in 214. Latin, Greek 212 and unchanged broader English context are independently displayed. The notice wraps within its pane.',
         'READER_213_dark.png': 'No independent Latin interval notice distinguishes the separate liberation account from 214 dating and the earlier military appointment. Greek 213 and the unchanged English paragraph remain displayed. Dark-theme text and notice are readable.',
         'READER_214_dark.png': 'Displayed Latin begins [214] Itaque iudaei feliciter and ends superauerunt, with reciprocal dating-in-212 notice. Greek 214 and unchanged English context including the dating and prosperity statements remain visible; dark-theme notice wraps within its pane.',
         'READER_216_light.png': 'No independent Latin interval notice specifically identifies missing assembly/warning correspondence and preserves demolition in 217. Greek 216 and unchanged English context remain visible in light theme.',
         'READER_269_light.png': 'The explicit 269 milestone in the anonymous source paragraph produces a nonempty Latin interval and matching Greek selection, with unchanged English broader context; no fabricated source paragraph ID is needed.',
         'READER_433_dark.png': 'Final Latin interval preserves the repeated mortem compleuit, with qualified terminal correspondence notice; Greek ending and unchanged English context are visible. Next navigation is disabled at the final identity.'}}
for b, items in observations.items():
    d = packet(b)
    data = {'book': b, 'result': 'PASS', 'inspected_at_UTC': datetime.now(timezone.utc).isoformat(),
            'method': 'Actual final local-reader PNGs opened using view_image and visually examined; automated selection/range evidence covers all identities and both themes',
            'screenshots': [{'path': str(d/name), 'sha256': digest((d/name).read_bytes()),
                             'observed': observed} for name, observed in items.items()],
            'scope': 'Final local build from the pinned baseline with both XII/XIII enabled; no canonical or published browser claimed as new-book certification'}
    if b == 12:
        previous = 'e66c19b6b8e65e472817baaa5442de26c209230a'
        paths = ['assets/xml/antiquities/Greek/book-12.xml', 'assets/xml/antiquities/Latin/book-12.xml',
                 'assets/xml/antiquities/niese/book-12.json',
                 str((d/'EDITORIAL_DECISIONS.json').relative_to(ROOT)).replace(chr(92), '/'),
                 str((d/'QUALIFIED_CORRESPONDENCE.json').relative_to(ROOT)).replace(chr(92), '/')]
        data['accepted_XII_preservation'] = []
        for rel in paths:
            old = subprocess.check_output(['git','show',f'{previous}:{rel}'],cwd=ROOT)
            current = (ROOT/rel).read_bytes()
            assert old == current, rel
            data['accepted_XII_preservation'].append({'path':rel,'sha256':digest(current),'equals_completed_XII_handoff_commit':previous})
    save(d/'FINAL_VISUAL_REVIEW.json',data)
shutil.copyfile(RUNTIME/'candidate-jekyll.log',PACK/'evidence/build/candidate-jekyll.log')
print('Recorded final visually inspected selections; completed XII corpus, decisions and qualifications unchanged')
