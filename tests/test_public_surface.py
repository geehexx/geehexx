from __future__ import annotations

from pathlib import Path

import pytest

from profile_cv.public_surface import (
    GENERIC_TEXT_RULES,
    Rule,
    is_public_surface,
    load_policy,
    scan_file,
    tracked_path_errors,
)


def test_public_surface_allows_sources_but_blocks_generated_and_private_paths() -> None:
    assert is_public_surface(Path("README.md"))
    assert is_public_surface(Path("resume.yaml"))
    assert is_public_surface(Path("AGENTS.md"))
    assert not is_public_surface(Path("uv.lock"))
    assert is_public_surface(Path("src/profile_cv/build.py"))
    assert not is_public_surface(Path("source/master.docx"))
    assert not is_public_surface(Path("dist/Andrew_Crozier_Resume.pdf"))

    fixture_paths = [
        Path("AGENTS.md"),  # public-surface-allow: scanner fixture
        Path("dist/out.pdf"),
        Path("source/master.docx"),
        Path("uv.lock"),
        Path(".venv/pyvenv.cfg"),
        Path("resume.yaml"),
        Path("AGENTS.md"),
    ]
    errors = tracked_path_errors(fixture_paths)
    assert len(errors) == 4
    assert not any("resume.yaml" in error for error in errors)
    assert not any("AGENTS.md" in error for error in errors)


def test_public_surface_policy_is_loaded_from_yaml() -> None:
    policy = load_policy(Path("quality-gates.yaml"))

    assert "AGENTS.md" in policy.public_files
    assert "resume.yaml" in policy.public_files
    assert "WestJet" in policy.fact_risk_tokens
    assert any(pattern.pattern == "^dist/" for pattern in policy.blocked_tracked_paths)


def test_public_surface_scanner_catches_tool_citation_leaks(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    path = tmp_path / "README.md"
    leak = "bad sandbox:" + "/mnt" + "/data/file.pdf\n"
    path.write_text(leak, encoding="utf-8")
    rules = [Rule(rule_id, pattern) for rule_id, pattern in GENERIC_TEXT_RULES.items()]

    hits = scan_file(Path("README.md"), rules)

    assert hits
    assert hits[0].rule_id == "tool-citation-leak"


def test_public_surface_scanner_catches_internal_package_index_leaks(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    path = tmp_path / "pyproject.toml"
    # public-surface-allow: scanner fixture
    index_url = 'index-url = "https://packages.example.'
    index_url += "internal/artifact"
    index_url += 'ory"\n'
    path.write_text(index_url, encoding="utf-8")
    rules = [Rule(rule_id, pattern) for rule_id, pattern in GENERIC_TEXT_RULES.items()]

    hits = scan_file(Path("pyproject.toml"), rules)

    assert hits
    assert hits[0].rule_id == "internal-package-index"


def test_public_surface_scanner_catches_common_secret_shapes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    path = tmp_path / "README.md"
    aws_key = "AKIA" + "1234567890ABCDEF"
    github_token = "ghp_" + "1234567890abcdefghijklmnopqrstuvwxyzAB"
    openai_key = "sk-" + "a" * 40
    anthropic_key = "sk-ant-" + "b" * 40
    google_key = "AIza" + "c" * 35
    slack_token = "xoxb-" + "1" * 24
    long_api_key = "abcdefghijklmnopqrstuvwxyzABCDEF123456"
    path.write_text(
        "\n".join(
            [
                aws_key,
                github_token,
                openai_key,
                anthropic_key,
                google_key,
                slack_token,
                f"api_key={long_api_key}",
            ]
        ),
        encoding="utf-8",
    )
    rules = [Rule(rule_id, pattern) for rule_id, pattern in GENERIC_TEXT_RULES.items()]

    hits = scan_file(Path("README.md"), rules)
    rule_ids = {hit.rule_id for hit in hits}

    assert {
        "aws-access-key-id",
        "github-token",
        "openai-api-key",
        "anthropic-api-key",
        "google-api-key",
        "slack-token",
        "generic-secret-assignment",
    }.issubset(rule_ids)
