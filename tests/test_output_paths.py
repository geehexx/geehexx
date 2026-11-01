from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from profile_cv import build as build_module
from profile_cv.build import build_all, build_review_package
from profile_cv.paths import mark_output, validate_output_directory
from profile_cv.source import load_source, serialize_source


@pytest.fixture
def fake_repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    (root / "resume.yaml").write_text("canonical")
    for name in ("src", "templates", "dist", "site"):
        (root / name).mkdir()
        (root / name / "sentinel").write_text("keep")
    return root


@pytest.mark.parametrize(
    "location", ["root", "ancestor", "src", "src/nested", "dist", "site", "site/review"]
)
def test_review_rejects_destructive_outputs(fake_repo: Path, location: str) -> None:
    output = {"root": fake_repo, "ancestor": fake_repo.parent}.get(location, fake_repo / location)
    with pytest.raises(ValueError):
        build_review_package(root=fake_repo, package_dir=output)
    assert (fake_repo / "resume.yaml").read_text() == "canonical"
    for name in ("src", "templates", "dist", "site"):
        assert (fake_repo / name / "sentinel").read_text() == "keep"


@pytest.mark.parametrize("clean", [False, True])
@pytest.mark.parametrize("kind", ["dist", "site"])
def test_build_rejects_source_output_before_loading(
    fake_repo: Path, monkeypatch: pytest.MonkeyPatch, clean: bool, kind: str
) -> None:
    def unexpected(*_args: Any, **_kwargs: Any) -> None:
        pytest.fail("Source loading must not happen before output validation")

    monkeypatch.setattr(build_module, "load_validated_resume", unexpected)
    with pytest.raises(ValueError):
        build_all(
            root=fake_repo,
            clean=clean,
            dist_dir=fake_repo / "src" if kind == "dist" else None,
            site_dir=fake_repo / "src" if kind == "site" else None,
        )
    assert (fake_repo / "src" / "sentinel").read_text() == "keep"


@pytest.mark.parametrize("nested", [False, True])
def test_build_rejects_overlapping_outputs(fake_repo: Path, nested: bool) -> None:
    dist = fake_repo / "dist"
    with pytest.raises(ValueError, match="must not overlap"):
        build_all(root=fake_repo, dist_dir=dist, site_dir=dist / "preview" if nested else dist)
    assert (dist / "sentinel").exists()


@pytest.mark.parametrize("leaf", [False, True])
def test_symlink_alias_is_rejected(fake_repo: Path, leaf: bool) -> None:
    link = fake_repo.parent / "alias"
    link.symlink_to(fake_repo / "src" if leaf else fake_repo, target_is_directory=True)
    with pytest.raises(ValueError, match="symlinks"):
        build_review_package(root=fake_repo, package_dir=link if leaf else link / "src")
    assert (fake_repo / "src" / "sentinel").read_text() == "keep"


def test_dotdot_alias_is_rejected(fake_repo: Path) -> None:
    with pytest.raises(ValueError):
        build_review_package(root=fake_repo, package_dir=fake_repo / "dist" / ".." / "src")
    assert (fake_repo / "src" / "sentinel").exists()


def test_nonempty_external_directory_is_not_owned(fake_repo: Path) -> None:
    external = fake_repo.parent / "unrelated"
    external.mkdir()
    (external / "precious").write_text("keep")
    with pytest.raises(ValueError, match="unowned"):
        build_review_package(root=fake_repo, package_dir=external)
    assert (external / "precious").read_text() == "keep"


def test_external_outputs_support_new_empty_and_marked_directories(fake_repo: Path) -> None:
    external = fake_repo.parent / "repo-output"
    validate_output_directory(external, root=fake_repo)
    external.mkdir()
    validate_output_directory(external, root=fake_repo)
    mark_output(external)
    (external / "old-artifact").write_text("old")
    validate_output_directory(external, root=fake_repo)


def test_relative_outputs_remain_cwd_relative(
    fake_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(fake_repo.parent)
    validate_output_directory(Path("external"), root=fake_repo)
    assert not (fake_repo / "external").exists()


def test_external_resume_cannot_be_cleaned(fake_repo: Path) -> None:
    external = fake_repo.parent / "custom-source"
    external.mkdir()
    source = external / "resume.yaml"
    source.write_text("keep")
    mark_output(external)
    with pytest.raises(ValueError, match="overlaps"):
        build_all(root=fake_repo, resume_path=source, dist_dir=external, clean=True)
    assert source.read_text() == "keep"


def test_existing_output_file_symlink_is_rejected(fake_repo: Path) -> None:
    (fake_repo / "dist" / "redirect").symlink_to(fake_repo / "resume.yaml")
    with pytest.raises(ValueError, match="symlinks"):
        build_all(root=fake_repo, clean=False)
    assert (fake_repo / "resume.yaml").read_text() == "canonical"


def test_missing_inputs_preserve_existing_package(fake_repo: Path) -> None:
    package = fake_repo / "dist" / "review-package"
    package.mkdir()
    (package / "previous-review").write_text("keep")
    with pytest.raises(FileNotFoundError):
        build_review_package(root=fake_repo)
    assert (package / "previous-review").read_text() == "keep"


def test_source_directory_cannot_be_reclassified_by_marker(fake_repo: Path) -> None:
    mark_output(fake_repo / "src")
    with pytest.raises(ValueError, match="overlaps"):
        build_review_package(root=fake_repo, package_dir=fake_repo / "src")
    assert (fake_repo / "src" / "sentinel").exists()


def test_empty_custom_directory_inside_repository_is_allowed(fake_repo: Path) -> None:
    output = fake_repo / "custom-output"
    output.mkdir()
    validate_output_directory(output, root=fake_repo)


def test_default_output_alias_cannot_authorize_source_deletion(fake_repo: Path) -> None:
    dist = fake_repo / "dist"
    (dist / "sentinel").unlink()
    dist.rmdir()
    dist.symlink_to(fake_repo / "src", target_is_directory=True)
    with pytest.raises(ValueError, match="symlinks"):
        build_all(root=fake_repo, dist_dir=fake_repo / "src", clean=True)
    assert (fake_repo / "src" / "sentinel").read_text() == "keep"
    with pytest.raises(ValueError, match="symlinks"):
        build_review_package(root=fake_repo, package_dir=fake_repo / "src")
    assert (fake_repo / "src" / "sentinel").read_text() == "keep"


def test_unsupported_basename_fails_before_cleaning_outputs(tmp_path: Path) -> None:
    from_root = Path(__file__).resolve().parents[1]
    resume = load_source(from_root / "resume.yaml")
    resume["meta"]["x_outputs"]["defaultResumeBasename"] = "unexpected"
    custom_source = tmp_path / "custom.yaml"
    custom_source.write_text(serialize_source(resume), encoding="utf-8")
    output = tmp_path / "dist"
    output.mkdir()
    mark_output(output)
    sentinel = output / "sentinel"
    sentinel.write_text("keep", encoding="utf-8")
    with pytest.raises(ValueError, match="defaultResumeBasename"):
        build_all(
            root=from_root,
            resume_path=custom_source,
            dist_dir=output,
            site_dir=tmp_path / "site",
            clean=True,
        )
    assert sentinel.read_text(encoding="utf-8") == "keep"
