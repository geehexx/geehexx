from __future__ import annotations

import json
import os
import subprocess
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest

from profile_cv import build as build_module
from profile_cv.build import _build_site_outputs, build_all, build_review_package
from profile_cv.qa import doctor
from profile_cv.semantic_qa import assert_semantic_alignment
from profile_cv.source import load_source, serialize_source

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.integration
def test_full_build_pipeline_outputs_all_distribution_formats(tmp_path: Path) -> None:
    status = doctor()
    missing = [
        name
        for name in ("rendercv", "pandoc", "pdfinfo", "pdftotext", "libreoffice", "java")
        if not status[name]
    ]
    if missing:
        pytest.skip(f"missing external tools: {missing}")

    custom_source = tmp_path / "custom.yaml"
    custom_resume = load_source(ROOT / "resume.yaml")
    custom_resume["basics"]["summary"] += " Custom source validation fixture."
    custom_source.write_text(serialize_source(custom_resume), encoding="utf-8")
    metrics = build_all(
        root=ROOT,
        resume_path=custom_source,
        dist_dir=tmp_path / "dist",
        site_dir=tmp_path / "site",
        clean=True,
        run_qa=True,
        update_profile=False,
        profile_check=False,
    )

    outputs = metrics["outputs"]
    for key in ("pdf", "typ", "markdown", "html", "docx", "json", "json_ld", "readme_generated"):
        assert Path(outputs[key]).exists()
    html = Path(outputs["html"]).read_text(encoding="utf-8")
    assert html.count("<h1") == 1
    assert "<title>Andrew Crozier Resume</title>" in html
    assert "APAC" not in html
    assert "overlap" not in html
    assert metrics["qa"]["pdf"]["pages"] >= 1
    assert metrics["qa"]["docx"]["chars"] > 8_000
    assert metrics["qa"]["docx"]["metadata_current"] is True
    assert metrics["qa"]["docx"]["metadata_pages"] >= 1
    assert metrics["qa"]["docx"]["metadata_words"] > 1_000
    # Standalone extraction includes the semantic Title, not only Pandoc body blocks.
    extracted = subprocess.run(
        ["pandoc", outputs["docx"], "--standalone", "--to", "plain"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    assert_semantic_alignment(extracted, resume=custom_resume, surface="docx")
    assert "APAC" not in extracted
    assert "overlap" not in extracted
    with zipfile.ZipFile(outputs["docx"]) as package:
        relationships = ET.fromstring(package.read("word/_rels/document.xml.rels"))
    targets = {
        item.attrib["Target"]
        for item in relationships
        if item.attrib.get("Type", "").endswith("/hyperlink")
    }
    resume = load_source(ROOT / "resume.yaml")
    assert f"mailto:{resume['basics']['email']}" in targets
    assert "https://linkedin.com/in/ancrozier" in targets
    assert "https://github.com/geehexx" in targets


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
    assert (package / "profile" / "README.generated.md").exists()
    assert (package / "site" / "index.html").exists()
    assert manifest["contact_boundary"]["public_readme_excludes_direct_resume_email"] is True

    written = json.loads((package / "manifest.json").read_text(encoding="utf-8"))
    paths = {item["path"] for item in written["files"]}
    assert "REVIEW.md" in paths
    assert "index.html" in paths
    assert "artifacts/Andrew_Crozier_Resume.docx" in paths
    assert "profile/README.generated.md" in paths
    assert "site/index.html" in paths


def test_review_package_fails_when_required_artifact_is_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_review_package_sources(tmp_path)
    (tmp_path / "dist" / "Andrew_Crozier_Resume.docx").unlink()
    monkeypatch.setattr(build_module, "run_quality_gates", _fake_run_quality_gates)

    with pytest.raises(FileNotFoundError, match="Review package source is missing"):
        build_review_package(root=tmp_path)


def _write_review_package_sources(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "resume.yaml").write_text(
        'meta:\n  lastModified: "2026-11-01T00:00:00Z"\n', encoding="utf-8"
    )
    dist = root / "dist"
    site = root / "site"
    for directory in (dist, site):
        directory.mkdir(parents=True, exist_ok=True)
    for suffix in ("pdf", "docx", "md", "html", "json"):
        (dist / f"Andrew_Crozier_Resume.{suffix}").write_text(suffix, encoding="utf-8")
    (dist / "profile.schemaorg.json").write_text("{}", encoding="utf-8")
    (dist / "README.generated.md").write_text("# README\n", encoding="utf-8")
    (site / "index.html").write_text("<html></html>\n", encoding="utf-8")
    (site / "resume.css").write_text("body {}\n", encoding="utf-8")
    (site / ".nojekyll").write_text("", encoding="utf-8")
    for artifact in dist.iterdir():
        if artifact.name != "README.generated.md":
            (site / artifact.name).write_bytes(artifact.read_bytes())


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


def _fake_run_quality_gates(
    *, root: Path, outputs: dict[str, Path] | None = None
) -> dict[str, dict[str, int | bool]]:
    assert root.exists()
    assert outputs is not None
    assert outputs["readme"].name == "README.generated.md"
    assert all(path.is_file() for path in outputs.values())
    return _fake_qa()


@pytest.mark.parametrize("failure", ["qa", "unexpected", "stale", "symlink"])
def test_review_failure_preserves_previous_package(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failure: str
) -> None:
    _write_review_package_sources(tmp_path)
    package = tmp_path / "dist" / "review-package"
    package.mkdir()
    (package / "previous-review").write_text("keep", encoding="utf-8")
    monkeypatch.setattr(build_module, "run_quality_gates", _fake_run_quality_gates)
    if failure == "qa":

        def fail_qa(**_kwargs: object) -> dict[str, object]:
            raise ValueError("QA failed")

        monkeypatch.setattr(build_module, "run_quality_gates", fail_qa)
    elif failure == "unexpected":
        (tmp_path / "site" / "private-notes.txt").write_text("private", encoding="utf-8")
    elif failure == "stale":
        (tmp_path / "site" / "Andrew_Crozier_Resume.md").write_text("old", encoding="utf-8")
    else:
        artifact = tmp_path / "dist" / "Andrew_Crozier_Resume.pdf"
        artifact.unlink()
        artifact.symlink_to(tmp_path / "site" / artifact.name)
    with pytest.raises(ValueError):
        build_review_package(root=tmp_path)
    assert (package / "previous-review").read_text(encoding="utf-8") == "keep"
    assert not list((tmp_path / "dist").glob(".profile-cv-review-*"))


def test_review_custom_package_can_be_rebuilt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "repo"
    _write_review_package_sources(root)
    monkeypatch.setattr(build_module, "run_quality_gates", _fake_run_quality_gates)
    package = tmp_path / "custom-package"
    manifest = build_review_package(root=root, package_dir=package)
    assert len(manifest["files"]) == 17
    assert not (package / ".profile-cv-output").exists()
    build_review_package(root=root, package_dir=package)
    assert (package / "manifest.json").is_file()


def test_review_package_rechecks_site_bytes_after_equal_stat_mutation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_review_package_sources(tmp_path)
    monkeypatch.setattr(build_module, "run_quality_gates", _fake_run_quality_gates)
    build_review_package(root=tmp_path)
    artifact = tmp_path / "site/Andrew_Crozier_Resume.pdf"
    stat = artifact.stat()
    artifact.write_bytes(b"BAD")
    os.utime(artifact, ns=(stat.st_atime_ns, stat.st_mtime_ns))
    with pytest.raises(ValueError, match="Stale review site artifact"):
        build_review_package(root=tmp_path)
