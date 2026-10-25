"""Regenerate only the audited AJ authority pins and include checksum.

Run the independent boundary audit before this command. --write is explicit;
the default is a byte-exact reproducibility check. Scholarly inputs are read-only.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
BASE = '5bb301c1b41d63c89c33a79826fc62892ac3890f'
CERT = '_docs/aj-latin-reconciliation/certified-boundaries.json'
CERT_SHA = '706a31747f16d5dc8dee37702f94b6e510b04135981ad5a76a4afbb11cf433f4'
LAYER = 'assets/data/deh-aj-display.v1.json'

def sha(b):
    return hashlib.sha256(b).hexdigest()

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', default=str(ROOT))
    p.add_argument('--write', action='store_true')
    args = p.parse_args()
    root = Path(args.root).resolve()
    assert sha((root / CERT).read_bytes()) == CERT_SHA, 'Boundary certification changed'
    subprocess.run([sys.executable, str(Path(__file__).with_name('aj-latin-boundary-audit.py')), '--root', str(root)], check=True)
    cert = json.loads((root / CERT).read_text(encoding='utf-8'))
    layer = json.loads((root / LAYER).read_text(encoding='utf-8'))
    allowed = {f'assets/xml/antiquities/Latin/book-{n:02}.xml' for n in [3,9,14,15,16,17,18,20]} | {'assets/js/renderTei.js'}
    authority = []
    for relative, expected in layer['source_sha256'].items():
        actual = sha((root / relative).read_bytes())
        if relative not in allowed:
            assert actual == expected, 'Unapproved source difference: ' + relative
        elif relative.endswith('.xml'):
            book = str(int(Path(relative).stem.split('-')[-1]))
            assert actual == cert['source_topology'][book]['current_sha256']
        else:
            assert actual == '39ded95fc3b7fdf39d9827cf513e6fc6c88922bb039435446b48b22ec4192848', 'Unaudited renderer'
        authority.append({'path':relative, 'current_sha256':actual})
        layer['source_sha256'][relative] = actual
    layer['baseline_commit'] = BASE
    layer['reconciliation'] = {'audit': CERT, 'audit_sha256': CERT_SHA,
                               'historical_baseline': cert['historical_baseline'],
                               'records':31, 'components':44,
                               'boundary_paths_and_sides_unchanged':True,
                               'character_offsets_recomputed':True,
                               'approved_selected_text_changes':1,
                               'unresolved_editorial_questions':0}
    raw = (json.dumps(layer, ensure_ascii=False, indent=2) + '\n').encode()
    include_path = root / '_includes/deh-parallels.html'
    include = include_path.read_bytes()
    new_include, count = re.subn(rb'data-aj-alignment-sha="[a-f0-9]{64}"', b'data-aj-alignment-sha="' + sha(raw).encode() + b'"', include)
    assert count == 1
    if args.write:
        (root / LAYER).write_bytes(raw)
        include_path.write_bytes(new_include)
    else:
        assert (root / LAYER).read_bytes() == raw, 'Derived layer regeneration differs'
        assert include == new_include, 'Include layer checksum differs'
    print(json.dumps({'status':'PASS','mode':'write' if args.write else 'check',
                      'layer_sha256':sha(raw),'audit_sha256':CERT_SHA,
                      'source_hashes_verified':len(authority),'scholarly_inputs_modified':False},indent=2))

if __name__ == '__main__':
    main()
