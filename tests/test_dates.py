from __future__ import annotations

from pathlib import Path

import pytest

from profile_cv.adapters import format_date
from profile_cv.source import load_repo_schema, load_source, validate_date, validate_source

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    ("value", "display"),
    [
        ("2026", "2026"),
        ("2026-01", "Jan 2026"),
        ("2026-12", "Dec 2026"),
        ("2026-02-28", "Feb 2026"),
        ("2024-02-29", "Feb 2024"),
        ("2000-02-29", "Feb 2000"),
    ],
)
def test_dates_accept_supported_precision_and_valid_leap_days(value: str, display: str) -> None:
    validate_date(value, "work[0].startDate")
    assert format_date(value) == display


@pytest.mark.parametrize(
    "value",
    [
        "2026-00",
        "2026-13",
        "2026-02-31",
        "2026-02-29",
        "1900-02-29",
        "2026-04-31",
        "2026-01-00",
        "2026-01-32",
        "2026-1",
        "2026-01-1",
        "2026-01-01\n",
        "2026-01-01-extra",
    ],
)
def test_dates_reject_impossible_or_malformed_calendar_values(value: str) -> None:
    with pytest.raises(ValueError, match=r"work\[0\].startDate"):
        validate_date(value, "work[0].startDate")
    with pytest.raises(ValueError, match="date"):
        format_date(value)


@pytest.mark.parametrize("section", ["work", "education", "projects"])
@pytest.mark.parametrize("field", ["startDate", "endDate"])
@pytest.mark.parametrize("value", ["2026-00", "2026-13", "2026-02-31"])
def test_source_rejects_impossible_dates_in_each_dated_section(
    section: str, field: str, value: str
) -> None:
    resume = load_source(ROOT / "resume.yaml")
    resume[section][0][field] = value
    with pytest.raises(ValueError, match="valid calendar date"):
        validate_source(resume, schema=load_repo_schema(ROOT))


@pytest.mark.parametrize("value", ["", "Present"])
def test_display_preserves_existing_open_ended_date_sentinel(value: str) -> None:
    assert format_date(value) == "Present"
