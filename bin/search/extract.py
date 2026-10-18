#!/usr/bin/env python3
"""Extract the seven Cardwell Bellum books without altering their TEI sources.

This deliberately narrow extractor accepts the tags present in the inspected
source. A new substantive tag or an unrecognised title requires an explicit
review, rather than a best-effort extraction that might lose or invent text.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET


TEI = "http://www.tei-c.org/ns/1.0"
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"
SOURCE = "assets/xml/bellum/Latin/book-01.xml"
EXPECTED_SECTIONS = 673
EXPECTED_PARAGRAPHS = 234
EXPECTED_MILESTONES = 439
# Physical alignment paragraphs are not necessarily Niese starts: two existing
# paragraphs in III and VI continue sections begun in the preceding paragraph.
BOOK_SPECS = {
    1: {"sections": 673, "numberedParagraphs": 234, "citationParagraphs": 234, "milestones": 439},
    2: {"sections": 654, "numberedParagraphs": 143, "citationParagraphs": 143, "milestones": 511},
    3: {"sections": 542, "numberedParagraphs": 88, "citationParagraphs": 87, "milestones": 455},
    4: {"sections": 663, "numberedParagraphs": 78, "citationParagraphs": 78, "milestones": 585},
    5: {"sections": 572, "numberedParagraphs": 65, "citationParagraphs": 65, "milestones": 507},
    6: {"sections": 442, "numberedParagraphs": 50, "citationParagraphs": 49, "milestones": 393},
    7: {"sections": 455, "numberedParagraphs": 46, "citationParagraphs": 46, "milestones": 409},
}
CONTINUATION_PARAGRAPHS = {
    3: {"latin-bellum3-num3": 3},
    6: {"latin-bellum6-num427": 427},
}
BOOK_ONE_PILOT_CORPUS_SHA256 = "9a3619160ec2fdd70b910065f190a30553e436a3069045e0cb51e7aae56d1e4c"
PARAGRAPH_SEPARATOR = "\n\n"
BOOK_TITLE = (
    "FLAVII JOSEPHI DE BELLO JUDAICO LIBRI SEPTEM, INTERPRETE RUFINO "
    "AQUILEIENSI, AD GRAECUM COLLATI ET EMENDATI PER SIGISMUNDUM GELENIUM."
)
NUMBER_LABEL = re.compile(r"\A\s*\[([1-9]\d*)\]\s*")
CHAPTER_LABEL = re.compile(r"\ACAP\.\s+([IVXLCDM]+)\.\s*")
SUBCHAPTER_LABEL = re.compile(r"\A([1-9]\d*)\.\s+")
WORD = re.compile(r"[^\W_]+", re.UNICODE)


class ExtractionError(ValueError):
    """The source does not satisfy the inspected pilot's extraction rules."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ExtractionError(message)


def q(name: str) -> str:
    return f"{{{TEI}}}{name}"


def sha(value: bytes | str) -> str:
    if isinstance(value, str):
        value = value.encode("utf-8")
    return hashlib.sha256(value).hexdigest()


def roman(number: int) -> str:
    result = ""
    for value, letters in ((1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
                           (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
                           (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")):
        count, number = divmod(number, value)
        result += letters * count
    return result


def container(element: ET.Element, allowed: set[str]) -> None:
    """Do not discard substantive text outside the recognised paragraphs."""
    require(not (element.text or "").strip(), f"Text outside paragraphs in {element.tag}")
    for child in element:
        require(child.tag in {q(name) for name in allowed}, f"Unexpected tag {child.tag}")
        require(not (child.tail or "").strip(), f"Text outside paragraphs after {child.tag}")


def strip_prefix(text: str, section: int, chapter: int, ordinal: int,
                 *, has_niese_label: bool = True) -> tuple[str, list[dict]]:
    """Remove only independently checked, leading structural labels.

    A dash after CAP. XI. and an apostrophe after CAP. XVI. in the current
    source are deliberately retained. They are not covered by these rules.
    """
    removals: list[dict] = []
    cursor = 0
    match = NUMBER_LABEL.match(text)
    if has_niese_label:
        require(match is not None, f"Section {section}: missing leading [N] label")
        require(int(match.group(1)) == section, f"Section {section}: [N] and xml:id disagree")
    else:
        require(match is None, f"Section {section}: unexpected Niese label on continuation paragraph")

    def remove(kind: str, matched: re.Match, value: int) -> None:
        nonlocal cursor
        end = cursor + matched.end()
        removals.append({"kind": kind, "start": cursor, "end": end,
                         "text": text[cursor:end], "value": value})
        cursor = end

    if has_niese_label:
        remove("niese-label", match, section)
    if ordinal == 1 and chapter != 0:
        match = CHAPTER_LABEL.match(text[cursor:])
        require(match is not None, f"Section {section}: missing chapter label")
        require(match.group(1) == roman(chapter), f"Section {section}: chapter label mismatch")
        remove("chapter-label", match, chapter)
    elif ordinal != 1:
        match = SUBCHAPTER_LABEL.match(text[cursor:])
        require(match is not None, f"Section {section}: missing subchapter label")
        require(int(match.group(1)) == ordinal, f"Section {section}: subchapter label mismatch")
        remove("subchapter-label", match, ordinal)
    return text[:cursor], removals


def extract_document(
    xml_bytes: bytes,
    *,
    book_number: int = 1,
    order_offset: int | None = None,
    expected_sections: int | None = None,
    expected_paragraphs: int | None = None,
    expected_citation_paragraphs: int | None = None,
    expected_milestones: int | None = None,
    source_name: str | None = None,
) -> tuple[list[dict], dict]:
    require(book_number in BOOK_SPECS, "This extractor accepts Latin Bellum Books I–VII only")
    if expected_sections is None:
        expected_sections = BOOK_SPECS[book_number]["sections"]
    if order_offset is None:
        order_offset = sum(BOOK_SPECS[n]["sections"] for n in range(1, book_number))
    require(order_offset >= 0, "Global order offset must not be negative")
    if source_name is None:
        source_name = f"assets/xml/bellum/Latin/book-{book_number:02}.xml"
    # Neither DTDs nor entity declarations are needed by this known source.
    require(b"<!DOCTYPE" not in xml_bytes.upper() and b"<!ENTITY" not in xml_bytes.upper(),
            "DTD/entity declarations are outside this pilot's accepted source format")
    try:
        parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True, insert_pis=True))
        root = ET.fromstring(xml_bytes, parser=parser)
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
    require(book_node.get("n") == str(book_number) and book_node.get("type") == "book"
            and book_node.get("subtype") == "Latin", "Book division does not match the requested Latin Bellum book")
    container(book_node, {"div2"})

    records: list[dict] = []
    paragraphs: list[dict] = []
    excluded: list[dict] = []
    all_raw: list[str] = []
    all_restored: list[str] = []
    expected_running: list[str] = []
    seen_ids: set[str] = set()
    seen_sections: set[int] = set()
    seen_chapters: set[int] = set()
    title_count = 0
    milestone_count = 0
    citation_paragraph_count = 0
    continuation_paragraph_count = 0
    active_record: dict | None = None
    paragraph_separators: list[dict] = []

    for name in ("teiHeader", "standOff"):
        element = root.find(q(name))
        if element is not None:
            text = "".join(element.itertext())
            excluded.append({"kind": name, "reason": "outside running text",
                             "textCharacters": len(text), "textSha256": sha(text),
                             "elementCounts": dict(sorted(Counter(
                                 el.tag.removeprefix(f"{{{TEI}}}")
                                 for el in element.iter() if isinstance(el.tag, str)
                             ).items()))})

    for chapter_node in book_node:
        require(chapter_node.get("type") == "chapter", "Expected a chapter div2")
        chapter_number = chapter_node.get("n", "")
        require(re.fullmatch(r"0|[1-9]\d*", chapter_number) is not None, "Invalid chapter number")
        chapter = int(chapter_number)
        require(chapter not in seen_chapters, f"Duplicate chapter {chapter}")
        seen_chapters.add(chapter)
        require(chapter_node.get(XML_ID) == f"latin-bellum{book_number}-chapter{chapter}",
                f"Chapter {chapter}: unexpected xml:id")
        container(chapter_node, {"p"})
        ordinal = 0

        for paragraph in chapter_node:
            source_id = paragraph.get(XML_ID)
            if source_id is None:
                require(book_number == 1 and chapter == 0 and ordinal == 0 and title_count == 0
                        and not records and not len(paragraph)
                        and (paragraph.text or "").strip() == BOOK_TITLE,
                        "Unrecognised unnumbered paragraph; refusing to omit possible running text")
                title_count += 1
                excluded.append({"kind": "book-title", "reason": "unnumbered book title",
                                 "chapter": chapter, "text": paragraph.text,
                                 "textSha256": sha(paragraph.text or "")})
                continue

            ordinal += 1
            require(source_id not in seen_ids, f"Duplicate paragraph xml:id {source_id}")
            seen_ids.add(source_id)
            match = re.fullmatch(rf"latin-bellum{book_number}-num([1-9]\d*)", source_id)
            require(match is not None, f"Unexpected paragraph xml:id {source_id}")
            section = int(match.group(1))
            initial = paragraph.text or ""
            has_niese_label = NUMBER_LABEL.match(initial) is not None
            if has_niese_label:
                citation_paragraph_count += 1
            else:
                require(CONTINUATION_PARAGRAPHS.get(book_number, {}).get(source_id) == section,
                        f"Section {section}: missing leading [N] label on an unrecognised continuation paragraph")
                require(active_record is not None and active_record["section"] == section
                        and active_record["chapter"] == chapter,
                        f"{source_id}: continuation does not follow its established Niese section")
                continuation_paragraph_count += 1
            removed_prefix, removals = strip_prefix(initial, section, chapter, ordinal,
                                                    has_niese_label=has_niese_label)

            # Every accepted paragraph child is an empty Niese milestone.
            # Each tail is exactly the interval that begins at that milestone.
            fragments = [(section, "paragraph" if has_niese_label else "continuation",
                          initial[len(removed_prefix):])]
            for marker in paragraph:
                require(marker.tag == q("milestone"), f"Unexpected substantive tag {marker.tag} in {source_id}")
                require(marker.get("unit") == "niese", f"Unexpected milestone unit in {source_id}")
                raw_number = marker.get("n", "")
                require(re.fullmatch(r"[1-9]\d*", raw_number) is not None,
                        f"Invalid milestone number in {source_id}")
                require(not len(marker) and not (marker.text or ""),
                        f"Niese milestone contains text in {source_id}")
                require(set(marker.attrib) == {"unit", "n"},
                        f"Unexpected milestone attributes in {source_id}")
                fragments.append((int(raw_number), "milestone", marker.tail or ""))
                milestone_count += 1

            raw_text = "".join(paragraph.itertext())
            running_text = raw_text[len(removed_prefix):]
            restored = removed_prefix
            cursor = len(removed_prefix)
            spans: list[dict] = []
            paragraph_words: list[str] = []

            for number, kind, fragment in fragments:
                if kind != "continuation":
                    if active_record is not None:
                        require(bool(active_record["text"]), f"Empty Niese section {active_record['section']}")
                    require(number not in seen_sections, f"Duplicate Niese section {number}")
                    seen_sections.add(number)
                    # Field order is retained from the approved Book I pilot,
                    # so its complete corpus shard remains byte-identical.
                    active_record = {"id": f"bellum-latin-cardwell-{book_number}-{number}",
                                     "work": "bellum", "book": book_number, "section": number,
                                     "language": "Latin", "edition": "Cardwell (1837)",
                                     "chapter": chapter, "text": "",
                                     "url": f"/bellum-judaicum/?book={book_number}&niese={number}",
                                     "sourceId": source_id, "order": order_offset + len(records)}
                    records.append(active_record)
                require(active_record is not None and active_record["section"] == number,
                        f"No established Niese section for {source_id}")
                text = fragment.strip()
                require(bool(text) or kind == "continuation", f"Empty Niese section {number}")
                left_count = len(fragment) - len(fragment.lstrip()) if text else len(fragment)
                right_count = len(fragment) - len(fragment.rstrip()) if text else 0
                left = fragment[:left_count]
                right = fragment[len(fragment) - right_count:] if right_count else ""
                require(left + text + right == fragment, f"Section {number}: failed exact restoration")

                # The XML paragraph boundary is represented as whitespace in
                # a section that continues into the next physical paragraph.
                # No punctuation or word is inserted or removed. A label-only
                # continuation, such as III.3's following paragraph, adds none.
                separator = PARAGRAPH_SEPARATOR if text and active_record["text"] else ""
                if separator:
                    paragraph_separators.append({"section": number, "sourceId": source_id,
                                                 "recordTextStart": len(active_record["text"]),
                                                 "recordTextEnd": len(active_record["text"]) + len(separator),
                                                 "separator": separator})
                    active_record["text"] += separator
                record_text_start = len(active_record["text"])
                active_record["text"] += text
                spans.append({"section": number, "startKind": kind,
                              "sourceTextStart": cursor, "sourceTextEnd": cursor + len(fragment),
                              "textStart": cursor + left_count,
                              "textEnd": cursor + len(fragment) - right_count,
                              "recordTextStart": record_text_start,
                              "recordTextEnd": len(active_record["text"]),
                              "separatorBefore": separator,
                              "contributesText": bool(text),
                              "leadingWhitespace": left, "trailingWhitespace": right,
                              "rawFragmentSha256": sha(fragment), "textSha256": sha(text)})
                cursor += len(fragment)
                restored += left + text + right
                paragraph_words.extend(WORD.findall(text))

            require(restored == raw_text, f"{source_id}: raw paragraph restoration failed")
            require(paragraph_words == WORD.findall(running_text),
                    f"{source_id}: section boundary splits or changes a word")
            require(cursor == len(raw_text), f"{source_id}: interval coverage is incomplete")
            all_raw.append(raw_text)
            all_restored.append(restored)
            expected_running.append(running_text)
            paragraphs.append({"sourceId": source_id, "chapter": chapter,
                               "subchapter": ordinal, "rawTextCharacters": len(raw_text),
                               "establishesNieseStart": has_niese_label,
                               "rawTextSha256": sha(raw_text), "removedPrefix": removed_prefix,
                               "prefixRemovals": removals, "sections": spans,
                               "exactRestorationVerified": True, "wordSequenceVerified": True})

    require(title_count == (1 if book_number == 1 else 0), "Unexpected number of unnumbered book titles")
    require(active_record is not None and bool(active_record["text"]), "Final Niese section is empty")
    expected = set(range(1, expected_sections + 1))
    missing = sorted(expected - seen_sections)
    unexpected = sorted(seen_sections - expected)
    require(not missing and not unexpected,
            f"Niese coverage differs: missing={missing}, unexpected={unexpected}")
    require(len(records) == citation_paragraph_count + milestone_count,
            "Paragraph-start plus milestone count does not equal section count")
    if expected_paragraphs is not None:
        require(len(paragraphs) == expected_paragraphs, "Unexpected number of numbered paragraphs")
    if expected_citation_paragraphs is not None:
        require(citation_paragraph_count == expected_citation_paragraphs,
                "Unexpected number of Niese paragraph starts")
    if expected_milestones is not None:
        require(milestone_count == expected_milestones, "Unexpected number of internal milestones")

    # Reconstruct again from the finished output records and their recorded
    # offsets, including the section that spans two physical paragraphs.
    by_section = {record["section"]: record for record in records}
    all_restored = []
    for audit, raw_text in zip(paragraphs, all_raw, strict=True):
        restored = audit["removedPrefix"]
        for span in audit["sections"]:
            actual_text = by_section[span["section"]]["text"][span["recordTextStart"]:span["recordTextEnd"]]
            restored += span["leadingWhitespace"] + actual_text + span["trailingWhitespace"]
        require(restored == raw_text, f"{audit['sourceId']}: final indexed output cannot restore source paragraph")
        all_restored.append(restored)

    indexed_words = [word for record in records for word in WORD.findall(record["text"])]
    source_words = [word for text in expected_running for word in WORD.findall(text)]
    require(indexed_words == source_words, "Full word-sequence coverage failed")
    source_content = re.sub(r"\s", "", "".join(expected_running))
    indexed_content = re.sub(r"\s", "", "".join(record["text"] for record in records))
    require(source_content == indexed_content, "Non-whitespace content or punctuation changed")
    removal_counts = Counter(item["kind"] for p in paragraphs for item in p["prefixRemovals"])
    section_numbers = [record["section"] for record in records]

    report = {
        "schemaVersion": 2,
        "status": "PASS",
        "scope": {"work": "Bellum Judaicum", "book": book_number, "language": "Latin",
                  "edition": "Cardwell (1837)", "unit": "Niese section"},
        "source": {"path": source_name, "sha256": sha(xml_bytes), "bytes": len(xml_bytes)},
        "rules": {
            "bodyTagsAccepted": ["body", "div1", "div2", "p", "milestone"],
            "sourceOrderPreserved": True,
            "paragraphStartRequiresMatchingVisibleNieseLabel": True,
            "textTransformations": "Remove verified leading citation/chapter/subchapter labels; trim section-fragment edge whitespace; represent a paragraph boundary within one section as two newlines.",
            "editorialChanges": "None. Original spelling, punctuation and internal whitespace are retained.",
            "specialPunctuation": "Punctuation outside the verified structural labels is retained, including the Book I dash after CAP. XI. and apostrophe after CAP. XVI.",
            "tokenCountDefinition": r"Unicode alphanumeric runs matched by [^\W_]+; no case folding or stemming.",
            "offsetDefinition": "Zero-based Python Unicode character offsets, end exclusive: sourceText/text offsets refer to the paragraph's concatenated XML text; recordText offsets refer to the indexed section text.",
            "orderDefinition": "Source section order within each book; global order continues across Books I–VII.",
            "readerRoute": f"/bellum-judaicum/?book={book_number}&niese={{section}}",
            "readerRouteEvidence": "assets/js/renderTei.js: Bellum uses Cardwell by default and accepts book/niese URL parameters."
        },
        "counts": {"bodyParagraphs": len(paragraphs) + title_count,
                   "numberedParagraphs": len(paragraphs),
                   "citationParagraphs": citation_paragraph_count,
                   "continuationParagraphs": continuation_paragraph_count,
                   "internalMilestones": milestone_count,
                   "sections": len(records), "chapterDivisionsIncludingPrologue": len(seen_chapters),
                   "excludedBookTitles": title_count, "runningWordTokens": len(indexed_words),
                   "removedPrefixCharacters": sum(len(p["removedPrefix"]) for p in paragraphs),
                   "paragraphSeparatorsInserted": len(paragraph_separators),
                   "prefixRemovals": dict(sorted(removal_counts.items()))},
        "coverage": {
            "missingSections": missing, "unexpectedSections": unexpected, "duplicateSections": [],
            "completeRange": [1, expected_sections],
            "globalOrderRange": [order_offset, order_offset + len(records) - 1],
            "sourceOrderIsConsecutive": section_numbers == list(range(1, expected_sections + 1)),
            "paragraphsExactlyRestored": len(paragraphs),
            "rawParagraphSequenceSha256": sha("\n".join(all_raw)),
            "restoredParagraphSequenceSha256": sha("\n".join(all_restored)),
            "sourceWordSequenceSha256": sha("\n".join(source_words)),
            "indexedWordSequenceSha256": sha("\n".join(indexed_words)),
            "sourceNonWhitespaceContentSha256": sha(source_content),
            "indexedNonWhitespaceContentSha256": sha(indexed_content),
            "wordSequencePreserved": True, "nonWhitespaceContentPreserved": True,
            "allSectionTextsNonempty": True,
        },
        "excluded": excluded,
        "paragraphSeparators": paragraph_separators,
        "paragraphs": paragraphs,
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
    """Validate all books before writing the combined corpus and audited shards."""
    combined: list[dict] = []
    books: list[dict] = []
    book_reports: list[dict] = []
    artifacts: dict[str, bytes] = {}
    totals: Counter = Counter()
    prefix_totals: Counter = Counter()

    for book_number, spec in BOOK_SPECS.items():
        source_path = f"assets/xml/bellum/Latin/book-{book_number:02}.xml"
        records, report = extract_document(
            (source_root / source_path).read_bytes(), book_number=book_number,
            order_offset=len(combined), expected_sections=spec["sections"],
            expected_paragraphs=spec["numberedParagraphs"],
            expected_citation_paragraphs=spec["citationParagraphs"],
            expected_milestones=spec["milestones"], source_name=source_path)
        corpus_path = f"data/book-{book_number:02}.corpus.json"
        report_path = f"data/book-{book_number:02}.extraction-report.json"
        corpus_bytes = json_bytes(records)
        report_bytes = json_bytes(report)
        if book_number == 1:
            require(sha(corpus_bytes) == BOOK_ONE_PILOT_CORPUS_SHA256,
                    "Book I corpus differs from the approved pilot; review before replacing it")
        artifacts[corpus_path] = corpus_bytes
        artifacts[report_path] = report_bytes
        books.append({"book": book_number, "status": report["status"],
                      "source": report["source"], "counts": report["counts"],
                      "orderStart": len(combined), "orderEnd": len(combined) + len(records) - 1,
                      "corpus": {"path": corpus_path, "sha256": sha(corpus_bytes),
                                 "bytes": len(corpus_bytes), "records": len(records)},
                      "extractionReport": {"path": report_path, "sha256": sha(report_bytes),
                                           "bytes": len(report_bytes)}})
        combined.extend(records)
        book_reports.append(report)
        for key, value in report["counts"].items():
            if key == "prefixRemovals":
                prefix_totals.update(value)
            else:
                totals[key] += value

    require(len(combined) == 4001, "Combined corpus must contain exactly 4,001 sections")
    require(len({record["id"] for record in combined}) == len(combined), "Duplicate global search ID")
    require([record["order"] for record in combined] == list(range(4001)), "Global section order is not continuous")
    combined_bytes = json_bytes(combined)
    artifacts["corpus.json"] = combined_bytes
    combined_report = {
        "schemaVersion": 2,
        "status": "PASS",
        "scope": {"work": "Bellum Judaicum", "books": list(BOOK_SPECS),
                  "language": "Latin", "edition": "Cardwell (1837)", "unit": "Niese section"},
        "counts": {"books": len(books), **dict(totals),
                   "prefixRemovals": dict(sorted(prefix_totals.items()))},
        "coverage": {
            "paragraphsExactlyRestored": sum(report["coverage"]["paragraphsExactlyRestored"] for report in book_reports),
            "wordSequencePreserved": all(report["coverage"]["wordSequencePreserved"] for report in book_reports),
            "nonWhitespaceContentPreserved": all(report["coverage"]["nonWhitespaceContentPreserved"] for report in book_reports),
            "globalIdsUnique": True, "globalOrderIsConsecutive": True,
            "globalOrderRange": [0, 4000], "bookOnePilotCorpusUnchanged": True,
            "completeSectionCoverageByBook": {str(book): [1, spec["sections"]] for book, spec in BOOK_SPECS.items()},
            "allSectionTextsNonempty": all(bool(record["text"]) for record in combined),
        },
        "corpus": {"path": "corpus.json", "sha256": sha(combined_bytes),
                   "bytes": len(combined_bytes), "records": len(combined)},
        "books": books,
    }
    artifacts["extraction-report.json"] = json_bytes(combined_report)
    for name, content in artifacts.items():
        write_bytes(output_dir / name, content)
    return combined_report


def main() -> None:
    directory = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=directory.parent.parent,
                        help="Repository root containing assets/xml/bellum/Latin/book-01.xml through book-07.xml")
    parser.add_argument("--output-dir", type=Path, default=directory)
    args = parser.parse_args()
    report = build_corpus(args.source_root, args.output_dir)
    print(json.dumps({"status": report["status"], "corpusSha256": report["corpus"]["sha256"],
                      "counts": report["counts"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
