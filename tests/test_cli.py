from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from profile_cv import cli

ROOT = Path(__file__).resolve().parents[1]


def test_review_package_cli_prints_concise_summary(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    def fake_build_review_package(*, root: Path, package_dir: Path | None = None) -> dict[str, Any]:
        assert root == ROOT
        assert package_dir is None
        return {"source": {"head_sha": "abcdef1234567890"}, "files": [{"path": "REVIEW.md"}]}

    monkeypatch.setattr(cli, "build_review_package", fake_build_review_package)

    assert cli.main(["--root", str(ROOT), "review-package"]) == 0

    captured = capsys.readouterr()
    assert captured.out == "review-package: ok path=dist/review-package files=1 head=abcdef123456\n"
    assert captured.err == ""


def test_review_package_cli_json_flag_emits_manifest(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    manifest = {"source": {"head_sha": "abcdef1234567890"}, "files": [{"path": "REVIEW.md"}]}

    def fake_build_review_package(*, root: Path, package_dir: Path | None = None) -> dict[str, Any]:
        assert root == ROOT
        assert package_dir is None
        return manifest

    monkeypatch.setattr(cli, "build_review_package", fake_build_review_package)

    assert cli.main(["--root", str(ROOT), "review-package", "--json"]) == 0

    captured = capsys.readouterr()
    assert json.loads(captured.out) == manifest
    assert captured.err == ""
