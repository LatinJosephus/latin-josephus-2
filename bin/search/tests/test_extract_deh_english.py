"""English DEH: complete source restoration and chapter-local citation tests."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

MODULE = Path(__file__).resolve().parents[1] / "extract-deh-english.py"
SPEC = importlib.util.spec_from_file_location("extract_deh_english", MODULE)
EXTRACTOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(EXTRACTOR)
ROOT = MODULE.parents[2]


def source(number):
    return (ROOT / f"assets/xml/deh/English/book-{number:02d}.xml").read_bytes()


def fixture(text='alpha beta', *, indent='\n            ', prefix='', attributes=None, label='[II.1.1]'):
    attrs = attributes or 'xml:id="english-deh2-num1" sameAs="#latin-deh2-num1"'
    return (f'<TEI xmlns="{EXTRACTOR.TEI}"><teiHeader><fileDesc><titleStmt><title>unsearchabletitle</title>'
            f'</titleStmt></fileDesc></teiHeader><text><body><note>{EXTRACTOR.CONTRACTS[2]["releaseNote"]}</note>'
            '<div1 n="II" xml:id="english-deh2" sameAs="#latin-deh2" subtype="English" type="book">'
            '<div2 n="1" xml:id="english-deh2-chapter1" sameAs="#latin-deh2-chapter1" type="chapter">'
            f'<head>Book II</head>{prefix}<p {attrs}>{indent}<num>{label}</num>{text}</p>'
            '</div2></div1></body></text></TEI>').encode('utf8')


def small(text='alpha beta', **kwargs):
    return EXTRACTOR.extract_document(fixture(text, **kwargs), book_number=2, verify_source=False,
                                     expected_sections=1, expected_chapters=1)


class EnglishDehExtraction(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.books = {book: EXTRACTOR.extract_document(source(book), book_number=book) for book in range(1, 6)}

    def test_all_five_books_restore_every_original_paragraph_and_running_word(self):
        total = tokens = 0
        for book, (records, report) in self.books.items():
            contract = EXTRACTOR.CONTRACTS[book]
            self.assertEqual(len(records), contract['sections'])
            self.assertEqual(report['counts']['runningWordTokens'], contract['tokens'])
            self.assertEqual(report['coverage']['rawParagraphSequenceSha256'], report['coverage']['restoredParagraphSequenceSha256'])
            self.assertEqual(report['coverage']['sourceWordSequenceSha256'], report['coverage']['indexedWordSequenceSha256'])
            by_id = {record['id']: record for record in records}
            for paragraph in report['paragraphs']:
                restored = ''.join(EXTRACTOR.utf16_slice(by_id[piece['recordId']]['text'], piece['recordStart'], piece['recordEnd'])
                                   if piece['kind'] == 'record' else piece['text'] for piece in paragraph['sourcePieces'])
                self.assertEqual(restored, paragraph['rawText'])
                notes = ''.join(piece['text'] for piece in paragraph['sourcePieces']
                                if piece.get('reason') == 'translation-comparison-note')
                self.assertEqual(paragraph['removedPrefix'] + paragraph['runningText'] + notes, paragraph['rawText'])
            total += len(records)
            tokens += report['counts']['runningWordTokens']
        self.assertEqual((total, tokens), (558, 136052))

    def test_indentation_before_num_is_removed_with_the_entire_label(self):
        self.assertEqual([sum(p['removedPrefix'].startswith('\n') for p in report['paragraphs'])
                          for _, report in self.books.values()], [126, 73, 18, 0, 0])
        for records, report in self.books.values():
            for record, paragraph in zip(records, report['paragraphs']):
                self.assertNotIn('[', record['text'])
                self.assertNotIn(']', record['text'])
                self.assertTrue(paragraph['removedPrefix'].endswith(f'[{record["citationLabel"]}]'))
                self.assertEqual(paragraph['sourcePieces'][0]['reason'], 'citation-label-and-preceding-whitespace')
        records, _ = small(' actual running text', indent='\n            ')
        self.assertEqual(records[0]['text'], 'actual running text')
        self.assertEqual(EXTRACTOR.words(records[0]['text']), ['actual', 'running', 'text'])

    def test_approved_translation_notes_are_preserved_but_not_searchable_prose(self):
        count = 0
        for records, report in self.books.values():
            by_id = {record['sourceId']: record for record in records}
            for paragraph in report['paragraphs']:
                for piece in paragraph['sourcePieces']:
                    if piece.get('reason') != 'translation-comparison-note':
                        continue
                    count += 1
                    self.assertTrue(piece['text'].startswith('Translation comparison: '))
                    self.assertNotIn('Translation comparison:', by_id[paragraph['sourceId']]['text'])
                    self.assertEqual(EXTRACTOR.utf16_slice(paragraph['rawText'], piece['sourceStart'], piece['sourceEnd']), piece['text'])
        self.assertEqual(count, 8)
        self.assertEqual(sum(report['counts']['excludedTranslationNotes'] for _, report in self.books.values()), 8)

    def test_unapproved_translation_note_attributes_are_refused(self):
        raw = source(1).replace(b'type="uncertainty" source="#latin-deh1-num31"',
                                b'type="certainty" source="#latin-deh1-num31"', 1)
        with self.assertRaisesRegex(EXTRACTOR.ExtractionError, 'inline markup'):
            EXTRACTOR.extract_document(raw, book_number=1, verify_source=False)

    def test_original_ids_same_as_and_chapter_local_reader_urls(self):
        for book, (records, report) in self.books.items():
            for record, paragraph in zip(records, report['paragraphs']):
                self.assertEqual(record['sourceId'], f'english-deh{book}-num{record["section"]}')
                self.assertEqual(record['sourceSameAs'], f'#latin-deh{book}-num{record["section"]}')
                self.assertEqual(record['sourceIds'], [record['sourceId']])
                self.assertEqual(paragraph['sourceAttributes']['sameAs'], record['sourceSameAs'])
                self.assertEqual(record['readerLink'], {'path': 'deh/', 'params': {'book': book,
                    'chapter': record['chapter'], 'unit': record['paragraph'], 'english': 'pollard'}})
                self.assertEqual(record['url'], f'/deh/?book={book}&chapter={record["chapter"]}&unit={record["paragraph"]}&english=pollard')
                self.assertEqual(record['citationScheme'], 'chapter-paragraph')
        self.assertEqual([records[0]['order'] for records, _ in self.books.values()], [0, 215, 288, 358, 437])

    def test_prologue_boundary_is_unique_and_exact(self):
        records = [record for part, _ in self.books.values() for record in part]
        self.assertEqual([record['citationLabel'] for record in records if record.get('breakBefore')], ['I.1.1'])
        self.assertEqual([record['citationLabel'] for record in records[:4]], ['Prol.1', 'Prol.2', 'Prol.3', 'I.1.1'])
        self.assertEqual([record['citation']['prologue'] for record in records[:4]], [True, True, True, False])
        self.assertTrue(all(record['phraseBreaks'] == [] for record in records))

    def test_metadata_and_verified_headings_are_recorded_outside_running_text(self):
        records, report = small()
        self.assertEqual(records[0]['text'], 'alpha beta')
        self.assertEqual([item['kind'] for item in report['excludedBlocks']], ['teiHeader', 'release-note', 'heading'])
        self.assertEqual(report['excludedBlocks'][-1]['text'], 'Book II')
        self.assertEqual(sum(report['counts']['excludedHeadings'] for _, report in self.books.values()), 6)
        self.assertEqual(sum(report['counts']['excludedReleaseNotes'] for _, report in self.books.values()), 5)

    def test_utf16_entities_and_all_whitespace_are_reversible(self):
        records, report = small(' \n𐐀lpha &amp; á, beta.  ', indent='\n    ')
        self.assertEqual(records[0]['text'], '𐐀lpha & á, beta.')
        paragraph = report['paragraphs'][0]
        record_piece = next(piece for piece in paragraph['sourcePieces'] if piece['kind'] == 'record')
        self.assertEqual(record_piece['recordEnd'], len(records[0]['text']) + 1)
        self.assertEqual([piece['kind'] for piece in paragraph['sourcePieces']], ['excluded', 'excluded', 'record', 'excluded'])
        self.assertTrue(report['coverage']['nonWhitespaceContentPreserved'])

    def test_plain_source_punctuation_does_not_invent_editorial_annotations(self):
        records, _ = small('[ordinary] † literal * punctuation')
        self.assertEqual(records[0]['text'], '[ordinary] † literal * punctuation')
        for field in ['editorialMarks', 'sourceMarkup', 'textGaps', 'phraseBreaks']:
            self.assertEqual(records[0][field], [])

    def test_lf_and_crlf_are_equivalent_but_metadata_changes_are_not(self):
        for book in range(1, 6):
            raw = source(book)
            crlf = raw.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')
            original, report = self.books[book]
            windows, windows_report = EXTRACTOR.extract_document(crlf, book_number=book)
            self.assertEqual(original, windows)
            self.assertEqual(report['coverage'], windows_report['coverage'])
            self.assertEqual(windows_report['source']['sha256'], EXTRACTOR.sha(crlf))
            with self.assertRaisesRegex(EXTRACTOR.ExtractionError, 'source differs'):
                EXTRACTOR.extract_document(raw.replace(b'version 1.1', b'version 1.2', 1), book_number=book)

    def test_unknown_inline_elements_never_silently_drop_or_invent_words(self):
        for markup in ['<note>annotation</note>', '<supplied>supplied</supplied>', '<del>deleted</del>', '<unclear/>',
                       '<gap/>', '<milestone unit="niese" n="1"/>', '<num>[II.1.2]</num>', '<!-- hidden -->']:
            with self.subTest(markup=markup), self.assertRaisesRegex(EXTRACTOR.ExtractionError, 'inline markup'):
                small('alpha ' + markup + ' beta')

    def test_changed_english_identity_or_alignment_is_refused(self):
        for attrs in ['xml:id="latin-deh2-num1" sameAs="#latin-deh2-num1"',
                      'xml:id="english-deh2-num1" sameAs="#latin-deh2-num2"',
                      'xml:id="english-deh2-num1"',
                      'xml:id="english-deh2-num1" sameAs="#latin-deh2-num1" n="1"']:
            with self.subTest(attrs=attrs), self.assertRaisesRegex(EXTRACTOR.ExtractionError, 'identity or alignment'):
                small(attributes=attrs)

    def test_wrong_or_nested_labels_and_running_words_before_num_are_refused(self):
        for label in ['[II.2.1]', '[II.1.2]', '[I.1.1]', '[Prol.1]', '<hi>[II.1.1]</hi>']:
            with self.subTest(label=label), self.assertRaises(EXTRACTOR.ExtractionError):
                small(label=label)
        with self.assertRaisesRegex(EXTRACTOR.ExtractionError, 'before its citation label'):
            small(indent='unclassified prose ')

    def test_changed_book_chapter_note_or_heading_structure_is_refused(self):
        raw = fixture()
        cases = [(b'english-deh2"', b'english-deh3"'), (b'#latin-deh2-chapter1', b'#latin-deh2-chapter2'),
                 (b'<head>Book II</head>', b'<head>New prose</head>'),
                 (b'<head>Book II</head>', b''), (b'<body>', b'<body>unclassified '),
                 (b'version 1.1:', b'version 1.2:'), (b'<p xml:id=', b'<note>unexpected</note><p xml:id=')]
        for before, after in cases:
            with self.subTest(after=after), self.assertRaises(EXTRACTOR.ExtractionError):
                EXTRACTOR.extract_document(raw.replace(before, after, 1), book_number=2, verify_source=False,
                                           expected_sections=1, expected_chapters=1)

    def test_empty_intervals_malformed_xml_and_dtd_are_refused(self):
        for text in ['', '   ', '...']:
            with self.subTest(text=text), self.assertRaisesRegex(EXTRACTOR.ExtractionError, 'Empty'):
                small(text)
        for raw in [fixture().replace(b'</p>', b'</q>'), b'<!DOCTYPE TEI>' + fixture()]:
            with self.assertRaises(EXTRACTOR.ExtractionError):
                EXTRACTOR.extract_document(raw, book_number=2, verify_source=False, expected_sections=1, expected_chapters=1)

    def test_only_reviewed_books_sources_and_nonnegative_order_offsets_are_allowed(self):
        for book in [0, 6]:
            with self.assertRaisesRegex(EXTRACTOR.ExtractionError, 'Unreviewed'):
                EXTRACTOR.extract_document(source(1), book_number=book)
        with self.assertRaisesRegex(EXTRACTOR.ExtractionError, 'source path'):
            EXTRACTOR.extract_document(source(1), book_number=1, source_path='assets/xml/deh/Latin/book-01.xml')
        for offset in [-1, True, 0.5]:
            with self.subTest(offset=offset), self.assertRaisesRegex(EXTRACTOR.ExtractionError, 'order offset'):
                EXTRACTOR.extract_document(source(1), book_number=1, order_offset=offset)

    def test_complete_build_is_deterministic_and_validates_before_writing(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / 'output'
            report = EXTRACTOR.build_corpus(ROOT, output)
            original = {path.name: path.read_bytes() for path in output.iterdir()}
            self.assertEqual(report, EXTRACTOR.build_corpus(ROOT, output))
            self.assertEqual(original, {path.name: path.read_bytes() for path in output.iterdir()})
            self.assertEqual(report['counts']['sections'], 558)
            self.assertTrue(report['coverage']['globalIdsUnique'])
            self.assertTrue(report['coverage']['globalOrderIsConsecutive'])
            fake_root = Path(temporary) / 'changed-source'
            for book in range(1, 6):
                filename = fake_root / f'assets/xml/deh/English/book-{book:02d}.xml'
                filename.parent.mkdir(parents=True, exist_ok=True)
                filename.write_bytes(source(book) + (b' ' if book == 5 else b''))
            with self.assertRaisesRegex(EXTRACTOR.ExtractionError, 'source differs'):
                EXTRACTOR.build_corpus(fake_root, output)
            self.assertEqual(original, {path.name: path.read_bytes() for path in output.iterdir()})


if __name__ == '__main__':
    unittest.main()
