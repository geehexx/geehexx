from __future__ import annotations

import os
import shutil

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

    assert qa.doctor() == dict.fromkeys(expected, True)
    qa.assert_doctor()
