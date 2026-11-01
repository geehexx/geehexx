from __future__ import annotations

import zipfile
from pathlib import Path

import pytest
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches

from profile_cv.docx_layout import assert_docx_portable_structure, normalize_docx_layout


def test_normalized_docx_has_explicit_page_geometry_and_preserves_reading_order(
    tmp_path: Path,
) -> None:
    path = tmp_path / "resume.docx"
    document = Document()
    document.add_heading("Andrew Crozier", 1)
    document.add_paragraph("Lead AI Engineer")
    document.add_paragraph("Sydney, Australia - andrew@example.com")
    document.add_heading("Experience", 2)
    document.add_heading("T3 | Lead AI Engineer", 3)
    document.add_paragraph("Remote / UK client | Feb 2026 - Jun 2026")
    document.add_paragraph("Built production systems", style="List Bullet")
    expected = [paragraph.text for paragraph in document.paragraphs]
    document.save(str(path))

    normalize_docx_layout(path)
    assert_docx_portable_structure(path)
    actual = Document(str(path))
    assert [paragraph.text for paragraph in actual.paragraphs] == expected
    assert actual.paragraphs[0].style is not None
    assert actual.paragraphs[0].style.name == "Title"
    assert actual.styles["Title"].font.size.pt == 22
    assert actual.styles["Normal"].font.name == "Times New Roman"
    assert actual.paragraphs[1].paragraph_format.alignment == WD_ALIGN_PARAGRAPH.CENTER
    section = actual.sections[0]
    assert section.page_width == Inches(8.5)
    assert section.page_height == Inches(11)
    assert section.left_margin is not None
    assert section.right_margin is not None
    assert section.left_margin.twips == Inches(0.58).twips
    assert section.right_margin.twips == Inches(0.58).twips
    assert actual.paragraphs[5].paragraph_format.keep_with_next is True
    assert not actual.tables


def test_structure_check_rejects_broken_relationship(tmp_path: Path) -> None:
    path = tmp_path / "broken.docx"
    Document().save(str(path))
    _replace_part(
        path,
        "_rels/.rels",
        b'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        b'<Relationship Id="rId1" Type="document" Target="missing.xml"/>'
        b"</Relationships>",
    )
    with pytest.raises(AssertionError, match="Missing DOCX relationship target"):
        assert_docx_portable_structure(path)


def test_structure_check_rejects_external_template_dependency(tmp_path: Path) -> None:
    path = tmp_path / "external.docx"
    Document().save(str(path))
    _replace_part(
        path,
        "_rels/.rels",
        b'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        b'<Relationship Id="rId1" Type="attachedTemplate" TargetMode="External" '
        b'Target="https://example.com/template.dotx"/></Relationships>',
    )
    with pytest.raises(AssertionError, match="external templates"):
        assert_docx_portable_structure(path)


def _replace_part(path: Path, name: str, content: bytes) -> None:
    with zipfile.ZipFile(path) as package:
        parts = {item: package.read(item) for item in package.namelist()}
    parts[name] = content
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as package:
        for item, data in parts.items():
            package.writestr(item, data)


def test_structure_check_rejects_duplicate_zip_members(tmp_path: Path) -> None:
    path = tmp_path / "duplicate.docx"
    Document().save(str(path))
    with (
        zipfile.ZipFile(path, "a") as package,
        pytest.warns(UserWarning, match="Duplicate name"),
    ):
        package.writestr("word/document.xml", package.read("word/document.xml"))
    with pytest.raises(AssertionError, match="duplicate ZIP"):
        assert_docx_portable_structure(path)
