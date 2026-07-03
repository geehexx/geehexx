from __future__ import annotations

import filecmp
import hashlib
import html
import json
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from . import __version__
from .adapters import DEFAULT_BASENAME, render_template, to_json_ld, to_rendercv, write_yaml
from .docx_metadata import modified_from_resume, normalize_docx_metadata
from .qa import (
    assert_doctor,
    expectations_from_resume,
    qa_docx,
    qa_pdf,
    qa_readme,
    qa_text_file,
)
from .source import load_repo_schema, load_source, validate_source, write_json

DEFAULT_DIST = Path("dist")
DEFAULT_SITE = Path("site")
DEFAULT_RESUME = Path("resume.yaml")
DEFAULT_REVIEW_PACKAGE = DEFAULT_DIST / "review-package"


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
        resume=resume,
        site_dir=site_dir,
        template_dir=template_dir,
        styles_dir=styles_dir,
        outputs=outputs,
    )

    metrics: dict[str, Any] = {"outputs": {key: str(path) for key, path in outputs.items()}}
    if run_qa:
        metrics["qa"] = run_quality_gates(root=root, outputs=outputs)
    return metrics


def _load_validated_resume(root: Path, resume_path: Path) -> dict[str, Any]:
    schema = load_repo_schema(root)
    resume = load_source(resume_path)
    validate_source(resume, schema=schema)
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
        title=f"{resume['basics']['name']} Resume",
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
    styles_dir: Path,
    outputs: dict[str, Path],
) -> None:
    site_dir.mkdir(parents=True, exist_ok=True)
    (site_dir / ".nojekyll").write_text("", encoding="utf-8")
    site_html = render_template(resume, template_dir, "site_index.html.j2", autoescape=True)
    (site_dir / "index.html").write_text(site_html, encoding="utf-8")
    shutil.copy2(styles_dir / "resume.css", site_dir / "resume.css")
    for key in ("pdf", "docx", "markdown", "html", "json", "json_ld"):
        shutil.copy2(outputs[key], site_dir / outputs[key].name)


def run_quality_gates(*, root: Path, outputs: dict[str, Path] | None = None) -> dict[str, Any]:
    outputs = outputs or {
        "pdf": root / DEFAULT_DIST / f"{DEFAULT_BASENAME}.pdf",
        "docx": root / DEFAULT_DIST / f"{DEFAULT_BASENAME}.docx",
        "markdown": root / DEFAULT_DIST / f"{DEFAULT_BASENAME}.md",
        "html": root / DEFAULT_DIST / f"{DEFAULT_BASENAME}.html",
        "readme": root / "README.md",
    }
    resume = load_source(root / DEFAULT_RESUME)
    expectations = expectations_from_resume(resume)
    return {
        "pdf": qa_pdf(outputs["pdf"], expectations=expectations, resume=resume),
        "docx": qa_docx(outputs["docx"], expectations=expectations, resume=resume),
        "markdown": qa_text_file(outputs["markdown"], expectations=expectations, resume=resume),
        "html": qa_text_file(
            outputs["html"], expectations=expectations, resume=resume, surface="html"
        ),
        "readme": qa_readme(outputs["readme"], expectations=expectations, resume=resume),
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


def build_review_package(
    *,
    root: Path,
    package_dir: Path | None = None,
) -> dict[str, Any]:
    """Assemble the ignored PR review bundle that CI uploads as one artifact."""

    dist_dir = root / DEFAULT_DIST
    site_dir = root / DEFAULT_SITE
    package_dir = package_dir or root / DEFAULT_REVIEW_PACKAGE

    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir(parents=True)

    required_files = [
        (dist_dir / f"{DEFAULT_BASENAME}.pdf", Path("artifacts") / f"{DEFAULT_BASENAME}.pdf"),
        (dist_dir / f"{DEFAULT_BASENAME}.docx", Path("artifacts") / f"{DEFAULT_BASENAME}.docx"),
        (dist_dir / f"{DEFAULT_BASENAME}.md", Path("artifacts") / f"{DEFAULT_BASENAME}.md"),
        (dist_dir / f"{DEFAULT_BASENAME}.html", Path("artifacts") / f"{DEFAULT_BASENAME}.html"),
        (dist_dir / f"{DEFAULT_BASENAME}.json", Path("artifacts") / f"{DEFAULT_BASENAME}.json"),
        (dist_dir / "profile.schemaorg.json", Path("artifacts") / "profile.schemaorg.json"),
        (dist_dir / "README.generated.md", Path("profile") / "README.generated.md"),
    ]
    for source, relative_target in required_files:
        _copy_required_file(source, package_dir / relative_target)

    _copy_required_tree(site_dir, package_dir / "site")

    qa = run_quality_gates(root=root)
    generated_at = datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
    manifest: dict[str, Any] = {
        "generated_at_utc": generated_at,
        "source": {
            "resume": str(DEFAULT_RESUME),
            "head_sha": _git_output(root, "rev-parse", "HEAD"),
            "branch": _git_output(root, "branch", "--show-current"),
        },
        "entrypoints": {
            "markdown": "REVIEW.md",
            "html": "index.html",
        },
        "contact_boundary": {
            "public_readme_excludes_direct_resume_email": True,
            "resume_source_and_artifacts_may_include_resume_contact_details": True,
            "github_pages_publishing_enabled": False,
        },
        "qa": qa,
    }

    (package_dir / "REVIEW.md").write_text(_review_markdown(manifest), encoding="utf-8")
    (package_dir / "index.html").write_text(_review_index_html(manifest), encoding="utf-8")
    manifest["files"] = _package_file_records(package_dir)
    manifest_text = json.dumps(manifest, indent=2) + "\n"
    (package_dir / "manifest.json").write_text(manifest_text, encoding="utf-8")
    return manifest


def _copy_required_file(source: Path, target: Path) -> None:
    if not source.is_file():
        raise FileNotFoundError(f"Review package source is missing: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def _copy_required_tree(source: Path, target: Path) -> None:
    if not source.is_dir():
        raise FileNotFoundError(f"Review package source directory is missing: {source}")
    shutil.copytree(source, target, ignore=shutil.ignore_patterns(".*"))


def _package_file_records(package_dir: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in sorted(package_dir.rglob("*")):
        if not path.is_file() or path.name == "manifest.json":
            continue
        relative = path.relative_to(package_dir).as_posix()
        records.append(
            {
                "path": relative,
                "size_bytes": path.stat().st_size,
                "sha256": _sha256(path),
            }
        )
    return records


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _review_markdown(manifest: dict[str, Any]) -> str:
    qa = manifest["qa"]
    return "\n".join(
        [
            "# Profile/CV Review Package",
            "",
            f"Generated: {manifest['generated_at_utc']}",
            f"Head: `{manifest['source']['head_sha'] or 'unknown'}`",
            "",
            "## Review Entrypoints",
            "",
            "- Open `index.html` for a local clickable review page.",
            "- Check `artifacts/` for PDF, DOCX, Markdown, HTML, JSON, and JSON-LD outputs.",
            "- Check `profile/` for the generated public profile README.",
            "- Check `site/` for the local static-site preview.",
            "",
            "## Contact Boundary",
            "",
            "- Public README must not expose the direct resume email.",
            "- Resume source and resume artifacts may include resume contact details.",
            "- GitHub Pages publishing is not enabled by this package.",
            "",
            "## Deterministic QA",
            "",
            "| Surface | Key evidence |",
            "| --- | --- |",
            f"| PDF | pages={qa['pdf']['pages']}, chars={qa['pdf']['chars']}, "
            f"semantic_required={qa['pdf']['semantic_required_checked']} |",
            f"| DOCX | paragraphs={qa['docx']['paragraphs']}, chars={qa['docx']['chars']}, "
            f"metadata_pages={qa['docx']['metadata_pages']}, "
            f"metadata_words={qa['docx']['metadata_words']} |",
            f"| Markdown | chars={qa['markdown']['chars']}, "
            f"semantic_required={qa['markdown']['semantic_required_checked']} |",
            f"| HTML | chars={qa['html']['chars']}, "
            f"semantic_required={qa['html']['semantic_required_checked']} |",
            f"| README | chars={qa['readme']['chars']}, "
            f"semantic_required={qa['readme']['semantic_required_checked']} |",
            "",
        ]
    )


def _review_index_html(manifest: dict[str, Any]) -> str:
    links = [
        ("Review notes", "REVIEW.md"),
        ("Manifest", "manifest.json"),
        ("PDF resume", f"artifacts/{DEFAULT_BASENAME}.pdf"),
        ("DOCX resume", f"artifacts/{DEFAULT_BASENAME}.docx"),
        ("ATS Markdown", f"artifacts/{DEFAULT_BASENAME}.md"),
        ("Standalone HTML", f"artifacts/{DEFAULT_BASENAME}.html"),
        ("Generated profile README", "profile/README.generated.md"),
        ("Local site preview", "site/index.html"),
    ]
    link_items = "\n".join(
        f'<li><a href="{html.escape(href)}">{html.escape(label)}</a></li>' for label, href in links
    )
    qa = manifest["qa"]
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Profile/CV Review Package</title>
  <style>
    body {{
      font-family: system-ui, sans-serif;
      margin: 2rem;
      max-width: 920px;
      line-height: 1.45;
    }}
    code {{ background: #f3f4f6; padding: 0.1rem 0.25rem; border-radius: 0.2rem; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #d1d5db; padding: 0.45rem; text-align: left; }}
  </style>
</head>
<body>
  <h1>Profile/CV Review Package</h1>
  <p>Generated {html.escape(str(manifest["generated_at_utc"]))} from
  <code>{html.escape(str(manifest["source"]["head_sha"] or "unknown"))}</code>.</p>
  <h2>Entrypoints</h2>
  <ul>
    {link_items}
  </ul>
  <h2>QA Summary</h2>
  <table>
    <tr><th>Surface</th><th>Evidence</th></tr>
    <tr><td>PDF</td><td>{qa["pdf"]["pages"]} pages, {qa["pdf"]["chars"]} chars</td></tr>
    <tr>
      <td>DOCX</td>
      <td>{qa["docx"]["paragraphs"]} paragraphs, {qa["docx"]["chars"]} chars</td>
    </tr>
    <tr><td>Markdown</td><td>{qa["markdown"]["chars"]} chars</td></tr>
    <tr><td>HTML</td><td>{qa["html"]["chars"]} chars</td></tr>
    <tr><td>README</td><td>{qa["readme"]["chars"]} chars</td></tr>
  </table>
</body>
</html>
"""


def _git_output(root: Path, *args: str) -> str | None:
    try:
        return subprocess.run(
            ["git", *args],
            cwd=root,
            check=True,
            text=True,
            capture_output=True,
        ).stdout.strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None


def run_rendercv(input_file: Path, output_dir: Path, *, root: Path) -> None:
    ensure_typst_package_cache(root)
    cmd = ["rendercv", "render", str(input_file), "--output-folder", str(output_dir)]
    try:
        subprocess.run(cmd, check=True, text=True, capture_output=True)
    except FileNotFoundError as exc:
        message = "RenderCV is not installed. Run `uv sync --frozen --extra dev`."
        raise RuntimeError(message) from exc
    except subprocess.CalledProcessError as exc:
        message = f"RenderCV failed for {input_file}\nSTDOUT:\n{exc.stdout}\nSTDERR:\n{exc.stderr}"
        raise RuntimeError(message) from exc


def run_pandoc(
    markdown_path: Path,
    *,
    html_path: Path,
    docx_path: Path,
    title: str,
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
        f"title={title}",
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


def ensure_typst_package_cache(root: Path) -> None:
    """Sync vendored Typst preview packages into typst-py's global cache.

    The RenderCV Typst package is vendored so CI and local builds do not depend
    on the preview package registry being reachable. typst-py resolves preview
    packages from this cache location, so keep writes minimal and only replace a
    package directory when the vendored copy differs.
    """
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
            if target.exists() and _directory_matches(version_dir, target):
                continue
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(version_dir, target)


def _directory_matches(left: Path, right: Path) -> bool:
    if not right.exists():
        return False
    comparison = filecmp.dircmp(left, right)
    if comparison.left_only or comparison.right_only or comparison.diff_files:
        return False
    return all(_directory_matches(left / name, right / name) for name in comparison.common_dirs)
