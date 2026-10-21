"""Regression tests for Whiston Contra Apionem's accepted English paragraphs."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

MODULE = Path(__file__).resolve().parents[1] / "extract-whiston-contra-apionem.py"
SPEC = importlib.util.spec_from_file_location("extract_whiston_contra_apionem", MODULE)
EXTRACTOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(EXTRACTOR)
ROOT = MODULE.parents[2]


def source(number):
    return (ROOT / f"assets/xml/contra-apionem/English/book-{number:02d}.xml").read_bytes()


def paragraph(number, text, *, attributes=None):
    attrs = attributes if attributes is not None else f'n="{number}" xml:id="english-apion1-num{number}"'
    return f'<p {attrs}>{text}</p>'


def fixture(content, *, prefix='<milestone unit="chapter" subtype="niese" n="1"/><milestone unit="whiston-section" n="1"/>', header=''):
    return (f'<TEI xmlns="{EXTRACTOR.TEI}">{header}<text xml:lang="eng"><body>'
            f'<div1 type="book" n="1" xml:id="english-apion1">{prefix}{content}</div1></body></text></TEI>').encode()


def small(content, expected=(1, 2), **kwargs):
    return EXTRACTOR.extract_document(fixture(content, **kwargs), book_number=1,
                                     verify_source=False, expected_sections=list(expected))


class WhistonContraApionemExtraction(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.books = {}
        offset = 0
        for book in (1, 2):
            cls.books[book] = EXTRACTOR.extract_document(source(book), book_number=book, order_offset=offset)
            offset += len(cls.books[book][0])

    def test_both_complete_books_restore_every_source_character(self):
        total = tokens = 0
        for book, (records, report) in self.books.items():
            contract = EXTRACTOR.CONTRACTS[book]
            self.assertEqual([record['section'] for record in records], list(range(1, contract['sections'] + 1)))
            self.assertEqual(report['counts']['runningWordTokens'], contract['tokens'])
            self.assertEqual(report['counts']['narrativeParagraphs'], contract['sections'])
            self.assertEqual(report['coverage']['rawParagraphSequenceSha256'], report['coverage']['restoredParagraphSequenceSha256'])
            self.assertEqual(report['coverage']['sourceWordSequenceSha256'], report['coverage']['indexedWordSequenceSha256'])
            by_id = {record['id']: record for record in records}
            for item in report['paragraphs']:
                restored = ''.join(EXTRACTOR.utf16_slice(by_id[piece['recordId']]['text'], piece['recordStart'], piece['recordEnd'])
                                   if piece['kind'] == 'record' else piece['text'] for piece in item['sourcePieces'])
                self.assertEqual(restored, item['rawText'])
                self.assertEqual(item['nieseMarkers'], [])
            total += len(records)
            tokens += report['counts']['runningWordTokens']
        self.assertEqual((total, tokens), (616, 36853))

    def test_xml_ids_and_english_reader_selection_are_exact(self):
        for book, (records, report) in self.books.items():
            for record in records:
                identity = f'english-apion{book}-num{record["section"]}'
                self.assertEqual(record['sourceId'], identity)
                self.assertEqual(record['sourceIds'], [identity])
                self.assertEqual(record['sourceIdentityKind'], 'xml:id')
                self.assertEqual(record['readerLink'], {'path': 'contra-apionem/',
                    'params': {'book': book, 'niese': record['section'], 'english': 'whiston'}})
                self.assertEqual(record['url'], f'/contra-apionem/?book={book}&niese={record["section"]}&english=whiston')
            self.assertTrue(all(item['sourceAttributes'] == {'n': str(item['sections'][0]['section']), 'xml:id': item['sourceId']}
                                for item in report['paragraphs']))
        self.assertEqual(self.books[2][0][0]['order'], 320)

    def test_inline_whiston_markers_preserve_tails_positions_and_continuity(self):
        records, report = self.books[2]
        expected = [(109, 9, 106, 'What then can we say of Apion'), (112, 10, 4, 'Nay, this miracle or piety')]
        for section, number, offset, following in expected:
            item = report['paragraphs'][section - 1]
            marker = item['structuralMarkers'][0]
            self.assertEqual(marker, {'unit': 'whiston-section', 'number': number,
                'sourceTextOffset': offset, 'sourceAttributes': {'unit': 'whiston-section', 'n': str(number)}})
            self.assertTrue(EXTRACTOR.utf16_slice(item['rawText'], offset, EXTRACTOR.utf16_length(item['rawText'])).startswith(following))
            self.assertEqual((item['whistonSectionStart'], item['whistonSectionEnd']), (number - 1, number))
            self.assertEqual(records[section - 1]['text'], item['rawText'])
            self.assertNotIn('breakBefore', records[section - 1])
            self.assertEqual(records[section - 1]['phraseBreaks'], [])
        self.assertEqual(report['counts']['inlineWhistonSectionMilestones'], 2)

    def test_every_chapter_and_whiston_marker_is_retained_with_original_position(self):
        for book, (_, report) in self.books.items():
            contract = EXTRACTOR.CONTRACTS[book]
            self.assertEqual(report['counts']['chapterMilestones'], contract['chapters'])
            self.assertEqual(report['counts']['whistonSectionMilestones'], contract['whistonSections'])
            self.assertEqual([marker['number'] for marker in report['structuralMarkers'] if marker['unit'] == 'chapter'],
                             list(range(1, contract['chapters'] + 1)))
            for marker in report['structuralMarkers']:
                self.assertEqual(marker['previousSection'], marker['beforeSection'] - 1 or None)
            self.assertEqual(report['structuralMarkers'][:2], [
                {'unit': 'chapter', 'number': 1, 'sourceAttributes': {'unit': 'chapter', 'subtype': 'niese', 'n': '1'},
                 'beforeSection': 1, 'previousSection': None, 'bookChildIndex': 0},
                {'unit': 'whiston-section', 'number': 1, 'sourceAttributes': {'unit': 'whiston-section', 'n': '1'},
                 'beforeSection': 1, 'previousSection': None, 'bookChildIndex': 1}])

    def test_literal_brackets_are_searchable_text_without_invented_editorial_status(self):
        records = [record for part, _ in self.books.values() for record in part]
        self.assertEqual(sum('[' in record['text'] for record in records), 44)
        self.assertIn('[as the Greeks have,]', self.books[1][0][37]['text'])
        for record in records:
            for key in ['editorialMarks', 'sourceMarkup', 'textGaps', 'phraseBreaks']:
                self.assertEqual(record[key], [])
            self.assertNotIn('breakBefore', record)

    def test_only_lf_crlf_equivalence_is_accepted(self):
        for book in (1, 2):
            raw = source(book)
            crlf = raw.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')
            original, report = EXTRACTOR.extract_document(raw, book_number=book)
            windows, windows_report = EXTRACTOR.extract_document(crlf, book_number=book)
            self.assertEqual(original, windows)
            self.assertEqual(report['coverage'], windows_report['coverage'])
            self.assertEqual(windows_report['source']['sha256'], EXTRACTOR.sha(crlf))
            with self.assertRaisesRegex(EXTRACTOR.ExtractionError, 'source differs'):
                EXTRACTOR.extract_document(raw.replace(b'<text ', b'<text altered="yes" ', 1), book_number=book)

    def test_utf16_offsets_entities_and_whitespace_restore_exactly(self):
        records, report = small(paragraph(1, ' \n𐐀lpha &amp; á, <milestone unit="whiston-section" n="2"/> beta.  ')
                                + paragraph(2, 'Last paragraph.'))
        self.assertEqual(records[0]['text'], '𐐀lpha & á,  beta.')
        item = report['paragraphs'][0]
        marker = item['structuralMarkers'][0]
        self.assertEqual(marker['sourceTextOffset'], EXTRACTOR.utf16_length(' \n𐐀lpha & á, '))
        self.assertEqual(item['sourcePieces'][1]['recordEnd'], len(records[0]['text']) + 1)
        self.assertEqual([piece['kind'] for piece in item['sourcePieces']], ['excluded', 'record', 'excluded'])

    def test_zero_width_division_does_not_split_a_word(self):
        records, _ = small(paragraph(1, 'al<milestone unit="whiston-section" n="2"/>pha') + paragraph(2, 'beta'))
        self.assertEqual(records[0]['text'], 'alpha')
        self.assertEqual(EXTRACTOR.words(records[0]['text']), ['alpha'])

    def test_header_notes_and_titles_are_outside_running_text(self):
        header = '<teiHeader><fileDesc><titleStmt><title>unsearchabletitle</title></titleStmt><notesStmt><note>unsearchablenote</note></notesStmt></fileDesc></teiHeader>'
        records, report = small(paragraph(1, 'alpha') + paragraph(2, 'beta'), header=header)
        self.assertEqual([record['text'] for record in records], ['alpha', 'beta'])
        self.assertEqual(report['counts']['runningWordTokens'], 2)

    def test_unreviewed_inline_elements_or_number_labels_are_refused(self):
        for content in ['<note>annotation</note>', '<gap/>', '<add>new word</add>', '<num>9</num>',
                        '<milestone unit="niese" n="3"/>', '<milestone unit="chapter" subtype="niese" n="2"/>',
                        '<milestone unit="whiston-section" n="2">text</milestone>',
                        '<milestone unit="whiston-section" n="2" cert="low"/>']:
            with self.subTest(content=content), self.assertRaises(EXTRACTOR.ExtractionError):
                small(paragraph(1, 'alpha ' + content) + paragraph(2, 'beta'))

    def test_malformed_or_substituted_paragraph_identity_is_refused(self):
        for attrs in ['n="1" xml:id="latin-apion1-num1"', 'n="1" xml:id="english-apion2-num1"',
                      'n="1" sameAs="#latin-apion1-num1"', 'n="one" xml:id="english-apion1-numone"',
                      'n="01" xml:id="english-apion1-num01"', 'n="1" xml:id="english-apion1-num2"',
                      'n="1" xml:id="english-apion1-num1" type="note"']:
            with self.subTest(attrs=attrs), self.assertRaises(EXTRACTOR.ExtractionError):
                small(paragraph(1, 'alpha', attributes=attrs) + paragraph(2, 'beta'))

    def test_missing_duplicate_reordered_or_empty_sections_are_refused(self):
        cases = [paragraph(1, 'alpha'), paragraph(1, 'alpha') + paragraph(1, 'beta'),
                 paragraph(2, 'beta') + paragraph(1, 'alpha'), paragraph(1, ' ') + paragraph(2, 'beta'),
                 paragraph(1, '...') + paragraph(2, 'beta')]
        for content in cases:
            with self.subTest(content=content), self.assertRaises(EXTRACTOR.ExtractionError):
                small(content)

    def test_chapter_and_whiston_divisions_are_required_and_sequential(self):
        for prefix in ['', '<milestone unit="chapter" subtype="niese" n="1"/>',
                       '<milestone unit="whiston-section" n="1"/>',
                       '<milestone unit="chapter" subtype="niese" n="2"/><milestone unit="whiston-section" n="1"/>',
                       '<milestone unit="chapter" subtype="niese" n="1"/><milestone unit="whiston-section" n="2"/>']:
            with self.subTest(prefix=prefix), self.assertRaises(EXTRACTOR.ExtractionError):
                small(paragraph(1, 'alpha') + paragraph(2, 'beta'), prefix=prefix)
        for number in [1, 3]:
            with self.subTest(number=number), self.assertRaisesRegex(EXTRACTOR.ExtractionError, 'division sequence'):
                small(paragraph(1, f'alpha <milestone unit="whiston-section" n="{number}"/>tail') + paragraph(2, 'beta'))

    def test_unknown_book_children_container_text_and_trailing_marker_are_refused(self):
        for content in ['unclassified ' + paragraph(1, 'alpha') + paragraph(2, 'beta'),
                        paragraph(1, 'alpha') + 'unclassified ' + paragraph(2, 'beta'),
                        '<head>New heading</head>' + paragraph(1, 'alpha') + paragraph(2, 'beta'),
                        paragraph(1, 'alpha') + paragraph(2, 'beta') + '<milestone unit="whiston-section" n="2"/>']:
            with self.subTest(content=content), self.assertRaises(EXTRACTOR.ExtractionError):
                small(content)

    def test_unreviewed_book_source_and_language_are_refused(self):
        for number in [0, 3]:
            with self.subTest(number=number), self.assertRaisesRegex(EXTRACTOR.ExtractionError, 'Unreviewed'):
                EXTRACTOR.extract_document(source(1), book_number=number)
        with self.assertRaisesRegex(EXTRACTOR.ExtractionError, 'source path differs'):
            EXTRACTOR.extract_document(source(1), book_number=1, source_path='assets/xml/contra-apionem/Latin/book-01.xml')
        for before, after in [(b'xml:lang="eng"', b'xml:lang="lat"'),
                              (b'xml:id="english-apion1"', b'xml:id="latin-apion1"')]:
            with self.subTest(after=after), self.assertRaises(EXTRACTOR.ExtractionError):
                EXTRACTOR.extract_document(source(1).replace(before, after), book_number=1, verify_source=False)

    def test_complete_build_is_deterministic_and_global_order_is_consecutive(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            report = EXTRACTOR.build_corpus(ROOT, output)
            first = {path.name: path.read_bytes() for path in output.iterdir()}
            repeated = EXTRACTOR.build_corpus(ROOT, output)
            self.assertEqual(report, repeated)
            self.assertEqual(first, {path.name: path.read_bytes() for path in output.iterdir()})
            self.assertEqual(report['counts']['sections'], 616)
            self.assertTrue(report['coverage']['globalIdsUnique'])
            self.assertTrue(report['coverage']['globalOrderIsConsecutive'])
            self.assertEqual([book['orderStart'] for book in report['books']], [0, 320])


if __name__ == '__main__':
    unittest.main()
