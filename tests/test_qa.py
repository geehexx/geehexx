from __future__ import annotations

import os
import shutil
import subprocess

import pytest

from profile_cv import qa


def test_doctor_reports_required_artifact_qa_tools(monkeypatch: pytest.MonkeyPatch) -> None:
    expected = (
        "rendercv",
        "pandoc",
        "pdfinfo",
        "pdftotext",
        "libreoffice",
        "java",
    )

    def fake_which(
        command: str,
        _mode: int = os.F_OK | os.X_OK,
        _path: str | None = None,
    ) -> str:
        assert command in expected
        return f"/usr/bin/{command}"

    monkeypatch.setattr(shutil, "which", fake_which)
    monkeypatch.setattr(qa, "assert_pandoc_version", lambda: None)

    assert qa.doctor() == dict.fromkeys(expected, True)
    qa.assert_doctor()


@pytest.mark.parametrize("version", ["3.1.3", "3.2", ""])
def test_pandoc_preflight_rejects_toolchain_drift(
    monkeypatch: pytest.MonkeyPatch, version: str
) -> None:
    def fake_run(*_args: object, **_kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess("pandoc", 0, f"pandoc {version}\n", "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    with pytest.raises(RuntimeError, match="require Pandoc 3.1.11.1"):
        qa.assert_pandoc_version()
