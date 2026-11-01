"""Portable single-column DOCX styling, independent of installed template defaults."""

from __future__ import annotations

import posixpath
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor


def normalize_docx_layout(path: Path) -> None:
    """Keep semantic paragraphs/lists while matching the PDF's page and title hierarchy.

    Times New Roman is intentionally used instead of the PDF's embedded XCharter:
    DOCX readers commonly lack XCharter, and must otherwise substitute it silently.
    This is a layout normalization, not a guarantee of every Word/ATS implementation.
    """
    document = Document(str(path))
    for section in document.sections:
        section.page_width = Inches(8.5)
        section.page_height = Inches(11)
        section.top_margin = Inches(0.55)
        section.bottom_margin = Inches(0.55)
        section.left_margin = Inches(0.58)
        section.right_margin = Inches(0.58)
    for style in document.styles:
        if style.type != 1:  # Paragraph styles only; retain character/hyperlink formatting.
            continue
        style.font.name = "Times New Roman"
        style.font.size = Pt(10)
        style.font.color.rgb = RGBColor(0, 0, 0)
        paragraph = style.paragraph_format
        paragraph.widow_control = True
        paragraph.line_spacing = 1.0
        paragraph.space_before = Pt(0)
        paragraph.space_after = Pt(3)
        if style.style_id.startswith("Heading"):
            style.font.bold = True
            paragraph.keep_with_next = True
            paragraph.space_before = Pt(8)
            paragraph.space_after = Pt(4)
            if style.style_id in {"Heading1", "Heading2"}:
                style.font.size = Pt(11)
                style.font.color.rgb = RGBColor(17, 70, 115)
    if "Hyperlink" in document.styles:
        hyperlink = document.styles["Hyperlink"]
        hyperlink.font.name = "Times New Roman"
        hyperlink.font.size = Pt(10)
        hyperlink.font.color.rgb = RGBColor(17, 70, 115)
        hyperlink.font.underline = True
    title = document.styles["Title"]
    title.font.size = Pt(22)
    title.font.bold = True
    title.font.color.rgb = RGBColor(0, 0, 0)
    title.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.paragraph_format.keep_with_next = True
    title.paragraph_format.space_after = Pt(5)
    paragraphs = document.paragraphs
    if paragraphs:
        paragraphs[0].style = title
    # The Markdown pipeline emits name, professional headline, then contact details.
    for paragraph in paragraphs[1:3]:
        paragraph.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        paragraph.paragraph_format.keep_with_next = True
    # Keep each role heading and its date with the first bullet, not the entire role.
    for previous, paragraph in zip(paragraphs, paragraphs[1:], strict=False):
        if previous.style is not None and previous.style.style_id == "Heading3":
            paragraph.paragraph_format.keep_with_next = True
    document.save(str(path))


def assert_docx_portable_structure(path: Path) -> None:
    """Check this pipeline's simple DOCX package, without claiming Word/ATS certification."""
    word_ns = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    rel_ns = "http://schemas.openxmlformats.org/package/2006/relationships"
    with zipfile.ZipFile(path) as package:
        members = package.namelist()
        names = set(members)
        if len(names) != len(members):
            raise AssertionError("DOCX contains duplicate ZIP entries")
        if package.testzip() is not None:
            raise AssertionError("DOCX ZIP integrity failure")
        required = {"[Content_Types].xml", "_rels/.rels", "word/document.xml", "word/styles.xml"}
        if not required.issubset(names):
            raise AssertionError("DOCX is missing required package parts")
        if any(name.lower().endswith("vbaproject.bin") for name in names):
            raise AssertionError("Resume must not contain macros")
        for name in names:
            if name.endswith((".xml", ".rels")):
                ET.fromstring(package.read(name))
            if not name.endswith(".rels"):
                continue
            root = ET.fromstring(package.read(name))
            base = posixpath.dirname(posixpath.dirname(name))
            for relationship in root.findall(f"{{{rel_ns}}}Relationship"):
                target = relationship.attrib["Target"]
                if relationship.get("TargetMode") == "External":
                    if not relationship.attrib["Type"].endswith("/hyperlink"):
                        raise AssertionError(
                            "Resume must not depend on external templates or objects"
                        )
                    continue
                resolved = posixpath.normpath(posixpath.join(base, target)).lstrip("/")
                if resolved not in names:
                    raise AssertionError(f"Missing DOCX relationship target: {resolved}")
        document = ET.fromstring(package.read("word/document.xml"))
        for element in ("altChunk", "txbxContent", "object", "tbl"):
            if document.find(f".//{{{word_ns}}}{element}") is not None:
                raise AssertionError(
                    f"Resume must use native single-column paragraphs, not {element}"
                )
