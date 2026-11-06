"""Export book-sized Antiquities reader data from an approved Froben candidate."""
from argparse import ArgumentParser
from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path


LAYERS = ("chapters", "subchapters", "alignmentUnits", "niese", "divisions")
DESTINATION = Path(__file__).resolve().parents[1] / "assets/data/antiquities-froben1524"


def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")


def selection(entry, exceptions):
    fields = ("id", "label", "kind", "spans", "status", "number", "printedChapter", "headingSpan", "location")
    item = {k: entry[k] for k in fields if k in entry}
    item["spans"] = [{k: span[k] for k in ("start", "end", "boundaryStatus") if k in span}
                     for span in item["spans"]]
    if "headingPlacement" in entry:
        item["headingBefore"] = entry["headingPlacement"]["proseStart"]
    if "approvedTranscription" in entry:
        item["approvedHeading"] = entry["approvedTranscription"]["text"]
    note = entry.get("parallelEvidence", {}).get("note") if entry.get("status") == "parallel-partial" else None
    if not item["spans"]:
        note = exceptions.get(entry.get("exception"), note)
    if note:
        item["note"] = note
    return item


def export(candidate, destination, checksum):
    books = candidate["books"]
    pages = candidate["pages"]
    assert [p["image"] for p in pages] == list(range(66, 658))
    assert [b["id"] for b in books] == ["preface", *(str(n) for n in range(1, 21))]
    rank = {}
    for page in pages:
        for row in page["rows"]:
            key = page["image"], row["id"]
            assert key not in rank and "[[WITHHELD]]" not in row["text"]
            rank[key] = len(rank), len(row["text"])

    def order(point):
        i, size = rank[tuple(point[:2])]
        assert 0 <= point[2] <= size, point
        return i, point[2]

    exceptions = {e["id"]: e["detail"] for e in candidate["exceptions"]}
    by_book = defaultdict(lambda: defaultdict(list))
    for layer in LAYERS:
        for item in candidate[layer]:
            by_book[item["book"]][layer].append(selection(item, exceptions))
    destination.mkdir(parents=True, exist_ok=True)
    for book in books:
        book_id = book["id"]
        start, end = (order(book["spans"][0][edge]) for edge in ("start", "end"))
        published_pages = []
        for p in pages:
            if start >= order(p["span"]["end"]) or order(p["span"]["start"]) >= end:
                continue
            assert Path(p["file"]).name == p["file"]
            exported = {k: p[k] for k in ("image", "id", "display", "span", "file", "signatures")}
            if p["image"] == 66:
                exported["display"] = "p. 1"
            exported["rows"] = [
                {k: r[k] for k in ("id", "text", "role", "joinedInto") if k in r} for r in p["rows"]
            ]
            published_pages.append(exported)
        assert published_pages
        locations = {(p["image"], row["id"]) for p in published_pages for row in p["rows"]}
        terminal = published_pages[-1]["span"]["end"]
        views = by_book[book_id]
        book_view = selection(book, exceptions)
        for item in [book_view, *[entry for layer in LAYERS for entry in views[layer]]]:
            intervals = item["spans"] + ([item["headingSpan"]] if "headingSpan" in item else [])
            for span in intervals:
                assert order(span["start"]) < order(span["end"]), item["id"]
                for point in span.values():
                    if isinstance(point, list):
                        assert tuple(point[:2]) in locations or point == terminal, (item["id"], point)
        name = "preface" if book_id == "preface" else f"book-{int(book_id):02}"
        write(destination / f"{name}.json", {
            "edition": "Froben 1524", "book": book_view, "pages": published_pages,
            **{layer: views[layer] for layer in LAYERS},
        })
    write(destination / "manifest.json", {
        "edition": "Froben 1524", "candidateSha256": checksum, "images": len(pages), "rows": len(rank),
        "books": [book["id"] for book in books],
        "nieseWithSpans": sum(bool(r["spans"]) for r in candidate["niese"]),
    })
    print(f"Exported {len(books)} books, {len(pages)} scans and {len(rank)} source rows")


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--sha256", required=True)
    args = parser.parse_args()
    raw = args.candidate.read_bytes()
    checksum = sha256(raw).hexdigest()
    if checksum != args.sha256.lower():
        raise SystemExit(f"Candidate checksum differs: {checksum}")
    export(json.loads(raw), DESTINATION, checksum)
