from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from . import __version__
from .adapters import DEFAULT_BASENAME, render_template, to_json_ld, to_rendercv, write_yaml
from .docx_metadata import modified_from_resume, normalize_docx_metadata
from .qa import assert_doctor, pdf_pages, pdftotext, qa_docx, qa_pdf, qa_readme, qa_text_file
from .quality_policy import load_policy
from .source import load_repo_schema, load_source, validate_source, write_json

DEFAULT_DIST = Path("dist")
DEFAULT_SITE = Path("site")
DEFAULT_RESUME = Path("resume.yaml")
DEFAULT_THEMES = ("engineeringresumes", "sb2nov", "classic")


def build_all(
    *,
    root: Path,
    resume_path: Path | None = None,
    dist_dir: Path | None = None,
    site_dir: Path | None = None,
    clean: bool = False,
    run_qa: bool = True,
    update_profile: bool = True,
    profile_check: bool = True,
) -> dict[str, Any]:
    resume_path = resume_path or root / DEFAULT_RESUME
    dist_dir = dist_dir or root / DEFAULT_DIST
    site_dir = site_dir or root / DEFAULT_SITE
    template_dir = root / "templates"
    styles_dir = root / "styles"
    resume = _load_validated_resume(root, resume_path)

    if clean and dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir(parents=True, exist_ok=True)
    assert_doctor()

    outputs: dict[str, Path] = {}
    _build_rendercv_outputs(root=root, resume=resume, dist_dir=dist_dir, outputs=outputs)
    _build_pandoc_outputs(
        resume=resume,
        dist_dir=dist_dir,
        template_dir=template_dir,
        styles_dir=styles_dir,
        outputs=outputs,
    )
    _build_structured_outputs(resume=resume, dist_dir=dist_dir, outputs=outputs)
    _build_profile_outputs(
        resume=resume,
        root=root,
        dist_dir=dist_dir,
        template_dir=template_dir,
        outputs=outputs,
        update_profile=update_profile,
        profile_check=profile_check,
    )
    _build_site_outputs(
        resume=resume, site_dir=site_dir, template_dir=template_dir, outputs=outputs
    )

    metrics: dict[str, Any] = {"outputs": {key: str(path) for key, path in outputs.items()}}
    if run_qa:
        metrics["qa"] = run_quality_gates(root=root, outputs=outputs)
    return metrics


def _load_validated_resume(root: Path, resume_path: Path) -> dict[str, Any]:
    schema = load_repo_schema(root)
    resume = load_source(resume_path)
    validate_source(resume, schema=schema, policy=load_policy(root / "quality-gates.yaml"))
    return resume


def _build_rendercv_outputs(
    *, root: Path, resume: dict[str, Any], dist_dir: Path, outputs: dict[str, Path]
) -> None:
    rendercv_dir = dist_dir / "rendercv"
    rendercv_yaml = rendercv_dir / f"{DEFAULT_BASENAME}.yaml"
    write_yaml(rendercv_yaml, to_rendercv(resume))
    outputs["rendercv_yaml"] = rendercv_yaml

    run_rendercv(rendercv_yaml, rendercv_dir, root=root)
    for suffix in ("pdf", "typ"):
        source = rendercv_dir / f"{DEFAULT_BASENAME}.{suffix}"
        target = dist_dir / f"{DEFAULT_BASENAME}.{suffix}"
        if source.exists():
            shutil.copy2(source, target)
            outputs[suffix] = target


def _build_pandoc_outputs(
    *,
    resume: dict[str, Any],
    dist_dir: Path,
    template_dir: Path,
    styles_dir: Path,
    outputs: dict[str, Path],
) -> None:
    markdown_path = dist_dir / f"{DEFAULT_BASENAME}.md"
    markdown = render_template(resume, template_dir, "resume.md.j2")
    markdown_path.write_text(markdown, encoding="utf-8")
    outputs["markdown"] = markdown_path

    html_path = dist_dir / f"{DEFAULT_BASENAME}.html"
    docx_path = dist_dir / f"{DEFAULT_BASENAME}.docx"
    run_pandoc(
        markdown_path,
        html_path=html_path,
        docx_path=docx_path,
        reference_docx=styles_dir / "reference.docx",
        css_path=styles_dir / "resume.css",
    )
    normalize_docx_metadata(
        docx_path,
        title=f"{resume['basics']['name']} - Resume",
        subject=resume["basics"]["label"],
        author=resume["basics"]["name"],
        keywords=docx_keywords(resume),
        modified=modified_from_resume(resume),
        application="profile-cv",
        app_version=__version__,
    )
    outputs["html"] = html_path
    outputs["docx"] = docx_path


def docx_keywords(resume: dict[str, Any]) -> str:
    keywords = [
        "resume",
        "applied AI",
        "software engineering",
        "platform engineering",
        "backend",
        "retrieval",
        "MCP",
        "agents",
    ]
    for skill in resume.get("skills", []):
        if not isinstance(skill, dict):
            continue
        for value in skill.get("keywords", []):
            text = str(value).strip()
            if text and text not in keywords:
                keywords.append(text)
            candidate = "; ".join(keywords)
            if len(candidate) >= 220:
                return candidate[:255]
    return "; ".join(keywords)[:255]


def _build_structured_outputs(
    *, resume: dict[str, Any], dist_dir: Path, outputs: dict[str, Path]
) -> None:
    json_copy = dist_dir / f"{DEFAULT_BASENAME}.json"
    write_json(json_copy, resume)
    outputs["json"] = json_copy

    json_ld_path = dist_dir / "profile.schemaorg.json"
    write_json(json_ld_path, to_json_ld(resume))
    outputs["json_ld"] = json_ld_path


def _build_profile_outputs(
    *,
    resume: dict[str, Any],
    root: Path,
    dist_dir: Path,
    template_dir: Path,
    outputs: dict[str, Path],
    update_profile: bool,
    profile_check: bool,
) -> None:
    readme_text = render_template(resume, template_dir, "README.md.j2")
    generated_readme = dist_dir / "README.generated.md"
    generated_readme.write_text(readme_text, encoding="utf-8")
    outputs["readme_generated"] = generated_readme
    outputs["readme"] = generated_readme

    if not update_profile:
        return

    readme_path = root / "README.md"
    if profile_check and readme_path.exists():
        existing = readme_path.read_text(encoding="utf-8")
        if existing != readme_text:
            message = "README.md is stale. Run `profile-cv render-profile` or `profile-cv build`."
            raise AssertionError(message)
    readme_path.write_text(readme_text, encoding="utf-8")
    outputs["readme"] = readme_path


def _build_site_outputs(
    *,
    resume: dict[str, Any],
    site_dir: Path,
    template_dir: Path,
    outputs: dict[str, Path],
) -> None:
    site_dir.mkdir(parents=True, exist_ok=True)
    (site_dir / ".nojekyll").write_text("", encoding="utf-8")
    site_html = render_template(resume, template_dir, "site_index.html.j2", autoescape=True)
    (site_dir / "index.html").write_text(site_html, encoding="utf-8")
    for key in ("pdf", "docx", "markdown", "html", "json", "json_ld"):
        shutil.copy2(outputs[key], site_dir / outputs[key].name)


def run_quality_gates(*, root: Path, outputs: dict[str, Path] | None = None) -> dict[str, Any]:
    outputs = outputs or {
        "pdf": root / DEFAULT_DIST / f"{DEFAULT_BASENAME}.pdf",
        "docx": root / DEFAULT_DIST / f"{DEFAULT_BASENAME}.docx",
        "markdown": root / DEFAULT_DIST / f"{DEFAULT_BASENAME}.md",
        "readme": root / "README.md",
    }
    return {
        "pdf": qa_pdf(outputs["pdf"]),
        "docx": qa_docx(outputs["docx"]),
        "markdown": qa_text_file(outputs["markdown"]),
        "readme": qa_readme(outputs["readme"]),
    }


def render_profile(*, root: Path, check: bool = False) -> Path:
    resume = _load_validated_resume(root, root / DEFAULT_RESUME)
    readme = render_template(resume, root / "templates", "README.md.j2")
    path = root / "README.md"
    if check:
        existing = path.read_text(encoding="utf-8") if path.exists() else ""
        if existing != readme:
            raise AssertionError("README.md is stale relative to resume.yaml")
    else:
        path.write_text(readme, encoding="utf-8")
    return path


def run_rendercv(input_file: Path, output_dir: Path, *, root: Path) -> None:
    ensure_typst_package_cache(root)
    cmd = ["rendercv", "render", str(input_file), "--output-folder", str(output_dir)]
    try:
        subprocess.run(cmd, check=True, text=True, capture_output=True)
    except FileNotFoundError as exc:
        raise RuntimeError("RenderCV is not installed. Run `uv sync --extra dev`.") from exc
    except subprocess.CalledProcessError as exc:
        message = f"RenderCV failed for {input_file}\nSTDOUT:\n{exc.stdout}\nSTDERR:\n{exc.stderr}"
        raise RuntimeError(message) from exc


def run_pandoc(
    markdown_path: Path,
    *,
    html_path: Path,
    docx_path: Path,
    reference_docx: Path | None = None,
    css_path: Path | None = None,
) -> None:
    html_path.parent.mkdir(parents=True, exist_ok=True)
    docx_path.parent.mkdir(parents=True, exist_ok=True)
    html_cmd = [
        "pandoc",
        str(markdown_path),
        "--from",
        "markdown+smart",
        "--to",
        "html5",
        "--standalone",
        "--metadata",
        "title=Andrew Crozier Resume",
        "--output",
        str(html_path),
    ]
    docx_cmd = [
        "pandoc",
        str(markdown_path),
        "--from",
        "markdown+smart",
        "--to",
        "docx",
        "--output",
        str(docx_path),
    ]
    if reference_docx and reference_docx.exists():
        docx_cmd.extend(["--reference-doc", str(reference_docx)])
    for cmd in (html_cmd, docx_cmd):
        try:
            subprocess.run(cmd, check=True, text=True, capture_output=True)
        except FileNotFoundError as exc:
            raise RuntimeError("pandoc is required for HTML/DOCX export") from exc
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(f"pandoc failed: {' '.join(cmd)}\n{exc.stderr}") from exc
    if css_path and css_path.exists():
        inline_css(html_path, css_path)


def inline_css(html_path: Path, css_path: Path) -> None:
    css = css_path.read_text(encoding="utf-8").strip()
    html = html_path.read_text(encoding="utf-8")
    style_block = f"<style>\n{css}\n</style>"
    if "</head>" not in html:
        raise RuntimeError(f"Cannot inline CSS into {html_path}: missing </head>")
    html_path.write_text(html.replace("</head>", f"{style_block}\n</head>"), encoding="utf-8")


def compare_themes(
    *,
    root: Path,
    themes: tuple[str, ...] = DEFAULT_THEMES,
    output_dir: Path | None = None,
    report_path: Path | None = None,
) -> list[dict[str, Any]]:
    resume = _load_validated_resume(root, root / DEFAULT_RESUME)
    out = output_dir or root / DEFAULT_DIST / "theme-comparison"
    if out.exists():
        shutil.rmtree(out)
    rows: list[dict[str, Any]] = []
    for theme in themes:
        rows.append(_build_theme(root=root, resume=resume, theme=theme, output_dir=out))
    write_theme_report(
        report_path or root / DEFAULT_DIST / "theme-comparison.md",
        rows,
        selected_theme="engineeringresumes",
    )
    return rows


def _build_theme(
    *, root: Path, resume: dict[str, Any], theme: str, output_dir: Path
) -> dict[str, Any]:
    theme_resume = to_rendercv(resume)
    theme_resume["design"]["theme"] = theme
    with tempfile.TemporaryDirectory(prefix="profile-cv-theme-") as tmp:
        input_path = Path(tmp) / f"{DEFAULT_BASENAME}.{theme}.yaml"
        write_yaml(input_path, theme_resume)
        theme_dir = output_dir / theme
        run_rendercv(input_path, theme_dir, root=root)
    pdf = theme_dir / f"{DEFAULT_BASENAME}.pdf"
    text = pdftotext(pdf)
    required_sections = ("Summary", "Experience", "Education")
    return {
        "theme": theme,
        "pages": pdf_pages(pdf),
        "text_chars": len(text),
        "has_required_sections": all(token in text for token in required_sections),
        "pdf": str(pdf.relative_to(root)) if pdf.is_relative_to(root) else str(pdf),
    }


def write_theme_report(path: Path, rows: list[dict[str, Any]], *, selected_theme: str) -> None:
    lines = [
        "# Theme comparison",
        "",
        "Generated by `profile-cv compare-themes`.",
        "",
        f"Selected default: `{selected_theme}`.",
        "",
        "| Theme | Pages | Extracted text chars | Required sections | PDF |",
        "| --- | ---: | ---: | --- | --- |",
    ]
    for row in rows:
        required = "yes" if row["has_required_sections"] else "no"
        lines.append(
            f"| `{row['theme']}` | {row['pages']} | {row['text_chars']} | "
            f"{required} | `{row['pdf']}` |"
        )
    lines.extend(
        [
            "",
            "Decision: keep `engineeringresumes` as the default. It preserves a single-column, "
            "ATS-safe extraction path while giving the PDF a restrained engineering-resume "
            "visual identity. `classic` is a useful review alternate; `sb2nov` "
            "remains a compact ATS-style reference.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def ensure_typst_package_cache(root: Path) -> None:
    vendor = root / "vendor" / "typst" / "packages" / "preview"
    if not vendor.exists():
        return
    cache = Path.home() / ".cache" / "typst" / "packages" / "preview"
    for package_dir in vendor.iterdir():
        if not package_dir.is_dir():
            continue
        for version_dir in package_dir.iterdir():
            if not version_dir.is_dir():
                continue
            target = cache / package_dir.name / version_dir.name
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(version_dir, target)
