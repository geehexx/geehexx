from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.check_workflows import (  # noqa: E402
    assert_dependabot_policy,
    assert_pages_workflow,
    assert_workflow_policy,
    workflow_paths,
)


def test_github_actions_workflows_keep_security_and_reproducibility_guards() -> None:
    paths = workflow_paths()
    assert paths
    errors = [error for path in paths for error in assert_workflow_policy(path)]
    errors.extend(assert_pages_workflow())
    errors.extend(assert_dependabot_policy())
    assert errors == []


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


def test_pull_request_template_captures_review_evidence() -> None:
    template = ROOT / ".github" / "pull_request_template.md"
    text = template.read_text(encoding="utf-8")

    assert "## Summary" in text
    assert "## Validation" in text
    assert "## Artifact Review" in text
    assert "## Local Limitations" in text
