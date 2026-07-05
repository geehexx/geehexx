from __future__ import annotations

from pathlib import Path

import pytest

from profile_cv.adapters import render_template
from profile_cv.semantic_qa import assert_semantic_alignment
from profile_cv.source import load_source

ROOT = Path(__file__).resolve().parents[1]
RESUME = ROOT / "resume.yaml"


def test_generated_readme_matches_profile_semantic_policy() -> None:
    resume = load_source(RESUME)
    text = render_template(resume, ROOT / "templates", "README.md.j2")

    result = assert_semantic_alignment(text, resume=resume, surface="readme")

    assert result.required_checked > 20
    assert result.forbidden_checked == 1


def test_generated_ats_markdown_matches_resume_semantic_policy() -> None:
    resume = load_source(RESUME)
    text = render_template(resume, ROOT / "templates", "resume.md.j2")

    result = assert_semantic_alignment(text, resume=resume, surface="markdown")

    assert result.required_checked > 50
    assert result.forbidden_checked == 3


def test_semantic_policy_catches_public_email_leak() -> None:
    resume = load_source(RESUME)
    text = render_template(resume, ROOT / "templates", "README.md.j2")

    with pytest.raises(AssertionError, match="forbidden facts present"):
        assert_semantic_alignment(
            f"{text}\n{resume['basics']['email']}", resume=resume, surface="readme"
        )
