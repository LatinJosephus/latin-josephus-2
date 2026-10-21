#!/usr/bin/env python3
"""Project the accepted Whiston Contra Apionem I–II XML into reversible records.

Its numbered English paragraphs already are Niese sections. Whiston's own
division milestones, including the two inside II.109 and II.112, are retained
as provenance without adding words or interrupting exact phrases.
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
COLLECTION = "contra-apionem-english-whiston"
SOURCE_PREFIX = "assets/xml/contra-apionem/English"
OUTPUT_PREFIX = f"data/{COLLECTION}"
ROMANS = {1: "I", 2: "II"}
CONTRACTS = {
    1: {"sha256": "2c7731cf1eb2f4b70ff2177ef192b7b0452bf2871de023ab405ec83b60f6125a", "sections": 320, "tokens": 18497, "chapters": 35, "whistonSections": 35, "inlineWhistonSections": 0},
    2: {"sha256": "12d006e8e0b296f84f5ef50ae7aa50c781ffe1b8821def5840e82cd317a7b467", "sections": 296, "tokens": 18356, "chapters": 41, "whistonSections": 42, "inlineWhistonSections": 2},
}
RULES = {
    "boundaries": "The accepted English p@n and xml:id define each Niese section. No boundaries or missing ranges are inferred from another language.",
    "text": "Preserve every running source character and punctuation; trim only section-edge whitespace. The TEI header and structural milestone numbers are not running text. No spelling repair or note invention.",
    "sourceIdentity": "Each original English xml:id identifies its complete source paragraph and Niese section.",
    "structuralMarkers": "Retain Niese chapter and Whiston-section milestone attributes and positions. The inline Whiston milestones in II.109 and II.112 contribute no words; all surrounding text and tails remain searchable.",
    "editorialMarkup": "Literal brackets and punctuation remain part of the original text. No additions, deletions, gaps or editorial annotations are inferred from their appearance or from another edition.",
    "phraseBoundaries": "Physically consecutive Niese sections and chapter or Whiston divisions remain joinable in whole-book scope. Phrases never cross books or editions.",
    "coordinates": "All sourcePieces, section and inline milestone coordinates are zero-based original-text UTF-16 offsets, end exclusive.",
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


def attributes(element: ET.Element) -> dict:
    return {"xml:id" if key == XML_ID else key: value for key, value in element.attrib.items()}


def milestone(element: ET.Element, *, inline: bool = False) -> dict:
    require(element.tag == q("milestone") and not len(element) and not element.text,
            "A Contra Apionem milestone contains text or children")
    attrs = attributes(element)
    unit = attrs.get("unit")
    require(re.fullmatch(r"[1-9][0-9]*", attrs.get("n", "")) is not None,
            "Contra Apionem milestone has an invalid number")
    require((unit == "whiston-section" and set(attrs) == {"unit", "n"})
            or (not inline and unit == "chapter" and set(attrs) == {"unit", "subtype", "n"}
                and attrs["subtype"] == "niese"), "Unreviewed Contra Apionem milestone")
    return {"unit": unit, "number": int(attrs["n"]), "sourceAttributes": attrs}


def flatten_paragraph(paragraph: ET.Element) -> dict:
    chunks = [paragraph.text or ""]
    markers = []
    for child in paragraph:
        marker = milestone(child, inline=True)
        markers.append({"unit": marker["unit"], "number": marker["number"],
                        "sourceTextOffset": utf16_length("".join(chunks)),
                        "sourceAttributes": marker["sourceAttributes"]})
        chunks.append(child.tail or "")
    raw = "".join(chunks)
    require(raw == "".join(paragraph.itertext()), "Contra Apionem traversal lost source text")
    return {"rawText": raw, "structuralMarkers": markers}


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
    require(raw == restored, "Contra Apionem source restoration differs")
    require(source_words == indexed_words, "Contra Apionem projection changes source words")
    require(source_content == indexed_content, "Contra Apionem projection lost source characters")
    return {**ranges, "missingSections": [], "unexpectedSections": [], "duplicateSections": [],
            "allSectionTextsNonempty": all(record["text"] for record in records),
            "paragraphsExactlyRestored": len(paragraphs), "wordSequencePreserved": True, "nonWhitespaceContentPreserved": True,
            "rawParagraphSequenceSha256": sha("\n".join(raw)), "restoredParagraphSequenceSha256": sha("\n".join(restored)),
            "sourceWordSequenceSha256": sha("\n".join(source_words)), "indexedWordSequenceSha256": sha("\n".join(indexed_words)),
            "sourceNonWhitespaceContentSha256": sha(source_content), "indexedNonWhitespaceContentSha256": sha(indexed_content)}


def extract_document(xml_bytes: bytes, *, book_number: int, order_offset: int = 0, source_path: str | None = None,
                     verify_source: bool = True, expected_sections: list[int] | None = None) -> tuple[list[dict], dict]:
    require(book_number in CONTRACTS, "Unreviewed Whiston Contra Apionem book")
    contract = CONTRACTS[book_number]
    path = source_path or f"{SOURCE_PREFIX}/book-{book_number:02d}.xml"
    require(path == f"{SOURCE_PREFIX}/book-{book_number:02d}.xml", "Contra Apionem source path differs")
    if verify_source:
        require(sha(xml_bytes.replace(b"\r\n", b"\n")) == contract["sha256"],
                "Whiston Contra Apionem source differs from the accepted source")
    wanted = list(range(1, contract["sections"] + 1)) if expected_sections is None else expected_sections
    require(wanted and all(isinstance(x, int) and not isinstance(x, bool) and x > 0 for x in wanted)
            and wanted == sorted(set(wanted)), "Expected Contra Apionem sections must be ordered unique positive integers")
    root = ET.fromstring(xml_bytes)
    require(root.tag == q("TEI"), "Whiston Contra Apionem source has no TEI root")
    texts = root.findall(q("text"))
    require(len(texts) == 1 and texts[0].attrib == {"{http://www.w3.org/XML/1998/namespace}lang": "eng"},
            "Whiston Contra Apionem language identity differs")
    bodies = root.findall(f".//{q('body')}")
    require(len(bodies) == 1 and list(texts[0]) == bodies, "Whiston Contra Apionem source must contain one body")
    body = bodies[0]
    require(not body.attrib and len(body) == 1 and body[0].tag == q("div1"), "Contra Apionem book container differs")
    book_div = body[0]
    require(attributes(book_div) == {"type": "book", "n": str(book_number), "xml:id": f"english-apion{book_number}"},
            "Contra Apionem book identity differs")
    for container in [texts[0], body, book_div]:
        require(not (container.text or "").strip() and all(not (child.tail or "").strip() for child in container),
                "Contra Apionem contains unclassified text outside paragraphs")
    records, paragraphs, structural_markers, chapters, whiston_sections = [], [], [], [], []
    current_chapter = current_whiston = None
    children = list(book_div)
    for child_index, child in enumerate(children):
        if child.tag == q("milestone"):
            marker = milestone(child)
            following = next((p for p in children[child_index + 1:] if p.tag == q("p")), None)
            require(following is not None, "Contra Apionem has a trailing structural milestone without a paragraph")
            require(re.fullmatch(r"[1-9][0-9]*", following.get("n", "")) is not None,
                    "Contra Apionem paragraph lacks its accepted Niese number")
            structural_markers.append({**marker, "beforeSection": int(following.get("n", "0")),
                                       "previousSection": records[-1]["section"] if records else None,
                                       "bookChildIndex": child_index})
            if marker["unit"] == "chapter":
                chapters.append(marker["number"])
                current_chapter = marker["number"]
            else:
                whiston_sections.append(marker["number"])
                current_whiston = marker["number"]
            continue
        require(child.tag == q("p"), "Contra Apionem has an unreviewed book child")
        paragraph = child
        attrs = attributes(paragraph)
        section_string = attrs.get("n", "")
        require(re.fullmatch(r"[1-9][0-9]*", section_string) is not None
                and attrs == {"n": section_string, "xml:id": f"english-apion{book_number}-num{section_string}"},
                "Contra Apionem paragraph lacks its accepted English xml:id and Niese number")
        require(current_chapter is not None and current_whiston is not None,
                "Contra Apionem paragraph precedes its chapter or Whiston division")
        section, source_id = int(section_string), attrs["xml:id"]
        flat = flatten_paragraph(paragraph)
        raw, markers = flat["rawText"], flat["structuralMarkers"]
        text = raw.strip()
        require(text and words(text), "Empty Whiston Contra Apionem citation interval")
        text_start = len(raw) - len(raw.lstrip())
        text_end = text_start + len(text)
        whiston_start = current_whiston
        for marker in markers:
            whiston_sections.append(marker["number"])
            current_whiston = marker["number"]
        record = {"id": f"{COLLECTION}-{book_number}-{section}", "work": "contra-apionem", "book": book_number,
            "section": section, "language": "English", "edition": "Whiston", "citationScheme": "niese",
            "citationLabel": f"{ROMANS[book_number]}.{section}", "citation": {"book": ROMANS[book_number], "section": section},
            "text": text, "editorialMarks": [], "sourceMarkup": [], "textGaps": [], "phraseBreaks": [],
            "url": f"/contra-apionem/?book={book_number}&niese={section}&english=whiston",
            "readerLink": {"path": "contra-apionem/", "params": {"book": book_number, "niese": section, "english": "whiston"}},
            "sourceId": source_id, "sourceIds": [source_id], "sourceIdentityKind": "xml:id", "sourcePath": path,
            "order": order_offset + len(records)}
        records.append(record)
        source_pieces = []

        def excluded(start: int, end: int) -> None:
            if start == end:
                return
            fragment = raw[start:end]
            require(fragment.isspace(), "Non-whitespace Contra Apionem narrative was excluded")
            source_pieces.append({"kind": "excluded", "reason": "section-edge-whitespace", "text": fragment,
                "sourceStart": utf16_length(raw[:start]), "sourceEnd": utf16_length(raw[:end]), "textSHA256": sha(fragment)})

        excluded(0, text_start)
        source_pieces.append({"kind": "record", "recordId": record["id"], "recordStart": 0,
            "recordEnd": utf16_length(text), "sourceStart": utf16_length(raw[:text_start]),
            "sourceEnd": utf16_length(raw[:text_end]), "textSHA256": sha(text)})
        excluded(text_end, len(raw))
        require(source_pieces[0]["sourceStart"] == 0 and source_pieces[-1]["sourceEnd"] == utf16_length(raw)
                and all(a["sourceEnd"] == b["sourceStart"] for a, b in zip(source_pieces, source_pieces[1:])),
                "Contra Apionem source pieces overlap or leave an interval uncovered")
        paragraphs.append({"sourceId": source_id, "sourceIdentityKind": "xml:id", "sourcePath": path,
            "sourceAttributes": attrs, "parentAttributes": attributes(book_div), "paragraphOrdinal": len(paragraphs),
            "sourceChapter": current_chapter, "whistonSectionStart": whiston_start, "whistonSectionEnd": current_whiston,
            "rawText": raw, "runningText": raw, "sourcePieces": source_pieces,
            "sections": [{"recordId": record["id"], "section": section, "sourceStart": 0, "sourceEnd": utf16_length(raw),
                "textStart": utf16_length(raw[:text_start]), "textEnd": utf16_length(raw[:text_end]),
                "leadingWhitespace": raw[:text_start], "trailingWhitespace": raw[text_end:], "textSHA256": sha(text)}],
            "nieseMarkers": [], "editorialSpans": [], "structuralMarkers": markers, "exactRestorationVerified": True})
    require([record["section"] for record in records] == wanted, "Contra Apionem section identities or physical order differ")
    require(chapters == list(range(1, len(chapters) + 1)), "Contra Apionem chapter sequence differs")
    require(whiston_sections == list(range(1, len(whiston_sections) + 1)), "Contra Apionem Whiston division sequence differs")
    counts = {"bodyParagraphs": len(paragraphs), "narrativeParagraphs": len(paragraphs), "numberedParagraphs": len(paragraphs),
        "sections": len(records), "runningWordTokens": sum(len(words(record["text"])) for record in records),
        "chapterMilestones": len(chapters), "whistonSectionMilestones": len(whiston_sections),
        "inlineWhistonSectionMilestones": sum(len(p["structuralMarkers"]) for p in paragraphs), "breakBeforeUnits": 0}
    if verify_source:
        require([counts[key] for key in ["sections", "runningWordTokens", "chapterMilestones", "whistonSectionMilestones", "inlineWhistonSectionMilestones"]]
                == [contract[key] for key in ["sections", "tokens", "chapters", "whistonSections", "inlineWhistonSections"]],
                "Contra Apionem source totals differ")
    source = {"path": path, "sha256": sha(xml_bytes), "bytes": len(xml_bytes)}
    report = {"schemaVersion": 1, "status": "PASS", "scope": {"work": "Contra Apionem", "book": book_number,
        "language": "English", "edition": "Whiston", "unit": "Niese section", "citationScheme": "niese"},
        "source": source, "additionalSources": [], "sources": [source],
        "sourceContract": {"normalizedSHA256": contract["sha256"], "hashMode": "CRLF-to-LF only", "verified": verify_source},
        "rules": RULES, "counts": counts, "coverage": coverage(paragraphs, records, {"completeRange": [min(wanted), max(wanted)]}),
        "excludedBlocks": [], "structuralMarkers": structural_markers, "paragraphs": paragraphs}
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
    all_paragraphs = [paragraph for report in reports for paragraph in report["paragraphs"]]
    corpus_bytes = json_bytes(records)
    write_bytes(output_dir / "corpus.json", corpus_bytes)
    combined = {"schemaVersion": 1, "status": "PASS", "scope": {"work": "Contra Apionem", "books": list(CONTRACTS),
        "language": "English", "edition": "Whiston", "unit": "Niese section", "citationScheme": "niese"},
        "counts": {"books": len(CONTRACTS), "sourceDocuments": len(CONTRACTS), **dict(counts)},
        "coverage": {**coverage(all_paragraphs, records, {"completeRangesByBook": {str(n): [1, c["sections"]] for n, c in CONTRACTS.items()}}),
            "globalIdsUnique": len({record["id"] for record in records}) == len(records),
            "globalOrderIsConsecutive": [record["order"] for record in records] == list(range(len(records)))},
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
