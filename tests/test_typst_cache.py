from __future__ import annotations

import os
from pathlib import Path

from profile_cv.build import _directory_matches


def test_directory_comparison_reads_equal_size_equal_mtime_contents(tmp_path: Path) -> None:
    left, right = tmp_path / "left", tmp_path / "right"
    left.mkdir()
    right.mkdir()
    for directory, content in ((left, "first"), (right, "other")):
        path = directory / "typst.typ"
        path.write_text(content, encoding="utf-8")
        os.utime(path, (1_700_000_000, 1_700_000_000))
    assert not _directory_matches(left, right)
    (right / "typst.typ").write_text("first", encoding="utf-8")
    assert _directory_matches(left, right)


def test_directory_comparison_rejects_file_directory_mismatch(tmp_path: Path) -> None:
    left, right = tmp_path / "left", tmp_path / "right"
    left.mkdir()
    right.mkdir()
    (left / "nested").mkdir()
    (right / "nested").write_text("not a directory", encoding="utf-8")
    assert not _directory_matches(left, right)
    assert not _directory_matches(left, right / "nested")


def test_directory_comparison_does_not_reuse_cached_stat_signatures(tmp_path: Path) -> None:
    left, right = tmp_path / "left", tmp_path / "right"
    left.mkdir()
    right.mkdir()
    for directory in (left, right):
        (directory / "same").write_text("first", encoding="utf-8")
        os.utime(directory / "same", (1_700_000_000, 1_700_000_000))
    assert _directory_matches(left, right)
    (right / "same").write_text("other", encoding="utf-8")
    os.utime(right / "same", (1_700_000_000, 1_700_000_000))
    assert not _directory_matches(left, right)
