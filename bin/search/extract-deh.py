#!/usr/bin/env python3
"""Extract the accepted Latin De excidio I–V without changing their TEI.

Every existing citation paragraph is one search unit. The generic ``section``
key is its stable XML paragraph ordinal, never a Niese reference. The ordinary
reader's chapter/paragraph citations and the Book I prologue labels are retained.

The accepted source has no apparatus, note, or gap within its main text. Unknown
body markup stops extraction for review instead of silently discarding words.
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
COLLECTION = "deh-latin-ussani"
OUTPUT_PREFIX = f"data/{COLLECTION}"
BOOK_SPECS = {
    1: {"units": 215, "chapters": 47, "headings": 2, "pb": 126, "lb": 47,
        "del": 2, "supplied": 0, "unclear": 2},
    2: {"units": 73, "chapters": 18, "headings": 1, "pb": 53, "lb": 18,
        "del": 2, "supplied": 2, "unclear": 1},
    3: {"units": 70, "chapters": 26, "headings": 1, "pb": 57, "lb": 26,
        "del": 2, "supplied": 1, "unclear": 0},
    4: {"units": 79, "chapters": 33, "headings": 1, "pb": 54, "lb": 33,
        "del": 2, "supplied": 0, "unclear": 0},
    5: {"units": 121, "chapters": 53, "headings": 1, "pb": 125, "lb": 52,
        "del": 1, "supplied": 6, "unclear": 0},
}
ROMANS = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V"}
BOOK_HEADINGS = {1: "LIBER PRIMVS", 2: "LIBER SECVNDVS", 3: "LIBER TERTIVS",
                 4: "LIBER QVARTVS", 5: "LIBER QVINTVS"}
INLINE_TAGS = {"pb", "lb", "del", "supplied", "unclear"}


class ExtractionError(ValueError):
    """The source is outside the reviewed De excidio extraction contract."""


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
    """Unchanged Unicode words: L/N start, L/M/N continuation, as in the engine."""
    result = []
    start = None
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


def empty_marker(element: ET.Element, tag: str) -> None:
    require(not len(element) and not (element.text or ""), f"{tag} marker contains text")
    if tag == "pb":
        require(set(element.attrib) == {"n"}
                and re.fullmatch(r"[1-9]\d*", element.get("n", "")) is not None,
                "Unexpected page-break attributes")
    else:
        require(not element.attrib, f"Unexpected {tag} attributes")


def heading(element: ET.Element, book: int, chapter: int) -> dict:
    require(not element.attrib, "Unexpected heading attributes")
    expected = "PROLOGVS" if book == 1 and chapter == 0 else BOOK_HEADINGS[book]
    require(chapter == (0 if expected == "PROLOGVS" else 1), "Heading occurs outside its established division")
    text = "".join(element.itertext())
    require(text.strip() == expected, "Unrecognised heading; possible running text would be lost")
    if expected == "PROLOGVS":
        require(len(element) == 1 and element[0].tag == q("supplied")
                and not element[0].attrib and not len(element[0]),
                "Unexpected prologue heading markup")
    else:
        require(not len(element), "Unexpected book heading markup")
    return {"kind": "heading", "chapter": chapter, "text": text,
            "textSha256": sha(text), "reason": "verified structural heading, outside running text"}


def extract_paragraph(paragraph: ET.Element, book: int, chapter: int,
                      ordinal: int, local_paragraph: int) -> tuple[str, dict, list[dict], Counter]:
    """Flatten one paragraph with a reversible source-to-display map."""
    source_id = f"latin-deh{book}-num{ordinal}"
    require(paragraph.attrib == {XML_ID: source_id}, f"Expected consecutive stable paragraph ID {source_id}")
    require(not (paragraph.text or "").strip(), f"{source_id}: text before the citation label")
    require(len(paragraph) and paragraph[0].tag == q("num"), f"{source_id}: missing leading num label")
    label_node = paragraph[0]
    require(not len(label_node) and not label_node.attrib, f"{source_id}: unexpected num markup")
    label = f"Prol.{local_paragraph}" if chapter == 0 else f"{ROMANS[book]}.{chapter}.{local_paragraph}"
    require(label_node.text == f"[{label}]", f"{source_id}: citation label disagrees with its chapter/paragraph")

    raw_text = "".join(paragraph.itertext())
    removed_prefix = (paragraph.text or "") + (label_node.text or "")
    raw_cursor = len(removed_prefix)
    display = ""
    pieces: list[dict] = []
    marks: list[dict] = []
    structural_markers: list[dict] = []
    counts = Counter()

    def emit(text: str) -> None:
        nonlocal raw_cursor, display
        if text:
            pieces.append({"kind": "source-text", "sourceTextStart": raw_cursor,
                           "sourceTextEnd": raw_cursor + len(text),
                           "displayStart": len(display), "displayEnd": len(display) + len(text)})
            raw_cursor += len(text)
            display += text

    def inline(element: ET.Element) -> None:
        nonlocal display
        tag = element.tag.removeprefix(f"{{{TEI}}}") if isinstance(element.tag, str) else "non-element"
        require(element.tag in {q(name) for name in INLINE_TAGS},
                f"{source_id}: unexpected substantive tag {element.tag}")
        counts[tag] += 1
        start = len(display)
        source_start = raw_cursor
        if tag in {"pb", "lb", "unclear"}:
            empty_marker(element, tag)
            if tag == "unclear":
                # This is the existing reader's dagger representation. It is
                # not a supplied word or an inferred lacuna.
                display += "†"
                pieces.append({"kind": "generated-crux", "sourceTextStart": raw_cursor,
                               "sourceTextEnd": raw_cursor, "displayStart": start,
                               "displayEnd": len(display), "generatedText": "†"})
            else:
                structural_markers.append({"kind": tag, "sourceTextOffset": raw_cursor,
                                           "displayOffset": start, **({"page": element.get("n")} if tag == "pb" else {})})
        else:
            require(not element.attrib, f"{source_id}: unexpected {tag} attributes")
            emit(element.text or "")
            for child in element:
                inline(child)
                emit(child.tail or "")
            require(bool(display[start:].strip()), f"{source_id}: empty editorial {tag}")
        if tag in {"del", "supplied", "unclear"}:
            mark = {"kind": tag, "displayStart": start, "displayEnd": len(display),
                    "sourceTextStart": source_start, "sourceTextEnd": raw_cursor}
            if tag == "unclear":
                mark.update({"representation": "generated-dagger", "sourceTag": "unclear"})
            marks.append(mark)

    emit(label_node.tail or "")
    for child in list(paragraph)[1:]:
        inline(child)
        emit(child.tail or "")
    require(raw_cursor == len(raw_text), f"{source_id}: source interval coverage failed")

    text = display.strip()
    require(bool(text) and bool(words(text)), f"{source_id}: empty citation unit")
    left = len(display) - len(display.lstrip())
    right = len(display.rstrip())
    leading, trailing = display[:left], display[right:]
    segments = []
    for piece in pieces:
        first, last = max(left, piece["displayStart"]), min(right, piece["displayEnd"])
        if first >= last:
            continue
        source_first = piece["sourceTextStart"]
        source_last = piece["sourceTextEnd"]
        if piece["kind"] == "source-text":
            source_first += first - piece["displayStart"]
            source_last -= piece["displayEnd"] - last
        segment = {"kind": piece["kind"], "sourceTextStart": source_first, "sourceTextEnd": source_last,
                   "recordTextStart": first - left, "recordTextEnd": last - left,
                   "textSha256": sha(text[first - left:last - left])}
        if piece["kind"] == "generated-crux":
            require(first == piece["displayStart"] and last == piece["displayEnd"], "Partial generated crux")
            segment["generatedText"] = "†"
        segments.append(segment)

    editorial_marks = []
    for mark in marks:
        start, end = max(0, mark["displayStart"] - left), min(len(text), mark["displayEnd"] - left)
        require(0 <= start < end <= len(text), f"{source_id}: editorial mark outside final text")
        actual = {"kind": mark["kind"], "start": utf16_length(text[:start]),
                  "end": utf16_length(text[:end]), "text": text[start:end]}
        if mark["kind"] == "unclear":
            actual.update({"representation": "generated-dagger", "sourceTag": "unclear"})
        editorial_marks.append(actual)
    editorial_marks.sort(key=lambda mark: (mark["start"], -mark["end"], mark["kind"]))

    source_projection = "".join(text[segment["recordTextStart"]:segment["recordTextEnd"]]
                                for segment in segments if segment["kind"] == "source-text")
    restored = removed_prefix + leading + source_projection + trailing
    require(restored == raw_text, f"{source_id}: exact paragraph restoration failed")
    require(words(text) == words(raw_text[len(removed_prefix):]),
            f"{source_id}: an inline transformation changed or divided a word")
    require("".join(text[s["recordTextStart"]:s["recordTextEnd"]] for s in segments) == text,
            f"{source_id}: display segments do not cover final text")
    report = {
        "sourceId": source_id, "section": ordinal, "citationLabel": label,
        "chapter": chapter, "paragraph": local_paragraph,
        "rawTextCharacters": len(raw_text), "rawTextSha256": sha(raw_text),
        "removedPrefix": removed_prefix, "leadingWhitespace": leading, "trailingWhitespace": trailing,
        "displayTextSha256": sha(text), "sourceProjectionSha256": sha(source_projection),
        "segments": segments,
        "inlineMarks": marks,
        "structuralMarkers": structural_markers,
        "exactRestorationVerified": True, "wordSequenceVerified": True,
    }
    return text, report, editorial_marks, counts


def extract_document(xml_bytes: bytes, *, book_number: int = 1, order_offset: int | None = None,
                     expected_units: int | None = None, expected_chapters: int | None = None,
                     expected_headings: int | None = None, expected_inline_counts: dict | None = None,
                     source_name: str | None = None) -> tuple[list[dict], dict]:
    require(book_number in BOOK_SPECS, "This extractor accepts Latin De excidio Books I–V only")
    spec = BOOK_SPECS[book_number]
    expected_units = spec["units"] if expected_units is None else expected_units
    expected_chapters = spec["chapters"] if expected_chapters is None else expected_chapters
    expected_headings = spec["headings"] if expected_headings is None else expected_headings
    order_offset = sum(BOOK_SPECS[n]["units"] for n in range(1, book_number)) if order_offset is None else order_offset
    require(isinstance(order_offset, int) and order_offset >= 0, "Global order offset must be a nonnegative integer")
    source_name = source_name or f"assets/xml/deh/Latin/book-{book_number:02}.xml"
    require(b"<!DOCTYPE" not in xml_bytes.upper() and b"<!ENTITY" not in xml_bytes.upper(),
            "DTD/entity declarations are outside the accepted source format")
    try:
        root = ET.fromstring(xml_bytes, parser=ET.XMLParser(target=ET.TreeBuilder(insert_comments=True, insert_pis=True)))
    except ET.ParseError as error:
        raise ExtractionError(f"XML is not well formed: {error}") from error
    require(root.tag == q("TEI"), "Expected a TEI root in the TEI namespace")
    container(root, {"teiHeader", "text", "standOff"})
    for name in ("teiHeader", "text", "standOff"):
        require(len(root.findall(q(name))) <= 1, f"Duplicate {name} element")
    texts = root.findall(q("text"))
    require(len(texts) == 1, "Expected one TEI text")
    container(texts[0], {"body"})
    bodies = texts[0].findall(q("body"))
    require(len(bodies) == 1, "Expected one TEI body")
    body = bodies[0]
    container(body, {"div1"})
    books = body.findall(q("div1"))
    require(len(books) == 1, "Expected one book division")
    book_node = books[0]
    require(book_node.attrib == {"n": ROMANS[book_number], "type": "book", "subtype": "Latin",
                                 XML_ID: f"latin-deh{book_number}"}, "Book division does not match the requested Latin De excidio book")
    container(book_node, {"div2"})

    excluded = []
    for name in ("teiHeader", "standOff"):
        element = root.find(q(name))
        if element is not None:
            text = "".join(element.itertext())
            excluded.append({"kind": name, "reason": "outside running text", "textCharacters": len(text),
                             "textSha256": sha(text), "elementCounts": dict(sorted(Counter(
                                 el.tag.removeprefix(f"{{{TEI}}}") for el in element.iter() if isinstance(el.tag, str)).items()))})
    records, paragraphs, raw_paragraphs, restored_paragraphs = [], [], [], []
    source_running, projections, display_texts = [], [], []
    seen_chapters, inline_counts = [], Counter()
    heading_count = 0
    paragraph_ordinal = 0
    for chapter_node in book_node:
        chapter_text = chapter_node.get("n", "")
        require(re.fullmatch(r"0|[1-9]\d*", chapter_text) is not None, "Invalid chapter number")
        chapter = int(chapter_text)
        expected_chapter = len(seen_chapters) + (0 if book_number == 1 else 1)
        require(chapter == expected_chapter, "Duplicate, missing, or reordered chapter")
        require(chapter_node.attrib == {"n": chapter_text, "type": "chapter",
                                        XML_ID: f"latin-deh{book_number}-chapter{chapter}"}, "Chapter identity differs")
        seen_chapters.append(chapter)
        container(chapter_node, {"p", "head", "pb"})
        local_paragraph = 0
        chapter_heading_count = 0
        for element in chapter_node:
            if element.tag == q("head"):
                require(local_paragraph == 0 and chapter_heading_count == 0, "Heading interrupts running text or is duplicated")
                excluded.append(heading(element, book_number, chapter))
                heading_count += 1
                chapter_heading_count += 1
                continue
            if element.tag == q("pb"):
                empty_marker(element, "pb")
                inline_counts["pb"] += 1
                excluded.append({"kind": "structural-page-marker", "chapter": chapter,
                                 "page": element.get("n"), "reason": "empty marker; contributes no characters or word break"})
                continue
            local_paragraph += 1
            paragraph_ordinal += 1
            text, audit, marks, counts = extract_paragraph(element, book_number, chapter, paragraph_ordinal, local_paragraph)
            inline_counts.update(counts)
            record = {
                "id": f"{COLLECTION}-{book_number}-{paragraph_ordinal}", "work": "deh", "book": book_number,
                "section": paragraph_ordinal, "language": "Latin", "edition": "Ussani (1932)",
                "chapter": chapter, "paragraph": local_paragraph,
                "citationScheme": "chapter-paragraph", "citationLabel": audit["citationLabel"],
                "citation": {"book": ROMANS[book_number], "chapter": chapter, "paragraph": local_paragraph,
                             "prologue": chapter == 0},
                "text": text, "editorialMarks": marks,
                "url": f"/deh/?book={book_number}&chapter={chapter}&unit={local_paragraph}",
                "readerLink": {"path": "deh/", "params": {"book": book_number, "chapter": chapter, "unit": local_paragraph}},
                "sourceId": audit["sourceId"], "order": order_offset + len(records),
            }
            if book_number == 1 and chapter == 1 and local_paragraph == 1:
                record.update({"breakBefore": True, "breakReason": "The separately labelled Prologue ends before Book I narrative."})
            records.append(record)
            paragraphs.append(audit)
            raw = "".join(element.itertext())
            projection = "".join(text[s["recordTextStart"]:s["recordTextEnd"]]
                                 for s in audit["segments"] if s["kind"] == "source-text")
            restored = audit["removedPrefix"] + audit["leadingWhitespace"] + projection + audit["trailingWhitespace"]
            require(restored == raw, f"{record['sourceId']}: finished record cannot restore its source")
            raw_paragraphs.append(raw)
            restored_paragraphs.append(restored)
            source_running.append(raw[len(audit["removedPrefix"]):])
            projections.append(projection)
            display_texts.append(text)
        require(local_paragraph > 0, f"Chapter {chapter} contains no citation units")
    require(len(records) == expected_units, f"Unexpected citation-unit count: expected {expected_units}, found {len(records)}")
    require(len(seen_chapters) == expected_chapters, "Unexpected chapter count")
    require(heading_count == expected_headings, "Unexpected heading count")
    if book_number == 1:
        require(sum(record["chapter"] == 0 for record in records) == 3, "The prologue must contain its three accepted units")
    if expected_inline_counts is not None:
        for tag in INLINE_TAGS:
            require(inline_counts[tag] == expected_inline_counts[tag], f"Unexpected {tag} count")

    source_words = [word for text in source_running for word in words(text)]
    indexed_words = [word for text in display_texts for word in words(text)]
    source_content = re.sub(r"\s", "", "".join(source_running))
    projected_content = re.sub(r"\s", "", "".join(projections))
    display_content = re.sub(r"\s", "", "".join(display_texts))
    require(source_words == indexed_words, "Full source word-sequence coverage failed")
    require(source_content == projected_content, "A source character or punctuation mark changed")
    require(len({record["sourceId"] for record in records}) == len(records), "Duplicate source paragraph ID")
    report = {
        "schemaVersion": 3, "status": "PASS",
        "scope": {"work": "De excidio Hierosolymitano", "book": book_number, "language": "Latin",
                  "edition": "Ussani (1932)", "unit": "existing chapter/paragraph citation unit",
                  "citationScheme": "chapter-paragraph"},
        "source": {"path": source_name, "sha256": sha(xml_bytes), "bytes": len(xml_bytes)},
        "rules": {
            "bodyTagsAccepted": ["body", "div1", "div2", "head", "p", "num", *sorted(INLINE_TAGS)],
            "sourceOrderPreserved": True,
            "sectionReferenceMeaning": "Stable XML paragraph ordinal within its book; never a Niese section.",
            "textTransformations": "Remove only verified num labels and trim citation-unit edge whitespace. Preserve all literal running characters, spelling, punctuation, and internal whitespace. Empty unclear gains the reader's dagger glyph.",
            "editorialMarkup": "Retain del and supplied letters as searchable visible text; preserve their distinct editorial status in UTF-16 editorialMarks. No brackets or separating spaces are inserted into words.",
            "cruxRepresentation": "Each empty unclear contributes one explicitly mapped generated †. It represents a crux, not an inferred lacuna. Remove only these mapped glyphs to recover source text.",
            "pageAndLineMarkers": "pb and lb contribute no characters and no spaces; word-internal page breaks remain joined. The source lb elements mark division ends.",
            "gapsAndUnknownContent": "No main-text gap, note, apparatus, choice, or foreign elements occur in the accepted source. Unknown body markup stops extraction for review.",
            "phraseBoundaries": "Ordinary consecutive citation units and chapters are joinable in whole-book scope. Book I's Prologue-to-narrative transition has breakBefore=true. Distinct books are never joined.",
            "offsetDefinition": "Audit source/recordText/display offsets are zero-based Python Unicode-character offsets, end exclusive, into concatenated parsed XML paragraph text or displayed record text as named. Record editorialMarks use JavaScript UTF-16 offsets.",
            "sourceProjectionDefinition": "Concatenate only source-text segments from the final indexed record; omit only generated-crux segments. Compatibility indexedNonWhitespaceContentSha256 describes this reversible source projection, not the extra publication glyphs.",
            "tokenCountDefinition": "Unicode L/N start, L/M/N continuation; original word strings without normalization or stemming.",
            "readerRoute": "/deh/?book={book}&chapter={chapter}&unit={paragraph}",
            "readerRouteEvidence": "assets/js/renderTei.js: DEH uses chapter-local URL units, num labels and Ussani by default; prologue chapter is 0.",
        },
        "counts": {
            "bodyParagraphs": len(records), "numberedParagraphs": len(records), "sections": len(records),
            "chapterDivisionsIncludingPrologue": len(seen_chapters),
            "prologueUnits": sum(record["chapter"] == 0 for record in records), "excludedHeadings": heading_count,
            "pageBreaks": inline_counts["pb"], "divisionEndMarkers": inline_counts["lb"],
            "deletedSpans": inline_counts["del"], "suppliedSpans": inline_counts["supplied"],
            "cruxMarkers": inline_counts["unclear"], "generatedCruxGlyphs": inline_counts["unclear"],
            "runningWordTokens": len(indexed_words),
            "removedCitationLabelCharacters": sum(len(p["removedPrefix"]) for p in paragraphs),
            "trimmedEdgeWhitespaceCharacters": sum(len(p["leadingWhitespace"]) + len(p["trailingWhitespace"]) for p in paragraphs),
        },
        "coverage": {
            "missingSections": [], "unexpectedSections": [], "duplicateSections": [],
            "completeRange": [1, expected_units], "rangeMeaning": "stable XML paragraph ordinal, not Niese",
            "globalOrderRange": [order_offset, order_offset + len(records) - 1],
            "sourceOrderIsConsecutive": True, "paragraphsExactlyRestored": len(records),
            "rawParagraphSequenceSha256": sha("\n".join(raw_paragraphs)),
            "restoredParagraphSequenceSha256": sha("\n".join(restored_paragraphs)),
            "sourceWordSequenceSha256": sha("\n".join(source_words)),
            "indexedWordSequenceSha256": sha("\n".join(indexed_words)),
            "sourceNonWhitespaceContentSha256": sha(source_content),
            "indexedNonWhitespaceContentSha256": sha(projected_content),
            "sourceProjectionNonWhitespaceContentSha256": sha(projected_content),
            "displayNonWhitespaceContentSha256": sha(display_content),
            "displayTextSequenceSha256": sha("\n".join(display_texts)),
            "generatedDisplayGlyphs": inline_counts["unclear"],
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
    """Validate all five books before writing within the DEH-only destination."""
    combined, books, reports = [], [], []
    artifacts: dict[str, bytes] = {}
    totals = Counter()
    for number, spec in BOOK_SPECS.items():
        source_path = f"assets/xml/deh/Latin/book-{number:02}.xml"
        records, report = extract_document((source_root / source_path).read_bytes(), book_number=number,
                                          order_offset=len(combined), expected_inline_counts=spec, source_name=source_path)
        corpus_name = f"book-{number:02}.corpus.json"
        report_name = f"book-{number:02}.extraction-report.json"
        corpus_bytes, report_bytes = json_bytes(records), json_bytes(report)
        artifacts[corpus_name], artifacts[report_name] = corpus_bytes, report_bytes
        books.append({"book": number, "status": "PASS", "source": report["source"], "counts": report["counts"],
                      "orderStart": len(combined), "orderEnd": len(combined) + len(records) - 1,
                      "corpus": {"path": f"{OUTPUT_PREFIX}/{corpus_name}", "sha256": sha(corpus_bytes),
                                 "bytes": len(corpus_bytes), "records": len(records)},
                      "extractionReport": {"path": f"{OUTPUT_PREFIX}/{report_name}", "sha256": sha(report_bytes), "bytes": len(report_bytes)}})
        combined.extend(records)
        reports.append(report)
        totals.update(report["counts"])
    require(len(combined) == 558 and len({record["id"] for record in combined}) == 558, "Combined DEH unit coverage differs")
    require([record["order"] for record in combined] == list(range(558)), "Combined source order is not continuous")
    combined_bytes = json_bytes(combined)
    artifacts["corpus.json"] = combined_bytes
    report = {
        "schemaVersion": 3, "status": "PASS",
        "scope": {"work": "De excidio Hierosolymitano", "books": list(BOOK_SPECS), "language": "Latin",
                  "edition": "Ussani (1932)", "unit": "existing chapter/paragraph citation unit",
                  "citationScheme": "chapter-paragraph", "includes": "The three separately labelled Book I prologue units."},
        "counts": {"books": len(books), **dict(totals)},
        "coverage": {
            "paragraphsExactlyRestored": sum(r["coverage"]["paragraphsExactlyRestored"] for r in reports),
            "wordSequencePreserved": True, "nonWhitespaceContentPreserved": True,
            "sourceProjectionExactlyRestoresSource": True, "generatedDisplayGlyphs": totals["generatedCruxGlyphs"],
            "sourceProjectionDefinition": "Original-source equality excludes only explicitly mapped generated † glyphs; all original characters and all words are preserved.",
            "globalIdsUnique": True, "globalOrderIsConsecutive": True, "globalOrderRange": [0, 557],
            "completeSectionCoverageByBook": {str(book): [1, spec["units"]] for book, spec in BOOK_SPECS.items()},
            "rangeMeaning": "stable XML paragraph ordinal, not Niese", "allSectionTextsNonempty": True,
        },
        "corpus": {"path": f"{OUTPUT_PREFIX}/corpus.json", "sha256": sha(combined_bytes),
                   "bytes": len(combined_bytes), "records": len(combined)},
        "books": books,
    }
    artifacts["extraction-report.json"] = json_bytes(report)
    for name, content in artifacts.items():
        write_bytes(output_dir / name, content)
    return report


def main() -> None:
    directory = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=directory.parent.parent)
    parser.add_argument("--output-dir", type=Path, default=directory / OUTPUT_PREFIX,
                        help="Direct destination for DEH corpus.json and per-book shards (default data/deh-latin-ussani)")
    args = parser.parse_args()
    report = build_corpus(args.source_root, args.output_dir)
    print(json.dumps({"status": report["status"], "corpusSha256": report["corpus"]["sha256"], "counts": report["counts"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
