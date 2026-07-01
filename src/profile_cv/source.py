from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft7Validator

from .quality_policy import QualityPolicy, default_policy

Resume = dict[str, Any]

DATE_RE = re.compile(r"^([1-2][0-9]{3})(-[0-1][0-9])?(-[0-3][0-9])?$")

FORBIDDEN_FACT_RISK_TOKENS = default_policy().fact_risk_tokens


def load_source(path: Path) -> Resume:
    """Load the canonical YAML source document."""
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected YAML mapping in {path}")
    return payload


def serialize_source(payload: Resume) -> str:
    return yaml.safe_dump(payload, sort_keys=False, allow_unicode=True, width=100)


def write_json(path: Path, payload: Resume) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_repo_schema(root: Path) -> Resume:
    path = root / "schemas" / "jsonresume.schema.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return payload


def validate_source(
    resume: Resume, *, schema: Resume | None = None, policy: QualityPolicy | None = None
) -> None:
    """Validate schema shape plus project-specific semantic invariants.

    The YAML source keeps JSON Resume-compatible sections and x_ extension fields.
    """
    policy = policy or default_policy()
    if schema is not None:
        errors = sorted(Draft7Validator(schema).iter_errors(resume), key=lambda error: error.path)
        if errors:
            formatted = "; ".join(f"{list(error.path)}: {error.message}" for error in errors[:5])
            raise ValueError(f"JSON Resume schema validation failed: {formatted}")

    missing = [key for key in policy.required_top_level if key not in resume]
    if missing:
        raise ValueError(f"resume.yaml missing required top-level keys: {missing}")

    basics = require_mapping(resume, "basics")
    for key in ("name", "label", "summary", "profiles"):
        if key not in basics:
            raise ValueError(f"resume.basics missing required field: {key}")

    work = require_list(resume, "work")
    if len(work) < 8:
        raise ValueError("resume.work unexpectedly short")
    for index, item in enumerate(work):
        if not isinstance(item, dict):
            raise ValueError(f"resume.work[{index}] must be an object")
        for key in ("name", "position", "location", "startDate", "highlights"):
            if key not in item:
                raise ValueError(f"resume.work[{index}] missing {key}")
        validate_date(str(item["startDate"]), f"work[{index}].startDate")
        if item.get("endDate"):
            validate_date(str(item["endDate"]), f"work[{index}].endDate")
        if not item["highlights"]:
            raise ValueError(f"resume.work[{index}] has no highlights")

    projects = require_list(resume, "projects")
    if len(projects) < 8:
        raise ValueError("resume.projects should include public GitHub work")
    project_names = {project.get("name") for project in projects if isinstance(project, dict)}
    for project_name in ("library-ops", "mcp-web"):
        if project_name not in project_names:
            raise ValueError(f"resume.projects missing {project_name}")

    text = serialize_source(resume)
    missing_tokens = [token for token in policy.required_tokens if token not in text]
    if missing_tokens:
        raise ValueError(f"resume.yaml missing expected resume tokens: {missing_tokens}")
    forbidden_tokens = [token for token in policy.fact_risk_tokens if token in text]
    if forbidden_tokens:
        raise ValueError(f"resume.yaml contains public-consistency risk tokens: {forbidden_tokens}")


def validate_date(value: str, field_name: str) -> None:
    if not DATE_RE.match(value):
        raise ValueError(f"{field_name} is not JSON Resume ISO-8601-like date: {value}")


def require_mapping(payload: Resume, key: str) -> Resume:
    value = payload.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"{key} must be an object")
    return value


def require_list(payload: Resume, key: str) -> list[Any]:
    value = payload.get(key)
    if not isinstance(value, list):
        raise ValueError(f"{key} must be an array")
    return value


def profile_url(resume: Resume, network: str) -> str | None:
    profiles = resume.get("basics", {}).get("profiles", [])
    for profile in profiles:
        if isinstance(profile, dict) and profile.get("network") == network:
            url = profile.get("url")
            return str(url) if url else None
    return None


def profile_username(resume: Resume, network: str) -> str | None:
    profiles = resume.get("basics", {}).get("profiles", [])
    for profile in profiles:
        if isinstance(profile, dict) and profile.get("network") == network:
            username = profile.get("username")
            return str(username) if username else None
    return None


def markdown_link(label: str, url: str) -> str:
    return f"[{label}]({url})"


def plain_markdown(value: str) -> str:
    value = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", value)
    return value.replace("**", "").replace("*", "")
