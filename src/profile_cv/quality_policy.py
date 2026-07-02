from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

DEFAULT_POLICY_PATH = Path("quality-gates.yaml")


@dataclass(frozen=True)
class QualityPolicy:
    public_files: frozenset[str]
    public_dir_prefixes: tuple[str, ...]
    blocked_tracked_paths: tuple[re.Pattern[str], ...]
    binary_suffixes: frozenset[str]


def load_policy(path: Path = DEFAULT_POLICY_PATH) -> QualityPolicy:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a YAML mapping")

    public_surface = _mapping(payload, "public_surface")
    return QualityPolicy(
        public_files=frozenset(_string_list(public_surface, "public_files")),
        public_dir_prefixes=tuple(_string_list(public_surface, "public_dir_prefixes")),
        blocked_tracked_paths=tuple(
            re.compile(pattern) for pattern in _string_list(public_surface, "blocked_tracked_paths")
        ),
        binary_suffixes=frozenset(_string_list(public_surface, "binary_suffixes")),
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
