#!/usr/bin/env python3
"""Extract the accepted Pollard v1.1 English De excidio without editing its TEI.

One original English paragraph is one chapter-local citation unit. Number labels
and their preceding indentation are excluded explicitly and reversibly. The
separate Prologue ends before Book I narrative; ordinary chapter seams remain
joinable in whole-book search.
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
COLLECTION = "deh-english-pollard"
SOURCE_PREFIX = "assets/xml/deh/English"
OUTPUT_PREFIX = f"data/{COLLECTION}"
ROMANS = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V"}
CONTRACTS = {
    1: {"sha256": "1f8a50242272c8cbb2fe2054c10e318cf00d0aab91b508eb1ca9e7a9e6a60b47", "sections": 215, "tokens": 40804, "chapters": 47, "headings": 2, "heading": "Book I", "releaseNote": "English translation, version 1.1: Prologue and Book I chapters 1–46, ending at [I.46.2]."},
    2: {"sha256": "b87360225888e3e66950905eb047bded590302bb28b2b0f4c43fdbf8b089db2c", "sections": 73, "tokens": 17142, "chapters": 18, "headings": 1, "heading": "Book II", "releaseNote": "English translation, version 1.1: complete Book II, chapters 1–18, [II.1.1]–[II.18.1]."},
    3: {"sha256": "f6c0c7ea4140e40bbe72d6a9293e5cbe6df73d15271d41d88d72a5eefd14e08c", "sections": 70, "tokens": 18640, "chapters": 26, "headings": 1, "heading": "BOOK III", "releaseNote": "English translation, version 1.1: complete Book III, chapters 1–26, [III.1.1]–[III.26.4]."},
    4: {"sha256": "1e5bf28ece4f00954924fe5aa9a704e647289a0c83e7e08ca99944b8412c0370", "sections": 79, "tokens": 17259, "chapters": 33, "headings": 1, "heading": "BOOK IV", "releaseNote": "English translation, version 1.1: complete Book IV, chapters 1–33, [IV.1.1]–[IV.33.3]."},
    5: {"sha256": "4df33b9d0409644e5f9f2bcacb87ca507e5ff2272d72d1a0b1c73e14f2484c91", "sections": 121, "tokens": 42207, "chapters": 53, "headings": 1, "heading": "BOOK V", "releaseNote": "English translation, version 1.1: complete Book V, chapters 1–53, [V.1.1]–[V.53.2]."},
}
BREAK_REASON = "The separately labelled Prologue ends before Book I narrative."
TRANSLATION_NOTE_UNITS = {1: {31, 36, 70, 141}, 2: {73}, 3: {36, 47}, 4: set(), 5: {72}}
RULES = {
    "boundaries": "Each accepted English xml:id and num label identify one complete chapter/paragraph citation unit. section is its stable paragraph ordinal within the book, never a Niese section.",
    "text": "Exclude the verified num label together with its preceding whitespace; trim only running-text edge whitespace. Preserve every other original running character, punctuation and internal whitespace. No spelling repair or generated text.",
    "sourceIdentity": "Retain each original English xml:id and its exact sameAs reference to the aligned Latin element. English text is extracted from its own source, not reconstructed from Latin.",
    "excludedBlocks": "The complete TEI header, verified body release note and exact chapter/book headings are metadata outside running text. Their source evidence is retained.",
    "editorialMarkup": "The accepted English paragraphs contain a leading num element and plain running text. Eight approved uncertainty notes are excluded from search and preserved in the source restoration ledger. No Latin additions, deletions, gaps or dagger representations are inherited. Unknown body markup stops extraction.",
    "phraseBoundaries": "Physically consecutive paragraphs and chapters remain joinable in whole-book scope. The Prologue-to-Book-I transition has breakBefore=true. Phrases never cross books, works or editions.",
    "coordinates": "All sourcePieces and section coordinates are zero-based original-text UTF-16 offsets, end exclusive. rawText includes the removed num label and its preceding whitespace; runningText excludes that prefix.",
    "readerRoute": "/deh/?book={book}&chapter={chapter}&unit={paragraph}&english=pollard; chapter 0 is the Prologue and unit is chapter-local.",
}


class ExtractionError(ValueError):
    """Source text or structure is outside the reviewed English DEH contract."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ExtractionError(message)


def q(name: str) -> str:
    return f"{{{TEI}}}{name}"


def sha(value: bytes | str) -> str:
    return hashlib.sha256(value.encode("utf-8") if isinstance(value, str) else value).hexdigest()


def utf16_length(text: str) -> int:
    return len(text.encode("utf-16-le")) // 2


def utf16_slice(text: str, start: int, end: int) -> str:
    return text.encode("utf-16-le")[start * 2:end * 2].decode("utf-16-le")


def words(text: str) -> list[str]:
    result, current = [], ""
    for char in text:
        category = unicodedata.category(char)[0]
        if category in {"L", "N"} or (current and category == "M"):
            current += char
        elif current:
            result.append(current)
            current = ""
    if current:
        result.append(current)
    return result


def attributes(element: ET.Element) -> dict:
    return {"xml:id" if key == XML_ID else key: value for key, value in element.attrib.items()}


def container(element: ET.Element, allowed: set[str]) -> None:
    require(not (element.text or "").strip(), "English DEH contains unclassified container text")
    for child in element:
        require(child.tag in {q(name) for name in allowed}, "English DEH has an unreviewed body or container child")
        require(not (child.tail or "").strip(), "English DEH contains unclassified text after a container child")


def coverage(paragraphs: list[dict], records: list[dict], ranges: dict) -> dict:
    by_id = {record["id"]: record for record in records}
    raw = [paragraph["rawText"] for paragraph in paragraphs]
    restored = ["".join(utf16_slice(by_id[piece["recordId"]]["text"], piece["recordStart"], piece["recordEnd"])
                        if piece["kind"] == "record" else piece["text"] for piece in paragraph["sourcePieces"])
                for paragraph in paragraphs]
    source_words = [word for paragraph in paragraphs for word in words(paragraph["runningText"])]
    indexed_words = [word for record in records for word in words(record["text"])]
    source_content = "".join(re.sub(r"\s", "", paragraph["runningText"]) for paragraph in paragraphs)
    indexed_content = "".join(re.sub(r"\s", "", record["text"]) for record in records)
    require(raw == restored, "English DEH source restoration differs")
    require(source_words == indexed_words, "English DEH projection changes source words")
    require(source_content == indexed_content, "English DEH projection lost source characters")
    return {**ranges, "rangeMeaning": "stable XML paragraph ordinal, not Niese", "missingSections": [],
            "unexpectedSections": [], "duplicateSections": [], "allSectionTextsNonempty": all(record["text"] for record in records),
            "paragraphsExactlyRestored": len(paragraphs), "wordSequencePreserved": True, "nonWhitespaceContentPreserved": True,
            "rawParagraphSequenceSha256": sha("\n".join(raw)), "restoredParagraphSequenceSha256": sha("\n".join(restored)),
            "sourceWordSequenceSha256": sha("\n".join(source_words)), "indexedWordSequenceSha256": sha("\n".join(indexed_words)),
            "sourceNonWhitespaceContentSha256": sha(source_content), "indexedNonWhitespaceContentSha256": sha(indexed_content)}


def extract_document(xml_bytes: bytes, *, book_number: int, order_offset: int | None = None,
                     source_path: str | None = None, verify_source: bool = True,
                     expected_sections: int | None = None, expected_chapters: int | None = None) -> tuple[list[dict], dict]:
    require(book_number in CONTRACTS, "Unreviewed English De excidio book")
    contract = CONTRACTS[book_number]
    source_path = source_path or f"{SOURCE_PREFIX}/book-{book_number:02d}.xml"
    require(source_path == f"{SOURCE_PREFIX}/book-{book_number:02d}.xml", "English DEH source path differs")
    if verify_source:
        require(sha(xml_bytes.replace(b"\r\n", b"\n")) == contract["sha256"], "English DEH source differs from the accepted source")
    require(b"<!DOCTYPE" not in xml_bytes.upper() and b"<!ENTITY" not in xml_bytes.upper(), "DTD/entity declarations are unreviewed")
    wanted = contract["sections"] if expected_sections is None else expected_sections
    chapter_count = contract["chapters"] if expected_chapters is None else expected_chapters
    require(isinstance(wanted, int) and not isinstance(wanted, bool) and wanted > 0, "Expected sections must be a positive integer")
    require(isinstance(chapter_count, int) and not isinstance(chapter_count, bool) and chapter_count > 0, "Expected chapters must be a positive integer")
    if order_offset is None:
        order_offset = sum(CONTRACTS[n]["sections"] for n in CONTRACTS if n < book_number)
    require(isinstance(order_offset, int) and not isinstance(order_offset, bool) and order_offset >= 0, "Global order offset must be a nonnegative integer")
    try:
        root = ET.fromstring(xml_bytes, parser=ET.XMLParser(target=ET.TreeBuilder(insert_comments=True, insert_pis=True)))
    except ET.ParseError as error:
        raise ExtractionError(f"English DEH XML is not well formed: {error}") from error
    require(root.tag == q("TEI") and not root.attrib, "English DEH root identity differs")
    container(root, {"teiHeader", "text"})
    require([child.tag for child in root] == [q("teiHeader"), q("text")], "English DEH must have one header and text")
    header, text_node = root
    require(not text_node.attrib, "English DEH text attributes differ")
    container(text_node, {"body"})
    require(len(text_node) == 1, "English DEH must have one body")
    body = text_node[0]
    require(not body.attrib, "English DEH body attributes differ")
    container(body, {"note", "div1"})
    require([child.tag for child in body] == [q("note"), q("div1")], "English DEH body note/book order differs")
    note, book_div = body
    require(not note.attrib and not len(note) and note.text == contract["releaseNote"], "English DEH release note differs")
    book_attrs = {"n": ROMANS[book_number], "xml:id": f"english-deh{book_number}", "sameAs": f"#latin-deh{book_number}", "subtype": "English", "type": "book"}
    require(attributes(book_div) == book_attrs, "English DEH book identity differs")
    container(book_div, {"div2"})
    header_text = "".join(header.itertext())
    excluded = [{"kind": "teiHeader", "reason": "metadata outside running text", "textCharacters": utf16_length(header_text), "textSHA256": sha(header_text)},
                {"kind": "release-note", "reason": "verified release metadata outside running text", "text": note.text, "textSHA256": sha(note.text)}]
    records, paragraphs, chapters = [], [], []
    heading_count = 0
    for chapter_div in book_div:
        chapter = len(chapters) + (0 if book_number == 1 else 1)
        chapter_attrs = {"n": str(chapter), "xml:id": f"english-deh{book_number}-chapter{chapter}",
                         "sameAs": f"#latin-deh{book_number}-chapter{chapter}", "type": "chapter"}
        require(attributes(chapter_div) == chapter_attrs, "English DEH chapter identity or order differs")
        container(chapter_div, {"head", "p"})
        chapters.append(chapter)
        local_paragraph = 0
        for child_index, paragraph in enumerate(chapter_div):
            if paragraph.tag == q("head"):
                expected = "Prologue" if chapter == 0 else contract["heading"]
                require(chapter in [0, 1] and child_index == 0 and not paragraph.attrib and not len(paragraph)
                        and paragraph.text == expected, "English DEH heading differs or interrupts running text")
                excluded.append({"kind": "heading", "chapter": chapter, "reason": "verified structural heading outside running text",
                                 "text": paragraph.text, "textSHA256": sha(paragraph.text)})
                heading_count += 1
                continue
            local_paragraph += 1
            section = len(records) + 1
            source_id = f"english-deh{book_number}-num{section}"
            same_as = f"#latin-deh{book_number}-num{section}"
            require(attributes(paragraph) == {"xml:id": source_id, "sameAs": same_as}, "English DEH paragraph identity or alignment differs")
            require(not (paragraph.text or "").strip(), "English DEH has running text before its citation label")
            require(1 <= len(paragraph) <= 2 and paragraph[0].tag == q("num"), "English DEH paragraph has unreviewed inline markup")
            annotation = ""
            if len(paragraph) == 2:
                note = paragraph[1]
                require(section in TRANSLATION_NOTE_UNITS[book_number] and note.tag == q("note")
                        and attributes(note) == {"type": "uncertainty", "source": same_as}
                        and not len(note) and not note.tail and bool(note.text)
                        and note.text.startswith("Translation comparison: "), "English DEH paragraph has unreviewed inline markup")
                annotation = note.text
            number = paragraph[0]
            label = f"Prol.{local_paragraph}" if chapter == 0 else f"{ROMANS[book_number]}.{chapter}.{local_paragraph}"
            require(not number.attrib and not len(number) and number.text == f"[{label}]", "English DEH citation label differs from chapter/paragraph")
            prefix = (paragraph.text or "") + number.text
            running = number.tail or ""
            running_end = len(prefix) + len(running)
            raw = prefix + running + annotation
            require(raw == "".join(paragraph.itertext()), "English DEH traversal lost paragraph text")
            text = running.strip()
            require(text and words(text), "Empty English DEH citation unit")
            start = len(prefix) + len(running) - len(running.lstrip())
            end = start + len(text)
            record = {"id": f"{COLLECTION}-{book_number}-{section}", "work": "deh", "book": book_number,
                "section": section, "language": "English", "edition": "Pollard v1.1", "chapter": chapter, "paragraph": local_paragraph,
                "citationScheme": "chapter-paragraph", "citationLabel": label,
                "citation": {"book": ROMANS[book_number], "chapter": chapter, "paragraph": local_paragraph, "prologue": chapter == 0},
                "text": text, "editorialMarks": [], "sourceMarkup": [], "textGaps": [], "phraseBreaks": [],
                "url": f"/deh/?book={book_number}&chapter={chapter}&unit={local_paragraph}&english=pollard",
                "readerLink": {"path": "deh/", "params": {"book": book_number, "chapter": chapter, "unit": local_paragraph, "english": "pollard"}},
                "sourceId": source_id, "sourceIds": [source_id], "sourceIdentityKind": "xml:id", "sourcePath": source_path,
                "sourceSameAs": same_as, "order": order_offset + len(records)}
            if book_number == 1 and chapter == 1 and local_paragraph == 1:
                record.update({"breakBefore": True, "breakReason": BREAK_REASON})
            records.append(record)
            pieces = [{"kind": "excluded", "reason": "citation-label-and-preceding-whitespace", "text": prefix,
                       "sourceStart": 0, "sourceEnd": utf16_length(prefix), "textSHA256": sha(prefix)}]

            def excluded_whitespace(first: int, last: int) -> None:
                if first == last:
                    return
                fragment = raw[first:last]
                require(fragment.isspace(), "Non-whitespace English DEH narrative was excluded")
                pieces.append({"kind": "excluded", "reason": "section-edge-whitespace", "text": fragment,
                    "sourceStart": utf16_length(raw[:first]), "sourceEnd": utf16_length(raw[:last]), "textSHA256": sha(fragment)})

            excluded_whitespace(len(prefix), start)
            pieces.append({"kind": "record", "recordId": record["id"], "recordStart": 0, "recordEnd": utf16_length(text),
                           "sourceStart": utf16_length(raw[:start]), "sourceEnd": utf16_length(raw[:end]), "textSHA256": sha(text)})
            excluded_whitespace(end, running_end)
            if annotation:
                pieces.append({"kind": "excluded", "reason": "translation-comparison-note", "text": annotation,
                    "sourceStart": utf16_length(raw[:running_end]), "sourceEnd": utf16_length(raw), "textSHA256": sha(annotation)})
            require(pieces[0]["sourceStart"] == 0 and pieces[-1]["sourceEnd"] == utf16_length(raw)
                    and all(a["sourceEnd"] == b["sourceStart"] for a, b in zip(pieces, pieces[1:])), "English DEH source ledger is discontinuous")
            paragraphs.append({"sourceId": source_id, "sourceIdentityKind": "xml:id", "sourcePath": source_path,
                "sourceAttributes": attributes(paragraph), "bookAttributes": book_attrs, "chapterAttributes": chapter_attrs,
                "paragraphOrdinal": len(paragraphs), "chapter": chapter, "paragraph": local_paragraph, "citationLabel": label,
                "rawText": raw, "runningText": running, "removedPrefix": prefix, "sourcePieces": pieces,
                "sections": [{"recordId": record["id"], "section": section, "sourceStart": 0, "sourceEnd": utf16_length(raw),
                    "textStart": utf16_length(raw[:start]), "textEnd": utf16_length(raw[:end]),
                    "leadingWhitespace": raw[len(prefix):start], "trailingWhitespace": raw[end:running_end], "textSHA256": sha(text)}],
                "editorialSpans": [], "structuralMarkers": [], "exactRestorationVerified": True})
        require(local_paragraph > 0, "English DEH chapter has no paragraphs")
    require(len(records) == wanted and len(chapters) == chapter_count, "English DEH unit or chapter count differs")
    require(heading_count == contract["headings"], "English DEH heading count differs")
    if book_number == 1:
        require(sum(record["chapter"] == 0 for record in records) == 3, "English DEH Prologue must retain its three units")
    counts = {"bodyParagraphs": len(paragraphs), "numberedParagraphs": len(paragraphs), "sections": len(records),
        "runningWordTokens": sum(len(words(record["text"])) for record in records), "chapterDivisionsIncludingPrologue": len(chapters),
        "prologueUnits": sum(record["chapter"] == 0 for record in records), "excludedCitationLabels": len(records),
        "excludedHeadings": heading_count, "excludedReleaseNotes": 1,
        "excludedTranslationNotes": sum(len(p) == 2 for p in root.findall('.//'+q('body')+'//'+q('p'))),
        "breakBeforeUnits": sum(bool(record.get("breakBefore")) for record in records)}
    if verify_source:
        require(counts["runningWordTokens"] == contract["tokens"], "English DEH running word count differs")
    source = {"path": source_path, "sha256": sha(xml_bytes), "bytes": len(xml_bytes)}
    report = {"schemaVersion": 1, "status": "PASS", "scope": {"work": "De excidio Hierosolymitano", "book": book_number,
        "language": "English", "edition": "Pollard v1.1", "unit": "existing chapter/paragraph citation unit", "citationScheme": "chapter-paragraph"},
        "source": source, "additionalSources": [], "sources": [source],
        "sourceContract": {"normalizedSHA256": contract["sha256"], "hashMode": "CRLF-to-LF only", "verified": verify_source},
        "rules": RULES, "counts": counts, "coverage": coverage(paragraphs, records, {"completeRange": [1, wanted]}),
        "excludedBlocks": excluded, "paragraphs": paragraphs}
    return records, report


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def build_corpus(source_root: Path, output_dir: Path) -> dict:
    records, reports, books, artifacts = [], [], [], {}
    for number in CONTRACTS:
        relative = f"{SOURCE_PREFIX}/book-{number:02d}.xml"
        part, report = extract_document((source_root / relative).read_bytes(), book_number=number, order_offset=len(records))
        stem = f"book-{number:02d}"
        corpus_bytes, report_bytes = json_bytes(part), json_bytes(report)
        artifacts[f"{stem}.corpus.json"], artifacts[f"{stem}.extraction-report.json"] = corpus_bytes, report_bytes
        books.append({"book": number, "status": "PASS", "source": report["source"], "additionalSources": [], "sources": report["sources"],
            "counts": report["counts"], "orderStart": len(records), "orderEnd": len(records) + len(part) - 1,
            "corpus": {"path": f"{OUTPUT_PREFIX}/{stem}.corpus.json", "sha256": sha(corpus_bytes), "bytes": len(corpus_bytes), "records": len(part)},
            "extractionReport": {"path": f"{OUTPUT_PREFIX}/{stem}.extraction-report.json", "sha256": sha(report_bytes), "bytes": len(report_bytes)}})
        records.extend(part)
        reports.append(report)
    counts = Counter()
    for report in reports:
        counts.update(report["counts"])
    corpus_bytes = json_bytes(records)
    artifacts["corpus.json"] = corpus_bytes
    combined = {"schemaVersion": 1, "status": "PASS", "scope": {"work": "De excidio Hierosolymitano", "books": list(CONTRACTS),
        "language": "English", "edition": "Pollard v1.1", "unit": "existing chapter/paragraph citation unit", "citationScheme": "chapter-paragraph"},
        "counts": {"books": len(CONTRACTS), "sourceDocuments": len(CONTRACTS), **dict(counts)},
        "coverage": {**coverage([p for report in reports for p in report["paragraphs"]], records,
            {"completeRangesByBook": {str(n): [1, c["sections"]] for n, c in CONTRACTS.items()}}),
            "globalIdsUnique": len({record["id"] for record in records}) == len(records),
            "globalOrderIsConsecutive": [record["order"] for record in records] == list(range(len(records)))},
        "corpus": {"path": f"{OUTPUT_PREFIX}/corpus.json", "sha256": sha(corpus_bytes), "bytes": len(corpus_bytes), "records": len(records)}, "books": books}
    artifacts["extraction-report.json"] = json_bytes(combined)
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, value in artifacts.items():
        (output_dir / name).write_bytes(value)
    return combined


def main() -> None:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=here.parent.parent)
    parser.add_argument("--output-dir", type=Path, default=here / "data" / COLLECTION)
    args = parser.parse_args()
    report = build_corpus(args.source_root.resolve(), args.output_dir.resolve())
    print(json.dumps({key: report[key] for key in ["status", "scope", "counts", "corpus"]}, indent=2))


if __name__ == "__main__":
    main()
