from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

DEFAULT_POLICY_PATH = Path("quality-gates.yaml")


@dataclass(frozen=True)
class TextRule:
    rule_id: str
    pattern: re.Pattern[str]


@dataclass(frozen=True)
class QualityPolicy:
    public_files: frozenset[str]
    public_dir_prefixes: tuple[str, ...]
    scan_excluded_files: frozenset[str]
    blocked_tracked_paths: tuple[re.Pattern[str], ...]
    binary_suffixes: frozenset[str]
    private_allow_marker: str
    text_rules: tuple[TextRule, ...]
    required_top_level: tuple[str, ...]
    required_tokens: tuple[str, ...]
    fact_risk_tokens: tuple[str, ...]
    required_text_tokens: tuple[str, ...]
    forbidden_text_tokens: tuple[str, ...]
    forbidden_ats_tokens: tuple[str, ...]


def load_policy(path: Path = DEFAULT_POLICY_PATH) -> QualityPolicy:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a YAML mapping")

    public_surface = _mapping(payload, "public_surface")
    source_validation = _mapping(payload, "source_validation")
    artifact_qa = _mapping(payload, "artifact_qa")
    text_rule_payload = _mapping(public_surface, "text_rules")

    return QualityPolicy(
        public_files=frozenset(_string_list(public_surface, "public_files")),
        public_dir_prefixes=tuple(_string_list(public_surface, "public_dir_prefixes")),
        scan_excluded_files=frozenset(_string_list(public_surface, "scan_excluded_files")),
        blocked_tracked_paths=tuple(
            re.compile(pattern) for pattern in _string_list(public_surface, "blocked_tracked_paths")
        ),
        binary_suffixes=frozenset(_string_list(public_surface, "binary_suffixes")),
        private_allow_marker=str(public_surface.get("private_allow_marker", "")),
        text_rules=tuple(
            TextRule(rule_id, re.compile(str(pattern), re.IGNORECASE))
            for rule_id, pattern in text_rule_payload.items()
        ),
        required_top_level=tuple(_string_list(source_validation, "required_top_level")),
        required_tokens=tuple(_string_list(source_validation, "required_tokens")),
        fact_risk_tokens=tuple(_string_list(source_validation, "fact_risk_tokens")),
        required_text_tokens=tuple(_string_list(artifact_qa, "required_text_tokens")),
        forbidden_text_tokens=tuple(_string_list(artifact_qa, "forbidden_text_tokens")),
        forbidden_ats_tokens=tuple(_string_list(artifact_qa, "forbidden_ats_tokens")),
    )


def default_policy() -> QualityPolicy:
    for path in (
        Path.cwd() / DEFAULT_POLICY_PATH,
        Path(__file__).resolve().parents[2] / DEFAULT_POLICY_PATH,
    ):
        if path.exists():
            return load_policy(path)
    raise FileNotFoundError(DEFAULT_POLICY_PATH)


def _mapping(payload: dict[str, Any], key: str) -> dict[str, Any]:
    value = payload.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"{key} must be a mapping")
    return value


def _string_list(payload: dict[str, Any], key: str) -> list[str]:
    value = payload.get(key, [])
    if not isinstance(value, list):
        raise ValueError(f"{key} must be a list")
    return [str(item) for item in value]
