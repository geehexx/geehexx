from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest
from docx import Document

from profile_cv.docx_metadata import (
    assert_docx_metadata,
    normalize_docx_metadata,
    read_app_properties,
    read_core_properties,
)
from profile_cv.qa import doctor

ROOT = Path(__file__).resolve().parents[1]


def test_normalize_docx_metadata_updates_shareable_properties(tmp_path: Path) -> None:
    missing = [name for name in ("libreoffice", "pdfinfo") if not doctor()[name]]
    if missing:
        pytest.skip(f"missing external tools: {missing}")

    docx_path = tmp_path / "resume.docx"
    document = Document(str(ROOT / "styles" / "reference.docx"))
    document.add_paragraph("Andrew Crozier")
    document.add_paragraph("Summary")
    document.add_paragraph("applied AI MCP platform engineering")
    document.save(str(docx_path))

    stats = normalize_docx_metadata(
        docx_path,
        title="Andrew Crozier - Resume",
        subject="Applied AI Engineering Leader",
        author="Andrew Crozier",
        keywords="resume; applied AI; MCP",
        modified=datetime(2026, 7, 1, tzinfo=UTC),
        application="profile-cv",
        app_version="0.3.1",
    )

    app = read_app_properties(docx_path)
    core = read_core_properties(docx_path)
    metadata = assert_docx_metadata(docx_path)

    assert metadata["metadata_current"] is True
    pages = app["Pages"]
    assert isinstance(pages, int)
    assert app["Application"] == "profile-cv"
    assert app["AppVersion"] == "0.3.1"
    assert app["Words"] == stats.words
    assert pages >= 1
    assert core["title"] == "Andrew Crozier - Resume"
    assert core["creator"] == "Andrew Crozier"
