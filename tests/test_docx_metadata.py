from __future__ import annotations

import zipfile
from datetime import UTC, datetime
from pathlib import Path

import pytest
from docx import Document

from profile_cv.docx_metadata import (
    assert_docx_metadata,
    assert_libreoffice_environment,
    modified_from_resume,
    normalize_docx_metadata,
    office_app_version,
    read_app_properties,
    read_core_properties,
    rendered_docx_page_count,
)
from profile_cv.qa import doctor

ROOT = Path(__file__).resolve().parents[1]


def test_normalize_docx_metadata_updates_shareable_properties(tmp_path: Path) -> None:
    missing = [name for name in ("libreoffice", "java", "pdfinfo") if not doctor()[name]]
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
        subject="Engineering Manager - Applied AI & Platform Systems",
        author="Andrew Crozier",
        keywords="resume; applied AI; MCP",
        modified=datetime(2026, 7, 1, tzinfo=UTC),
        application="profile-cv",
        app_version="1.0.0",
    )

    app = read_app_properties(docx_path)
    core = read_core_properties(docx_path)
    metadata = assert_docx_metadata(docx_path)

    assert metadata["metadata_current"] is True
    pages = app["Pages"]
    assert isinstance(pages, int)
    assert app["Application"] == "profile-cv"
    assert app["AppVersion"] == "01.0000"
    assert app["Words"] == stats.words
    assert pages >= 1
    assert core["title"] == "Andrew Crozier - Resume"
    assert core["creator"] == "Andrew Crozier"


def test_normalize_docx_metadata_preserves_package_parts_and_removes_custom_props(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("profile_cv.docx_metadata.rendered_docx_page_count", lambda _: 1)
    docx_path = tmp_path / "resume.docx"
    document = Document(str(ROOT / "styles" / "reference.docx"))
    document.add_paragraph("Andrew Crozier")
    document.add_paragraph("applied AI platform engineering")
    document.save(str(docx_path))
    _write_docx_parts(
        docx_path,
        {
            "customXml/item1.xml": b"<root>preserve me</root>",
            "docProps/custom.xml": (
                b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                b'<Properties xmlns="http://schemas.openxmlformats.org/'
                b'officeDocument/2006/custom-properties" '
                b'xmlns:vt="http://schemas.openxmlformats.org/officeDocument/'
                b'2006/docPropsVTypes">'
                b'<property fmtid="{D5CDD505-2E9C-101B-9397-08002B2CF9AE}" '
                b'pid="2" name="PrivateNote"><vt:lpwstr>remove me</vt:lpwstr></property>'
                b"</Properties>"
            ),
        },
    )

    normalize_docx_metadata(
        docx_path,
        title="Andrew Crozier - Resume",
        subject="Engineering Manager - Applied AI & Platform Systems",
        author="Andrew Crozier",
        keywords="; ".join(f"keyword-{index}" for index in range(100)),
        modified=datetime(2026, 7, 1, tzinfo=UTC),
        application="profile-cv",
        app_version="1.0.0",
    )

    with zipfile.ZipFile(docx_path) as package:
        assert package.read("customXml/item1.xml") == b"<root>preserve me</root>"
    core = read_core_properties(docx_path)
    metadata = assert_docx_metadata(docx_path)
    assert len(core["keywords"]) <= 255
    assert metadata["custom_properties"] == 0


def _write_docx_parts(docx_path: Path, parts: dict[str, bytes]) -> None:
    tmp_path = docx_path.with_suffix(".tmp.docx")
    with (
        zipfile.ZipFile(docx_path) as source,
        zipfile.ZipFile(tmp_path, "w", compression=zipfile.ZIP_DEFLATED) as target,
    ):
        for item in source.infolist():
            if item.filename not in parts:
                target.writestr(item, source.read(item.filename))
        for filename, payload in parts.items():
            target.writestr(filename, payload)
    tmp_path.replace(docx_path)


@pytest.mark.parametrize(
    ("version", "expected"), [("1.0.0", "01.0000"), ("2.8", "02.0008"), ("16.0000", "16.0000")]
)
def test_application_version_uses_office_numeric_format(version: str, expected: str) -> None:
    assert office_app_version(version) == expected


@pytest.mark.parametrize("version", ["release", "100.0.0", "1.10000.0"])
def test_application_version_rejects_invalid_values(version: str) -> None:
    with pytest.raises(ValueError):
        office_app_version(version)


@pytest.mark.parametrize(
    "diagnostic",
    [
        "Warning: failed to launch javaldx - java may not function correctly",
        "javaldx: Could not find a Java Runtime Environment!",
        "JRE is not installed",
        "User installation could not be completed.",
        "Error: Unable to create user installation.",
        "User profile is locked by another instance",
    ],
)
def test_libreoffice_actionable_environment_warnings_fail_qa(diagnostic: str) -> None:
    with pytest.raises(RuntimeError, match="Java/profile setup needs repair"):
        assert_libreoffice_environment(diagnostic)


@pytest.mark.parametrize(
    "diagnostic", ["", "error : Unknown IO error", "Using Java Runtime Environment 21"]
)
def test_libreoffice_unrelated_diagnostics_are_not_blanket_rejected(diagnostic: str) -> None:
    assert_libreoffice_environment(diagnostic)


@pytest.mark.parametrize("stderr", ["", "Warning: failed to launch javaldx"])
def test_successful_conversion_still_checks_environment_diagnostics(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, stderr: str
) -> None:
    docx_path = tmp_path / "resume.docx"
    docx_path.write_bytes(b"mocked converter input")

    class SuccessfulProcess:
        returncode = 0

        def communicate(self, *, timeout: int) -> tuple[str, str]:
            assert timeout == 90
            return "convert resume.docx -> resume.pdf", stderr

    monkeypatch.setattr(
        "profile_cv.docx_metadata.subprocess.Popen", lambda *_args, **_kwargs: SuccessfulProcess()
    )
    monkeypatch.setattr("profile_cv.docx_metadata._wait_for_stable_file", lambda _: None)
    monkeypatch.setattr(
        "profile_cv.docx_metadata._wait_for_pdf", lambda *_args: tmp_path / "resume.pdf"
    )
    monkeypatch.setattr("profile_cv.docx_metadata._pdf_pages", lambda _: 3)
    if stderr:
        with pytest.raises(RuntimeError, match="Java/profile setup needs repair"):
            rendered_docx_page_count(docx_path)
    else:
        assert rendered_docx_page_count(docx_path) == 3


def test_metadata_normalization_is_byte_stable_across_zip_times_and_order(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("profile_cv.docx_metadata.rendered_docx_page_count", lambda _: 1)
    source = tmp_path / "source.docx"
    document = Document()
    document.add_heading("Andrew Crozier", 1)
    document.add_paragraph("T3 - Lead AI Engineer - Feb 2026 - Jun 2026")
    document.save(str(source))
    with zipfile.ZipFile(source) as package:
        parts = {item: package.read(item) for item in package.namelist()}
    first, second = tmp_path / "first.docx", tmp_path / "second.docx"
    cases = [
        (first, list(parts), (2024, 2, 3, 4, 5, 6)),
        (second, list(reversed(parts)), (2026, 11, 1, 12, 30, 40)),
    ]
    for path, names, timestamp in cases:
        with zipfile.ZipFile(path, "w") as package:
            for name in names:
                info = zipfile.ZipInfo(name, date_time=timestamp)
                package.writestr(info, parts[name])
        normalize_docx_metadata(
            path,
            title="Andrew Crozier - Resume",
            subject="Lead AI Engineer",
            author="Andrew Crozier",
            keywords="resume; AI",
            modified=datetime(2026, 11, 1, tzinfo=UTC),
        )
    expected = first.read_bytes()
    assert second.read_bytes() == expected
    assert [p.text for p in Document(str(first)).paragraphs] == [
        "Andrew Crozier",
        "T3 - Lead AI Engineer - Feb 2026 - Jun 2026",
    ]
    with zipfile.ZipFile(first) as package:
        assert package.namelist() == sorted(parts)
        assert all(info.date_time == (1980, 1, 1, 0, 0, 0) for info in package.infolist())
        for name, content in parts.items():
            if name not in {"docProps/core.xml", "docProps/app.xml"}:
                assert package.read(name) == content
    normalize_docx_metadata(
        first,
        title="Andrew Crozier - Resume",
        subject="Lead AI Engineer",
        author="Andrew Crozier",
        keywords="resume; AI",
        modified=datetime(2026, 11, 1, tzinfo=UTC),
    )
    assert first.read_bytes() == expected


@pytest.mark.parametrize(
    "resume",
    [
        {},
        {"meta": None},
        {"meta": {}},
        {"meta": {"lastModified": ""}},
        {"meta": {"lastModified": "2026-11-01"}},
        {"meta": {"lastModified": "2026-11-01T00:00:00"}},
        {"meta": {"lastModified": "2026-02-31T00:00:00Z"}},
    ],
)
def test_source_modified_timestamp_must_be_explicit_and_timezone_aware(
    resume: dict[str, object],
) -> None:
    with pytest.raises(ValueError, match="lastModified.*timezone-aware"):
        modified_from_resume(resume)


def test_source_modified_timestamp_is_normalized_to_utc() -> None:
    assert modified_from_resume({"meta": {"lastModified": "2026-11-01T11:00:00+11:00"}}) == (
        datetime(2026, 11, 1, tzinfo=UTC)
    )


def test_standalone_metadata_without_source_timestamp_has_stable_epoch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("profile_cv.docx_metadata.rendered_docx_page_count", lambda _: 1)
    path = tmp_path / "standalone.docx"
    Document().save(str(path))
    normalize_docx_metadata(path, title="Resume", subject="AI", author="Andrew", keywords="resume")
    expected = path.read_bytes()
    normalize_docx_metadata(path, title="Resume", subject="AI", author="Andrew", keywords="resume")
    assert path.read_bytes() == expected
    with zipfile.ZipFile(path) as package:
        assert b"1980-01-01T00:00:00Z" in package.read("docProps/core.xml")
