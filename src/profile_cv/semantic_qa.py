from __future__ import annotations

import html
import re
from dataclasses import dataclass
from typing import Any, Literal

from .adapters import display_date
from .source import profile_url

Surface = Literal["readme", "markdown", "pdf", "docx", "html"]
RESUME_SURFACES: set[Surface] = {"markdown", "pdf", "docx", "html"}


@dataclass(frozen=True)
class SemanticResult:
    required_checked: int
    forbidden_checked: int

    def as_dict(self) -> dict[str, int | bool]:
        return {
            "semantic_reviewed": True,
            "semantic_required_checked": self.required_checked,
            "semantic_forbidden_checked": self.forbidden_checked,
        }


def assert_semantic_alignment(
    text: str, *, resume: dict[str, Any], surface: Surface
) -> SemanticResult:
    required, forbidden = surface_facts(resume, surface=surface)
    normalized = normalize_text(text)

    missing = [fact for fact in required if normalize_text(fact) not in normalized]
    leaked = [fact for fact in forbidden if fact and normalize_text(fact) in normalized]
    if missing or leaked:
        details: list[str] = []
        if missing:
            details.append(f"missing required facts: {missing[:8]}")
        if leaked:
            details.append(f"forbidden facts present: {leaked[:8]}")
        raise AssertionError(f"{surface} semantic QA failed: {'; '.join(details)}")

    return SemanticResult(required_checked=len(required), forbidden_checked=len(forbidden))


def surface_facts(resume: dict[str, Any], *, surface: Surface) -> tuple[list[str], list[str]]:
    basics = _mapping(resume, "basics")
    email = str(basics.get("email", ""))
    required = [
        str(basics.get("name", "")),
        profile_url(resume, "LinkedIn") or "",
        profile_url(resume, "GitHub") or "",
    ]
    forbidden: list[str] = []

    if surface == "readme":
        contact = basics.get("x_contact", {})
        if isinstance(contact, dict):
            required.append(str(contact.get("publicLocation", "")))
        required.extend(_profile_facts(resume))
        required.extend(_project_names(resume, "x_profile"))
        forbidden.append(email)
    elif surface in RESUME_SURFACES:
        required.append(email)
        required.extend(_resume_work_facts(resume))
        required.extend(_resume_skill_facts(resume))
        required.extend(_project_names(resume, "x_resume"))
        forbidden.extend(
            project
            for project in _project_names(resume, "x_profile")
            if project not in set(_project_names(resume, "x_resume"))
        )
    else:  # pragma: no cover - Surface typing prevents this branch.
        raise ValueError(f"Unsupported semantic QA surface: {surface}")

    return _clean_facts(required), _clean_facts(forbidden)


def normalize_text(value: str) -> str:
    value = html.unescape(value)
    value = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 \2", value)
    value = re.sub(r"https?://(?:www\.)?", "", value)
    value = value.replace("\u2013", "-").replace("\u2014", "-").replace("\u00a0", " ")
    value = value.replace("\u00ad", "").replace("\ufffe", "")
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value.casefold().strip()


def _profile_facts(resume: dict[str, Any]) -> list[str]:
    facts: list[str] = []
    for item in _list(resume, "work"):
        if not isinstance(item, dict):
            continue
        profile = item.get("x_profile", {})
        if not isinstance(profile, dict) or profile.get("section") == "omit":
            continue
        facts.append(str(profile.get("context") or item.get("name", "")))
        facts.append(str(profile.get("signal", "")))
    return facts


def _resume_work_facts(resume: dict[str, Any]) -> list[str]:
    facts: list[str] = []
    for item in _list(resume, "work"):
        if not isinstance(item, dict):
            continue
        facts.extend(
            [
                str(item.get("name", "")),
                str(item.get("position", "")),
                display_date(item),
            ]
        )
    return facts


def _resume_skill_facts(resume: dict[str, Any]) -> list[str]:
    facts: list[str] = []
    for skill in _list(resume, "skills"):
        if not isinstance(skill, dict):
            continue
        facts.append(str(skill.get("name", "")))
        facts.extend(str(keyword) for keyword in skill.get("keywords", [])[:2])
    return facts


def _project_names(resume: dict[str, Any], surface_key: str) -> list[str]:
    names: list[str] = []
    for project in _list(resume, "projects"):
        if (
            isinstance(project, dict)
            and isinstance(project.get(surface_key), dict)
            and project[surface_key].get("featured", False)
        ):
            names.append(str(project.get("name", "")))
    return names


def _clean_facts(values: list[str]) -> list[str]:
    seen: set[str] = set()
    facts: list[str] = []
    for raw_value in values:
        value = raw_value.strip()
        normalized = normalize_text(value)
        if value and normalized not in seen:
            seen.add(normalized)
            facts.append(value)
    return facts


def _mapping(payload: dict[str, Any], key: str) -> dict[str, Any]:
    value = payload.get(key)
    return value if isinstance(value, dict) else {}


def _list(payload: dict[str, Any], key: str) -> list[Any]:
    value = payload.get(key)
    return value if isinstance(value, list) else []
