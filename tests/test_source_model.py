from __future__ import annotations

from pathlib import Path

from profile_cv.adapters import render_template, to_rendercv
from profile_cv.source import (
    load_repo_schema,
    load_source,
    serialize_source,
    validate_source,
)

ROOT = Path(__file__).resolve().parents[1]
RESUME = ROOT / "resume.yaml"


def test_canonical_yaml_resume_validates_and_contains_portable_sections() -> None:
    resume = load_source(RESUME)
    validate_source(resume, schema=load_repo_schema(ROOT))
    serialized = serialize_source(resume)

    assert resume["basics"]["name"] == "Andrew Crozier"
    assert resume["basics"]["profiles"][0]["network"] == "LinkedIn"
    assert resume["basics"]["x_contact"]["workAuthorization"] == "Australian citizen"
    assert resume["meta"]["version"] == "0.3.1"
    assert resume["meta"]["canonical"].endswith("/resume.yaml")
    assert len(resume["work"]) >= 10
    assert len(resume["projects"]) >= 8
    assert any(project["name"] == "library-ops" for project in resume["projects"])
    assert any(project["name"] == "mcp-web" for project in resume["projects"])
    assert any(skill["name"] == "Applied AI & Retrieval" for skill in resume["skills"])
    assert "KrisFlyer" in serialized
    assert "millions of properties" in serialized
    assert all(item["x_profile"]["section"] for item in resume["work"])
    assert all(
        item["x_profile"]["section"] == "omit" or item["x_profile"].get("signal")
        for item in resume["work"]
    )


def test_generated_readme_is_public_safe_and_source_aligned() -> None:
    resume = load_source(RESUME)
    generated = render_template(resume, ROOT / "templates", "README.md.j2")
    current = (ROOT / "README.md").read_text(encoding="utf-8")

    assert generated == current
    assert "andrewcrozier86@gmail.com" not in current
    assert "library-ops" in current
    assert "mcp-web" in current
    assert "Thailand-based Australian citizen" in current
    assert "## Engineering Biases" in current
    assert "{{" not in current


def test_generated_ats_markdown_uses_plain_contact_separators() -> None:
    resume = load_source(RESUME)
    generated = render_template(resume, ROOT / "templates", "resume.md.j2")

    first_lines = "\n".join(generated.splitlines()[:5])
    assert " | " not in first_lines
    assert " - LinkedIn:" in first_lines


def test_rendercv_adapter_preserves_resume_sections_without_becoming_canonical() -> None:
    resume = load_source(RESUME)
    rendercv = to_rendercv(resume)
    sections = rendercv["cv"]["sections"]

    assert rendercv["design"]["theme"] == "engineeringresumes"
    assert any(
        connection["placeholder"] == "Australian citizen"
        for connection in rendercv["cv"]["custom_connections"]
    )
    assert sections["Experience"][0]["company"] == "Stealth Startup"
    assert sections["Selected Public Work"][0]["name"].startswith("[library-ops](")
    assert "data/resume.rendercv.yaml" not in serialize_source(rendercv)
    for item in sections["Experience"]:
        for highlight in item["highlights"]:
            assert not highlight.lstrip().startswith("-")


def test_canonical_source_controls_project_inclusion_across_outputs() -> None:
    resume = load_source(RESUME)
    readme_projects = [p["name"] for p in resume["projects"] if p["x_profile"]["featured"]]
    resume_projects = [p["name"] for p in resume["projects"] if p["x_resume"]["featured"]]
    profile_sections = {item["name"]: item["x_profile"]["section"] for item in resume["work"]}

    assert set(resume_projects).issubset(set(readme_projects))
    assert "library-ops" in resume_projects
    assert "msteams-mcp" in readme_projects
    assert "msteams-mcp" not in resume_projects
    assert "PragmaLens" in readme_projects
    assert "PragmaLens" not in resume_projects
    assert profile_sections["Toptal"] in {"career_snapshot", "omit"}
    assert profile_sections["Agoda"] == "omit"
    assert profile_sections["Independent Freelance / Contract Engagements"] == "earlier_work"
