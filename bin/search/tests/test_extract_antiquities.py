"""Citation, source preservation and refusal tests for Antiquities I–V."""

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
spec = importlib.util.spec_from_file_location("antiquities_extract", SEARCH / "extract-antiquities.py")
extract = importlib.util.module_from_spec(spec)
spec.loader.exec_module(extract)
NS = "{http://www.tei-c.org/ns/1.0}"
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"


def utf16_slice(text: str, start: int, end: int) -> str:
    return text.encode("utf-16-le")[start * 2:end * 2].decode("utf-16-le")


def paragraph(text: str, section: int = 27) -> str:
    return f'<p xml:id="latin-book01-num{section}"><num>[I.i.{section}]</num>{text}</p>'


def fixture(contents: str) -> bytes:
    return (f'<TEI xmlns="{extract.TEI}"><teiHeader><p>Metadata outside the Latin text.</p></teiHeader>'
            '<text xml:id="book-01-text"><body><note>Bamberg Msc. Class. 78</note>'
            '<div1 n="I" type="book" subtype="Latin" xml:id="latin-book01">'
            '<div2 n="1" type="chapter" xml:id="latin-book01-chapter1">'
            f'{contents}</div2></div1></body></text></TEI>').encode("utf-8")


def small(source: bytes, last: int = 27):
    return extract.extract_document(source, book_number=1, order_offset=0, expected_range=[27, last])


class AntiquitiesRealSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = {key: (REPOSITORY / f"assets/xml/antiquities/Latin/{key}.xml").read_bytes()
                       for key in ["preface"] + [f"book-{n:02}" for n in range(1, 6)]}
        cls.documents = {key: extract.extract_document(data, book_number=1 if key == "preface" else int(key[-2:]),
                                                       preface=key == "preface",
                                                       expected_counts=extract.PREFACE_SPEC if key == "preface"
                                                       else extract.BOOK_SPECS[int(key[-2:])])
                         for key, data in cls.sources.items()}
        cls.records = [r for records, _ in cls.documents.values() for r in records]
        cls.by_citation = {r["citationLabel"]: r for r in cls.records}

    def test_full_tranche_has_1710_citations_and_67657_original_word_tokens(self):
        self.assertEqual(len(self.records), 1710)
        self.assertEqual(len({r["id"] for r in self.records}), 1710)
        self.assertEqual([r["order"] for r in self.records], list(range(1710)))
        self.assertEqual(sum(len(extract.words(r["text"])) for r in self.records), 67657)
        expected = {"preface": (26, 986), "book-01": (320, 13223), "book-02": (349, 13570),
                    "book-03": (322, 12793), "book-04": (331, 13180), "book-05": (362, 13905)}
        for key, (units, tokens) in expected.items():
            records, report = self.documents[key]
            self.assertEqual(len(records), units)
            self.assertEqual(report["counts"]["runningWordTokens"], tokens)
            self.assertEqual(report["source"]["sha256"], hashlib.sha256(self.sources[key]).hexdigest())

    def test_proem_has_its_own_reader_route_and_a_boundary_before_the_narrative(self):
        proem, _ = self.documents["preface"]
        self.assertEqual([r["section"] for r in proem], list(range(1, 27)))
        for record in proem:
            self.assertEqual(record["book"], 1)
            self.assertEqual(record["division"], "proem")
            self.assertTrue(record["citation"]["proem"])
            self.assertEqual(record["readerLink"], {"path": "antiquities/", "params": {"book": "preface", "niese": record["section"]}})
            self.assertEqual(record["url"], f"/antiquities/?book=preface&niese={record['section']}")
            self.assertNotIn("chapter", record)
        narrative = self.by_citation["I.27"]
        self.assertTrue(narrative["breakBefore"])
        self.assertNotIn("division", narrative)
        self.assertEqual(narrative["url"], "/antiquities/?book=1&niese=27")
        self.assertTrue(narrative["text"].startswith("In principio creauit deus"))

    def test_all_finished_record_slices_restore_every_source_paragraph_exactly(self):
        for key, (records, report) in self.documents.items():
            by_section = {r["section"]: r for r in records}
            root = ET.fromstring(self.sources[key])
            originals = {p.get(XML_ID): "".join(p.itertext()) for p in root.findall(f".//{NS}body//{NS}p") if p.get(XML_ID)}
            self.assertEqual(len(originals), len(report["paragraphs"]))
            for paragraph in report["paragraphs"]:
                source = originals[paragraph["sourceId"]]
                cursor, restored = 0, ""
                for segment in paragraph["segments"]:
                    self.assertEqual(segment["sourceTextStart"], cursor)
                    if segment["kind"] == "source-text":
                        part = by_section[segment["section"]]["text"][segment["recordTextStart"]:segment["recordTextEnd"]]
                        self.assertEqual(hashlib.sha256(part.encode()).hexdigest(), segment["textSha256"])
                    else:
                        self.assertIn(segment["kind"], ("excluded-note", "excluded-label", "trimmed-edge-whitespace"))
                        part = segment["text"]
                    self.assertEqual(part, source[segment["sourceTextStart"]:segment["sourceTextEnd"]])
                    restored += part
                    cursor = segment["sourceTextEnd"]
                self.assertEqual(restored, source)
                self.assertEqual(cursor, len(source))
                self.assertEqual(hashlib.sha256(source.encode()).hexdigest(), paragraph["rawTextSha256"])
            for first, second in (("rawParagraphSequenceSha256", "restoredParagraphSequenceSha256"),
                                  ("sourceWordSequenceSha256", "indexedWordSequenceSha256"),
                                  ("sourceNonWhitespaceContentSha256", "displayNonWhitespaceContentSha256")):
                self.assertEqual(report["coverage"][first], report["coverage"][second])

    def test_six_continuation_labels_do_not_create_false_niese_starts(self):
        expected = {"II.95": "latin-book02-num95", "III.178": "latin-book03-num179",
                    "IV.106": "latin-book04-num107", "IV.155": "latin-book04-num156",
                    "IV.276": "latin-book04-num276b", "V.32": "latin-book05-num33"}
        for citation, continuation_id in expected.items():
            record = self.by_citation[citation]
            self.assertIn(continuation_id, record["sourceIds"])
            self.assertNotEqual(record["sourceId"], continuation_id)
            self.assertEqual(record["text"].count("\n\n"), 1)
        self.assertTrue(self.by_citation["III.179"]["text"].startswith("mirari siquidem"))
        self.assertTrue(self.by_citation["IV.107"]["text"].startswith("Mazianitas"))
        self.assertEqual(self.by_citation["IV.276"]["text"].split("\n\n")[-1], "Nemo blasphemet absentem")
        self.assertEqual(sum(r["counts"]["continuationParagraphs"] for _, r in self.documents.values()), 6)

    def test_nested_sentence_markers_establish_sections_102_and_103(self):
        marked = {r["section"]: m for r in self.documents["book-01"][0]
                  for m in r["sourceMarkup"] if m["kind"] == "s"}
        self.assertEqual(set(marked), {101, 102, 103})
        for section, mark in marked.items():
            record = self.by_citation[f"I.{section}"]
            self.assertEqual(utf16_slice(record["text"], mark["start"], mark["end"]), mark["text"])
        self.assertTrue(self.by_citation["I.102"]["text"].startswith("Moneo tamen"))

    def test_all_19_additions_23_deletions_and_nested_refs_remain_searchable(self):
        marks = [m for r in self.records for m in r["editorialMarks"]]
        self.assertEqual(sum(m["kind"] == "add" for m in marks), 19)
        self.assertEqual(sum(m["kind"] == "del" for m in marks), 23)
        self.assertEqual(sum(m["kind"] == "ref" for r in self.records for m in r["sourceMarkup"]), 3)
        first = self.by_citation["I.34"]
        self.assertTrue(first["text"].startswith("Post septimam uero diem"))
        self.assertIn("quem<...>", first["text"])
        for record in self.records:
            for mark in record["editorialMarks"] + record["sourceMarkup"]:
                self.assertEqual(utf16_slice(record["text"], mark["start"], mark["end"]), mark["text"])
                self.assertEqual(mark["kind"], mark["sourceTag"])
                self.assertIsInstance(mark["sourceAttributes"], dict)
        self.assertTrue(any(m["sourceAttributes"] == {"hand": "post", "place": "interlinear"} for m in marks))
        self.assertTrue(any(m["sourceAttributes"] == {"hand": "orig", "rend": "strikethrough"} for m in marks))

    def test_six_literal_dot_gaps_are_conservative_boundaries_but_double_period_is_not(self):
        expected = {"I.34": [(257, 260)], "I.53": [(355, 358)], "II.80": [(360, 365)],
                    "II.93": [(95, 98)], "IV.84": [(245, 247), (251, 252)]}
        observed = {r["citationLabel"]: [(m["start"], m["end"]) for m in r["textGaps"] if m["kind"] == "literal-dots"]
                    for r in self.records if any(m["kind"] == "literal-dots" for m in r["textGaps"])}
        self.assertEqual(observed, expected)
        for citation, spans in observed.items():
            record = self.by_citation[citation]
            self.assertEqual(record["phraseBreaks"], [a for a, _ in spans])
            for gap in record["textGaps"]:
                self.assertEqual(utf16_slice(record["text"], gap["start"], gap["end"]), gap["text"])
        self.assertIn("triginta..", self.by_citation["I.149"]["text"])
        self.assertEqual(self.by_citation["I.149"]["phraseBreaks"], [])
        self.assertTrue(all(not r["textGaps"] for r in self.documents["preface"][0]))

    def test_only_iii_240_is_empty_and_its_omission_is_explicit(self):
        self.assertEqual([r["citationLabel"] for r in self.records if not r["text"]], ["III.240"])
        gap = self.by_citation["III.240"]
        self.assertEqual(gap["phraseBreaks"], [0])
        self.assertEqual(gap["textGaps"], [{"kind": "tei-gap", "start": 0, "end": 0, "text": "", "sourceAttributes": {"reason": "omitted"}}])
        self.assertEqual(gap["sourceId"], "latin-book03-num239")
        self.assertEqual([r["citationLabel"] for r in self.records if r.get("breakBefore")], ["I.27", "III.240", "III.241"])
        self.assertEqual(self.documents["book-03"][1]["coverage"]["allowedEmptySections"], [240])
        self.assertFalse(self.documents["book-03"][1]["coverage"]["allSectionTextsNonempty"])

    def test_notes_titles_and_reference_labels_are_excluded_with_provenance(self):
        latin = "\n".join(r["text"] for r in self.records)
        for excluded in ("annotation illisible", "arcam dicit", "EXPLICITPRAEFATIO", "INCIP. LIB.", "[I.i.27]"):
            self.assertNotIn(excluded, latin)
        self.assertEqual(sum(r["counts"]["excludedAnnotationNotes"] for _, r in self.documents.values()), 12)
        note_segments = [s for _, report in self.documents.values() for p in report["paragraphs"] for s in p["segments"] if s["kind"] == "excluded-note"]
        self.assertEqual(len(note_segments), 12)
        self.assertTrue(all(s["sourceAttributes"].get("source") in extract.NOTE_SOURCES for s in note_segments))

    def test_combined_build_is_deterministic_with_six_source_bindings_and_only_five_books(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            sentinel = root / "previous-work.json"
            sentinel.write_bytes(b"preserved earlier collection")
            output = root / "data" / extract.COLLECTION
            report = extract.build_corpus(REPOSITORY, output)
            original = {p.name: p.read_bytes() for p in output.iterdir()}
            extract.build_corpus(REPOSITORY, output)
            self.assertEqual(original, {p.name: p.read_bytes() for p in output.iterdir()})
            self.assertEqual(len(original), 12)
            self.assertEqual(report["counts"]["sections"], 1710)
            self.assertEqual(report["counts"]["sourceDocuments"], 6)
            self.assertEqual(report["counts"]["runningWordTokens"], 67657)
            self.assertEqual([b["book"] for b in report["books"]], [1, 2, 3, 4, 5])
            self.assertEqual(report["books"][0]["source"]["path"], "assets/xml/antiquities/Latin/book-01.xml")
            self.assertEqual([s["path"] for s in report["books"][0]["additionalSources"]], ["assets/xml/antiquities/Latin/preface.xml"])
            self.assertEqual(sentinel.read_bytes(), b"preserved earlier collection")
            for book in report["books"]:
                for kind in ("corpus", "extractionReport"):
                    data = (root / book[kind]["path"]).read_bytes()
                    self.assertEqual(hashlib.sha256(data).hexdigest(), book[kind]["sha256"])
                    self.assertEqual(len(data), book[kind]["bytes"])
            self.assertEqual(json.loads(original["corpus.json"]), sum([json.loads(original[f"book-{b:02}.corpus.json"]) for b in range(1, 6)], []))

    def test_invalid_final_source_cannot_partially_replace_existing_outputs(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source_directory = root / "assets/xml/antiquities/Latin"
            source_directory.mkdir(parents=True)
            for key, source in self.sources.items():
                if key == "book-05":
                    source = source.replace(b'<milestone unit="niese" n="362"', b'<milestone unit="niese" n="999"', 1)
                (source_directory / f"{key}.xml").write_bytes(source)
            destination = root / "output"
            destination.mkdir()
            (destination / "corpus.json").write_bytes(b"previous complete tranche")
            with self.assertRaisesRegex(extract.ExtractionError, "consecutive Niese"):
                extract.build_corpus(root, destination)
            self.assertEqual({p.name: p.read_bytes() for p in destination.iterdir()}, {"corpus.json": b"previous complete tranche"})


class AntiquitiesCorruptionTests(unittest.TestCase):
    def test_utf16_markup_offsets_preserve_astral_letters_and_word_internal_page_markers(self):
        target = "note_" + "a" * 32
        records, report = small(fixture(paragraph(
            f' 𐐀ve Á<add>li</add>us post<del><ref target="{target}">ra</ref></del> '
            'Ro<pb n="2v"/>manos <s>unus <milestone unit="niese" n="28"/>alter</s> ')), last=28)
        first, second = records
        self.assertEqual(first["text"], "𐐀ve Álius postra Romanos unus")
        self.assertEqual(second["text"], "alter")
        self.assertEqual(first["editorialMarks"][0]["start"], 7)
        self.assertEqual(first["editorialMarks"][0]["text"], "li")
        for record in records:
            for mark in record["editorialMarks"] + record["sourceMarkup"]:
                self.assertEqual(utf16_slice(record["text"], mark["start"], mark["end"]), mark["text"])
        self.assertTrue(report["coverage"]["sourceProjectionExactlyRestoresSource"])

    def test_conservative_dot_detection_does_not_reinterpret_letter_supplements(self):
        records, _ = small(fixture(paragraph(" &lt;similiter&gt; respo&lt;nderet&gt;ur nosc&lt;untur&gt; triginta.. con&lt;...&gt;perit [f...s] se&lt;.&gt;ba ")))
        self.assertEqual([g["text"] for g in records[0]["textGaps"]], ["...", "...", "."])
        self.assertEqual(records[0]["text"], "<similiter> respo<nderet>ur nosc<untur> triginta.. con<...>perit [f...s] se<.>ba")

    def test_unknown_substantive_tag_cannot_be_silently_dropped(self):
        for tag in ("choice", "app", "supplied", "foreign", "unclear"):
            with self.subTest(tag=tag), self.assertRaisesRegex(extract.ExtractionError, "unexpected running-text markup"):
                small(fixture(paragraph(f"ante <{tag}>uerbum</{tag}> post")))

    def test_unknown_editorial_attributes_require_review(self):
        with self.assertRaisesRegex(extract.ExtractionError, "addition attributes"):
            small(fixture(paragraph('ante <add resp="unknown">uerbum</add> post')))

    def test_unreviewed_note_or_a_note_inside_running_text_requires_review(self):
        for text in ('<note>possibly main text</note>ante', 'ante <note source="#BernBBMs50">new position</note>'):
            with self.subTest(text=text), self.assertRaisesRegex(extract.ExtractionError, "unreviewed running-text note"):
                small(fixture(paragraph(text)))

    def test_duplicate_missing_and_reordered_niese_markers_fail(self):
        for marker in (27, 29):
            with self.subTest(marker=marker), self.assertRaisesRegex(extract.ExtractionError, "consecutive Niese"):
                small(fixture(paragraph(f'prima <milestone unit="niese" n="{marker}"/>secunda')), last=28)
        with self.assertRaisesRegex(extract.ExtractionError, "citation coverage"):
            small(fixture(paragraph("prima")), last=28)

    def test_niese_marker_cannot_split_an_original_word(self):
        with self.assertRaisesRegex(extract.ExtractionError, "divides or changes an original word"):
            small(fixture(paragraph('di<milestone unit="niese" n="28"/>cit')), last=28)

    def test_unmarked_empty_sections_fail(self):
        with self.assertRaisesRegex(extract.ExtractionError, "unmarked empty Niese section"):
            small(fixture(paragraph('prima<milestone unit="niese" n="28"/>')), last=28)

    def test_gap_outside_the_reviewed_iii_240_omission_fails(self):
        with self.assertRaisesRegex(extract.ExtractionError, "only reviewed explicit omission"):
            small(fixture(paragraph('<gap reason="omitted"/>')))
        with self.assertRaisesRegex(extract.ExtractionError, "gap attributes"):
            small(fixture(paragraph('<gap reason="illegible"/>')))

    def test_deleted_gap_marker_cannot_turn_iii_240_into_an_unmarked_empty_record(self):
        source = (REPOSITORY / "assets/xml/antiquities/Latin/book-03.xml").read_bytes()
        source = source.replace(b'<gap reason="omitted"/>', b'', 1)
        with self.assertRaisesRegex(extract.ExtractionError, "unmarked empty Niese section"):
            extract.extract_document(source, book_number=3)

    def test_duplicate_paragraph_ids_fail(self):
        source = fixture(paragraph("prima") + paragraph("secunda", 28))
        source = source.replace(b'xml:id="latin-book01-num28"', b'xml:id="latin-book01-num27"', 1)
        with self.assertRaisesRegex(extract.ExtractionError, "Duplicate paragraph identity"):
            small(source, last=28)

    def test_unreviewed_unnumbered_paragraph_cannot_be_discarded(self):
        with self.assertRaisesRegex(extract.ExtractionError, "Unreviewed unnumbered paragraph"):
            small(fixture('<p>Substantive text without numbering</p>' + paragraph("prima")))

    def test_dtd_comments_and_processing_instructions_are_not_ignored(self):
        for source in (b'<!DOCTYPE TEI [<!ENTITY x "unsafe">]>' + fixture(paragraph("prima")),
                       fixture(paragraph("prima<!--additional material-->")),
                       fixture(paragraph("prima<?target processing?>"))):
            with self.subTest(source=source[:100]), self.assertRaises(extract.ExtractionError):
                small(source)

    def test_missing_or_nested_num_label_fails(self):
        with self.assertRaisesRegex(extract.ExtractionError, "missing citation num label"):
            small(fixture('<p xml:id="latin-book01-num27">No label</p>'))
        with self.assertRaisesRegex(extract.ExtractionError, "citation or note nested"):
            small(fixture(paragraph('ante <s><num>[I.ii.28]</num>post</s>')))

    def test_sixth_book_requires_a_future_reviewed_tranche(self):
        with self.assertRaisesRegex(extract.ExtractionError, "I–V"):
            extract.extract_document(fixture(paragraph("prima")), book_number=6)


if __name__ == "__main__":
    unittest.main()
