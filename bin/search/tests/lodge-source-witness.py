"""Independent DOM check of the Lodge main-text projection."""
import json
from pathlib import Path
import re
import sys
from xml.dom import Node, minidom

NS = "http://www.tei-c.org/ns/1.0"
ANCHOR = re.compile(r"\x01([0-9]+):([^\x02]+)\x02")


def text(node):
    if node.nodeType == Node.TEXT_NODE:
        return node.data
    return "".join(text(child) for child in node.childNodes)


def witness(filename):
    doc = minidom.parse(str(filename))
    body = doc.getElementsByTagNameNS(NS, "body")[0]
    for element in reversed(list(body.getElementsByTagNameNS(NS, "*"))):
        tag = element.localName
        role = element.getAttribute("type").removeprefix("tcp-") if tag == "seg" else tag
        parent = element.parentNode

        def replace(value):
            parent.replaceChild(doc.createTextNode(value), element)

        if tag == "milestone":
            if element.getAttribute("unit") == "niese":
                replace(f"\x01{element.getAttribute('n')}:{element.getAttribute('xml:id')}\x02")
            else:
                replace("")
        elif tag == "gap":
            anchor = "".join(match.group() for match in ANCHOR.finditer(text(element)))
            replace(anchor + ("\0" if element.getAttribute("reason") == "omitted" else "[…]"))
        elif role in ("head", "byline", "argument", "trailer", "note"):
            parent.removeChild(element)
        elif role == "list" and (tag == "seg" or parent.getAttribute("type") == "book"):
            parent.removeChild(element)
        elif tag == "g" and element.getAttribute("ref") == "char:EOLhyphen":
            parent.removeChild(element)
        elif role in ("p", "l", "item", "opener", "closer", "salute", "signed"):
            parent.insertBefore(doc.createTextNode(" "), element)
            parent.insertBefore(doc.createTextNode(" "), element.nextSibling)

    before, *parts = ANCHOR.split(text(body))
    assert not before.strip(), filename
    assert parts and len(parts) % 3 == 0, filename
    return [[int(section), identity, " ".join(prose.split()).replace("\0", "")]
            for section, identity, prose in zip(parts[::3], parts[1::3], parts[2::3])]


root = Path(sys.argv[1])
results = {name: witness(root / name) for name in sys.argv[2:]}
print(json.dumps(results, ensure_ascii=True, separators=(",", ":")))
