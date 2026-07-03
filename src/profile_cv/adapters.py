from __future__ import annotations

import copy
import html
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import quote

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined

from .source import Resume, markdown_link, plain_markdown, profile_url, profile_username

DEFAULT_BASENAME = "Andrew_Crozier_Resume"


@dataclass(frozen=True)
class Badge:
    alt: str
    url: str
    src: str


@dataclass(frozen=True)
class CareerSignal:
    context: str
    signal: str


@dataclass(frozen=True)
class WorkView:
    name: str
    position: str
    location: str
    date_label: str
    highlights: list[str]


@dataclass(frozen=True)
class EducationView:
    institution: str
    study_type: str
    area: str
    date_label: str


@dataclass(frozen=True)
class SkillView:
    name: str
    keywords: list[str]


@dataclass(frozen=True)
class ProjectView:
    name: str
    description: str
    url: str
    type: str


@dataclass(frozen=True)
class ProfileView:
    name: str
    label: str
    summary: str
    email: str
    public_location: str
    contact_line: str
    github_url: str
    github_user: str
    linkedin_url: str
    linkedin_user: str
    profile: dict[str, Any]
    featured_projects: list[ProjectView]
    resume_projects: list[ProjectView]
    career_snapshot: list[CareerSignal]
    early_work: list[CareerSignal]
    resume_work: list[WorkView]
    education: list[EducationView]
    skills: list[SkillView]
    skill_map: dict[str, str]
    skill_chunks: dict[str, list[str]]
    profile_badges: list[Badge]
    resume_basename: str


def env_for(template_dir: Path, *, autoescape: bool = False) -> Environment:
    return Environment(
        loader=FileSystemLoader(str(template_dir)),
        undefined=StrictUndefined,
        autoescape=autoescape,
        trim_blocks=False,
        lstrip_blocks=False,
    )


def render_template(
    resume: Resume, template_dir: Path, name: str, *, autoescape: bool = False
) -> str:
    template = env_for(template_dir, autoescape=autoescape).get_template(name)
    text = template.render(resume=resume, view=view_model(resume)).rstrip() + "\n"
    return re.sub(r"\n{3,}", "\n\n", text)


def view_model(resume: Resume) -> ProfileView:
    basics = resume["basics"]
    meta = resume["meta"]
    profile = meta["x_profile"]
    github_url = profile_url(resume, "GitHub") or "https://github.com/geehexx"
    linkedin_url = profile_url(resume, "LinkedIn") or "https://linkedin.com/in/ancrozier"
    github_user = profile_username(resume, "GitHub") or "geehexx"
    featured_projects = projects_for_surface(resume, "x_profile")
    resume_projects = projects_for_surface(resume, "x_resume")
    career_snapshot = [
        CareerSignal(
            context=str(item.get("x_profile", {}).get("context") or item["name"]),
            signal=str(item.get("x_profile", {}).get("signal", "")),
        )
        for item in resume.get("work", [])
        if isinstance(item, dict) and item.get("x_profile", {}).get("section") == "career_snapshot"
    ]
    early_work = [
        CareerSignal(
            context=str(item.get("x_profile", {}).get("context") or item["name"]),
            signal=str(item.get("x_profile", {}).get("signal", "")),
        )
        for item in resume.get("work", [])
        if isinstance(item, dict) and item.get("x_profile", {}).get("section") == "earlier_work"
    ]
    resume_work = work_views(resume)
    education = education_views(resume)
    skills = skill_views(resume)
    skill_map = {skill.name: " · ".join(skill.keywords) for skill in skills}
    skill_chunks = {
        skill["name"]: chunk_keywords(skill.get("keywords", []))
        for skill in resume["skills"]
        if isinstance(skill, dict) and skill.get("name")
    }
    return ProfileView(
        name=basics["name"],
        label=basics["label"],
        summary=basics["summary"],
        email=basics.get("email", ""),
        public_location=basics.get("x_contact", {}).get("publicLocation")
        or basics.get("location", {}).get("address", ""),
        contact_line=contact_line(resume),
        github_url=github_url,
        github_user=github_user,
        linkedin_url=linkedin_url,
        linkedin_user=profile_username(resume, "LinkedIn") or "ancrozier",
        profile=profile,
        featured_projects=featured_projects,
        resume_projects=resume_projects,
        career_snapshot=career_snapshot,
        early_work=early_work,
        resume_work=resume_work,
        education=education,
        skills=skills,
        skill_map=skill_map,
        skill_chunks=skill_chunks,
        profile_badges=profile_badges(
            github_url=github_url,
            github_user=github_user,
            linkedin_url=linkedin_url,
            linkedin_label=basics["name"],
        ),
        resume_basename=meta.get("x_outputs", {}).get("defaultResumeBasename", DEFAULT_BASENAME),
    )


def profile_badges(
    *, github_url: str, github_user: str, linkedin_url: str, linkedin_label: str
) -> list[Badge]:
    linked_in_badge = quote(linkedin_label.replace(" ", "_"), safe="")
    github_badge = quote(github_user, safe="")
    return [
        Badge(
            alt="LinkedIn",
            url=linkedin_url,
            src=(
                "https://img.shields.io/badge/"
                f"LinkedIn-{linked_in_badge}-0A66C2?style=for-the-badge"
                "&logo=linkedin&logoColor=white"
            ),
        ),
        Badge(
            alt="GitHub",
            url=github_url,
            src=(
                "https://img.shields.io/badge/"
                f"GitHub-{github_badge}-181717?style=for-the-badge"
                "&logo=github&logoColor=white"
            ),
        ),
        Badge(
            alt="Focus",
            url="#now",
            src="https://img.shields.io/badge/Focus-production_AI_systems-7C3AED?style=for-the-badge",
        ),
        Badge(
            alt="Open to",
            url="#reach-me",
            src="https://img.shields.io/badge/Open_to-AI_%2F_platform_%2F_backend_roles-16A34A?style=for-the-badge",
        ),
    ]


def projects_for_surface(resume: Resume, surface_key: str) -> list[ProjectView]:
    projects: list[ProjectView] = []
    for project in resume.get("projects", []):
        if not isinstance(project, dict) or not project.get(surface_key, {}).get("featured", False):
            continue
        projects.append(
            ProjectView(
                name=str(project["name"]),
                description=str(project.get("description", "")),
                url=str(project.get("url", "")),
                type=str(project.get("type", "")),
            )
        )
    return projects


def work_views(resume: Resume) -> list[WorkView]:
    views: list[WorkView] = []
    for item in resume.get("work", []):
        if not isinstance(item, dict):
            continue
        views.append(
            WorkView(
                name=str(item["name"]),
                position=str(item["position"]),
                location=str(item.get("location", "")),
                date_label=display_date(item),
                highlights=clean_highlights(item.get("highlights", [])),
            )
        )
    return views


def education_views(resume: Resume) -> list[EducationView]:
    views: list[EducationView] = []
    for item in resume.get("education", []):
        if not isinstance(item, dict):
            continue
        views.append(
            EducationView(
                institution=str(item["institution"]),
                study_type=str(item.get("studyType", "")),
                area=str(item.get("area", "")),
                date_label=display_date(item),
            )
        )
    return views


def skill_views(resume: Resume) -> list[SkillView]:
    return [
        SkillView(
            name=str(skill["name"]),
            keywords=[str(keyword) for keyword in skill.get("keywords", [])],
        )
        for skill in resume.get("skills", [])
        if isinstance(skill, dict) and skill.get("name")
    ]


def chunk_keywords(values: list[Any], *, max_chars: int = 120) -> list[str]:
    chunks: list[str] = []
    current: list[str] = []
    for value in values:
        keyword = str(value).strip()
        if not keyword:
            continue
        candidate = " · ".join([*current, keyword])
        if current and len(candidate) > max_chars:
            chunks.append(" · ".join(current))
            current = [keyword]
        else:
            current.append(keyword)
    if current:
        chunks.append(" · ".join(current))
    return chunks


def contact_line(resume: Resume) -> str:
    basics = resume["basics"]
    contact = basics.get("x_contact", {})
    location = basics.get("location", {}).get("address", "")
    parts = [
        part
        for part in [
            location,
            contact.get("workAuthorization"),
            contact.get("remote"),
            contact.get("relocation"),
            basics.get("email"),
        ]
        if part
    ]
    return " - ".join(str(part) for part in parts)


def to_rendercv(resume: Resume) -> dict[str, Any]:
    """Adapt canonical profile/CV source into RenderCV YAML."""
    basics = resume["basics"]
    cv: dict[str, Any] = {
        "name": basics["name"],
        "headline": basics["label"],
        "location": basics.get("location", {}).get("address", ""),
        "email": basics.get("email", ""),
        "social_networks": [],
        "custom_connections": [],
        "sections": {},
    }
    for profile in basics.get("profiles", []):
        if not isinstance(profile, dict):
            continue
        if profile.get("network") in {"LinkedIn", "GitHub"} and profile.get("username"):
            cv["social_networks"].append(
                {"network": str(profile["network"]), "username": str(profile["username"])}
            )
    contact = basics.get("x_contact", {})
    connection_icons = {
        "workAuthorization": "passport",
        "remote": "globe",
        "relocation": "location-arrow",
    }
    for key in ("workAuthorization", "remote", "relocation"):
        if contact.get(key):
            cv["custom_connections"].append(
                {
                    "fontawesome_icon": connection_icons[key],
                    "placeholder": str(contact[key]),
                    "url": None,
                }
            )

    cv["sections"]["Summary"] = [basics["summary"]]
    cv["sections"]["Technologies"] = [
        {"label": skill["name"], "details": ", ".join(skill.get("keywords", []))}
        for skill in resume.get("skills", [])
        if isinstance(skill, dict) and skill.get("name")
    ]
    cv["sections"]["Experience"] = [
        {
            "company": item["name"],
            "position": item["position"],
            "date": display_date(item),
            "location": item.get("location", ""),
            "highlights": clean_highlights(item.get("highlights", [])),
        }
        for item in resume.get("work", [])
        if isinstance(item, dict) and item.get("name") and item.get("position")
    ]
    cv["sections"]["Selected Public Work"] = [
        {
            "name": markdown_link(project["name"], project["url"]),
            "summary": project["description"],
        }
        for project in resume.get("projects", [])
        if isinstance(project, dict)
        and project.get("x_resume", {}).get("featured", False)
        and project.get("url")
    ]
    cv["sections"]["Education"] = [
        {
            "institution": item["institution"],
            "degree": item.get("studyType", ""),
            "area": item.get("area", ""),
            "date": display_date(item),
        }
        for item in resume.get("education", [])
        if isinstance(item, dict) and item.get("institution")
    ]

    rendercv_meta = resume["meta"].get("x_rendercv", {})
    settings = copy.deepcopy(rendercv_meta.get("settings", {}))
    settings.setdefault("current_date", resume["meta"].get("lastModified", "")[:10])
    settings.setdefault("pdf_title", f"{basics['name']} - Resume")
    return {
        "cv": cv,
        "design": copy.deepcopy(rendercv_meta.get("design", {})),
        "locale": copy.deepcopy(rendercv_meta.get("locale", {"language": "english"})),
        "settings": settings,
    }


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    schema_line = (
        "# yaml-language-server: "
        "$schema=https://raw.githubusercontent.com/rendercv/rendercv/refs/tags/v2.8/schema.json\n"
    )
    path.write_text(
        schema_line + yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=110),
        encoding="utf-8",
    )


def date_range(item: dict[str, Any]) -> str:
    start = str(item.get("startDate") or "")
    end = str(item.get("endDate") or "Present")
    return f"{format_date(start)} - {format_date(end)}" if start else format_date(end)


def display_date(item: dict[str, Any]) -> str:
    display = item.get("x_display", {})
    if isinstance(display, dict) and display.get("dateLabel"):
        return str(display["dateLabel"])
    return date_range(item)


def format_date(value: str) -> str:
    if not value:
        return "Present"
    if value == "Present":
        return value
    parts = value.split("-")
    if len(parts) == 1:
        return parts[0]
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    month = months[int(parts[1]) - 1]
    return f"{month} {parts[0]}"


def clean_highlights(values: list[Any]) -> list[str]:
    return [
        str(value).replace(" - ", " -- ").replace("\u00ad", "").replace("\ufffe", "").strip()
        for value in values
        if str(value).strip()
    ]


def to_json_ld(resume: Resume) -> dict[str, Any]:
    basics = resume["basics"]
    return {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": basics["name"],
        "jobTitle": basics["label"],
        "url": profile_url(resume, "GitHub"),
        "sameAs": [
            profile.get("url") for profile in basics.get("profiles", []) if profile.get("url")
        ],
        "knowsAbout": sorted(
            {keyword for skill in resume["skills"] for keyword in skill.get("keywords", [])}
        ),
    }


def strip_markdown_for_docx(text: str) -> str:
    return plain_markdown(html.unescape(text))
