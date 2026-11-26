"""Project the approved Bellum transcription onto the website reader's data format."""

from argparse import ArgumentParser
from hashlib import sha256
import json
from pathlib import Path
from urllib.parse import urlsplit


DESTINATION = Path(__file__).resolve().parents[1] / "assets/data/bellum-froben1524/reader.json"
LAYERS = ("books", "chapters", "subchapters", "niese", "frobenBooks", "divisions")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def select(record):
    fields = ("id", "label", "book", "number", "kind", "frobenBook", "rubric")
    return {
        **{key: record[key] for key in fields if key in record},
        "spans": [{key: span[key] for key in ("start", "end")} for span in record["spans"]],
    }


def export(proof):
    raw = (proof / "draft/segmentation.json").read_bytes()
    source = json.loads(raw)
    validation = json.loads((proof / "validation.json").read_bytes())
    approved = json.loads((proof / "boundary-decisions.json").read_bytes())
    images = list(range(658, 918))
    require(validation["remainingImages"] == validation["boundaryReview"]["forDecision"] == 0 and not source["exceptions"],
            "The Froben draft still has an open review")
    require(source["editorial"]["reviewedImages"] == [page["image"] for page in source["pages"]] == images,
            "The publication source does not include all 260 reviewed scans")
    body = "".join(row["text"] for page in source["pages"] for row in page["rows"])
    digest = sha256(body.encode("utf-8")).hexdigest()
    require(digest == approved["bodySha256"] == source["editorial"]["bodySha256"], "The approved text checksum differs")
    require("[[WITHHELD]]" not in body, "The draft contains withheld text")

    pages = []
    for page in source["pages"]:
        link = urlsplit(page["facsimile"])
        require(link.scheme == "https" and link.hostname == "www.e-rara.ch"
                and link.path.startswith("/bau_1/content/pageview/") and link.path.rsplit("/", 1)[-1].isdigit(),
                f'Bad Basel facsimile link on image {page["image"]}')
        pages.append({
            **{key: page[key] for key in ("image", "id", "display", "span", "facsimile")},
            "rows": [{key: row[key] for key in ("id", "role", "text")} for row in page["rows"]],
            "marginalia": [row["text"].strip() for row in page["ancillaryRows"]
                           if row["role"] == "marginalia" and row["text"].strip()],
        })

    row_keys = [(p["image"], r["id"], len(r["text"])) for p in pages for r in p["rows"]]
    rank = {(image, id_): (i, width) for i, (image, id_, width) in enumerate(row_keys)}
    require(len(rank) == len(row_keys), "Duplicate Froben line")

    def position(point):
        row, width = rank[tuple(point[:2])]
        require(0 <= point[2] <= width, f"Invalid source coordinate {point}")
        return row, point[2]

    layers = {layer: [select(record) for record in source[layer]] for layer in LAYERS}
    require(len(layers["books"]) == 7 and len(layers["frobenBooks"]) == 8 and
            len(layers["niese"]) == 4001 and len(layers["divisions"]) == 138, "The Bellum navigation register differs")
    for selection in [record for entries in layers.values() for record in entries]:
        require(selection["spans"] and all(position(span["start"]) < position(span["end"])
                                           for span in selection["spans"]), f'Invalid span for {selection["id"]}')
    for page in pages:
        require(position(page["span"]["start"]) < position(page["span"]["end"]), f'Empty image {page["image"]}')
    niese = {item["id"]: item for item in layers["niese"]}
    for decision in approved["boundaries"]:
        if not (decision.get("options") and decision["decision"] == "move"):
            continue
        reviewed = next(record for record in source["niese"]
                        if record["referenceTextOffsets"][0] in decision["offsets"])
        require(niese[reviewed["id"]]["spans"][0]["start"] == decision["after"],
                f'The approved boundary for {reviewed["id"]} was lost')

    data = {"edition": "Froben 1524", "textSha256": digest, "sourceSha256": sha256(raw).hexdigest(), "pages": pages, **layers}
    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n"
    DESTINATION.write_text(rendered, encoding="utf-8", newline="\n")
    print(f"Exported {len(pages)} scans, {len(rank)} text lines, and {len(niese)} Niese sections.")


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("proof_folder", type=Path, help="Folder containing the approved transcript and validation records")
    export(parser.parse_args().proof_folder)
