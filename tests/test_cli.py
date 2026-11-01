from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

import pytest

import profile_cv.cli
from profile_cv.cli import main
from profile_cv.source import load_source, serialize_source

ROOT = Path(__file__).resolve().parents[1]


def test_review_package_cli_prints_concise_summary(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    def fake_build_review_package(*, root: Path, package_dir: Path | None = None) -> dict[str, Any]:
        assert root == ROOT
        assert package_dir is None
        return {"source": {"head_sha": "head-sha-for-test"}, "files": [{"path": "REVIEW.md"}]}

    monkeypatch.setattr(profile_cv.cli, "build_review_package", fake_build_review_package)

    assert main(["--root", str(ROOT), "review-package"]) == 0

    captured = capsys.readouterr()
    assert captured.out == "review-package: ok path=dist/review-package files=1 head=head-sha-for\n"
    assert captured.err == ""


def test_review_package_cli_json_flag_emits_manifest(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    manifest = {"source": {"head_sha": "head-sha-for-test"}, "files": [{"path": "REVIEW.md"}]}

    def fake_build_review_package(*, root: Path, package_dir: Path | None = None) -> dict[str, Any]:
        assert root == ROOT
        assert package_dir is None
        return manifest

    monkeypatch.setattr(profile_cv.cli, "build_review_package", fake_build_review_package)

    assert main(["--root", str(ROOT), "review-package", "--json"]) == 0

    captured = capsys.readouterr()
    assert json.loads(captured.out) == manifest
    assert captured.err == ""


@pytest.mark.parametrize("invalid", ["timestamp", "basename"])
def test_validate_cli_rejects_unsupported_build_metadata(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], invalid: str
) -> None:
    resume = load_source(ROOT / "resume.yaml")
    if invalid == "timestamp":
        resume["meta"]["lastModified"] = "2026-11-01"
    else:
        resume["meta"]["x_outputs"]["defaultResumeBasename"] = "other"
    (tmp_path / "resume.yaml").write_text(serialize_source(resume), encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text("", encoding="utf-8")
    shutil.copytree(ROOT / "schemas", tmp_path / "schemas")
    assert main(["--root", str(tmp_path), "validate"]) == 1
    assert "error:" in capsys.readouterr().err


def test_doctor_cli_rejects_incompatible_renderer(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(profile_cv.cli, "doctor", lambda: {"pandoc": True})

    def incompatible() -> None:
        raise RuntimeError("Reproducible builds require Pandoc 3.1.11.1")

    monkeypatch.setattr(profile_cv.cli, "assert_doctor", incompatible)
    assert main(["--root", str(ROOT), "doctor"]) == 1
    assert "require Pandoc" in capsys.readouterr().err
