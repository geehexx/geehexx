from __future__ import annotations

import json
from pathlib import Path

import pytest

from profile_cv import build as build_module
from profile_cv.build import _build_site_outputs, build_all, build_review_package, compare_themes
from profile_cv.qa import doctor
from profile_cv.source import load_source

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.integration
def test_full_build_pipeline_outputs_all_distribution_formats(tmp_path: Path) -> None:
    status = doctor()
    missing = [
        name
        for name in ("rendercv", "pandoc", "pdfinfo", "pdftotext", "libreoffice")
        if not status[name]
    ]
    if missing:
        pytest.skip(f"missing external tools: {missing}")

    metrics = build_all(
        root=ROOT,
        dist_dir=tmp_path / "dist",
        clean=True,
        run_qa=True,
        update_profile=False,
        profile_check=False,
    )

    outputs = metrics["outputs"]
    for key in ("pdf", "typ", "markdown", "html", "docx", "json", "json_ld", "readme_generated"):
        assert Path(outputs[key]).exists()
    assert metrics["qa"]["pdf"]["pages"] >= 1
    assert metrics["qa"]["docx"]["chars"] > 8_000
    assert metrics["qa"]["docx"]["metadata_current"] is True
    assert metrics["qa"]["docx"]["metadata_pages"] >= 1
    assert metrics["qa"]["docx"]["metadata_words"] > 1_000


@pytest.mark.integration
def test_theme_comparison_is_small_but_meaningful(tmp_path: Path) -> None:
    status = doctor()
    missing = [name for name in ("rendercv", "pdfinfo", "pdftotext") if not status[name]]
    if missing:
        pytest.skip(f"missing external tools: {missing}")

    rows = compare_themes(
        root=ROOT,
        themes=("engineeringresumes", "sb2nov"),
        output_dir=tmp_path / "themes",
        report_path=tmp_path / "theme-comparison.md",
    )
    assert [row["theme"] for row in rows] == ["engineeringresumes", "sb2nov"]
    assert all(row["has_required_sections"] for row in rows)
    assert all(row["pages"] >= 1 for row in rows)


def test_site_output_is_self_contained(tmp_path: Path) -> None:
    resume = load_source(ROOT / "resume.yaml")
    dist = tmp_path / "dist"
    dist.mkdir()
    outputs = {}
    for key, suffix in {
        "pdf": ".pdf",
        "docx": ".docx",
        "markdown": ".md",
        "html": ".html",
        "json": ".json",
        "json_ld": ".schemaorg.json",
    }.items():
        path = dist / f"Andrew_Crozier_Resume{suffix}"
        path.write_text(f"{key}\n", encoding="utf-8")
        outputs[key] = path

    _build_site_outputs(
        resume=resume,
        site_dir=tmp_path / "site",
        template_dir=ROOT / "templates",
        styles_dir=ROOT / "styles",
        outputs=outputs,
    )

    index = (tmp_path / "site" / "index.html").read_text(encoding="utf-8")
    assert 'href="resume.css"' in index
    assert (tmp_path / "site" / "resume.css").exists()


def test_review_package_collects_artifacts_and_review_evidence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_review_package_sources(tmp_path)
    monkeypatch.setattr(build_module, "run_quality_gates", _fake_run_quality_gates)

    manifest = build_review_package(root=tmp_path)

    package = tmp_path / "dist" / "review-package"
    assert (package / "REVIEW.md").exists()
    assert (package / "index.html").exists()
    assert (package / "manifest.json").exists()
    assert (package / "artifacts" / "Andrew_Crozier_Resume.pdf").exists()
    assert (package / "site" / "index.html").exists()
    assert (package / "visual-review" / "pdf" / "page-1.png").exists()
    assert (package / "visual-review" / "docx" / "page-1.png").exists()
    assert (package / "theme-comparison.md").exists()
    assert manifest["contact_boundary"]["public_readme_excludes_direct_resume_email"] is True

    written = json.loads((package / "manifest.json").read_text(encoding="utf-8"))
    paths = {item["path"] for item in written["files"]}
    assert "REVIEW.md" in paths
    assert "index.html" in paths
    assert "artifacts/Andrew_Crozier_Resume.docx" in paths
    assert "theme-comparison/engineeringresumes/Andrew_Crozier_Resume.pdf" in paths


def test_review_package_fails_when_visual_evidence_is_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_review_package_sources(tmp_path)
    (tmp_path / "_qa_docx" / "page-1.png").unlink()
    monkeypatch.setattr(build_module, "run_quality_gates", _fake_run_quality_gates)

    with pytest.raises(FileNotFoundError, match="DOCX preview PNGs"):
        build_review_package(root=tmp_path)


def _write_review_package_sources(root: Path) -> None:
    dist = root / "dist"
    site = root / "site"
    rendercv = dist / "rendercv"
    theme = dist / "theme-comparison" / "engineeringresumes"
    for directory in (dist, site, rendercv, theme, root / "_qa_pdf", root / "_qa_docx"):
        directory.mkdir(parents=True, exist_ok=True)
    for suffix in ("pdf", "docx", "md", "html", "json"):
        (dist / f"Andrew_Crozier_Resume.{suffix}").write_text(suffix, encoding="utf-8")
    (dist / "profile.schemaorg.json").write_text("{}", encoding="utf-8")
    (dist / "README.generated.md").write_text("# README\n", encoding="utf-8")
    (dist / "theme-comparison.md").write_text("# Theme comparison\n", encoding="utf-8")
    (site / "index.html").write_text("<html></html>\n", encoding="utf-8")
    (site / "resume.css").write_text("body {}\n", encoding="utf-8")
    (rendercv / "Andrew_Crozier_Resume_1.png").write_bytes(b"png")
    (theme / "Andrew_Crozier_Resume.pdf").write_text("theme pdf", encoding="utf-8")
    (theme / "Andrew_Crozier_Resume_1.png").write_bytes(b"theme png")
    (root / "_qa_pdf" / "page-1.png").write_bytes(b"pdf png")
    (root / "_qa_docx" / "page-1.png").write_bytes(b"docx png")


def _fake_qa() -> dict[str, dict[str, int | bool]]:
    return {
        "pdf": {
            "pages": 3,
            "chars": 11223,
            "semantic_required_checked": 53,
        },
        "docx": {
            "paragraphs": 82,
            "chars": 11180,
            "metadata_pages": 3,
            "metadata_words": 1390,
        },
        "markdown": {"chars": 11421, "semantic_required_checked": 53},
        "html": {"chars": 16985, "semantic_required_checked": 53},
        "readme": {"chars": 10357, "semantic_required_checked": 30},
    }


def _fake_run_quality_gates(*, root: Path) -> dict[str, dict[str, int | bool]]:
    assert root.exists()
    return _fake_qa()
