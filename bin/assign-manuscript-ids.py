#!/usr/bin/env python3
"""Assign unused LJ codes after adding catalogue rows, then commit the page and registry.

Run python bin/assign-manuscript-ids.py from the development checkout.
Retain registry entries for retired records, and keep each ljm-* row key with
its original record through changes to the shelfmark or other description.
"""

import json
from pathlib import Path
import re
from secrets import choice
from tempfile import NamedTemporaryFile


LETTERS = "ABCDEFGHJKMNPQRSTUVWXYZ"
CHARACTERS = LETTERS + "23456789"
CODE = re.compile(rf"LJ-[{LETTERS}][{CHARACTERS}]{{3}}")
ROW = re.compile(r'(<tr\b[^>]*\bid="ljm-([A-Z][0-9]+)"[^>]*>)(.*?</tr>)', re.S)
NAME = re.compile(r'(<span class="ljm-name">)(.*?)(</span>)', re.S)


def unique_keys(pairs):
    entries = dict(pairs)
    if len(entries) != len(pairs):
        raise ValueError("The manuscript ID registry contains a duplicate record key.")
    return entries


def load_registry(path):
    if not path.exists():
        return {}
    registry = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_keys)
    if not isinstance(registry, dict) or any(
        not isinstance(code, str) or not CODE.fullmatch(code) for code in registry.values()
    ):
        raise ValueError("The manuscript ID registry contains an invalid code.")
    if len(set(registry.values())) != len(registry):
        raise ValueError("The manuscript ID registry contains a duplicate code.")
    return registry


def next_code(issued):
    while True:
        suffix = choice(LETTERS) + "".join(choice(CHARACTERS) for _ in range(3))
        code = f"LJ-{suffix}"
        if code not in issued:
            return code


def add_label(row):
    opening, key, body = row.groups()
    anchor = f' {{% include manuscript-id.html record="{key}" %}}'
    names = list(NAME.finditer(body))
    if len(names) != 1:
        raise ValueError(f"{key} must have exactly one manuscript name.")
    name = names[0]
    if anchor in name[2]:
        return row[0]
    if "manuscript-id.html" in body:
        raise ValueError(f"{key} has a mismatched manuscript ID label.")
    return opening + body[:name.start(3)] + anchor + body[name.start(3):]


def replace_file(path, data):
    with NamedTemporaryFile(dir=path.parent, delete=False) as temporary:
        pending = Path(temporary.name)
        temporary.write(data)
    try:
        pending.replace(path)
    finally:
        pending.unlink(missing_ok=True)


def assign(page_path, registry_path):
    source = page_path.read_bytes()
    page = source.decode("utf-8")
    row_keys = [match[2] for match in ROW.finditer(page)]
    if not row_keys or len(row_keys) != len(set(row_keys)):
        raise ValueError("The catalogue has no manuscript row keys or has duplicate keys.")
    rendered_source = ROW.sub(add_label, page).encode("utf-8")
    registry = load_registry(registry_path)
    issued = set(registry.values())
    added = 0
    for key in row_keys:
        if key not in registry:
            code = next_code(issued)
            registry[key] = code
            issued.add(code)
            added += 1

    if page_path.read_bytes() != source:
        raise ValueError("The catalogue changed during assignment. Run the command again.")
    if added:
        data = json.dumps(registry, indent=2, sort_keys=True) + "\n"
        replace_file(registry_path, data.encode("utf-8"))
    if rendered_source != source:
        replace_file(page_path, rendered_source)
    return len(row_keys), added


def main():
    root = Path(__file__).resolve().parent.parent
    registry = root / "_data/manuscript_ids.json"
    lock = registry.with_suffix(".lock")
    try:
        handle = lock.open("x")
    except FileExistsError:
        raise SystemExit(f"Manuscript ID assignment is already locked at {lock}.") from None

    handle.close()
    try:
        count, added = assign(root / "_pages/manuscripts.html", registry)
        print(f"{count} catalogue records, {added} new manuscript IDs.")
    finally:
        lock.unlink()


if __name__ == "__main__":
    main()
