"""Project the published Froben running text into searchable printed pages."""
from argparse import ArgumentParser
from pathlib import Path
import json
import unicodedata

from extract import json_bytes, require, roman, sha, write_bytes

HERE = Path(__file__).resolve().parent
COLLECTION = "antiquities-latin-froben1524"
SOURCE = Path("assets/data/antiquities-froben1524")


def words(text):
    """Count Unicode L/N starts with L/M/N continuations, as in the index."""
    result = []
    word = ""
    for char in text:
        category = unicodedata.category(char)[0]
        if category in "LN" or (word and category == "M"):
            word += char
        elif word:
            result.append(word)
            word = ""
    return result + ([word] if word else [])


def page_texts(data):
    """Clip shared opening and closing pages to the reader's book boundaries."""
    rows = [(page, row) for page in data["pages"] for row in page["rows"]]
    row_index = {(page["image"], row["id"]): i for i, (page, row) in enumerate(rows)}
    terminal = data["pages"][-1]["span"]["end"]
    row_index.setdefault(tuple(terminal[:2]), len(rows))

    def point(location):
        index = row_index[tuple(location[:2])]
        offset = location[2]
        require(0 <= offset <= (len(rows[index][1]["text"]) if index < len(rows) else 0),
                f"Invalid Froben character offset: {location}")
        return index, offset

    span, = data["book"]["spans"]
    (first, start), (last, end) = (point(span[key]) for key in ("start", "end"))
    pages = {}
    for index in range(first, last + bool(end)):
        page, row = rows[index]
        if row["role"] != "body" or row.get("joinedInto"):
            continue
        line = row["text"][start if index == first else 0:end if index == last else None].strip()
        if line:
            pages.setdefault(page["image"], (page, []))[1].append(line)
    pages = list(pages.values())

    source = "\n".join(line for _, lines in pages for line in lines)
    expected = source.replace("¬\n", "").replace("\n", " ")
    # Attribute a word continued onto the next page to the page where it starts.
    for (_, lines), (_, following) in zip(pages, pages[1:]):
        if lines[-1].endswith("¬"):
            parts = following[0].split(maxsplit=1)
            require(len(parts) == 2 and not parts[0].endswith("¬"), "Unresolved Froben page continuation")
            lines[-1] = lines[-1][:-1] + parts[0]
            following[0] = parts[1]

    require(bool(pages) and not pages[-1][1][-1].endswith("¬"),
            f"Unresolved end of Froben division {data['book']['id']}")
    projected = [(page, "\n".join(lines).replace("¬\n", "").replace("\n", " ")) for page, lines in pages]
    require(" ".join(text for _, text in projected) == expected,
            f"Froben pagination changed the source text for {data['book']['id']}")
    return projected


def coverage(records):
    return {
        "pagesExactlyRestored": len(records),
        "wordSequencePreserved": True,
        "nonWhitespaceContentPreserved": True,
        "globalIdsUnique": len({record["id"] for record in records}) == len(records),
        "globalOrderIsConsecutive": all(right["order"] == left["order"] + 1 for left, right in zip(records, records[1:])),
        "allSectionTextsNonempty": all(record["text"] for record in records),
    }


def build(root, output):
    manifest = json.loads((HERE / "config" / f"{COLLECTION}.json").read_bytes())
    combined, book_reports, outputs = [], [], {}

    def fingerprint(filename, value):
        data = json_bytes(value)
        outputs[filename] = data
        return {"path": f"data/{COLLECTION}/{filename}", "sha256": sha(data), "bytes": len(data)}

    for spec in manifest["books"]:
        number = spec["number"]
        filename = f"book-{number:02}"
        sources = []
        records = []
        names = ["preface", filename] if number == 1 else [filename]
        for name in names:
            relative = SOURCE / f"{name}.json"
            raw = (root / relative).read_bytes()
            data = json.loads(raw)
            proem = name == "preface"
            book_id = "preface" if proem else str(number)
            require(data["edition"] == manifest["edition"] and data["book"]["id"] == book_id,
                    f"Unexpected Froben source identity: {relative}")
            sources.append({"path": relative.as_posix(), "sha256": sha(raw), "bytes": len(raw)})
            for page, text in page_texts(data):
                require("¬" not in text and "[[WITHHELD]]" not in text, f"Unresolved text on {page['id']}")
                label = f"{'Proem' if proem else roman(number)}, {page['display']}"
                records.append({
                    "id": f"{COLLECTION}-{book_id}-{page['image']}",
                    "work": manifest["work"], "language": manifest["language"], "edition": manifest["edition"],
                    "book": number, "section": len(records) + 1, "order": len(combined) + len(records),
                    "citationScheme": manifest["citationScheme"], "citationLabel": label,
                    "citationUnitCitation": label, "sourceImage": page["image"],
                    **({"division": "proem"} if proem else {}),
                    **({"breakBefore": True} if number == 1 and not proem and records[-1].get("division") == "proem" else {}),
                    "text": text,
                })

        require(len(records) == spec["sections"], f"Froben page count differs in {spec['label']}")
        corpus = {**fingerprint(f"{filename}.corpus.json", records), "records": len(records)}
        report = {
            "status": "PASS", "book": number, "source": sources[-1], "additionalSources": sources[:-1],
            "corpus": corpus,
            "counts": {"pages": len(records), "runningWordTokens": sum(len(words(record["text"])) for record in records)},
            "coverage": {**coverage(records), "missingSections": [], "unexpectedSections": [], "duplicateSections": []},
        }
        book_reports.append({**report, "extractionReport": fingerprint(f"{filename}.extraction-report.json", report)})
        combined.extend(records)

    report = {
        "status": "PASS", "collection": COLLECTION,
        "corpus": {**fingerprint("corpus.json", combined), "records": len(combined)},
        "counts": {"books": len(book_reports), "sections": len(combined), "pages": len(combined),
                   "runningWordTokens": sum(book["counts"]["runningWordTokens"] for book in book_reports)},
        "coverage": coverage(combined), "books": book_reports,
    }
    fingerprint("extraction-report.json", report)
    require(all(report["coverage"].values()), "Froben corpus coverage check failed")
    for name, data in outputs.items():
        write_bytes(output / name, data)
    return report["counts"]


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=HERE.parent.parent)
    parser.add_argument("--output-dir", type=Path, default=HERE / "data" / COLLECTION)
    args = parser.parse_args()
    print(json.dumps(build(args.source_root, args.output_dir)))
