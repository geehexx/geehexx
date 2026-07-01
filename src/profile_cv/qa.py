from __future__ import annotations

import shutil
import subprocess
from collections.abc import Iterable
from pathlib import Path

from docx import Document

from .docx_metadata import assert_docx_metadata
from .quality_policy import default_policy

_POLICY = default_policy()
REQUIRED_TEXT_TOKENS = _POLICY.required_text_tokens
FORBIDDEN_TEXT_TOKENS = _POLICY.forbidden_text_tokens
FORBIDDEN_ATS_TOKENS = _POLICY.forbidden_ats_tokens
FORBIDDEN_FACT_RISK_TOKENS = _POLICY.fact_risk_tokens


def doctor() -> dict[str, bool]:
    commands = {
        "rendercv": "rendercv",
        "pandoc": "pandoc",
        "pdfinfo": "pdfinfo",
        "pdftotext": "pdftotext",
        "libreoffice": "libreoffice",
    }
    return {name: shutil.which(command) is not None for name, command in commands.items()}


def assert_doctor(
    required: Iterable[str] = ("rendercv", "pandoc", "pdfinfo", "pdftotext", "libreoffice"),
) -> None:
    status = doctor()
    missing = [name for name in required if not status.get(name)]
    if missing:
        raise RuntimeError(f"Missing required external tools: {', '.join(missing)}")


def qa_pdf(pdf_path: Path, *, max_pages: int = 5) -> dict[str, int | bool]:
    if not pdf_path.exists():
        raise FileNotFoundError(pdf_path)
    text = pdftotext(pdf_path)
    pages = pdf_pages(pdf_path)
    assert_text_quality(text, source=pdf_path)
    if pages < 1 or pages > max_pages:
        raise AssertionError(f"Unexpected page count for {pdf_path}: {pages}")
    return {"pages": pages, "chars": len(text), "required_tokens": True}


def qa_docx(docx_path: Path) -> dict[str, int | bool]:
    if not docx_path.exists():
        raise FileNotFoundError(docx_path)
    document = Document(str(docx_path))
    text = "\n".join(paragraph.text for paragraph in document.paragraphs)
    assert_text_quality(text, source=docx_path)
    metadata = assert_docx_metadata(docx_path)
    return {
        "paragraphs": len(document.paragraphs),
        "chars": len(text),
        "required_tokens": True,
        "metadata_pages": int(metadata["pages"]),
        "metadata_words": int(metadata["words"]),
        "metadata_current": bool(metadata["metadata_current"]),
    }


def qa_text_file(path: Path) -> dict[str, int | bool]:
    text = path.read_text(encoding="utf-8")
    assert_text_quality(text, source=path)
    return {"chars": len(text), "required_tokens": True}


def qa_readme(path: Path) -> dict[str, int | bool]:
    text = path.read_text(encoding="utf-8")
    for token in ("## Now", "## Selected Public Work", "## Engineering Biases", "## Reach Me"):
        if token not in text:
            raise AssertionError(f"{path} missing profile section: {token}")
    if "andrewcrozier86@gmail.com" in text:
        raise AssertionError("README must not expose the direct resume email")
    if text.count("# Andrew Crozier") != 1:
        raise AssertionError("README must contain exactly one H1")
    if "{{" in text or "}}" in text:
        raise AssertionError("README contains unreplaced template marker")
    forbidden = [token for token in FORBIDDEN_FACT_RISK_TOKENS if token in text]
    if forbidden:
        raise AssertionError(f"README contains public-consistency risk tokens: {forbidden}")
    return {"chars": len(text), "required_tokens": True}


def assert_text_quality(text: str, *, source: Path) -> None:
    missing = [token for token in REQUIRED_TEXT_TOKENS if token not in text]
    if missing:
        raise AssertionError(f"{source} is missing required tokens: {missing}")
    forbidden = [token for token in FORBIDDEN_TEXT_TOKENS if token in text]
    if forbidden:
        raise AssertionError(f"{source} contains forbidden tokens: {forbidden}")
    ats_hits = [token for token in FORBIDDEN_ATS_TOKENS if token.lower() in text.lower()]
    if ats_hits:
        raise AssertionError(f"{source} contains ATS-risk language/artifacts: {ats_hits}")
    fact_hits = [token for token in FORBIDDEN_FACT_RISK_TOKENS if token in text]
    if fact_hits:
        raise AssertionError(f"{source} contains public-consistency risk tokens: {fact_hits}")


def pdftotext(pdf_path: Path) -> str:
    try:
        return subprocess.run(
            ["pdftotext", str(pdf_path), "-"], check=True, text=True, capture_output=True
        ).stdout
    except FileNotFoundError as exc:
        raise RuntimeError("pdftotext is required for PDF QA") from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"pdftotext failed for {pdf_path}: {exc.stderr}") from exc


def pdf_pages(pdf_path: Path) -> int:
    try:
        output = subprocess.run(
            ["pdfinfo", str(pdf_path)], check=True, text=True, capture_output=True
        ).stdout
    except FileNotFoundError as exc:
        raise RuntimeError("pdfinfo is required for PDF QA") from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"pdfinfo failed for {pdf_path}: {exc.stderr}") from exc
    for line in output.splitlines():
        if line.startswith("Pages:"):
            return int(line.split(":", 1)[1].strip())
    raise RuntimeError(f"Could not read page count from {pdf_path}")
