from __future__ import annotations

from pathlib import Path

import pytest

from profile_cv.build import _build_site_outputs, build_all, compare_themes
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
