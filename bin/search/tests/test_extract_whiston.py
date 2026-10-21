"""Whiston source preservation, explicit boundaries and refusal tests."""

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
spec = importlib.util.spec_from_file_location("whiston_extract", SEARCH / "extract-whiston.py")
extract = importlib.util.module_from_spec(spec)
spec.loader.exec_module(extract)
NS = "{http://www.tei-c.org/ns/1.0}"
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"
ORDER_STARTS = {"preface": 0, "book-01": 26, "book-02": 346, "book-03": 695,
                "book-04": 1017, "book-05": 1348, "book-06": 1710, "book-07": 2088,
                "book-08": 2482, "book-09": 2902, "book-10": 3193, "book-11": 0}
PRIOR_ARTIFACT_HASHES = {
    "book-01.corpus.json": "5d94451f1363230e0578d995ece458dd8a4b40e56064487f1362194de21404f0",
    "book-01.extraction-report.json": "5ff96ccfd1a08a6abdc3a37e6e832db53db7d9f9a7e12c6eb02bfee6130e53a9",
    "book-02.corpus.json": "7000e802415b3246a14e3fb9fc0c5e40490fb8fa31351c228aaf31353b7b663f",
    "book-02.extraction-report.json": "3eab5244d80df012cfc7c5dec46a78be90ba3b805c759c009954eed8cb18f6ab",
    "book-03.corpus.json": "26e09b435952e06b7911a4d985b44ede81bdc291ea10d18a8218f79f340fd36b",
    "book-03.extraction-report.json": "67acd98bdc96a4e357fdfac47276f375f021c5e917f2b42e5c08d151213afa6c",
    "book-04.corpus.json": "108edd83587cf34f2a901a74ba92bd7821f0b64a7555b505a9f7f855b42d1d78",
    "book-04.extraction-report.json": "e771f5e133a471447489a16f08b1d2fedab03356f6543143e9858ee637dae500",
    "book-05.corpus.json": "fb309ee22dc2f98b65d189679657219fc808b00e64fa5737ecb8e7044e876a80",
    "book-05.extraction-report.json": "d59fe5d530f2a5ea401957dc2d1bcdf542670711b98c9d2c2b19b20e670d7d6a",
}


def utf16_slice(text: str, start: int, end: int) -> str:
    return text.encode("utf-16-le")[start * 2:end * 2].decode("utf-16-le")


def fixture(contents: str) -> bytes:
    return (f'<TEI xmlns="{extract.TEI}"><teiHeader><p>Unindexed metadata.</p></teiHeader>'
            '<text><body><note>William Whiston (1737)</note><div1><div2>'
            f'{contents}</div2></div1></body></text></TEI>').encode("utf-8")


def paragraph(contents: str, source_id: str = "english-book01-test") -> str:
    return f'<p xml:id="{source_id}">{contents}</p>'


def small(contents: str, expected: list[int] | None = None):
    return extract.extract_document(fixture(contents), verify_source=False,
                                    expected_sections=[27] if expected is None else expected)


class WhistonAcceptedSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = {name: (REPOSITORY / f"assets/xml/antiquities/English/{name}.xml").read_bytes()
                       for name in ORDER_STARTS}
        cls.documents = {name: extract.extract_document(data, book_number=1 if name == "preface" else int(name[-2:]),
                                                       preface=name == "preface", order_offset=ORDER_STARTS[name])
                         for name, data in cls.sources.items()}
        cls.pilot = cls.documents["preface"][0] + cls.documents["book-01"][0]
        cls.collection = cls.pilot + [record for book in range(2, 11) for record in cls.documents[f"book-{book:02}"][0]]

    def test_reviewed_pilot_has_346_intervals_and_21994_tokens(self):
        self.assertEqual([r["section"] for r in self.pilot], list(range(1, 347)))
        self.assertEqual([r["order"] for r in self.pilot], list(range(346)))
        self.assertEqual(len({r["id"] for r in self.pilot}), 346)
        self.assertEqual(sum(len(extract.words(r["text"])) for r in self.pilot), 21994)
        for name, expected in {"preface": (26, 1646), "book-01": (320, 20348),
                               "book-02": (349, 23020), "book-03": (322, 20955),
                               "book-04": (331, 22900), "book-05": (362, 23396),
                               "book-06": (378, 28422), "book-07": (394, 28285),
                               "book-08": (420, 29968), "book-09": (291, 19074),
                               "book-10": (281, 18035), "book-11": (347, 20213)}.items():
            records, report = self.documents[name]
            self.assertEqual((len(records), report["counts"]["runningWordTokens"]), expected)
            self.assertEqual(report["source"]["sha256"], hashlib.sha256(self.sources[name]).hexdigest())

    def test_expanded_collection_has_3474_intervals_and_236049_tokens(self):
        self.assertEqual(len(self.collection), 3474)
        self.assertEqual(len({r["id"] for r in self.collection}), 3474)
        self.assertEqual([r["order"] for r in self.collection], list(range(3474)))
        self.assertEqual(sum(len(extract.words(r["text"])) for r in self.collection), 236049)
        for book, last in [(2, 349), (3, 322), (4, 331), (5, 362), (6, 378), (7, 394), (8, 420), (9, 291), (10, 281)]:
            records = self.documents[f"book-{book:02}"][0]
            self.assertEqual([r["section"] for r in records], list(range(1, last + 1)))
            for record in records:
                self.assertEqual(record["id"], f"antiquities-english-whiston-{book}-{record['section']}")
                self.assertEqual(record["readerLink"]["params"], {"book": book, "niese": record["section"], "english": "whiston"})
                self.assertNotIn("division", record)
                self.assertNotIn("breakBefore", record)
                self.assertTrue(record["text"])
                self.assertEqual(record["textGaps"], [])
                self.assertEqual(record["phraseBreaks"], [])

    def test_proem_reader_edition_and_narrative_boundary(self):
        self.assertEqual([r["section"] for r in self.pilot if r.get("breakBefore")], [27])
        for record in self.pilot:
            proem = record["section"] <= 26
            book = "preface" if proem else 1
            self.assertEqual(record["language"], "English")
            self.assertEqual(record["edition"], "Whiston")
            self.assertEqual(record["readerLink"], {"path": "antiquities/", "params":
                             {"book": book, "niese": record["section"], "english": "whiston"}})
            self.assertEqual(record["url"], f"/antiquities/?book={book}&niese={record['section']}&english=whiston")
            self.assertEqual(record.get("sourceDivision"), "proem" if proem else None)
            self.assertEqual(record.get("division"), "proem" if proem else None)
            self.assertEqual(record["citation"].get("proem", False), proem)
        self.assertTrue(self.pilot[26]["text"].startswith("In the beginning God created the heaven and the earth."))

    def test_every_record_and_exclusion_restores_actual_xml_paragraphs(self):
        for name, (records, report) in self.documents.items():
            by_id = {r["id"]: r for r in records}
            root = ET.fromstring(self.sources[name])
            originals = {p.get(XML_ID): "".join(p.itertext()) for p in root.findall(f".//{NS}body//{NS}p")
                         if p.findall(f".//{NS}milestone[@unit='niese']") or p.get(XML_ID) == "english-book04-num276b"}
            self.assertEqual(len(originals), len(report["paragraphs"]))
            for paragraph in report["paragraphs"]:
                original = originals[paragraph["sourceId"]]
                cursor, restored = 0, ""
                for piece in paragraph["sourcePieces"]:
                    self.assertEqual(piece["sourceStart"], cursor)
                    part = (utf16_slice(by_id[piece["recordId"]]["text"], piece["recordStart"], piece["recordEnd"])
                            if piece["kind"] == "record" else piece["text"])
                    self.assertEqual(part, utf16_slice(original, piece["sourceStart"], piece["sourceEnd"]))
                    self.assertEqual(hashlib.sha256(part.encode()).hexdigest(), piece["textSHA256"])
                    restored += part
                    cursor = piece["sourceEnd"]
                self.assertEqual(restored, original)
                self.assertEqual(cursor, len(original.encode("utf-16-le")) // 2)

    def test_iv_276_retains_its_markerless_paragraph_and_audited_separator(self):
        records, report = self.documents["book-04"]
        record = records[275]
        first = ("It is also a duty to show the roads to those who do not know them, and not to esteem it a matter "
                 "for sport, when we hinder others' advantages, by setting them in a wrong way.")
        second = "In like manner, let no one revile a person blind or dumb."
        self.assertEqual(record["text"], first + "\n\n" + second)
        self.assertEqual(record["sourceIds"], ["english-book04-num276", "english-book04-num276b"])
        self.assertEqual(record["sourceId"], "english-book04-num276")
        self.assertEqual(report["counts"]["continuationParagraphs"], 1)
        continuation = next(p for p in report["paragraphs"] if p["sourceId"] == "english-book04-num276b")
        self.assertEqual(continuation["nieseMarkers"], [])
        self.assertEqual(continuation["recordJoin"], {"kind": "paragraph-separator", "recordId": record["id"],
                         "start": len(first), "end": len(first) + 2, "text": "\n\n"})
        self.assertEqual(continuation["sections"][0]["recordOffset"], len(first) + 2)
        self.assertEqual("".join(utf16_slice(record["text"], p["recordStart"], p["recordEnd"])
                                 for p in continuation["sourcePieces"] if p["kind"] == "record"), second)
        self.assertNotIn("32.", record["text"])

    def test_v_contents_and_repeated_chapter_headings_are_both_excluded(self):
        records, report = self.documents["book-05"]
        headings = [block["text"] for block in report["excludedBlocks"] if block["kind"] == "heading"]
        self.assertEqual(len(headings), 23)
        self.assertEqual(headings[1:12], headings[12:23])
        self.assertEqual(report["counts"]["narrativeParagraphs"], 98)
        self.assertNotIn("Concerning The Fortitude Of Samson", " ".join(r["text"] for r in records))

    def test_viii_255_retains_all_42_prefix_words_with_exact_original_spans(self):
        records, report = self.documents["book-08"]
        record = records[254]
        first = ("Now therefore when he fell upon the country of the Hebrews, he took the strongest cities of Rehoboam's "
                 "kingdom without fighting; and when he had put garrisons in them, he came last of all to Jerusalem.")
        second = ("Now when Rehoboam, and the multitude with him, were shut up in Jerusalem by the means of the army "
                  "of Shishak, and when they besought God to give them victory and deliverance, they could not persuade "
                  "God to be on their side.")
        self.assertEqual(len(extract.words(second)), 42)
        self.assertEqual(record["text"], first + "\n\n" + second)
        self.assertEqual(record["sourceIds"], ["english-book08-num251", "english-book08-num255"])
        self.assertEqual(record["sourceId"], "english-book08-num251")
        self.assertEqual(report["counts"]["continuationParagraphs"], 1)
        continuation = next(p for p in report["paragraphs"] if p["sourceId"] == "english-book08-num255")
        self.assertEqual([m["section"] for m in continuation["nieseMarkers"]], list(range(256, 263)))
        self.assertEqual([s["section"] for s in continuation["sections"]], list(range(255, 263)))
        self.assertEqual(continuation["recordJoin"], {"kind": "paragraph-separator", "recordId": record["id"],
                         "start": 201, "end": 203, "text": "\n\n"})
        self.assertEqual(continuation["continuationOf"], {"recordId": record["id"], "section": 255,
                         "previousSourceId": "english-book08-num251", "nextSourceId": "english-book08-num263",
                         "firstMilestone": 256, "nextSection": 263})
        self.assertEqual(continuation["sections"][0]["recordOffset"], 203)
        self.assertTrue(all("recordOffset" not in section for section in continuation["sections"][1:]))
        pieces = [p for p in continuation["sourcePieces"] if p.get("recordId") == record["id"]]
        self.assertEqual([(p["sourceStart"], p["sourceEnd"], p["recordStart"], p["recordEnd"]) for p in pieces],
                         [(3, 226, 203, 426)])
        self.assertEqual(utf16_slice(record["text"], 203, 426), second)
        self.assertTrue(records[255]["text"].startswith("But Shemaiah the prophet told them"))

    def test_viii_letter_salutation_and_x_bold_words_remain_narrative(self):
        letter, report = self.documents["book-08"]
        self.assertIn("Hiram To King Solomon", letter[52]["text"])
        self.assertEqual(report["counts"]["structuralMarkers"], 2)
        records = self.documents["book-10"][0]
        for section, words in [(184, ["Samaritans"]), (243, ["Number"]), (244, ["weight", "fragment"])]:
            record = records[section - 1]
            for word in words:
                self.assertIn(word, record["text"])
            self.assertEqual(record["editorialMarks"], [])
            self.assertEqual(record["sourceMarkup"], [])
            self.assertEqual(record["phraseBreaks"], [])

    def test_english_iii_240_does_not_inherit_the_latin_omission(self):
        record = self.documents["book-03"][0][239]
        self.assertEqual(record["section"], 240)
        self.assertTrue(record["text"])
        self.assertEqual(record["textGaps"], [])
        self.assertEqual(record["phraseBreaks"], [])

    def test_only_punctuation_before_accepted_first_marker_is_excluded(self):
        records, report = self.documents["preface"]
        paragraph = next(p for p in report["paragraphs"] if p["sourceId"] == "english-preface-num5")
        prefix = [p for p in paragraph["sourcePieces"] if p.get("reason") == "pre-marker-label-punctuation"]
        self.assertEqual([(p["text"], p["sourceStart"], p["sourceEnd"]) for p in prefix], [(" . ", 6, 9)])
        self.assertTrue(records[4]["text"].startswith("Now I have undertaken the present work"))
        punctuated, _ = small('<p xml:id="test"><num>[1.1.]</num> . '
                             '<milestone unit="niese" n="27"/>. First; second—third! </p>')
        self.assertEqual(punctuated[0]["text"], ". First; second—third!")

    def test_ix_footnotes_are_excluded_and_narrative_adjacency_survives(self):
        records, report = self.documents["book-09"]
        text = " ".join(r["text"] for r in records)
        notes = [p for paragraph in report["paragraphs"] for p in paragraph["sourcePieces"]
                 if p.get("reason") == "whiston-footnote"]
        self.assertEqual(len(notes), 7)
        self.assertNotIn("Dr. Hudson", text)
        self.assertNotIn("What M. Le Clerc pretends", text)
        self.assertNotIn("CONCERNING THE WICKEDNESS", text)
        self.assertIn("Elisha also sent a hasty message to Joram, and exhorted him", text)
        self.assertIn("Joram, who was the son of a murderer, had sent one", text)
        self.assertIn("an epistle from Elijah the prophet, which declared", text)
        self.assertEqual([r["section"] for r in records if 51 <= r["section"] <= 109], list(range(51, 110)))
        self.assertTrue(all(not r.get("breakBefore") and not r["phraseBreaks"] for r in records))

    def test_xi_records_preserve_physical_order_at_three_non_numeric_seams(self):
        records, report = self.documents["book-11"]
        expected = list(range(1, 312)) + list(range(326, 343)) + list(range(312, 326)) + list(range(343, 348))
        self.assertEqual([r["section"] for r in records], expected)
        self.assertEqual([r["order"] for r in records], list(range(347)))
        self.assertEqual(records[310]["section"], 311)
        self.assertTrue(records[311]["text"].startswith("and Jaddua the high priest"))
        self.assertEqual(records[327]["section"], 342)
        self.assertTrue(records[328]["text"].startswith("But there was now a great disturbance"))
        self.assertEqual(records[341]["section"], 325)
        self.assertTrue(records[342]["text"].startswith("to whom he promised"))
        self.assertEqual(report["coverage"]["sourceWordSequenceSha256"], report["coverage"]["indexedWordSequenceSha256"])

    def test_source_changes_fail_but_crlf_only_representation_is_accepted(self):
        for book in range(1, 11):
            name = f"book-{book:02}"
            original = self.sources[name]
            with self.subTest(book=book), self.assertRaisesRegex(extract.ExtractionError, "accepted source"):
                extract.extract_document(original + b"\n<!-- Unreviewed source change -->", book_number=book)
            crlf_records, _ = extract.extract_document(original.replace(b"\n", b"\r\n"), book_number=book,
                                                       order_offset=ORDER_STARTS[name])
            self.assertEqual(crlf_records, self.documents[name][0])

    def test_build_is_reproducible_preserves_books_i_v_and_publishes_only_eleven_sources(self):
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            report = extract.build_corpus(REPOSITORY, Path(first))
            extract.build_corpus(REPOSITORY, Path(second))
            self.assertEqual(report["scope"]["books"], list(range(1, 11)))
            self.assertNotIn("pilot", report["scope"])
            self.assertEqual(report["counts"]["sourceDocuments"], 11)
            self.assertEqual(report["counts"]["runningWordTokens"], 236049)
            self.assertEqual({s["path"] for book in report["books"] for s in book["sources"]},
                             {f"assets/xml/antiquities/English/{name}.xml" for name in ["preface"] + [f"book-{b:02}" for b in range(1, 11)]})
            self.assertEqual(sorted(p.name for p in Path(first).iterdir()),
                             [name for b in range(1, 11) for name in [f"book-{b:02}.corpus.json", f"book-{b:02}.extraction-report.json"]]
                             + ["corpus.json", "extraction-report.json"])
            for file in Path(first).iterdir():
                self.assertEqual(file.read_bytes(), (Path(second) / file.name).read_bytes())
            self.assertEqual(json.loads((Path(first) / "corpus.json").read_text()), self.collection)
            for name, expected in PRIOR_ARTIFACT_HASHES.items():
                self.assertEqual(hashlib.sha256((Path(first) / name).read_bytes()).hexdigest(), expected)

    def test_iv_continuation_cannot_be_removed_reassigned_or_given_a_fake_milestone(self):
        for mode in ["remove", "rename", "move", "milestone"]:
            root = ET.fromstring(self.sources["book-04"])
            continuation = root.find(f".//{NS}p[@xml:id='english-book04-num276b']", {"xml": "http://www.w3.org/XML/1998/namespace"})
            parent = next(p for p in root.iter() if continuation in list(p))
            if mode == "remove":
                parent.remove(continuation)
            elif mode == "rename":
                continuation.set(XML_ID, "english-book04-unreviewed")
            elif mode == "move":
                index = list(parent).index(continuation)
                parent.remove(continuation)
                parent.insert(index + 1, continuation)
            else:
                continuation.insert(0, ET.Element(NS + "milestone", {"unit": "niese", "n": "276"}))
            with self.subTest(mode=mode), self.assertRaises(extract.ExtractionError):
                extract.extract_document(ET.tostring(root), book_number=4, verify_source=False)

    def test_viii_prefix_continuation_cannot_be_removed_reassigned_or_given_a_fake_milestone(self):
        for mode in ["remove_prefix", "rename", "move", "milestone"]:
            root = ET.fromstring(self.sources["book-08"])
            continuation = root.find(f".//{NS}p[@xml:id='english-book08-num255']", {"xml": "http://www.w3.org/XML/1998/namespace"})
            parent = next(p for p in root.iter() if continuation in list(p))
            if mode == "remove_prefix":
                continuation.find(NS + "num").tail = ""
            elif mode == "rename":
                continuation.set(XML_ID, "english-book08-unreviewed")
            elif mode == "move":
                index = list(parent).index(continuation)
                parent.remove(continuation)
                parent.insert(index + 1, continuation)
            else:
                continuation.insert(0, ET.Element(NS + "milestone", {"unit": "niese", "n": "255"}))
            with self.subTest(mode=mode), self.assertRaises(extract.ExtractionError):
                extract.extract_document(ET.tostring(root), book_number=8, verify_source=False)


class WhistonBoundaryAndRefusalTests(unittest.TestCase):
    def test_partial_paragraph_continuation_uses_utf16_and_resets_later_record_offsets(self):
        source = fixture(paragraph('<milestone unit="niese" n="255"/>😀 First.', "english-book08-num251") +
                         paragraph('<num>3.</num> 😀 Continued. <milestone unit="niese" n="256"/>Next section.',
                                   "english-book08-num255") +
                         paragraph('<milestone unit="niese" n="263"/>Third.', "english-book08-num263"))
        records, report = extract.extract_document(source, book_number=8, verify_source=False, expected_sections=[255, 256, 263])
        self.assertEqual(records[0]["text"], "😀 First.\n\n😀 Continued.")
        self.assertEqual(records[1]["text"], "Next section.")
        continuation = report["paragraphs"][1]
        self.assertEqual((continuation["recordJoin"]["start"], continuation["recordJoin"]["end"]), (9, 11))
        pieces = [piece for piece in continuation["sourcePieces"] if piece["kind"] == "record"]
        self.assertEqual([(p["recordStart"], p["recordEnd"]) for p in pieces], [(11, 24), (0, 13)])
        self.assertNotIn("recordOffset", continuation["sections"][1])
        self.assertEqual([m["section"] for m in continuation["nieseMarkers"]], [256])

    def test_continuation_record_offsets_count_utf16_code_units(self):
        source = fixture(paragraph('<milestone unit="niese" n="276"/>😀 First.', "english-book04-num276") +
                         paragraph('<num>32.</num> Second.', "english-book04-num276b") +
                         paragraph('<milestone unit="niese" n="277"/>Third.', "english-book04-num277"))
        records, report = extract.extract_document(source, book_number=4, verify_source=False, expected_sections=[276, 277])
        self.assertEqual(records[0]["text"], "😀 First.\n\nSecond.")
        continuation = report["paragraphs"][1]
        self.assertEqual((continuation["recordJoin"]["start"], continuation["recordJoin"]["end"]), (9, 11))
        piece = next(piece for piece in continuation["sourcePieces"] if piece["kind"] == "record")
        self.assertEqual((piece["recordStart"], piece["recordEnd"]), (11, 18))
        self.assertEqual(utf16_slice(records[0]["text"], piece["recordStart"], piece["recordEnd"]), "Second.")

    def test_inline_content_and_utf16_source_offsets_preserve_original_characters(self):
        records, report = small(paragraph('<num>[I.i.27]</num> <milestone unit="niese" n="27"/>'
                                         '😀 A<hi>br</hi>aham <note type="whiston-footnote">excluded π</note>'
                                         'and <emph>Isaac</emph><lb/>.'))
        self.assertEqual(records[0]["text"], "😀 Abraham and Isaac.")
        pieces = report["paragraphs"][0]["sourcePieces"]
        selected = [p for p in pieces if p["kind"] == "record"]
        self.assertEqual(selected[0]["recordStart"], 0)
        self.assertEqual(selected[0]["recordEnd"], 4)
        self.assertEqual("".join(utf16_slice(records[0]["text"], p["recordStart"], p["recordEnd"]) for p in selected),
                         "😀 Abraham and Isaac.")

    def test_unknown_or_unclassified_structure_is_refused(self):
        samples = [
            paragraph('<milestone unit="niese" n="27"/>Known <unclear>word</unclear>.'),
            paragraph('Unassigned words <milestone unit="niese" n="27"/>Known.'),
            paragraph('<milestone unit="niese" n="27"/>Known <lb>hidden words</lb>.'),
            paragraph('<milestone unit="niese" n="27"/>Known <note>unreviewed note</note>.'),
            '<head>Unclassified hidden words</head>' + paragraph('<milestone unit="niese" n="27"/>Known.'),
            '<milestone unit="niese" n="1"/>' + paragraph('<milestone unit="niese" n="27"/>Known.'),
            '<p>Unmarked narrative.</p>' + paragraph('<milestone unit="niese" n="27"/>Known.'),
            paragraph('<milestone unit="niese" n="27"/>Known.') + '<p xml:id="unassigned">More narrative.</p>',
        ]
        for source in samples:
            with self.subTest(source=source), self.assertRaises(extract.ExtractionError):
                small(source)

    def test_empty_duplicate_reordered_and_mid_word_boundaries_are_refused(self):
        samples = [
            '<milestone unit="niese" n="27"/><milestone unit="niese" n="28"/>Second.',
            '<milestone unit="niese" n="27"/>First. <milestone unit="niese" n="27"/>Second.',
            '<milestone unit="niese" n="28"/>First. <milestone unit="niese" n="27"/>Second.',
            '<milestone unit="niese" n="27"/>Abra<milestone unit="niese" n="28"/>ham.',
        ]
        for source in samples:
            with self.subTest(source=source), self.assertRaises(extract.ExtractionError):
                small(paragraph(source), [27, 28])

    def test_duplicate_source_ids_are_refused(self):
        with self.assertRaisesRegex(extract.ExtractionError, "Duplicate.*source ID"):
            small(paragraph('<milestone unit="niese" n="27"/>First.') +
                  paragraph('<milestone unit="niese" n="28"/>Second.'), [27, 28])


if __name__ == "__main__":
    unittest.main()
