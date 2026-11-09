#!/usr/bin/env python3
"""Build the DEH reading editions from the site XML.

Requires Pandoc, ReportLab, and the regular, bold and italic Gentium TrueType
fonts (https://github.com/silnrsi/font-gentium/releases). Build before Jekyll:

    python bin/export-deh.py --font-dir path/to/Gentium-7.000

The four files go in assets/downloads/deh. Use --output-dir to stage them
elsewhere and --site-url to set the public reader links inside the books.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date
from html import escape, unescape
import json
import os
from pathlib import Path
import re
import subprocess
from tempfile import TemporaryDirectory
import xml.etree.ElementTree as ET

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import BaseDocTemplate, Frame, PageBreak, PageTemplate, Paragraph, Spacer
from reportlab.platypus.tableofcontents import TableOfContents


ROOT = Path(__file__).resolve().parent.parent
TEI = "{http://www.tei-c.org/ns/1.0}"
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"
TITLE = "De excidio Hierosolymitano"
AUTHOR = "Pseudo-Hegesippus"
PROJECT = "Latin Josephus Project"
LICENSE = "https://creativecommons.org/licenses/by-nc-sa/3.0/it/"
ROMANS = ("I", "II", "III", "IV", "V")
CHAPTER_COUNTS = (46, 18, 26, 33, 53)


@dataclass(frozen=True)
class Edition:
    directory: str
    language: str
    slug: str
    subtitle: str
    version: str
    released: date
    guide: str


LATIN = Edition(
    "Latin", "la", "deh-ussani-latin", "Latin text edited by Vincenzo Ussani (1932)",
    "Electronic edition, 2026", date(2026, 9, 9), "latin-deh",
)
ENGLISH = Edition(
    "English", "en", "deh-pollard-english", "English translation by R. M. Pollard",
    "Version 1.2, 2026", date(2026, 10, 31), "pollard",
)


@dataclass(frozen=True)
class Passage:
    id: str
    label: str
    text: str
    note: str | None
    note_number: int | None


@dataclass(frozen=True)
class Chapter:
    book: int
    number: int
    opening: str
    passages: list[Passage]
    online_link: str

    @property
    def id(self) -> str:
        return "prologue" if self.number == 0 else f"book-{self.book}-chapter-{self.number}"


def inline_text(node: ET.Element) -> str:
    """Render the inline conventions used in the two canonical reading texts."""
    parts = [escape(node.text or "")]
    for child in node:
        tag = child.tag.removeprefix(TEI)
        if tag == "supplied":
            parts.append(f"[{inline_text(child)}]")
        elif tag == "del":
            parts.append(f"<del>{inline_text(child)}</del>")
        elif tag == "unclear" and not "".join(child.itertext()).strip():
            parts.append("†")
        elif tag not in {"num", "pb", "lb", "note"}:
            raise ValueError(f"Unrecognised DEH inline element {child.tag}")
        parts.append(escape(child.tail or ""))
    return re.sub(r"[ \t\r\n]+", " ", "".join(parts)).strip()


def read_edition(edition: Edition, commentary: dict, site: str) -> list[Chapter]:
    chapters = []
    note_number = 0
    for book, (roman, count) in enumerate(zip(ROMANS, CHAPTER_COUNTS), 1):
        path = ROOT / "assets/xml/deh" / edition.directory / f"book-{book:02d}.xml"
        tree = ET.parse(path)
        if edition == ENGLISH:
            source_title = tree.findtext(f".//{TEI}title")
            if not source_title or not re.search(r"\bversion 1\.2\b", source_title):
                raise ValueError(f"Update the edition metadata for {path}")
        book_node = tree.find(f"./{TEI}text/{TEI}body/{TEI}div1")
        if book_node is None or book_node.get("n") != roman:
            raise ValueError(f"Unexpected book number in {path}")
        chapter_nodes = book_node.findall(TEI + "div2")
        expected = list(range(0 if book == 1 else 1, count + 1))
        if [int(node.attrib["n"]) for node in chapter_nodes] != expected:
            raise ValueError(f"Unexpected chapter order in {path}")
        for number, chapter_node in zip(expected, chapter_nodes):
            head = chapter_node.find(TEI + "head")
            opening = inline_text(head) if head is not None else ""
            if number <= 1 and not opening:
                raise ValueError(f"Missing opening heading for book {book}, chapter {number}")
            passages = []
            has_commentary = False
            for unit, p in enumerate(chapter_node.findall(TEI + "p"), 1):
                label = p.findtext(TEI + "num")
                expected_label = f"[{roman}.{number}.{unit}]" if number else f"[Prol.{unit}]"
                if label != expected_label:
                    raise ValueError(f"Expected {expected_label}, found {label}")
                id = p.attrib[XML_ID]
                latin_id = p.get("sameAs", id).removeprefix("#")
                has_commentary |= bool(commentary[latin_id]["notes"])
                notes = p.findall(TEI + "note")
                note = None
                if notes:
                    if len(notes) != 1 or notes[0].get("type") != "uncertainty":
                        raise ValueError(f"Unexpected note in {label}")
                    note = inline_text(notes[0])
                    note_number += 1
                passages.append(Passage(id, label, inline_text(p), note, note_number if note else None))
            url = f"{site}/deh/?book={book}&chapter={number}"
            if has_commentary:
                url += "&commentary=1"
            if edition == ENGLISH:
                url += "&english=pollard"
            if not passages or any(not p.text for p in passages):
                raise ValueError(f"Missing reading text for book {book}, chapter {number}")
            chapters.append(Chapter(book, number, opening, passages, url))
    ids = [p.id for chapter in chapters for p in chapter.passages]
    if len(ids) != 558 or len(set(ids)) != len(ids):
        raise ValueError(f"Unexpected passage count in the {edition.directory} edition")
    return chapters


def link(url: str, text: str) -> str:
    return f'<a href="{escape(url, quote=True)}">{text}</a>'


def credit_paragraphs(edition: Edition, site: str) -> list[str]:
    if edition == LATIN:
        credits = [
            "<i>Hegesippi qui dicitur Historiae libri V</i>, edited by Vincenzo Ussani "
            "(CSEL 66/1, Vienna and Leipzig, 1932). Electronic edition by R. M. Pollard "
            "for the Latin Josephus Project, 2026.",
            "Based on the digilibLT transcription DLT000241 (2014), with linguistic correction "
            "by Elisa Della Calce and Simone Mollea and XML encoding by Alice Borgna. "
            "The project text incorporates corrections and Ussani’s addenda. "
            + link(LICENSE, "Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Italy") + ".",
        ]
    else:
        credits = [
            "English translation from the project’s Latin text of Vincenzo Ussani’s edition "
            "(CSEL 66/1, 1932). Drafted with AI assistance under the supervision and editorial "
            "direction of Richard Matthew Pollard, who adjudicated and approved the revisions.",
            "Version 1.2 was approved on 31 October 2026. "
            "Linked endnotes contain the translator’s comparisons with Millet and Lauro.",
        ]
    return [
        *credits,
        "Cite by book, chapter and paragraph, or by Prologue paragraph. "
        "For example, <i>De excidio Hierosolymitano</i> III.17.1.",
        link(f"{site}/texts/{edition.guide}/", "About this edition")
        + " &nbsp;·&nbsp; " + link(f"{site}/deh/", "Online reader"),
    ]


def chapter_title(edition: Edition, chapter: Chapter) -> str:
    return f"{'Caput' if edition == LATIN else 'Chapter'} {chapter.number}"


def chapter_link(chapter: Chapter) -> str:
    label = "Online text and commentary" if "commentary=1" in chapter.online_link else "Online text"
    return link(chapter.online_link, label)


def build_epub(edition: Edition, chapters: list[Chapter], site: str, output: Path, pandoc: str) -> None:
    fragments = ['<h1 id="edition-credits" lang="en" epub:type="credits">Edition and citation</h1>']
    fragments.extend(f'<p lang="en">{p}</p>' for p in credit_paragraphs(edition, site))
    notes = []
    for chapter in chapters:
        if chapter.number == 0:
            fragments.append(f'<h1 id="{chapter.id}" epub:type="prologue">{chapter.opening}</h1>')
        else:
            if chapter.number == 1:
                fragments.append(f'<h1 id="book-{chapter.book}">{chapter.opening}</h1>')
            fragments.append(f'<h2 id="{chapter.id}">{chapter_title(edition, chapter)}</h2>')
        fragments.append(f'<p class="online" lang="en">{chapter_link(chapter)}</p>')
        for p in chapter.passages:
            marker = ""
            if p.note:
                note_id = f"translation-note-{p.note_number}"
                marker = f' <sup><a href="#{note_id}" epub:type="noteref">[{p.note_number}]</a></sup>'
                back = link(f"#{p.id}", p.label)
                notes.append(f'<p><span id="{note_id}">{p.note_number}. {back}</span> {p.note}</p>')
            fragments.append(
                f'<p><span class="citation" id="{p.id}">{p.label}</span> {p.text}{marker}</p>'
            )
    if notes:
        fragments.append('<h1 id="translation-notes" epub:type="endnotes">Translation notes</h1>')
        fragments.extend(notes)

    html = output.parent / "reading.html"
    html.write_text("\n".join(fragments), encoding="utf-8")
    metadata = {
        "title": TITLE,
        "subtitle": f"{edition.subtitle}. {edition.version}.",
        "author": AUTHOR,
        "publisher": PROJECT,
        "identifier": f"urn:latin-josephus:{edition.slug}:{edition.released.isoformat()}",
        "lang": edition.language,
        "date": edition.released.isoformat(),
        "description": "Prologue and all five books with Ussani’s passage references.",
    }
    if edition == LATIN:
        metadata["rights"] = f"Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Italy. {LICENSE}"
    metadata_file = output.parent / "metadata.json"
    metadata_file.write_text(json.dumps(metadata, ensure_ascii=False), encoding="utf-8")
    env = dict(os.environ, SOURCE_DATE_EPOCH=str((edition.released - date(1970, 1, 1)).days * 86400))
    subprocess.run(
        [
            pandoc, str(html), "--from=html", "--to=epub3",
            "--toc", "--toc-depth=2", "--split-level=2",
            "--metadata-file", str(metadata_file),
            "--css", str(Path(__file__).with_name("deh-epub.css")),
            "--output", str(output),
        ],
        check=True,
        env=env,
    )


class SectionHeading(Paragraph):
    def __init__(self, text, style, label, key, level=0):
        super().__init__(text, style)
        self.label = label
        self.key = key
        self.level = level

    def draw(self):
        self.canv.bookmarkHorizontal(self.key, 0, self.height + 5)
        super().draw()


class ReadingPDF(BaseDocTemplate):
    def beforeDocument(self):
        self.running_head = ""

    def afterFlowable(self, flowable):
        if isinstance(flowable, SectionHeading):
            self.canv.addOutlineEntry(flowable.label, flowable.key, flowable.level, closed=True)
            if flowable.level == 0:
                self.running_head = flowable.label
                if flowable.key != "contents":
                    self.notify("TOCEntry", (0, flowable.label, self.page, flowable.key))


def register_fonts(font_dir: Path) -> None:
    for suffix, name in (("Regular", "Gentium"), ("Bold", "Gentium-Bold"), ("Italic", "Gentium-Italic")):
        pdfmetrics.registerFont(TTFont(name, str(font_dir / f"Gentium-{suffix}.ttf")))
    pdfmetrics.registerFontFamily("Gentium", normal="Gentium", bold="Gentium-Bold", italic="Gentium-Italic")


def build_pdf(edition: Edition, chapters: list[Chapter], site: str, output: Path) -> None:
    ink = colors.HexColor("#202326")
    secondary = colors.HexColor("#414b57")
    rule = colors.HexColor("#bec5cc")
    width, height = LETTER
    inset = 83
    body = ParagraphStyle(
        "Body", fontName="Gentium", fontSize=11.7, leading=15.1, textColor=ink,
        spaceAfter=7.5, allowWidows=0, allowOrphans=0,
    )
    small = ParagraphStyle("Small", parent=body, fontSize=10, leading=13, textColor=secondary)
    cover = ParagraphStyle("Cover", parent=body, fontName="Gentium-Italic",
                           fontSize=38, leading=40, spaceAfter=18)
    main_heading = ParagraphStyle(
        "Part", parent=body, fontName="Gentium-Bold", fontSize=25, leading=30,
        spaceAfter=17, keepWithNext=True,
    )
    chapter_heading = ParagraphStyle(
        "Chapter", parent=body, fontName="Gentium-Bold", fontSize=15, leading=18,
        spaceBefore=12, spaceAfter=2, keepWithNext=True,
    )
    chapter_credit = ParagraphStyle("Online", parent=small, spaceAfter=8, keepWithNext=True)
    doc = ReadingPDF(
        str(output), pagesize=LETTER, title=TITLE, author=AUTHOR, creator=PROJECT,
        subject=f"{edition.subtitle}. {edition.version}.", invariant=1,
    )

    def running_matter(canvas, current):
        if current.page == 1:
            return
        canvas.saveState()
        canvas.setFont("Gentium", 9)
        canvas.setFillColor(secondary)
        canvas.drawString(inset, height - 45, TITLE)
        canvas.drawRightString(width - inset, height - 45, current.running_head)
        canvas.setStrokeColor(rule)
        canvas.setLineWidth(0.45)
        canvas.line(inset, height - 52, width - inset, height - 52)
        canvas.drawCentredString(width / 2, 36, str(current.page))
        canvas.restoreState()

    frame = Frame(inset, 60, width - 2 * inset, height - 126,
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates(PageTemplate(id="reading", frames=[frame], onPageEnd=running_matter))
    contents = TableOfContents()
    contents.levelStyles = [
        ParagraphStyle("Contents entry", parent=body, fontSize=13, leading=21, spaceBefore=7)
    ]
    contents.dotsMinLevel = 0
    story = [
        Spacer(1, 92), Paragraph(PROJECT.upper(), small), Spacer(1, 27),
        Paragraph(AUTHOR, body), Paragraph(TITLE, cover),
        Paragraph(edition.subtitle, body), Paragraph(edition.version, small),
        Paragraph("Prologue and all five books", small), Spacer(1, 20),
        *[Paragraph(p, small) for p in credit_paragraphs(edition, site)],
        PageBreak(), SectionHeading("Contents", main_heading, "Contents", "contents"), contents,
        Spacer(1, 22), Paragraph("The PDF bookmarks also list each chapter.", small),
    ]
    notes = []
    for chapter in chapters:
        if chapter.number <= 1:
            label = "Prologue" if chapter.number == 0 else f"Book {ROMANS[chapter.book - 1]}"
            key = "prologue" if chapter.number == 0 else f"book-{chapter.book}"
            story += [PageBreak(), SectionHeading(chapter.opening, main_heading, label, key)]
        if chapter.number:
            heading = chapter_title(edition, chapter)
            story.append(SectionHeading(heading, chapter_heading, heading, chapter.id, level=1))
        story.append(Paragraph(chapter_link(chapter), chapter_credit))
        for p in chapter.passages:
            # ReportLab uses strike markup for the reader's deletions.
            text = p.text.replace("<del>", "<strike>").replace("</del>", "</strike>")
            citation = f'<a name="{p.id}"/><font size="10" color="#414b57"><b>{p.label}</b></font>'
            marker = ""
            if p.note:
                key = f"translation-note-{p.note_number}"
                marker = " <super>" + link(f"#{key}", f"[{p.note_number}]") + "</super>"
                back = link(f"#{p.id}", p.label)
                notes.append(Paragraph(f'<a name="{key}"/>{p.note_number}. {back} {p.note}', body))
            story.append(Paragraph(f"{citation} {text}{marker}", body))
    if notes:
        story += [
            PageBreak(), SectionHeading("Translation notes", main_heading, "Translation notes", "translation-notes"),
            *notes,
        ]
    doc.multiBuild(story)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--font-dir", type=Path, required=True, help="directory with the Gentium TrueType faces")
    parser.add_argument("--pandoc", default="pandoc", help="Pandoc executable")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "assets/downloads/deh")
    parser.add_argument("--site-url", default="https://latinjosephus.github.io", help="public site base URL")
    args = parser.parse_args()
    site = args.site_url.rstrip("/")
    commentary = json.loads((ROOT / "assets/data/deh-combined-commentary-en.json").read_text(encoding="utf-8"))
    latin = read_edition(LATIN, commentary["by_section"], site)
    english = read_edition(ENGLISH, commentary["by_section"], site)
    labels = lambda chapters: [p.label for chapter in chapters for p in chapter.passages]
    if labels(latin) != labels(english):
        raise ValueError("The Latin and English passage sequences differ")
    register_fonts(args.font_dir)
    chars = set(unescape("".join(p.text for chapters in (latin, english) for c in chapters for p in c.passages)))
    missing = {char for char in chars if not char.isspace() and ord(char) not in pdfmetrics.getFont("Gentium").face.charToGlyph}
    if missing:
        raise ValueError(f"Gentium is missing source glyphs: {sorted(missing)}")

    args.output_dir.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix="deh-", dir=args.output_dir.parent) as temp:
        directory = Path(temp)
        files = []
        for edition, chapters in ((LATIN, latin), (ENGLISH, english)):
            epub = directory / f"{edition.slug}.epub"
            pdf = directory / f"{edition.slug}.pdf"
            build_epub(edition, chapters, site, epub, args.pandoc)
            build_pdf(edition, chapters, site, pdf)
            files.extend((epub, pdf))
        args.output_dir.mkdir(exist_ok=True)
        for file in files:
            target = args.output_dir / file.name
            file.replace(target)
            print(f"{target} ({target.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
