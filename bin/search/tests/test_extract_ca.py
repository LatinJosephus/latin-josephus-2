"""Source preservation, citation identity, and failure tests for Contra Apionem."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET


SEARCH = Path(__file__).resolve().parents[1]
REPOSITORY = SEARCH.parents[1]
spec = importlib.util.spec_from_file_location("ca_extract", SEARCH / "extract-ca.py")
extract = importlib.util.module_from_spec(spec)
spec.loader.exec_module(extract)
NS = "{http://www.tei-c.org/ns/1.0}"
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"


def paragraph(text: str, number: int = 1) -> str:
    return f'<p n="{number}" xml:id="latin-apion1-num{number}">{text}</p>'


def fixture(contents: str) -> bytes:
    return (f'<TEI xmlns="{extract.TEI}"><teiHeader><p>Metadata excluded.</p></teiHeader>'
            '<text xml:id="apion-latin-book-1-text" xml:lang="lat"><body>'
            '<note type="source">Boysen, CSEL 37 (1898), Contra Apionem Book 1.</note><pb n="3"/>'
            '<div1 n="I" type="book" subtype="Latin" xml:id="latin-apion1">'
            f'{contents}</div1></body></text></TEI>').encode("utf-8")


def small(source: bytes, units: int = 1, chapters: int = 1):
    return extract.extract_document(source, book_number=1, order_offset=0,
                                    expected_units=units, expected_chapters=chapters)


CHAPTER = '<milestone n="1" unit="chapter" subtype="boysen"/>'


def utf16_slice(text: str, start: int, end: int) -> str:
    return text.encode("utf-16-le")[start * 2:end * 2].decode("utf-16-le")


class ContraApionemRealSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.xml = {b: (REPOSITORY / f"assets/xml/contra-apionem/Latin/book-{b:02}.xml").read_bytes()
                   for b in (1, 2)}
        cls.extracted = {b: extract.extract_document(data, book_number=b,
                                                     expected_inline_counts=extract.BOOK_SPECS[b])
                         for b, data in cls.xml.items()}

    def test_two_books_have_all_616_niese_sections_and_21018_word_tokens(self):
        all_records = []
        for book, units, tokens in ((1, 320, 10657), (2, 296, 10361)):
            records, report = self.extracted[book]
            self.assertEqual(len(records), units)
            self.assertEqual(report["counts"]["runningWordTokens"], tokens)
            self.assertEqual(report["counts"]["nieseMilestones"], 0)
            self.assertEqual([r["section"] for r in records], list(range(1, units + 1)))
            self.assertEqual(report["source"]["sha256"], hashlib.sha256(self.xml[book]).hexdigest())
            all_records.extend(records)
        self.assertEqual(len(all_records), 616)
        self.assertEqual(len({r["id"] for r in all_records}), 616)
        self.assertEqual([r["order"] for r in all_records], list(range(616)))

    def test_all_citations_and_reader_links_follow_current_p_numbering(self):
        for book, (records, _) in self.extracted.items():
            source_paragraphs = ET.fromstring(self.xml[book]).findall(f"{NS}text/{NS}body/{NS}div1/{NS}p")
            for source, record in zip(source_paragraphs, records, strict=True):
                section = int(source.get("n"))
                self.assertEqual(record["sourceId"], source.get(XML_ID))
                self.assertEqual(record["citationScheme"], "niese")
                self.assertEqual(record["citationLabel"], f"{extract.ROMANS[book]}.{section}")
                self.assertEqual(record["citation"], {"book": extract.ROMANS[book], "section": section})
                self.assertEqual(record["url"], f"/contra-apionem/?book={book}&niese={section}")
                self.assertEqual(record["readerLink"],
                                 {"path": "contra-apionem/", "params": {"book": book, "niese": section}})
                self.assertNotIn("chapter", record)

    def test_every_original_character_is_restored_from_finished_record_segments(self):
        for book, (records, report) in self.extracted.items():
            originals = {p.get(XML_ID): "".join(p.itertext()) for p in
                         ET.fromstring(self.xml[book]).findall(f"{NS}text/{NS}body/{NS}div1/{NS}p")}
            for record, audit in zip(records, report["paragraphs"], strict=True):
                text = record["text"]
                self.assertEqual(text, originals[record["sourceId"]].strip())
                projected = "".join(text[s["recordTextStart"]:s["recordTextEnd"]] for s in audit["segments"])
                self.assertEqual(projected, text)
                restored = audit["leadingWhitespace"] + projected + audit["trailingWhitespace"]
                self.assertEqual(restored, originals[record["sourceId"]])
                for segment in audit["segments"]:
                    part = text[segment["recordTextStart"]:segment["recordTextEnd"]]
                    self.assertEqual(segment["kind"], "source-text")
                    self.assertEqual(part, restored[segment["sourceTextStart"]:segment["sourceTextEnd"]])
                    self.assertEqual(hashlib.sha256(part.encode()).hexdigest(), segment["textSha256"])
            coverage = report["coverage"]
            for first, second in (("rawParagraphSequenceSha256", "restoredParagraphSequenceSha256"),
                                  ("sourceWordSequenceSha256", "indexedWordSequenceSha256"),
                                  ("sourceNonWhitespaceContentSha256", "displayNonWhitespaceContentSha256")):
                self.assertEqual(coverage[first], coverage[second])
            self.assertEqual(coverage["generatedDisplayGlyphs"], 0)

    def test_all_25_original_asterisk_clusters_are_kept_and_mapped(self):
        expected = {
            1: {95: "***", 97: "***", 118: "***", 146: "*", 167: "***", 237: "***", 247: "***",
                251: "***", 259: "** *", 270: "***", 275: "***", 291: "***"},
            2: {12: "*", 26: "***", 31: "***", 99: "***", 101: "***", 113: "*", 146: "**",
                164: "***", 199: "***", 217: "*", 232: "*", 259: "***", 270: "***"},
        }
        for book, (records, report) in self.extracted.items():
            observed = {}
            for record in records:
                gaps = record["textGaps"]
                self.assertEqual(record["phraseBreaks"], [gap["start"] for gap in gaps])
                if gaps:
                    self.assertEqual(len(gaps), 1)
                    observed[record["section"]] = gaps[0]["text"]
                for gap in gaps:
                    self.assertEqual(gap["kind"], "literal-asterisks")
                    self.assertEqual(utf16_slice(record["text"], gap["start"], gap["end"]), gap["text"])
            self.assertEqual(observed, expected[book])
            self.assertEqual(report["counts"]["asteriskMarkerClusters"], len(expected[book]))
        self.assertEqual(self.extracted[2][0][11]["phraseBreaks"], [0])
        self.assertTrue(self.extracted[1][0][117]["text"].endswith("***"))
        self.assertTrue(self.extracted[1][0][145]["text"].endswith("*"))

    def test_source_annotations_are_retained_without_reopening_accepted_readings(self):
        all_records = [r for records, _ in self.extracted.values() for r in records]
        annotated = {r["citationLabel"]: r["sourceAnnotations"] for r in all_records if r.get("sourceAnnotations")}
        self.assertEqual(annotated, {
            "I.119": ["#niese-boundary-within-preceding-lacuna"],
            "I.147": ["#niese-boundary-within-preceding-lacuna"],
            "II.68": ["#transcription-restoration-is"],
        })
        self.assertEqual([r["citationLabel"] for r in all_records if r.get("breakBefore")], ["I.119", "I.147"])
        self.assertTrue(self.extracted[2][0][67]["text"].startswith("is autem"))
        overlap = self.extracted[2][0][277]
        self.assertTrue(overlap["text"].startswith("igitur si propter uirtutem"))
        self.assertFalse(overlap.get("breakBefore"))
        self.assertEqual(overlap["phraseBreaks"], [])

    def test_added_word_quotation_and_all_greek_spans_keep_their_distinct_source_status(self):
        all_records = [r for records, _ in self.extracted.values() for r in records]
        added = [(r["citationLabel"], m) for r in all_records for m in r["editorialMarks"]]
        self.assertEqual(added, [("I.290", {"kind": "add", "start": 35, "end": 40,
                                           "text": "milia", "sourceTag": "add"})])
        foreign = [(r["citationLabel"], m) for r in all_records for m in r["sourceMarkup"] if m["kind"] == "foreign"]
        self.assertEqual([label for label, _ in foreign], ["I.311", "I.318", "II.138"])
        self.assertEqual(sum(len(extract.words(mark["text"])) for _, mark in foreign), 7)
        quote_record = self.extracted[1][0][203]
        self.assertEqual([m["kind"] for m in quote_record["sourceMarkup"]], ["q"])
        self.assertTrue(quote_record["sourceMarkup"][0]["text"].startswith("quid furitis"))
        for record in all_records:
            for mark in record["editorialMarks"] + record["sourceMarkup"]:
                self.assertEqual(utf16_slice(record["text"], mark["start"], mark["end"]), mark["text"])

    def test_boysen_chapter_boundaries_can_occur_inside_niese_units(self):
        _, report = self.extracted[2]
        chapter_ten = [m for m in report["paragraphs"][119]["structuralMarkers"]
                       if m["kind"] == "chapter"]
        self.assertEqual(len(chapter_ten), 1)
        self.assertEqual(chapter_ten[0]["number"], 10)
        self.assertEqual(chapter_ten[0]["sourceTextOffset"], 297)
        self.assertGreater(chapter_ten[0]["recordTextOffset"], 0)
        self.assertEqual([self.extracted[b][1]["counts"]["chapterMilestones"] for b in (1, 2)], [35, 41])
        word_break = self.extracted[2][0][185]
        self.assertIn("praecellentes", word_break["text"])
        self.assertNotIn("praecel lentes", word_break["text"])

    def test_build_is_deterministic_and_does_not_touch_other_collection_outputs(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            sentinel = root / "corpus.json"
            sentinel.write_bytes(b"accepted Bellum sentinel\n")
            destination = root / "data" / extract.COLLECTION
            report = extract.build_corpus(REPOSITORY, destination)
            first = {p.name: p.read_bytes() for p in destination.iterdir()}
            extract.build_corpus(REPOSITORY, destination)
            self.assertEqual(first, {p.name: p.read_bytes() for p in destination.iterdir()})
            self.assertEqual(len(first), 6)
            self.assertEqual(sentinel.read_bytes(), b"accepted Bellum sentinel\n")
            self.assertEqual(report["counts"]["sections"], 616)
            self.assertEqual(report["counts"]["runningWordTokens"], 21018)
            for book in report["books"]:
                for kind in ("corpus", "extractionReport"):
                    data = (root / book[kind]["path"]).read_bytes()
                    self.assertEqual(len(data), book[kind]["bytes"])
                    self.assertEqual(hashlib.sha256(data).hexdigest(), book[kind]["sha256"])
            self.assertEqual(json.loads(first["corpus.json"]),
                             json.loads(first["book-01.corpus.json"]) + json.loads(first["book-02.corpus.json"]))

    def test_invalid_second_book_cannot_partially_replace_existing_outputs(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            sources = root / "assets/xml/contra-apionem/Latin"
            sources.mkdir(parents=True)
            for book, data in self.xml.items():
                (sources / f"book-{book:02}.xml").write_bytes(data)
            final = sources / "book-02.xml"
            final.write_bytes(final.read_bytes().replace(b'xml:id="latin-apion2-num296"', b'xml:id="latin-apion2-num999"', 1))
            destination = root / "output"
            destination.mkdir()
            (destination / "corpus.json").write_bytes(b"previous valid output")
            with self.assertRaisesRegex(extract.ExtractionError, "consecutive source identity"):
                extract.build_corpus(root, destination)
            self.assertEqual({p.name: p.read_bytes() for p in destination.iterdir()},
                             {"corpus.json": b"previous valid output"})


class ContraApionemCorruptionTests(unittest.TestCase):
    def test_utf16_offsets_retain_astral_letters_combining_accents_and_nested_pagebreaks(self):
        source = fixture(paragraph(CHAPTER + " 𐐀ve Á<add>li</add>us: "
                                   '<q>Ro<pb n="4"/>manos</q> <foreign xml:lang="grc">ἀπό</foreign> ** * postea. '))
        records, report = small(source)
        record = records[0]
        self.assertEqual(record["text"], "𐐀ve Álius: Romanos ἀπό ** * postea.")
        self.assertEqual(record["editorialMarks"], [{"kind": "add", "start": 7, "end": 9, "text": "li", "sourceTag": "add"}])
        for mark in record["editorialMarks"] + record["sourceMarkup"] + record["textGaps"]:
            self.assertEqual(utf16_slice(record["text"], mark["start"], mark["end"]), mark["text"])
        self.assertEqual(len(record["phraseBreaks"]), 1)
        self.assertEqual(record["textGaps"][0]["text"], "** *")
        self.assertEqual(report["counts"]["pageBreaks"], 2)

    def test_literal_editorial_punctuation_and_internal_whitespace_are_never_normalized(self):
        text = " \tQuid?  [quia] &lt;cur&gt; †\nAliud—nunc. \n"
        records, report = small(fixture(paragraph(CHAPTER + text)))
        self.assertEqual(records[0]["text"], "Quid?  [quia] <cur> †\nAliud—nunc.")
        self.assertEqual(records[0]["editorialMarks"], [])
        self.assertEqual(report["paragraphs"][0]["leadingWhitespace"], " \t")
        self.assertEqual(report["paragraphs"][0]["trailingWhitespace"], " \n")

    def test_multiple_asterisk_clusters_map_individual_boundaries(self):
        records, _ = small(fixture(paragraph(CHAPTER + "* prima *** altera * * tertia*")))
        record = records[0]
        self.assertEqual(record["phraseBreaks"], [0, 8, 19, 29])
        self.assertEqual([g["text"] for g in record["textGaps"]], ["*", "***", "* *", "*"])

    def test_duplicate_missing_reordered_and_renumbered_sections_are_rejected(self):
        for number in (1, 3):
            with self.subTest(number=number), self.assertRaisesRegex(extract.ExtractionError, "consecutive source identity"):
                small(fixture(paragraph(CHAPTER + "Prima.") + paragraph("Secunda.", number)), units=2)
        with self.assertRaisesRegex(extract.ExtractionError, "Unexpected Niese-unit count"):
            small(fixture(paragraph(CHAPTER + "Prima.")), units=2)

    def test_unknown_or_reinterpreted_source_annotations_are_rejected(self):
        source = fixture(paragraph(CHAPTER + "Prima.")).replace(b'n="1" xml:id=', b'n="1" ana="#inferred-gap" xml:id=')
        with self.assertRaisesRegex(extract.ExtractionError, "consecutive source identity"):
            small(source)
        for old, new in ((b' ana="#niese-boundary-within-preceding-lacuna"', b''),
                         (b'<p n="119"', b'<p n="119" type="empty"')):
            data = (REPOSITORY / "assets/xml/contra-apionem/Latin/book-01.xml").read_bytes().replace(old, new, 1)
            with self.assertRaisesRegex(extract.ExtractionError, "consecutive source identity"):
                extract.extract_document(data, book_number=1)

    def test_lacuna_annotation_requires_the_existing_preceding_marker(self):
        data = (REPOSITORY / "assets/xml/contra-apionem/Latin/book-01.xml").read_bytes()
        root = ET.fromstring(data)
        paragraph_118 = root.find(f"{NS}text/{NS}body/{NS}div1/{NS}p[@n='118']")
        for node in paragraph_118.iter():
            if node.text:
                node.text = node.text.replace("***", "")
            if node.tail:
                node.tail = node.tail.replace("***", "")
        with self.assertRaisesRegex(extract.ExtractionError, "preceding lacuna has no terminal"):
            extract.extract_document(ET.tostring(root), book_number=1)

    def test_unknown_running_markup_and_non_elements_fail_closed(self):
        cases = ('<note>critical note</note>', '<gap/>', '<supplied>word</supplied>', '<del>word</del>',
                 '<unclear/>', '<app><lem>word</lem></app>', '<choice><orig>word</orig></choice>',
                 '<hi>word</hi>', '<!-- running comment -->', '<?unreviewed value?>')
        for markup in cases:
            with self.subTest(markup=markup), self.assertRaises(extract.ExtractionError):
                small(fixture(paragraph(CHAPTER + "Prima " + markup + " postea.")))

    def test_unreviewed_inline_attributes_and_nested_substantive_tags_are_rejected(self):
        for markup in ('<add type="correction">milia</add>', '<q rend="new">dicta</q>',
                       '<foreign xml:lang="eng">words</foreign>', '<add><q>word</q></add>',
                       '<q><foreign xml:lang="grc">λόγος</foreign></q>', '<add/>', '<q> </q>'):
            with self.subTest(markup=markup), self.assertRaises(extract.ExtractionError):
                small(fixture(paragraph(CHAPTER + "Prima " + markup)))

    def test_chapter_milestones_are_not_misread_as_niese_or_allowed_to_drop_text(self):
        for milestone in ('<milestone unit="niese" n="1"/>',
                          '<milestone unit="chapter" subtype="boysen" n="01"/>',
                          '<milestone unit="chapter" subtype="boysen" n="1">lost text</milestone>',
                          '<milestone unit="chapter" subtype="other" n="1"/>'):
            with self.subTest(milestone=milestone), self.assertRaises(extract.ExtractionError):
                small(fixture(paragraph(milestone + "Prima.")))
        with self.assertRaisesRegex(extract.ExtractionError, "reordered Boysen chapter"):
            small(fixture(paragraph(CHAPTER + "Prima." + CHAPTER)))

    def test_page_markers_cannot_hide_text_or_add_unreviewed_attributes(self):
        for markup in ('<pb n="4">word</pb>', '<pb n="4" break="no"/>', '<pb n="0"/>'):
            with self.subTest(markup=markup), self.assertRaises(extract.ExtractionError):
                small(fixture(paragraph(CHAPTER + "Prima " + markup + " postea.")))

    def test_running_text_outside_paragraphs_and_changed_source_notice_are_rejected(self):
        for source in (fixture("Lost words." + paragraph(CHAPTER + "Prima.")),
                       fixture(paragraph(CHAPTER + "Prima.")).replace(b'Book 1.</note>', b'Book 1. New prose.</note>'),
                       fixture(paragraph(CHAPTER + "Prima.")).replace(b'</div1>', b'</div1><note>New prose.</note>')):
            with self.subTest(source=source), self.assertRaises(extract.ExtractionError):
                small(source)

    def test_dtd_entities_language_confusion_and_empty_units_are_rejected(self):
        valid = fixture(paragraph(CHAPTER + "Prima."))
        cases = (b'<!DOCTYPE TEI [<!ENTITY secret "hidden">]>' + valid,
                 valid.replace(b'xml:lang="lat"', b'xml:lang="eng"'),
                 valid.replace(b'latin-apion1"', b'latin-apion2"'),
                 fixture(paragraph(CHAPTER + " *** ")))
        for source in cases:
            with self.subTest(source=source), self.assertRaises(extract.ExtractionError):
                small(source)


if __name__ == "__main__":
    unittest.main()
