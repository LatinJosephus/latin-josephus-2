#!/usr/bin/env python3
"""Extract the site's accepted Latin Contra Apionem I–II without editing TEI.

Each existing p@n is one Niese search unit. Literal characters and source order
are retained exactly apart from trimming unit-edge whitespace. The asterisk
markers in the accepted source remain visible and define conservative phrase
barriers; their precise editorial meaning is not newly adjudicated here.
Unknown running-text markup or attributes stop extraction for review.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import unicodedata
import xml.etree.ElementTree as ET


TEI = "http://www.tei-c.org/ns/1.0"
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"
XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"
COLLECTION = "contra-apionem-latin-boysen"
OUTPUT_PREFIX = f"data/{COLLECTION}"
ROMANS = {1: "I", 2: "II"}
BOOK_SPECS = {
    1: {"units": 320, "chapters": 35, "pb": 70, "add": 1, "q": 1, "foreign": 2,
        "asteriskMarkerClusters": 12, "sourceAnnotations": 2, "firstPage": 3},
    2: {"units": 296, "chapters": 41, "pb": 70, "add": 0, "q": 0, "foreign": 1,
        "asteriskMarkerClusters": 13, "sourceAnnotations": 1, "firstPage": 73},
}
INLINE_TAGS = {"pb", "milestone", "add", "q", "foreign"}
SOURCE_ANNOTATIONS = {
    (1, 119): "#niese-boundary-within-preceding-lacuna",
    (1, 147): "#niese-boundary-within-preceding-lacuna",
    (2, 68): "#transcription-restoration-is",
}
ASTERISK_GROUP = re.compile(r"\*(?:\s*\*)*")


class ExtractionError(ValueError):
    """The source is outside the reviewed Contra Apionem extraction contract."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ExtractionError(message)


def q(name: str) -> str:
    return f"{{{TEI}}}{name}"


def sha(value: bytes | str) -> str:
    return hashlib.sha256(value.encode("utf-8") if isinstance(value, str) else value).hexdigest()


def utf16_length(text: str) -> int:
    return len(text.encode("utf-16-le")) // 2


def words(text: str) -> list[str]:
    """Original Unicode L/N-start and L/M/N-continuation words, as in search."""
    result, start = [], None
    for index, character in enumerate(text):
        category = unicodedata.category(character)[0]
        if start is None:
            if category in "LN":
                start = index
        elif category not in "LMN":
            result.append(text[start:index])
            start = None
    if start is not None:
        result.append(text[start:])
    return result


def container(element: ET.Element, allowed: set[str]) -> None:
    require(not (element.text or "").strip(), f"Text outside paragraphs in {element.tag}")
    for child in element:
        require(child.tag in {q(name) for name in allowed}, f"Unexpected tag {child.tag}")
        require(not (child.tail or "").strip(), f"Text outside paragraphs after {child.tag}")


def page_marker(element: ET.Element) -> None:
    require(not len(element) and not (element.text or ""), "Page marker contains text")
    require(set(element.attrib) == {"n"}
            and re.fullmatch(r"[1-9]\d*", element.get("n", "")) is not None,
            "Unexpected page-break attributes")


def extract_paragraph(paragraph: ET.Element, book: int, section: int) -> tuple[dict, dict, Counter]:
    """Flatten one paragraph and prove exact restoration from final text slices."""
    source_id = f"latin-apion{book}-num{section}"
    attributes = {"n": str(section), XML_ID: source_id}
    annotation = SOURCE_ANNOTATIONS.get((book, section))
    if annotation is not None:
        attributes["ana"] = annotation
    require(paragraph.attrib == attributes, f"Expected consecutive source identity and accepted annotation for {source_id}")
    raw_text = "".join(paragraph.itertext())
    flattened = ""
    pieces, inline_marks, markers = [], [], []
    counts = Counter()

    def emit(text: str) -> None:
        nonlocal flattened
        if text:
            start = len(flattened)
            flattened += text
            pieces.append({"sourceTextStart": start, "sourceTextEnd": len(flattened)})

    def inline(element: ET.Element) -> None:
        tag = element.tag.removeprefix(f"{{{TEI}}}") if isinstance(element.tag, str) else "non-element"
        require(element.tag in {q(name) for name in INLINE_TAGS},
                f"{source_id}: unexpected substantive tag {element.tag}")
        counts[tag] += 1
        start = len(flattened)
        if tag == "pb":
            page_marker(element)
            markers.append({"kind": "pb", "sourceTextOffset": start, "page": element.get("n")})
            return
        if tag == "milestone":
            require(not len(element) and not (element.text or ""), "Chapter milestone contains text")
            require(set(element.attrib) == {"unit", "subtype", "n"}
                    and element.get("unit") == "chapter" and element.get("subtype") == "boysen"
                    and re.fullmatch(r"[1-9]\d*", element.get("n", "")) is not None,
                    f"{source_id}: unreviewed milestone attributes")
            markers.append({"kind": "chapter", "sourceTextOffset": start,
                            "number": int(element.get("n")), "edition": "Boysen (1898)"})
            return
        if tag == "foreign":
            require(element.attrib == {XML_LANG: "grc"}, f"{source_id}: unexpected foreign-language attributes")
        else:
            require(not element.attrib, f"{source_id}: unexpected {tag} attributes")
        emit(element.text or "")
        for child in element:
            # No nested substantive element occurs in the accepted source.
            # Page boundaries may still be represented inside a marked span.
            require(child.tag == q("pb"), f"{source_id}: unreviewed nested {tag} markup")
            inline(child)
            emit(child.tail or "")
        require(bool(flattened[start:].strip()), f"{source_id}: empty substantive {tag}")
        mark = {"kind": tag, "sourceTextStart": start, "sourceTextEnd": len(flattened)}
        if tag == "foreign":
            mark["language"] = "grc"
        inline_marks.append(mark)

    emit(paragraph.text or "")
    for child in paragraph:
        inline(child)
        emit(child.tail or "")
    require(flattened == raw_text, f"{source_id}: inline flattening changed original characters")
    text = flattened.strip()
    require(bool(text) and bool(words(text)), f"{source_id}: empty Niese unit")
    left = len(flattened) - len(flattened.lstrip())
    right = len(flattened.rstrip())
    leading, trailing = flattened[:left], flattened[right:]
    segments = []
    for piece in pieces:
        first, last = max(left, piece["sourceTextStart"]), min(right, piece["sourceTextEnd"])
        if first < last:
            segments.append({"kind": "source-text", "sourceTextStart": first, "sourceTextEnd": last,
                             "recordTextStart": first - left, "recordTextEnd": last - left,
                             "textSha256": sha(text[first - left:last - left])})
    editorial, source_markup = [], []
    for mark in inline_marks:
        start, end = max(0, mark["sourceTextStart"] - left), min(len(text), mark["sourceTextEnd"] - left)
        require(0 <= start < end <= len(text), f"{source_id}: source markup outside final text")
        published = {"kind": mark["kind"], "start": utf16_length(text[:start]),
                     "end": utf16_length(text[:end]), "text": text[start:end]}
        if mark["kind"] == "add":
            published["sourceTag"] = "add"
            editorial.append(published)
        else:
            if mark["kind"] == "foreign":
                published["language"] = "grc"
            source_markup.append(published)
    for marker in markers:
        relative = max(0, min(len(text), marker["sourceTextOffset"] - left))
        marker["recordTextOffset"] = relative
        marker["recordTextOffsetUTF16"] = utf16_length(text[:relative])
    text_gaps = [{"start": utf16_length(text[:m.start()]), "end": utf16_length(text[:m.end()]),
                  "text": m.group(), "kind": "literal-asterisks"}
                 for m in ASTERISK_GROUP.finditer(text)]
    counts["asteriskMarkerClusters"] = len(text_gaps)
    counts["sourceAnnotations"] = int(annotation is not None)
    label = f"{ROMANS[book]}.{section}"
    record = {
        "id": f"{COLLECTION}-{book}-{section}", "work": "contra-apionem", "book": book,
        "section": section, "language": "Latin", "edition": "Boysen (1898)",
        "citationScheme": "niese", "citationLabel": label,
        "citation": {"book": ROMANS[book], "section": section},
        "text": text, "editorialMarks": editorial, "sourceMarkup": source_markup,
        "textGaps": text_gaps, "phraseBreaks": [gap["start"] for gap in text_gaps],
        "url": f"/contra-apionem/?book={book}&niese={section}",
        "readerLink": {"path": "contra-apionem/", "params": {"book": book, "niese": section}},
        "sourceId": source_id,
    }
    if annotation is not None:
        record["sourceAnnotations"] = [annotation]
    if annotation == "#niese-boundary-within-preceding-lacuna":
        record["breakBefore"] = True
        record["breakReason"] = "The source marks this Niese boundary within the preceding lacuna."
    restored = leading + "".join(text[s["recordTextStart"]:s["recordTextEnd"]] for s in segments) + trailing
    require(restored == raw_text, f"{source_id}: exact paragraph restoration failed")
    require(words(text) == words(raw_text), f"{source_id}: inline markup changed a word")
    report = {
        "sourceId": source_id, "section": section, "citationLabel": label,
        "sourceAttributes": paragraph.attrib,
        "rawTextCharacters": len(raw_text), "rawTextSha256": sha(raw_text),
        "removedPrefix": "", "leadingWhitespace": leading, "trailingWhitespace": trailing,
        "displayTextSha256": sha(text), "sourceProjectionSha256": sha(text), "segments": segments,
        "inlineMarks": inline_marks, "structuralMarkers": markers,
        "textGaps": text_gaps, "phraseBreaks": record["phraseBreaks"],
        "exactRestorationVerified": True, "wordSequenceVerified": True,
    }
    return record, report, counts


def extract_document(xml_bytes: bytes, *, book_number: int = 1, order_offset: int | None = None,
                     expected_units: int | None = None, expected_chapters: int | None = None,
                     expected_inline_counts: dict | None = None,
                     source_name: str | None = None) -> tuple[list[dict], dict]:
    require(book_number in BOOK_SPECS, "This extractor accepts Latin Contra Apionem Books I–II only")
    spec = BOOK_SPECS[book_number]
    expected_units = spec["units"] if expected_units is None else expected_units
    expected_chapters = spec["chapters"] if expected_chapters is None else expected_chapters
    order_offset = sum(BOOK_SPECS[n]["units"] for n in range(1, book_number)) if order_offset is None else order_offset
    require(isinstance(order_offset, int) and order_offset >= 0, "Global order offset must be a nonnegative integer")
    source_name = source_name or f"assets/xml/contra-apionem/Latin/book-{book_number:02}.xml"
    require(b"<!DOCTYPE" not in xml_bytes.upper() and b"<!ENTITY" not in xml_bytes.upper(),
            "DTD/entity declarations are outside the accepted source format")
    try:
        root = ET.fromstring(xml_bytes, parser=ET.XMLParser(target=ET.TreeBuilder(insert_comments=True, insert_pis=True)))
    except ET.ParseError as error:
        raise ExtractionError(f"XML is not well formed: {error}") from error
    require(root.tag == q("TEI") and not root.attrib, "Expected a plain TEI root in the TEI namespace")
    container(root, {"teiHeader", "text"})
    require(len(root.findall(q("teiHeader"))) == 1, "Expected exactly one TEI header")
    texts = root.findall(q("text"))
    require(len(texts) == 1, "Expected one TEI text")
    require(texts[0].attrib == {XML_ID: f"apion-latin-book-{book_number}-text", XML_LANG: "lat"},
            "TEI text identity or language differs")
    container(texts[0], {"body"})
    bodies = texts[0].findall(q("body"))
    require(len(bodies) == 1 and not bodies[0].attrib, "Expected one plain TEI body")
    body = bodies[0]
    container(body, {"note", "pb", "div1"})
    require([el.tag for el in body] == [q("note"), q("pb"), q("div1")],
            "Unexpected body structure; source notice and initial page marker must precede the book")
    notice, initial_page, book_node = body
    require(not len(notice) and notice.attrib == {"type": "source"}
            and notice.text == f"Boysen, CSEL 37 (1898), Contra Apionem Book {book_number}.",
            "Unrecognised source notice; possible running text would be lost")
    page_marker(initial_page)
    require(book_node.attrib == {"n": ROMANS[book_number], "type": "book", "subtype": "Latin",
                                 XML_ID: f"latin-apion{book_number}"}, "Book division identity differs")
    container(book_node, {"p"})
    header = root.find(q("teiHeader"))
    header_text = "".join(header.itertext())
    excluded = [
        {"kind": "teiHeader", "reason": "outside running text", "textCharacters": len(header_text),
         "textSha256": sha(header_text)},
        {"kind": "source-notice", "text": notice.text, "textSha256": sha(notice.text),
         "reason": "verified bibliographical notice outside running text"},
        {"kind": "structural-page-marker", "page": initial_page.get("n"),
         "reason": "empty marker; contributes no characters or word break"},
    ]
    records, paragraphs, raw_paragraphs, restored_paragraphs, displays = [], [], [], [], []
    counts = Counter({"pb": 1})
    chapters, pages = [], [int(initial_page.get("n"))]
    for section, paragraph in enumerate(book_node, 1):
        record, audit, paragraph_counts = extract_paragraph(paragraph, book_number, section)
        record["order"] = order_offset + len(records)
        records.append(record)
        paragraphs.append(audit)
        counts.update(paragraph_counts)
        raw = "".join(paragraph.itertext())
        restored = audit["leadingWhitespace"] + "".join(
            record["text"][s["recordTextStart"]:s["recordTextEnd"]] for s in audit["segments"]) + audit["trailingWhitespace"]
        require(restored == raw, f"{record['sourceId']}: finished record cannot restore its source")
        raw_paragraphs.append(raw)
        restored_paragraphs.append(restored)
        displays.append(record["text"])
        for marker in audit["structuralMarkers"]:
            if marker["kind"] == "chapter":
                chapters.append(marker["number"])
            elif marker["kind"] == "pb":
                pages.append(int(marker["page"]))
    require(len(records) == expected_units, f"Unexpected Niese-unit count: expected {expected_units}, found {len(records)}")
    require(chapters == list(range(1, expected_chapters + 1)), "Duplicate, missing, or reordered Boysen chapter")
    if expected_inline_counts is not None:
        for name in ("pb", "add", "q", "foreign", "asteriskMarkerClusters", "sourceAnnotations"):
            require(counts[name] == expected_inline_counts[name], f"Unexpected {name} count")
        require(pages == list(range(spec["firstPage"], spec["firstPage"] + spec["pb"])),
                "Duplicate, missing, or reordered source page marker")
    for index, record in enumerate(records):
        if record.get("breakBefore"):
            require(index > 0 and records[index - 1]["text"].endswith("*"),
                    "Annotated preceding lacuna has no terminal source asterisk marker")
    source_words = [word for text in raw_paragraphs for word in words(text)]
    indexed_words = [word for text in displays for word in words(text)]
    source_content = re.sub(r"\s", "", "".join(raw_paragraphs))
    display_content = re.sub(r"\s", "", "".join(displays))
    require(source_words == indexed_words, "Full source word-sequence coverage failed")
    require(source_content == display_content, "An original character or punctuation mark changed")
    report = {
        "schemaVersion": 3, "status": "PASS",
        "scope": {"work": "Contra Apionem", "book": book_number, "language": "Latin",
                  "edition": "Boysen (1898)", "unit": "existing Latin Niese section", "citationScheme": "niese"},
        "source": {"path": source_name, "sha256": sha(xml_bytes), "bytes": len(xml_bytes)},
        "rules": {
            "bodyTagsAccepted": ["body", "note", "div1", "p", *sorted(INLINE_TAGS)],
            "sourceOrderPreserved": True,
            "sectionReferenceMeaning": "The existing accepted Latin p@n Niese numbering, confirmed by its stable xml:id. No Niese milestone elements occur in this source.",
            "textTransformations": "Trim only citation-unit edge whitespace. Preserve all literal running characters, spelling, punctuation, internal whitespace, bracket notation, asterisks and Greek fragments. Generate no characters.",
            "editorialMarkup": "Retain the literal content of add and preserve its source identity in UTF-16 editorialMarks. Do not silently reinterpret add as supplied, or insert punctuation into the indexed text.",
            "quotationAndLanguageMarkup": "Preserve q and foreign spans in sourceMarkup and the extraction audit. No quotation marks, spaces or language substitutions are generated.",
            "pageMarkers": "pb contributes no characters or spaces, including the word-internal break praecel/pb/lentes in II.186.",
            "chapterMarkers": "Boysen chapter milestones contribute no characters. They are independent of Niese units; chapter 10 starts inside II.120.",
            "asteriskMarkers": "Preserve each maximal literal asterisk cluster (asterisks optionally separated by whitespace) in textGaps. Its start is a phraseBreaks UTF-16 offset. This is a conservative search barrier, not a new editorial adjudication of every marker.",
            "phraseBoundaries": "Phrases cannot cross literal asterisk clusters, including clusters at unit edges. I.119 and I.147 also retain breakBefore from their explicit preceding-lacuna annotations. Ordinary consecutive Niese sections are joinable in whole-book scope; distinct books never join. Boolean conditions may relate text on either side of a marker.",
            "nonlinearAlignment": "The accepted Latin II.277–278 sequence is retained without rearrangement, duplication or a phrase barrier. The documented overlap with Greek numbering is not a Latin textual gap.",
            "sourceAnnotations": "Retain the two preceding-lacuna annotations and II.68 transcription-restoration-is without reopening their accepted editorial decisions.",
            "gapsAndUnknownContent": "No TEI gap, supplied, del, unclear, app, choice or running-text note occurs. Unknown substantive markup or attributes stop extraction for review.",
            "offsetDefinition": "Audit sourceText and recordText offsets are zero-based Python Unicode-character offsets, end exclusive. Record editorialMarks, sourceMarkup, textGaps and phraseBreaks use zero-based JavaScript UTF-16 offsets. Structural markers supply both coordinate types explicitly.",
            "sourceProjectionDefinition": "Every indexed character comes from parsed source text. Source projection equals final record text; edge whitespace restores the exact original paragraph.",
            "tokenCountDefinition": "Unicode L/N start, L/M/N continuation; original word strings, including the source's Greek fragments, without normalization or stemming.",
            "readerRoute": "/contra-apionem/?book={book}&niese={section}",
            "readerRouteEvidence": "assets/js/renderTei.js: Contra Apionem uses the Boysen Latin source by default; sectionLevelUsesNiese and URL handling accept the existing paragraph Niese identity.",
        },
        "counts": {
            "bodyParagraphs": len(records), "numberedParagraphs": len(records), "sections": len(records),
            "chapterMilestones": len(chapters), "nieseMilestones": 0, "pageBreaks": counts["pb"],
            "addedSpans": counts["add"], "quotationSpans": counts["q"], "foreignSpans": counts["foreign"],
            "asteriskMarkerClusters": counts["asteriskMarkerClusters"],
            "asteriskMarkedUnits": sum(bool(r["textGaps"]) for r in records),
            "breakBeforeUnits": sum(bool(r.get("breakBefore")) for r in records),
            "sourceAnnotations": counts["sourceAnnotations"],
            "runningWordTokens": len(indexed_words), "generatedCruxGlyphs": 0,
            "trimmedEdgeWhitespaceCharacters": sum(len(p["leadingWhitespace"]) + len(p["trailingWhitespace"]) for p in paragraphs),
        },
        "coverage": {
            "missingSections": [], "unexpectedSections": [], "duplicateSections": [],
            "completeRange": [1, expected_units], "rangeMeaning": "existing accepted Latin Niese section",
            "globalOrderRange": [order_offset, order_offset + len(records) - 1],
            "sourceOrderIsConsecutive": True, "paragraphsExactlyRestored": len(records),
            "rawParagraphSequenceSha256": sha("\n".join(raw_paragraphs)),
            "restoredParagraphSequenceSha256": sha("\n".join(restored_paragraphs)),
            "sourceWordSequenceSha256": sha("\n".join(source_words)),
            "indexedWordSequenceSha256": sha("\n".join(indexed_words)),
            "sourceNonWhitespaceContentSha256": sha(source_content),
            "indexedNonWhitespaceContentSha256": sha(display_content),
            "sourceProjectionNonWhitespaceContentSha256": sha(display_content),
            "displayNonWhitespaceContentSha256": sha(display_content),
            "displayTextSequenceSha256": sha("\n".join(displays)), "generatedDisplayGlyphs": 0,
            "sourceProjectionExactlyRestoresSource": True,
            "wordSequencePreserved": True, "nonWhitespaceContentPreserved": True,
            "allSectionTextsNonempty": True,
        },
        "excluded": excluded, "paragraphs": paragraphs,
    }
    return records, report


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def write_bytes(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(value)
    temporary.replace(path)


def build_corpus(source_root: Path, output_dir: Path) -> dict:
    """Validate both books completely before replacing any CA-only output."""
    combined, books, reports = [], [], []
    artifacts: dict[str, bytes] = {}
    totals = Counter()
    for number, spec in BOOK_SPECS.items():
        source_path = f"assets/xml/contra-apionem/Latin/book-{number:02}.xml"
        records, report = extract_document((source_root / source_path).read_bytes(), book_number=number,
                                          order_offset=len(combined), expected_inline_counts=spec, source_name=source_path)
        corpus_name, report_name = f"book-{number:02}.corpus.json", f"book-{number:02}.extraction-report.json"
        corpus_bytes, report_bytes = json_bytes(records), json_bytes(report)
        artifacts[corpus_name], artifacts[report_name] = corpus_bytes, report_bytes
        books.append({"book": number, "status": "PASS", "source": report["source"], "counts": report["counts"],
                      "orderStart": len(combined), "orderEnd": len(combined) + len(records) - 1,
                      "corpus": {"path": f"{OUTPUT_PREFIX}/{corpus_name}", "sha256": sha(corpus_bytes),
                                 "bytes": len(corpus_bytes), "records": len(records)},
                      "extractionReport": {"path": f"{OUTPUT_PREFIX}/{report_name}",
                                           "sha256": sha(report_bytes), "bytes": len(report_bytes)}})
        combined.extend(records)
        reports.append(report)
        totals.update(report["counts"])
    require(len(combined) == 616 and len({r["id"] for r in combined}) == 616, "Combined Contra Apionem coverage differs")
    require([r["order"] for r in combined] == list(range(616)), "Combined source order is not continuous")
    combined_bytes = json_bytes(combined)
    artifacts["corpus.json"] = combined_bytes
    report = {
        "schemaVersion": 3, "status": "PASS",
        "scope": {"work": "Contra Apionem", "books": list(BOOK_SPECS), "language": "Latin",
                  "edition": "Boysen (1898)", "unit": "existing Latin Niese section", "citationScheme": "niese"},
        "counts": {"books": len(books), **dict(totals)},
        "coverage": {
            "paragraphsExactlyRestored": sum(r["coverage"]["paragraphsExactlyRestored"] for r in reports),
            "wordSequencePreserved": True, "nonWhitespaceContentPreserved": True,
            "sourceProjectionExactlyRestoresSource": True, "generatedDisplayGlyphs": 0,
            "sourceProjectionDefinition": "Every indexed character comes from source text; the original paragraph is restored exactly by reinstating its recorded edge whitespace.",
            "globalIdsUnique": True, "globalOrderIsConsecutive": True, "globalOrderRange": [0, 615],
            "completeSectionCoverageByBook": {str(b): [1, spec["units"]] for b, spec in BOOK_SPECS.items()},
            "rangeMeaning": "existing accepted Latin Niese section", "allSectionTextsNonempty": True,
        },
        "corpus": {"path": f"{OUTPUT_PREFIX}/corpus.json", "sha256": sha(combined_bytes),
                   "bytes": len(combined_bytes), "records": len(combined)}, "books": books,
    }
    artifacts["extraction-report.json"] = json_bytes(report)
    for name, data in artifacts.items():
        write_bytes(output_dir / name, data)
    return report


def main() -> None:
    directory = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=directory.parent.parent)
    parser.add_argument("--output-dir", type=Path, default=directory / OUTPUT_PREFIX,
                        help="Direct destination for CA corpus and per-book shards (default data/contra-apionem-latin-boysen)")
    args = parser.parse_args()
    report = build_corpus(args.source_root, args.output_dir)
    print(json.dumps({"status": report["status"], "corpusSha256": report["corpus"]["sha256"],
                      "counts": report["counts"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
