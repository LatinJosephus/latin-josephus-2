"""Index the running text of the reader's certified Lodge 1602 XML."""
from argparse import ArgumentParser
import json
from pathlib import Path
import re
import unicodedata
from xml.etree import ElementTree as ET

from extract import json_bytes, require, roman, sha, write_bytes

HERE = Path(__file__).resolve().parent
TEI = "{http://www.tei-c.org/ns/1.0}"
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"
PARATEXT = {"head", "byline", "argument", "trailer", "note"}
BLOCKS = {"p", "l", "item", "opener", "closer", "salute", "signed"}
GAP = "[…]"


def events(element):
    tag = element.tag.removeprefix(TEI)
    kind = element.get("type", "").removeprefix("tcp-") if tag == "seg" else tag
    if kind in PARATEXT or (kind == "list" and (
        tag == "seg" or any("Contents of the Chapters" in "".join(head.itertext())
                            for head in element.findall(TEI + "head"))
    )):
        return
    if tag == "milestone":
        if element.get("unit") == "niese":
            yield element
        return
    if tag == "gap":
        yield from (child for child in element.iter(TEI + "milestone") if child.get("unit") == "niese")
        yield element
        return
    if tag == "g" and element.get("ref") == "char:EOLhyphen":
        return
    if kind in BLOCKS:
        yield " "
    if element.text:
        yield element.text
    for child in element:
        yield from events(child)
        if child.tail:
            yield child.tail
    if kind in BLOCKS:
        yield " "


def count_words(text):
    total = 0
    in_word = False
    for char in text:
        category = unicodedata.category(char)[0]
        starts_word = category in "LN"
        total += starts_word and not in_word
        in_word = starts_word or (in_word and category == "M")
    return total


def project(raw, manifest, number, preface):
    body = ET.fromstring(raw).find(f"{TEI}text/{TEI}body")
    require(body is not None, "Lodge document has no TEI body")
    rows = []
    parts, gaps = [], []
    marker = None

    def finish():
        require(marker is not None, "Expected Lodge Niese marker")
        section = int(marker.get("n"))
        text = re.sub(r"\s+", " ", "".join(parts)).strip()
        omitted = [gap for gap in gaps if gap["reason"] == "omitted"]
        if omitted:
            require(manifest["work"] == "bellum" and number == 6 and section == 3
                    and text == "\0" and len(gaps) == 1, "Unexpected Lodge omission")
        record = {
            "id": f"{manifest['id']}-{number}-{section}",
            "sourceId": marker.get(XML_ID),
            "work": manifest["work"], "book": number, "section": section,
            "language": "English", "edition": manifest["edition"], "citationScheme": "niese",
            **({"division": "proem", "readerLink": {"params": {"book": "preface"}}} if preface else {}),
        }
        if gaps:
            value = ""
            offsets, markers = [], []
            chunks = text.split("\0")
            require(len(chunks) == len(gaps) + 1, "Lodge gap event count differs")
            for chunk, attributes in zip(chunks, gaps):
                value += chunk
                start = len(value.encode("utf-16-le")) // 2
                mark = "" if omitted else GAP
                offsets.append(start)
                markers.append({"kind": "tei-gap", "start": start, "end": start + len(mark),
                                "text": mark, "sourceAttributes": attributes})
                value += mark
            text = value + chunks[-1]
            record.update(textGaps=markers, phraseBreaks=sorted(set(offsets)))
        record["text"] = text
        if not text and not omitted:
            record["emptySource"] = {"kind": "empty-source-interval"}
        rows.append(record)

    for event in events(body):
        if isinstance(event, str):
            parts.append(event)
        elif event.tag == TEI + "milestone":
            if marker is not None:
                finish()
            else:
                require(not "".join(parts).strip() and not gaps, "Unaligned prose before the first Lodge section")
            marker = event
            parts, gaps = [], []
        else:
            require(event.tag == TEI + "gap", f"Unexpected Lodge text event: {event.tag}")
            gaps.append(dict(event.attrib))
            parts.append("\0")
    finish()
    return rows


def coverage(records):
    return {
        "sectionsExactlyRestored": len(records),
        "wordSequencePreserved": True,
        "nonWhitespaceContentPreserved": True,
        "globalIdsUnique": len({record["id"] for record in records}) == len(records),
        "globalOrderIsConsecutive": all(right["order"] == left["order"] + 1 for left, right in zip(records, records[1:])),
        "allSectionTextsNonempty": all(record["text"] for record in records),
    }


def build(root, output):
    manifest = json.loads((HERE / "config" / f"{output.name}.json").read_bytes())
    combined, reports, outputs = [], [], {}

    def fingerprint(filename, value):
        data = json_bytes(value)
        outputs[filename] = data
        return {"path": f"data/{manifest['id']}/{filename}", "sha256": sha(data), "bytes": len(data)}

    for spec in manifest["books"]:
        number = spec["number"]
        records, sources = [], []
        for relative in [*spec.get("additionalSources", []), spec["source"]]:
            raw = (root / relative).read_bytes()
            sources.append({"path": relative, "sha256": sha(raw), "bytes": len(raw)})
            preface = relative.endswith("/preface.xml")
            part = project(raw, manifest, number, preface)
            if records:
                part[0]["breakBefore"] = True
            records.extend(part)
        start, end = spec["sectionRange"]
        require([record["section"] for record in records] == list(range(start, end + 1)),
                f"Lodge Niese identities differ for {manifest['id']} Book {number}")
        require([record["section"] for record in records if not record["text"]] == spec.get("emptySections", spec.get("omittedSections", [])),
                f"Lodge omission inventory differs for {manifest['id']} Book {number}")
        for previous, record in zip(records, records[1:]):
            if not previous["text"] and record["text"]:
                record["breakBefore"] = True
        for index, record in enumerate(records, len(combined)):
            record["order"] = index
        stem = f"book-{number:02d}"
        corpus = {**fingerprint(f"{stem}.corpus.json", records), "records": len(records)}
        report = {
            "status": "PASS", "book": number, "source": sources[-1], "additionalSources": sources[:-1], "corpus": corpus,
            "counts": {"sections": len(records), "runningWordTokens": sum(count_words(row["text"]) for row in records)},
            "coverage": {**coverage(records), "completeRange": [start, end], "missingSections": [],
                         "unexpectedSections": [], "duplicateSections": []},
        }
        reports.append({**report, "extractionReport": fingerprint(f"{stem}.extraction-report.json", report)})
        combined.extend(records)
    report = {
        "status": "PASS", "collection": manifest["id"], "coverage": coverage(combined),
        "counts": {"books": len(reports), "sections": len(combined),
                   "runningWordTokens": sum(book["counts"]["runningWordTokens"] for book in reports)},
        "corpus": {**fingerprint("corpus.json", combined), "records": len(combined)}, "books": reports,
    }
    fingerprint("extraction-report.json", report)
    for name, data in outputs.items():
        write_bytes(output / name, data)
    return report["counts"]


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=HERE.parent.parent)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build(args.source_root, args.output_dir)))
