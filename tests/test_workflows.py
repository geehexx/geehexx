from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.check_workflows import (  # noqa: E402
    assert_dependabot_policy,
    assert_workflow_policy,
    workflow_paths,
)


def test_github_actions_workflows_keep_security_and_reproducibility_guards() -> None:
    paths = workflow_paths()
    assert paths
    errors = [error for path in paths for error in assert_workflow_policy(path)]
    errors.extend(assert_dependabot_policy())
    assert errors == []
    assert not (ROOT / ".github" / "workflows" / "pages.yml").exists()


def test_docs_are_consolidated_into_maintainer_guide() -> None:
    docs = ROOT / "docs"

    assert (docs / "maintainer-guide.md").exists()
    assert not (docs / "quality-gates.md").exists()
    assert not (docs / "source-model.md").exists()
    assert not (docs / "tooling-decisions.md").exists()
    assert not (ROOT / "CONTRIBUTING.md").exists()
    assert not (ROOT / "SECURITY.md").exists()


def test_pre_commit_uses_standard_secret_scanner() -> None:
    text = (ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8")
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

    assert "https://github.com/Yelp/detect-secrets" in text
    assert "detect-secrets" in text
    assert "detect-secrets-hook" in ci


def test_hooks_and_ci_use_standard_workflow_tools() -> None:
    pre_commit = (ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8")
    lefthook = (ROOT / "lefthook.yml").read_text(encoding="utf-8")
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

    for token in ("actionlint", "check-jsonschema", "yamllint", "zizmor"):
        assert token in pre_commit
        assert token in lefthook
        assert token in ci

    assert ".github/workflows/*.yml" in pre_commit
    assert ".github/workflows/*.yml" in lefthook


def test_workflows_use_frozen_lockfile_installs() -> None:
    for workflow in workflow_paths():
        text = workflow.read_text(encoding="utf-8")
        assert "uv.lock" in text
        assert "uv sync --frozen --extra dev" in text


def test_ci_uploads_review_package_artifact() -> None:
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

    assert "libreoffice-java-common" in ci
    assert "default-jre-headless" in ci
    assert "profile-cv compare-" not in ci
    assert "scripts/render_" not in ci
    assert "uv run profile-cv review-package" in ci
    assert "path: dist/review-package/" in ci
    assert "artifact-url" in ci
    assert "artifact-digest" in ci


def test_pull_request_template_captures_review_evidence() -> None:
    template = ROOT / ".github" / "pull_request_template.md"
    text = template.read_text(encoding="utf-8")

    assert "## Summary" in text
    assert "## Validation" in text
    assert "## Source, Artifact, And Contact Boundary" in text
    assert "## CI / Artifact Evidence" in text
    assert "## Artifact Review" in text
    assert "## Release Readiness" in text
    assert "## Local Limitations" in text
