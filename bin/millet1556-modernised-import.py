"""Export the reviewed Millet reading and its recorded correspondences for the viewer."""

import argparse
from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path


ASSETS = Path(__file__).resolve().parents[1] / "assets/data"
ACCEPTED = {"ACCEPTED", "ACCEPTED_WITH_UNCERTAINTY"}


def digest(value):
    return sha256(value.encode("utf-8") if isinstance(value, str) else value).hexdigest()


def joined_ranges(ranges):
    joined = []
    for start, end in sorted(ranges):
        if joined and start <= joined[-1][1]:
            joined[-1][1] = max(joined[-1][1], end)
        else:
            joined.append([start, end])
    return joined


def encode(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def export(corpus, historical):
    manifest_bytes = (corpus / "CORPUS_MANIFEST.json").read_bytes()
    release = json.loads((corpus / "RELEASE.json").read_bytes())
    assert release["state"] == "REVIEWED" and release["manifest_sha256"] == digest(manifest_bytes)
    manifest = json.loads(manifest_bytes)

    def pinned_rows(name):
        data = (corpus / name).read_bytes()
        assert digest(data) == manifest["file_pins"][name], name
        return [json.loads(line) for line in data.splitlines()]

    original = json.loads((historical / "manifest.json").read_bytes())
    scope = manifest["source_scope"]
    assert original["version"] == scope["source_release"]
    assert original["authority"]["master_xml_sha256"] == scope["authority"]["master"]["sha256"]
    assert original["authority"]["machine_data_sha256"] == scope["authority"]["alignment"]["sha256"]

    lines = {}
    fragments = {}
    for record in original["books"]:
        payload = (historical / record["path"]).read_bytes()
        # Git for Windows can convert the outer JSON line endings on checkout.
        if digest(payload) != record["sha256"]:
            payload = payload.replace(b"\r\n", b"\n")
        assert digest(payload) == record["sha256"], record["path"]
        book = json.loads(payload)
        lines.update((line["TEI_line_id"], line["text_exact"]) for line in book["lines"])
        for mapping in book["mappings"]:
            for position, fragment in enumerate(mapping["fragments"], 1):
                fragments[mapping["id"], position] = fragment

    books = defaultdict(list)
    units = {}
    word_count = 0
    for component in manifest["components"]:
        book = 1 if component["component"] == "prologue" else int(component["component"].split("_")[1])
        for row in pinned_rows(component["text"]):
            uid, text = row["unit_id"], row["modern_text"]
            assert uid not in units and row["state"] in ACCEPTED and digest(text) == row["modern_text_sha256"], uid
            spans = row["source_spans"]
            for span in spans:
                line = lines[span["tei_line_id"]]
                assert line[span["start_cp"]:span["end_cp"]] == span["text_exact"], span["tei_line_id"]
            entry = {
                "id": uid,
                "heading": row["kind"] == "heading",
                "text": text,
                "lines": list(dict.fromkeys(span["tei_line_id"] for span in spans)),
                "pages": list(dict.fromkeys(span["image_number"] for span in spans)),
                "notes": [[note["source_anchor"], note["text"]] for note in row["editorial_notes"]],
                "uncertain": row["state"] == "ACCEPTED_WITH_UNCERTAINTY",
                "correspondences": {},
            }
            assert not entry["uncertain"] or entry["notes"], uid
            units[uid] = entry
            books[book].append(entry)
            word_count += row["source_words"]
    assert word_count == scope["total_source_words"]
    assert len(units) == sum(manifest["states"].values())

    clips = defaultdict(list)
    for row in pinned_rows(manifest["structured_indices"]["canonical_targets"]):
        key = row["mapping_id"], row["inherited_position"]
        fragment = fragments[key]
        line_id = row["source_TEI_line_id"]
        assert fragment["line"] == line_id
        original_span = row["original_fragment"]
        assert (fragment["start_cp"], fragment["end_cp"]) == (original_span["start_cp"], original_span["end_cp"]), key
        start, end = row["source_clip_cp"]
        assert fragment["start_cp"] <= start < end <= fragment["end_cp"], key
        assert lines[line_id][start:end] == row["source_clip_exact"], key
        clips[key].append([start, end])
        entry = units[row["unit_id"]]
        assert line_id in entry["lines"], row["unit_id"]
        ranges = entry["correspondences"].setdefault(key[0], [])
        projection = row["book_projection"] if "book_projection" in row else row["tranche_projection"]
        for part in projection:
            for target in part["modern_targets"]:
                a, b = target["range"]
                assert 0 <= a <= b <= len(entry["text"]) and entry["text"][a:b] == target["text_exact"], row["unit_id"]
                if a < b:
                    ranges.append([a, b])
    assert set(clips) == set(fragments)
    for key, parts in clips.items():
        position = fragments[key]["start_cp"]
        for start, end in sorted(parts):
            assert start == position, key
            position = end
        assert position == fragments[key]["end_cp"], key
    for unit in units.values():
        unit["correspondences"] = {key: joined_ranges(ranges) for key, ranges in unit["correspondences"].items()}

    output = {}
    catalogue = []
    for book, passages in books.items():
        name = f"book-{book:02d}.json"
        output[name] = encode({"schema": "millet1556-modernised-book/1", "book": book, "passages": passages})
        catalogue.append({"book": book, "path": name, "sha256": digest(output[name])})
    output["manifest.json"] = encode({
        "schema": "millet1556-modernised-reader/1",
        "historical_release": original["version"],
        "reviewed_corpus_sha256": release["manifest_sha256"],
        "source_words": word_count,
        "books": catalogue,
    })
    return output, len(units)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("corpus", type=Path)
    parser.add_argument("--historical", type=Path, default=ASSETS / "deh-millet1556")
    parser.add_argument("--output", type=Path, default=ASSETS / "deh-millet1556-modernised")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    output, count = export(args.corpus, args.historical)
    if not args.check:
        args.output.mkdir(parents=True, exist_ok=True)
    for name, data in output.items():
        target = args.output / name
        if args.check:
            assert target.read_bytes() == data, name
        else:
            target.write_bytes(data)
    print(f"{count} reviewed passages in {len(output) - 1} books. The Prologue occurs once in Book I.")


if __name__ == "__main__":
    main()
