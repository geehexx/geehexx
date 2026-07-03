from __future__ import annotations

from pathlib import Path

import yaml

from profile_cv.public_surface import (
    is_public_surface,
    load_policy,
    tracked_path_errors,
)


def test_public_surface_allows_sources_but_blocks_generated_and_non_public_paths() -> None:
    assert is_public_surface(Path("README.md"))
    assert is_public_surface(Path("resume.yaml"))
    assert is_public_surface(Path("AGENTS.md"))
    assert not is_public_surface(Path("uv.lock"))
    assert is_public_surface(Path("src/profile_cv/build.py"))
    assert not is_public_surface(Path("source/master.docx"))
    assert not is_public_surface(Path("dist/Andrew_Crozier_Resume.pdf"))

    fixture_paths = [
        Path("AGENTS.md"),
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
    assert any(pattern.pattern == "^dist/" for pattern in policy.blocked_tracked_paths)


def test_quality_policy_is_limited_to_repository_surface_boundaries() -> None:
    payload = yaml.safe_load(Path("quality-gates.yaml").read_text(encoding="utf-8"))

    assert set(payload) == {"public_surface"}
    assert set(payload["public_surface"]) == {
        "public_files",
        "public_dir_prefixes",
        "blocked_tracked_paths",
    }


def test_public_surface_policy_does_not_own_secret_or_content_scanning() -> None:
    policy = load_policy(Path("quality-gates.yaml"))

    assert set(policy.__dataclass_fields__) == {
        "public_files",
        "public_dir_prefixes",
        "blocked_tracked_paths",
    }


def test_public_surface_blocks_unknown_tracked_paths() -> None:
    errors = tracked_path_errors([Path("unexpected.md")])

    assert errors == ["unexpected.md: tracked path outside public surface allowlist"]
