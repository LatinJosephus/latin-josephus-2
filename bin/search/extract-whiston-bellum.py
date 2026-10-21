#!/usr/bin/env python3
"""Project accepted Whiston Bellum I–VII milestones into reversible search records.

The canonical XML is read only.  Its existing supplied span at VII.208–209
remains searchable and marked; its nested milestone still begins section209.
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
COLLECTION = "bellum-english-whiston"
SOURCE_PREFIX = "assets/xml/bellum/English"
OUTPUT_PREFIX = f"data/{COLLECTION}"
ROMANS = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI", 7: "VII"}
CONTRACTS = {
    1: {"sha256": "39713b6768eef8e7d6ac9640255eacd962ac9677175fbc05077aafe296a1b5ec", "sections": 673, "tokens": 50097, "paragraphs": 234, "chapters": 34},
    2: {"sha256": "52c0e14514dc6ba6942a2ff98e5a87c96122f117fe0122f112b697cbfc12f941", "sections": 654, "tokens": 38098, "paragraphs": 143, "chapters": 22},
    3: {"sha256": "ced7460be53bc6f7f94e4a842f9a3c3f28624cdaaced38d433acf2f4dd3d0cd2", "sections": 542, "tokens": 24777, "paragraphs": 88, "chapters": 10},
    4: {"sha256": "b5b299ee96671784527fc1edef4777e5a766e6f9496fcfb63470874c71824c96", "sections": 663, "tokens": 30489, "paragraphs": 78, "chapters": 11},
    5: {"sha256": "5a6647478976c860b7fb771b058b4af34181eff8201d502f037f0610ca536ee7", "sections": 572, "tokens": 29415, "paragraphs": 65, "chapters": 13},
    6: {"sha256": "edf957eb0501feebbe595f44703c2caa185c9acb6d28efbe69875f3aaa8b2799", "sections": 442, "tokens": 21949, "paragraphs": 50, "chapters": 10},
    7: {"sha256": "2d2c308a500711fddad5cc7ba436f59c38890dd4988f6f5b505817e04e5b200b", "sections": 455, "tokens": 20247, "paragraphs": 46, "chapters": 11},
}
SUPPLIED_ATTRIBUTES = {"reason": "omitted", "source": "https://lexundria.com/j_bj/7.208-7.209/wst"}
SUPPLIED_TEXT = (" were slain, to the number of one thousand seven hundred, as were the women and the children made slaves; "
                 "but as Bassus thought he must perform the covenant, he had made with those that had surrendered the citadel, "
                 "he let them go, and restored Eleazar to them. ")
RULES = {
    "boundaries": "Only accepted English milestone unit=niese positions define sections; sameAs is paragraph provenance, never a boundary inference.",
    "text": "Preserve all running source characters and punctuation; trim only section-edge whitespace. No stemming, spelling repair or note invention.",
    "sourceIdentity": "The original sameAs value, including its leading #, identifies each source paragraph. It is an alignment reference, not an invented English xml:id.",
    "editorialMarkup": "The accepted supplied element at VII.208–209 is retained as searchable text with clipped UTF-16 supplied marks and its exact reason/source attributes. The nested209 milestone is respected. No phrase barrier is introduced.",
    "phraseBoundaries": "Consecutive sections, paragraphs and chapters remain joinable in whole-book scope, including embedded Book I chapter0 sections1–30 and section31. Phrases never cross books or editions.",
    "coordinates": "All sourcePieces, section, milestone and editorial coordinates are zero-based original-text UTF-16 offsets, end exclusive.",
}


class ExtractionError(ValueError):
    """Source text or structure is outside the reviewed extraction contract."""


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


def flatten_paragraph(paragraph: ET.Element, book: int) -> dict:
    chunks, markers, marks = [], [], []
    length = 0

    def append(text: str | None) -> None:
        nonlocal length
        if text:
            chunks.append(text)
            length += len(text)

    def visit(element: ET.Element, in_supplied: bool = False) -> None:
        append(element.text)
        for child in element:
            if child.tag == q("milestone"):
                require(not len(child) and not child.text, "A Bellum Niese milestone contains text")
                require(set(child.attrib) == {"unit", "n"} and child.get("unit") == "niese"
                        and re.fullmatch(r"[1-9][0-9]*", child.get("n", "")), "Unreviewed Bellum milestone")
                markers.append({"section": int(child.get("n")), "offset": length, "sourceAttributes": dict(child.attrib)})
            elif child.tag == q("supplied"):
                require(not in_supplied and book == 7 and paragraph.get("sameAs") == "#latin-bellum7-num190",
                        "Bellum supplied text is outside its reviewed source paragraph")
                require(child.attrib == SUPPLIED_ATTRIBUTES, "Bellum supplied source attributes differ")
                require("".join(child.itertext()) == SUPPLIED_TEXT, "Bellum supplied text differs from the accepted restoration")
                start = length
                visit(child, True)
                marks.append({"kind": "supplied", "start": start, "end": length, "sourceAttributes": dict(child.attrib)})
            else:
                raise ExtractionError(f"Unreviewed Whiston Bellum inline element: {child.tag}")
            append(child.tail)

    visit(paragraph)
    raw = "".join(chunks)
    require(raw == "".join(paragraph.itertext()), "Whiston Bellum traversal lost source text")
    return {"rawText": raw, "markers": markers, "editorialSpans": marks}


def coverage(paragraphs: list[dict], records: list[dict], ranges: dict) -> dict:
    by_id = {record["id"]: record for record in records}
    raw = [paragraph["rawText"] for paragraph in paragraphs]
    restored = ["".join(utf16_slice(by_id[piece["recordId"]]["text"], piece["recordStart"], piece["recordEnd"])
                        if piece["kind"] == "record" else piece["text"] for piece in paragraph["sourcePieces"])
                for paragraph in paragraphs]
    source_words = [word for text in raw for word in words(text)]
    indexed_words = [word for record in records for word in words(record["text"])]
    source_content = "".join(re.sub(r"\s", "", text) for text in raw)
    indexed_content = "".join(re.sub(r"\s", "", record["text"]) for record in records)
    require(raw == restored, "Whiston Bellum source restoration differs")
    require(source_words == indexed_words, "Whiston Bellum milestones split or change source words")
    require(source_content == indexed_content, "Whiston Bellum projection lost source characters")
    return {**ranges, "missingSections": [], "unexpectedSections": [], "duplicateSections": [],
            "allSectionTextsNonempty": all(record["text"] for record in records),
            "paragraphsExactlyRestored": len(paragraphs), "wordSequencePreserved": True, "nonWhitespaceContentPreserved": True,
            "rawParagraphSequenceSha256": sha("\n".join(raw)), "restoredParagraphSequenceSha256": sha("\n".join(restored)),
            "sourceWordSequenceSha256": sha("\n".join(source_words)), "indexedWordSequenceSha256": sha("\n".join(indexed_words)),
            "sourceNonWhitespaceContentSha256": sha(source_content), "indexedNonWhitespaceContentSha256": sha(indexed_content)}


def extract_document(xml_bytes: bytes, *, book_number: int, order_offset: int = 0, source_path: str | None = None,
                     verify_source: bool = True, expected_sections: list[int] | None = None) -> tuple[list[dict], dict]:
    require(book_number in CONTRACTS, "Unreviewed Whiston Bellum book")
    contract = CONTRACTS[book_number]
    path = source_path or f"{SOURCE_PREFIX}/book-{book_number:02d}.xml"
    require(path == f"{SOURCE_PREFIX}/book-{book_number:02d}.xml", "Whiston Bellum source path differs")
    if verify_source:
        require(sha(xml_bytes.replace(b"\r\n", b"\n")) == contract["sha256"], "Whiston Bellum source differs from the accepted source")
    wanted = list(range(1, contract["sections"] + 1)) if expected_sections is None else expected_sections
    require(wanted and all(isinstance(x, int) and x > 0 for x in wanted), "Expected Bellum sections must be positive integers")
    root = ET.fromstring(xml_bytes)
    require(root.tag == q("TEI"), "Whiston Bellum source has no TEI root")
    bodies = root.findall(f".//{q('body')}")
    require(len(bodies) == 1, "Whiston Bellum source must contain one body")
    body = bodies[0]
    require(not body.attrib and len(body) == 1 and body[0].tag == q("div1"), "Whiston Bellum book container differs")
    book_div = body[0]
    require(book_div.attrib == {"n": str(book_number), "subtype": "English", "type": "book"}, "Whiston Bellum book identity differs")
    require(all(chapter.tag == q("div2") for chapter in book_div), "Whiston Bellum has an unreviewed book child")
    chapters = list(book_div)
    for container in [body, book_div, *chapters]:
        require(not (container.text or "").strip() and all(not (child.tail or "").strip() for child in container),
                "Whiston Bellum contains unclassified text outside paragraphs")
    if verify_source:
        first = 0 if book_number == 1 else 1
        require([chapter.get("n") for chapter in chapters] == [str(n) for n in range(first, first + contract["chapters"])],
                "Whiston Bellum chapter sequence differs")
    records, paragraphs = [], []
    for chapter in chapters:
        chapter_number = chapter.get("n", "")
        chapter_attributes = {"n": chapter_number, "sameAs": f"#latin-bellum{book_number}-chapter{chapter_number}"}
        # The accepted Book V chapter13 container has no type attribute.
        if not (book_number == 5 and chapter_number == "13"):
            chapter_attributes["type"] = "chapter"
        require(re.fullmatch(r"0|[1-9][0-9]*", chapter_number)
                and chapter.attrib == chapter_attributes,
                "Whiston Bellum chapter identity differs")
        require(len(chapter) and all(p.tag == q("p") for p in chapter), "Whiston Bellum chapter has unreviewed children")
        for paragraph in chapter:
            source_id = paragraph.get("sameAs", "")
            require(set(paragraph.attrib) == {"sameAs"} and re.fullmatch(fr"#latin-bellum{book_number}-num[1-9][0-9]*", source_id),
                    "Whiston Bellum paragraph lacks its accepted sameAs identity")
            require(source_id not in {p["sourceId"] for p in paragraphs}, "Duplicate Whiston Bellum paragraph identity")
            flat = flatten_paragraph(paragraph, book_number)
            raw, markers = flat["rawText"], flat["markers"]
            require(markers and not raw[:markers[0]["offset"]].strip(), "Whiston Bellum narrative precedes its first Niese marker")
            source_pieces, sections = [], []

            def excluded(start: int, end: int) -> None:
                if start == end:
                    return
                text = raw[start:end]
                require(text.isspace(), "Non-whitespace Whiston Bellum narrative was excluded")
                source_pieces.append({"kind": "excluded", "reason": "section-edge-whitespace", "text": text,
                    "sourceStart": utf16_length(raw[:start]), "sourceEnd": utf16_length(raw[:end]), "textSHA256": sha(text)})

            excluded(0, markers[0]["offset"])
            for index, marker in enumerate(markers):
                start, end = marker["offset"], markers[index + 1]["offset"] if index + 1 < len(markers) else len(raw)
                fragment = raw[start:end]
                text = fragment.strip()
                require(text and words(text), "Empty Whiston Bellum citation interval")
                left = len(fragment) - len(fragment.lstrip())
                text_start, text_end = start + left, start + left + len(text)
                section = marker["section"]
                editorial_marks = []
                for mark in flat["editorialSpans"]:
                    a, b = max(text_start, mark["start"]), min(text_end, mark["end"])
                    if a < b:
                        editorial_marks.append({"kind": mark["kind"], "start": utf16_length(raw[text_start:a]),
                            "end": utf16_length(raw[text_start:b]), "text": raw[a:b], "sourceTag": "supplied",
                            "sourceAttributes": mark["sourceAttributes"]})
                record = {"id": f"{COLLECTION}-{book_number}-{section}", "work": "bellum", "book": book_number,
                    "section": section, "language": "English", "edition": "Whiston", "citationScheme": "niese",
                    "citationLabel": f"{ROMANS[book_number]}.{section}", "citation": {"book": ROMANS[book_number], "section": section},
                    "text": text, "editorialMarks": editorial_marks, "sourceMarkup": [], "textGaps": [], "phraseBreaks": [],
                    "url": f"/bellum-judaicum/?book={book_number}&niese={section}&english=whiston",
                    "readerLink": {"path": "bellum-judaicum/", "params": {"book": book_number, "niese": section, "english": "whiston"}},
                    "sourceId": source_id, "sourceIds": [source_id], "sourceIdentityKind": "sameAs", "sourcePath": path,
                    "order": order_offset + len(records)}
                records.append(record)
                excluded(start, text_start)
                source_pieces.append({"kind": "record", "recordId": record["id"], "recordStart": 0,
                    "recordEnd": utf16_length(text), "sourceStart": utf16_length(raw[:text_start]),
                    "sourceEnd": utf16_length(raw[:text_end]), "textSHA256": sha(text)})
                excluded(text_end, end)
                sections.append({"recordId": record["id"], "section": section, "sourceStart": utf16_length(raw[:start]),
                    "sourceEnd": utf16_length(raw[:end]), "textStart": utf16_length(raw[:text_start]), "textEnd": utf16_length(raw[:text_end]),
                    "leadingWhitespace": fragment[:left], "trailingWhitespace": fragment[left + len(text):], "textSHA256": sha(text)})
            require(source_pieces[0]["sourceStart"] == 0 and source_pieces[-1]["sourceEnd"] == utf16_length(raw)
                    and all(a["sourceEnd"] == b["sourceStart"] for a, b in zip(source_pieces, source_pieces[1:])),
                    "Whiston Bellum source pieces overlap or leave an interval uncovered")
            paragraphs.append({"sourceId": source_id, "sourceIdentityKind": "sameAs", "sourcePath": path,
                "sourceAttributes": dict(paragraph.attrib), "parentAttributes": dict(chapter.attrib),
                "paragraphOrdinal": len(paragraphs), "rawText": raw, "runningText": raw,
                "sourcePieces": source_pieces, "sections": sections,
                "nieseMarkers": [{"section": marker["section"], "sourceTextOffset": utf16_length(raw[:marker["offset"]]),
                                  "sourceAttributes": marker["sourceAttributes"]} for marker in markers],
                "editorialSpans": [{"kind": mark["kind"], "sourceStart": utf16_length(raw[:mark["start"]]),
                    "sourceEnd": utf16_length(raw[:mark["end"]]), "text": raw[mark["start"]:mark["end"]],
                    "sourceAttributes": mark["sourceAttributes"]} for mark in flat["editorialSpans"]],
                "structuralMarkers": [], "exactRestorationVerified": True})
    require([r["section"] for r in records] == wanted, "Whiston Bellum milestone identities or physical order differ")
    annotated = [r["section"] for r in records if r["editorialMarks"]]
    require(annotated == ([208, 209] if book_number == 7 else []), "Whiston Bellum supplied interval inventory differs")
    counts = {"bodyParagraphs": len(paragraphs), "narrativeParagraphs": len(paragraphs), "numberedParagraphs": len(paragraphs),
        "sections": len(records), "runningWordTokens": sum(len(words(r["text"])) for r in records), "nieseMilestones": len(records),
        "chapterDivisions": len(chapters), "suppliedSpans": sum(len(p["editorialSpans"]) for p in paragraphs),
        "suppliedRecordMarks": sum(len(r["editorialMarks"]) for r in records), "breakBeforeUnits": 0}
    if verify_source:
        require([counts[k] for k in ["sections", "runningWordTokens", "narrativeParagraphs", "chapterDivisions"]]
                == [contract[k] for k in ["sections", "tokens", "paragraphs", "chapters"]], "Whiston Bellum source totals differ")
    source = {"path": path, "sha256": sha(xml_bytes), "bytes": len(xml_bytes)}
    report = {"schemaVersion": 1, "status": "PASS", "scope": {"work": "Bellum Judaicum", "book": book_number,
        "language": "English", "edition": "Whiston", "unit": "Niese section", "citationScheme": "niese", "includesEmbeddedPreface": book_number == 1},
        "source": source, "additionalSources": [], "sources": [source],
        "sourceContract": {"normalizedSHA256": contract["sha256"], "hashMode": "CRLF-to-LF only", "verified": verify_source},
        "rules": RULES, "counts": counts, "coverage": coverage(paragraphs, records, {"completeRange": [min(wanted), max(wanted)]}),
        "excludedBlocks": [], "paragraphs": paragraphs}
    return records, report


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def write_bytes(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(value)


def build_corpus(source_root: Path, output_dir: Path) -> dict:
    records, reports, books = [], [], []
    for number in CONTRACTS:
        relative = f"{SOURCE_PREFIX}/book-{number:02d}.xml"
        part, report = extract_document((source_root / relative).read_bytes(), book_number=number, order_offset=len(records))
        stem = f"book-{number:02d}"
        corpus_bytes, report_bytes = json_bytes(part), json_bytes(report)
        write_bytes(output_dir / f"{stem}.corpus.json", corpus_bytes)
        write_bytes(output_dir / f"{stem}.extraction-report.json", report_bytes)
        books.append({"book": number, "status": "PASS", "source": report["source"], "additionalSources": [], "sources": report["sources"],
            "counts": report["counts"], "orderStart": len(records), "orderEnd": len(records) + len(part) - 1,
            "corpus": {"path": f"{OUTPUT_PREFIX}/{stem}.corpus.json", "sha256": sha(corpus_bytes), "bytes": len(corpus_bytes), "records": len(part)},
            "extractionReport": {"path": f"{OUTPUT_PREFIX}/{stem}.extraction-report.json", "sha256": sha(report_bytes), "bytes": len(report_bytes)}})
        records.extend(part)
        reports.append(report)
    counts = Counter()
    for report in reports:
        counts.update(report["counts"])
    all_paragraphs = [p for report in reports for p in report["paragraphs"]]
    corpus_bytes = json_bytes(records)
    write_bytes(output_dir / "corpus.json", corpus_bytes)
    combined = {"schemaVersion": 1, "status": "PASS", "scope": {"work": "Bellum Judaicum", "books": list(CONTRACTS),
        "language": "English", "edition": "Whiston", "unit": "Niese section", "citationScheme": "niese", "includesEmbeddedPreface": True},
        "counts": {"books": 7, "sourceDocuments": 7, **dict(counts)},
        "coverage": {**coverage(all_paragraphs, records, {"completeRangesByBook": {str(n): [1, c["sections"]] for n, c in CONTRACTS.items()}}),
            "globalIdsUnique": len({r["id"] for r in records}) == len(records),
            "globalOrderIsConsecutive": [r["order"] for r in records] == list(range(len(records)))},
        "corpus": {"path": f"{OUTPUT_PREFIX}/corpus.json", "sha256": sha(corpus_bytes), "bytes": len(corpus_bytes), "records": len(records)}, "books": books}
    write_bytes(output_dir / "extraction-report.json", json_bytes(combined))
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
