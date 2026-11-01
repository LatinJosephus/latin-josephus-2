import importlib.util
import json
from pathlib import Path
import unittest
import copy

base = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('lauro_projector', base/'extract-lauro.py')
projector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(projector)


class PhysicalProjection(unittest.TestCase):
    def test_several_targets_do_not_emit_several_occurrences(self):
        source = json.loads((base.parents[1]/'assets/data/deh-lauro1544/book-01.json').read_text(encoding='utf-8'))
        original, accounting = projector.project(source)
        duplicate = copy.deepcopy(source['mappings'][0])
        duplicate['id'] = 'synthetic-additional-target'
        duplicate['canonical']['citation'] = 'Synthetic extra target'
        source['mappings'].append(duplicate)
        projected, second_accounting = projector.project(source)
        self.assertEqual(''.join(r['text'] for r in original), ''.join(r['text'] for r in projected))
        self.assertEqual(accounting, second_accounting)
        self.assertEqual(len(original), len(projected))
        self.assertEqual(len(projected[0]['canonicalCorrespondences']), 2)


if __name__ == '__main__':
    unittest.main()
