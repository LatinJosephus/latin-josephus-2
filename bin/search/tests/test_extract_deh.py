"""Real-corpus coverage and corruption tests for the De excidio adapter."""

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
spec = importlib.util.spec_from_file_location("deh_extract", SEARCH / "extract-deh.py")
extract = importlib.util.module_from_spec(spec)
spec.loader.exec_module(extract)
NS = "{http://www.tei-c.org/ns/1.0}"
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"


def fixture(contents: str, *, extra_chapter: str = "") -> bytes:
    return (f'<TEI xmlns="{extract.TEI}"><teiHeader><p>Not running text.</p></teiHeader><text><body>'
            '<div1 n="II" type="book" subtype="Latin" xml:id="latin-deh2">'
            '<div2 n="1" type="chapter" xml:id="latin-deh2-chapter1">'
            f'<head> LIBER SECVNDVS </head>{contents}</div2>{extra_chapter}'
            '</div1></body></text></TEI>').encode("utf-8")


def paragraph(text: str, number: int = 1, label: str | None = None) -> str:
    return f'<p xml:id="latin-deh2-num{number}"><num>[{label or f"II.1.{number}"}]</num>{text}</p>'


def small(source: bytes, *, units: int = 1, chapters: int = 1):
    return extract.extract_document(source, book_number=2, order_offset=0,
                                    expected_units=units, expected_chapters=chapters, expected_headings=1)


def record_source_projection(record: dict, audit: dict) -> str:
    return "".join(record["text"][s["recordTextStart"]:s["recordTextEnd"]]
                   for s in audit["segments"] if s["kind"] == "source-text")


class DehRealCorpusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.xml = {book: (REPOSITORY / f"assets/xml/deh/Latin/book-{book:02}.xml").read_bytes()
                   for book in range(1, 6)}
        cls.extracted = {book: extract.extract_document(data, book_number=book,
                                                        expected_inline_counts=extract.BOOK_SPECS[book])
                         for book, data in cls.xml.items()}

    def test_all_five_books_and_prologue_have_the_existing_558_units(self):
        expected_counts = [215, 73, 70, 79, 121]
        expected_tokens = [26310, 11011, 12091, 11027, 27033]
        combined = []
        for book, (records, report) in self.extracted.items():
            with self.subTest(book=book):
                self.assertEqual(len(records), expected_counts[book - 1])
                self.assertEqual(report["counts"]["runningWordTokens"], expected_tokens[book - 1])
                self.assertEqual([r["section"] for r in records], list(range(1, len(records) + 1)))
                self.assertEqual(report["source"]["sha256"], hashlib.sha256(self.xml[book]).hexdigest())
                self.assertEqual(report["source"]["bytes"], len(self.xml[book]))
            combined.extend(records)
        self.assertEqual(len(combined), 558)
        self.assertEqual(len({r["id"] for r in combined}), 558)
        self.assertEqual([r["order"] for r in combined], list(range(558)))
        self.assertEqual(sum(report["counts"]["runningWordTokens"] for _, report in self.extracted.values()), 87472)

    def test_citations_and_canonical_reader_links_match_every_source_label(self):
        for book, (records, report) in self.extracted.items():
            root = ET.fromstring(self.xml[book])
            source_paragraphs = root.findall(f"{NS}text/{NS}body//{NS}p")
            self.assertEqual(len(source_paragraphs), len(records))
            for source, record in zip(source_paragraphs, records, strict=True):
                with self.subTest(source=source.get(XML_ID)):
                    self.assertEqual(record["sourceId"], source.get(XML_ID))
                    self.assertEqual(record["citationLabel"], source.findtext(NS + "num")[1:-1])
                    self.assertEqual(record["citationScheme"], "chapter-paragraph")
                    self.assertEqual(record["url"],
                                     f"/deh/?book={book}&chapter={record['chapter']}&unit={record['paragraph']}")
                    self.assertNotIn("niese", record["url"])
                    self.assertEqual(record["readerLink"]["params"],
                                     {"book": book, "chapter": record["chapter"], "unit": record["paragraph"]})
            self.assertEqual(report["coverage"]["rangeMeaning"], "stable XML paragraph ordinal, not Niese")

    def test_every_original_paragraph_is_restored_from_finished_record_slices(self):
        restored_count = 0
        for book, (records, report) in self.extracted.items():
            originals = {p.get(XML_ID): "".join(p.itertext())
                         for p in ET.fromstring(self.xml[book]).findall(f"{NS}text/{NS}body//{NS}p")}
            for record, audit in zip(records, report["paragraphs"], strict=True):
                text = record["text"]
                self.assertEqual("".join(text[s["recordTextStart"]:s["recordTextEnd"]]
                                         for s in audit["segments"]), text)
                projection = record_source_projection(record, audit)
                restored = audit["removedPrefix"] + audit["leadingWhitespace"] + projection + audit["trailingWhitespace"]
                self.assertEqual(restored, originals[record["sourceId"]], record["sourceId"])
                for segment in audit["segments"]:
                    part = text[segment["recordTextStart"]:segment["recordTextEnd"]]
                    self.assertEqual(hashlib.sha256(part.encode()).hexdigest(), segment["textSha256"])
                    if segment["kind"] == "source-text":
                        self.assertEqual(part, restored[segment["sourceTextStart"]:segment["sourceTextEnd"]])
                    else:
                        self.assertEqual(part, "†")
                        self.assertEqual(segment["sourceTextStart"], segment["sourceTextEnd"])
                restored_count += 1
            coverage = report["coverage"]
            for a, b in (("rawParagraphSequenceSha256", "restoredParagraphSequenceSha256"),
                         ("sourceWordSequenceSha256", "indexedWordSequenceSha256"),
                         ("sourceNonWhitespaceContentSha256", "sourceProjectionNonWhitespaceContentSha256")):
                self.assertEqual(coverage[a], coverage[b])
            self.assertEqual(coverage["generatedDisplayGlyphs"], report["counts"]["cruxMarkers"])
        self.assertEqual(restored_count, 558)

    def test_page_breaks_do_not_split_words_and_editorial_readings_remain_identifiable(self):
        by_book = {book: {r["section"]: r for r in records} for book, (records, _) in self.extracted.items()}
        self.assertIn("Romanos in se conuerterint", by_book[1][2]["text"])
        cenedai = by_book[2][61]
        self.assertIn("Cenedaei", cenedai["text"])
        self.assertEqual(cenedai["citationLabel"], "II.14.5")
        supplied = next(mark for mark in cenedai["editorialMarks"] if mark["kind"] == "supplied")
        self.assertEqual(supplied["text"], "ne")
        alexander = by_book[1][128]
        self.assertIn("Alexander", alexander["text"])
        self.assertEqual(alexander["citationLabel"], "I.34.2")
        deleted = next(mark for mark in alexander["editorialMarks"] if mark["kind"] == "del")
        self.assertEqual(deleted["text"], "der")
        for record in (cenedai, alexander):
            utf16 = record["text"].encode("utf-16-le")
            for mark in record["editorialMarks"]:
                self.assertEqual(utf16[mark["start"] * 2:mark["end"] * 2].decode("utf-16-le"), mark["text"])

    def test_all_nine_deletions_nine_supplies_and_three_cruces_are_preserved(self):
        counts = {kind: 0 for kind in ("del", "supplied", "unclear")}
        for records, report in self.extracted.values():
            for record in records:
                for mark in record["editorialMarks"]:
                    counts[mark["kind"]] += 1
                    encoded = record["text"].encode("utf-16-le")
                    self.assertEqual(encoded[mark["start"] * 2:mark["end"] * 2].decode("utf-16-le"), mark["text"])
                    if mark["kind"] == "unclear":
                        self.assertEqual(mark["text"], "†")
                        self.assertEqual(mark["representation"], "generated-dagger")
            self.assertEqual(report["counts"]["generatedCruxGlyphs"], report["counts"]["cruxMarkers"])
        self.assertEqual(counts, {"del": 9, "supplied": 9, "unclear": 3})

    def test_only_prologue_to_narrative_transition_gets_an_internal_phrase_break(self):
        all_records = [record for records, _ in self.extracted.values() for record in records]
        marked = [record for record in all_records if record.get("breakBefore")]
        self.assertEqual([record["citationLabel"] for record in marked], ["I.1.1"])
        self.assertEqual(marked[0]["sourceId"], "latin-deh1-num4")
        self.assertIn("Prologue", marked[0]["breakReason"])
        first_book = self.extracted[1][0]
        self.assertEqual([r["citationLabel"] for r in first_book[:3]], ["Prol.1", "Prol.2", "Prol.3"])
        self.assertTrue(all(r["citation"]["prologue"] for r in first_book[:3]))
        self.assertEqual(first_book[0]["url"], "/deh/?book=1&chapter=0&unit=1")

    def test_only_verified_headings_and_metadata_are_excluded(self):
        headings = []
        for records, report in self.extracted.values():
            headings.extend(item for item in report["excluded"] if item["kind"] == "heading")
            self.assertTrue(any(item["kind"] == "teiHeader" for item in report["excluded"]))
            self.assertFalse(any("[Prol." in record["text"] for record in records))
            self.assertTrue(all(not record["text"].startswith(f"[{record['citationLabel']}]") for record in records))
        self.assertEqual(len(headings), 6)
        self.assertEqual({item["text"].strip() for item in headings},
                         {"PROLOGVS", "LIBER PRIMVS", "LIBER SECVNDVS", "LIBER TERTIVS", "LIBER QVARTVS", "LIBER QVINTVS"})

    def test_build_is_deterministic_and_keeps_all_artifacts_in_deh_destination(self):
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            bellum = parent / "corpus.json"
            bellum.write_bytes(b"accepted Bellum sentinel\n")
            destination = parent / "data" / "deh-latin-ussani"
            report = extract.build_corpus(REPOSITORY, destination)
            first = {path.name: path.read_bytes() for path in destination.iterdir()}
            extract.build_corpus(REPOSITORY, destination)
            self.assertEqual(first, {path.name: path.read_bytes() for path in destination.iterdir()})
            self.assertEqual(len(first), 12)
            self.assertEqual(bellum.read_bytes(), b"accepted Bellum sentinel\n")
            self.assertEqual(report["counts"]["sections"], 558)
            self.assertEqual(report["counts"]["prologueUnits"], 3)
            self.assertEqual(report["counts"]["runningWordTokens"], 87472)
            for book in report["books"]:
                for kind in ("corpus", "extractionReport"):
                    data = (parent / book[kind]["path"]).read_bytes()
                    self.assertEqual(len(data), book[kind]["bytes"])
                    self.assertEqual(hashlib.sha256(data).hexdigest(), book[kind]["sha256"])
            self.assertEqual(hashlib.sha256(first["corpus.json"]).hexdigest(), report["corpus"]["sha256"])
            self.assertEqual(json.loads(first["corpus.json"]),
                             [r for book in range(1, 6) for r in json.loads(first[f"book-{book:02}.corpus.json"])])

    def test_invalid_final_book_cannot_partially_replace_existing_outputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sources = root / "assets/xml/deh/Latin"
            sources.mkdir(parents=True)
            for book, data in self.xml.items():
                (sources / f"book-{book:02}.xml").write_bytes(data)
            final = sources / "book-05.xml"
            final.write_bytes(final.read_bytes().replace(b"[V.53.2]", b"[V.53.9]", 1))
            destination = root / "output"
            destination.mkdir()
            (destination / "corpus.json").write_bytes(b"previous valid output")
            with self.assertRaisesRegex(extract.ExtractionError, "citation label disagrees"):
                extract.build_corpus(root, destination)
            self.assertEqual({p.name: p.read_bytes() for p in destination.iterdir()},
                             {"corpus.json": b"previous valid output"})


class DehExtractionCorruptionTests(unittest.TestCase):
    def test_inline_boundaries_preserve_word_identity_and_utf16_mark_offsets(self):
        source = fixture(paragraph(" 𐐀ve Á<supplied>li</supplied>us: Ro<pb n=\"4\"/>manos "
                                   "Alexan<del>der</del>!<lb/> "))
        records, report = small(source)
        record = records[0]
        self.assertEqual(record["text"], "𐐀ve Álius: Romanos Alexander!")
        self.assertEqual(record["editorialMarks"][0], {"kind": "supplied", "start": 7, "end": 9, "text": "li"})
        self.assertEqual(report["counts"]["runningWordTokens"], 4)
        self.assertEqual(report["counts"]["pageBreaks"], 1)
        self.assertEqual(report["counts"]["divisionEndMarkers"], 1)

    def test_literal_dagger_survives_source_projection_alongside_generated_crux(self):
        source = fixture(paragraph("Prima † nota; altera <unclear/> causa."))
        records, report = small(source)
        self.assertEqual(records[0]["text"], "Prima † nota; altera † causa.")
        audit = report["paragraphs"][0]
        self.assertEqual(record_source_projection(records[0], audit), "Prima † nota; altera  causa.")
        self.assertEqual(report["coverage"]["generatedDisplayGlyphs"], 1)
        self.assertNotEqual(report["coverage"]["displayNonWhitespaceContentSha256"],
                            report["coverage"]["sourceNonWhitespaceContentSha256"])

    def test_internal_whitespace_and_punctuation_are_not_normalized(self):
        text = " \tQuid?  vere: ita!\n Alterum—nunc. \n"
        records, report = small(fixture(paragraph(text)))
        self.assertEqual(records[0]["text"], "Quid?  vere: ita!\n Alterum—nunc.")
        self.assertEqual(report["paragraphs"][0]["leadingWhitespace"], " \t")
        self.assertEqual(report["paragraphs"][0]["trailingWhitespace"], " \n")

    def test_duplicate_missing_or_reordered_stable_ids_are_rejected(self):
        for number in (1, 3):
            with self.subTest(number=number), self.assertRaisesRegex(extract.ExtractionError, "consecutive stable paragraph ID"):
                small(fixture(paragraph("Prima.") + paragraph("Secunda.", number, "II.1.2")), units=2)
        with self.assertRaisesRegex(extract.ExtractionError, "Unexpected citation-unit count"):
            small(fixture(paragraph("Prima.")), units=2)

    def test_wrong_citation_chapter_paragraph_or_prologue_label_is_rejected(self):
        for label in ("I.1.1", "II.2.1", "II.1.2", "Prol.1", "2.1.1", "II.01.1"):
            with self.subTest(label=label), self.assertRaisesRegex(extract.ExtractionError, "citation label disagrees"):
                small(fixture(paragraph("Prima.", label=label)))

    def test_num_must_be_first_and_unambiguous(self):
        sources = [
            '<p xml:id="latin-deh2-num1">Prima.</p>',
            '<p xml:id="latin-deh2-num1">Do not drop me.<num>[II.1.1]</num>Prima.</p>',
            '<p xml:id="latin-deh2-num1"><num>[II.1.1]</num><num>[II.1.1]</num>Prima.</p>',
            '<p xml:id="latin-deh2-num1"><num type="other">[II.1.1]</num>Prima.</p>',
        ]
        for contents in sources:
            with self.subTest(contents=contents), self.assertRaises(extract.ExtractionError):
                small(fixture(contents))

    def test_unknown_body_markup_cannot_silently_drop_or_index_apparatus(self):
        for tag in ("note", "gap", "app", "choice", "foreign", "hi", "sic", "corr"):
            with self.subTest(tag=tag), self.assertRaisesRegex(extract.ExtractionError, "unexpected substantive tag"):
                small(fixture(paragraph(f"Prima <{tag}>do not guess</{tag}> secunda.")))
        for extra in ("lost words", "<!-- substantive annotation -->", "<?processing instruction?>"):
            with self.subTest(extra=extra), self.assertRaises(extract.ExtractionError):
                small(fixture(paragraph("Prima.") + extra))

    def test_nonempty_or_extended_marker_semantics_require_review(self):
        for marker in ('<pb n="4">lost</pb>', '<pb n="4" break="no"/>', '<lb>lost</lb>',
                       '<unclear>dubium</unclear>', '<unclear reason="lacuna"/>', '<del rend="erase">verba</del>'):
            with self.subTest(marker=marker), self.assertRaises(extract.ExtractionError):
                small(fixture(paragraph(f"Prima {marker} secunda.")))
        with self.assertRaisesRegex(extract.ExtractionError, "changed or divided a word"):
            small(fixture(paragraph("Ro<unclear/>manos.")))

    def test_unknown_or_relocated_heading_is_rejected(self):
        original = fixture(paragraph("Prima."))
        with self.assertRaisesRegex(extract.ExtractionError, "Unrecognised heading"):
            small(original.replace(b"LIBER SECVNDVS", b"Unknown potentially substantive text"))
        with self.assertRaisesRegex(extract.ExtractionError, "Heading interrupts"):
            small(fixture(paragraph("Prima.") + "<head>LIBER SECVNDVS</head>"))

    def test_wrong_book_and_chapter_identity_are_rejected(self):
        source = fixture(paragraph("Prima."))
        for before, after in ((b'n="II"', b'n="III"'), (b'latin-deh2-chapter1', b'latin-deh2-chapter9'),
                              (b'n="1" type="chapter"', b'n="2" type="chapter"')):
            with self.subTest(before=before), self.assertRaises(extract.ExtractionError):
                small(source.replace(before, after, 1))
        duplicate = '<div2 n="1" type="chapter" xml:id="latin-deh2-chapter1">' + paragraph("Secunda.", 2) + '</div2>'
        with self.assertRaisesRegex(extract.ExtractionError, "Duplicate, missing, or reordered chapter"):
            small(fixture(paragraph("Prima."), extra_chapter=duplicate), units=2, chapters=2)

    def test_empty_units_and_unapproved_xml_entities_are_rejected(self):
        with self.assertRaisesRegex(extract.ExtractionError, "empty citation unit"):
            small(fixture(paragraph(" \n ")))
        with self.assertRaisesRegex(extract.ExtractionError, "DTD/entity"):
            small(b'<!DOCTYPE TEI [<!ENTITY injected "hello">]>' + fixture(paragraph("Prima.")))
        with self.assertRaisesRegex(extract.ExtractionError, "not well formed"):
            small(fixture(paragraph("Prima."))[:-5])


if __name__ == "__main__":
    unittest.main()
