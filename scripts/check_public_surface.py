#!/usr/bin/env python3
"""Redacted public-surface checks for this profile repository."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

PUBLIC_FILES = ("README.md", "lefthook.yml")
PRIVATE_ALLOW_MARKER = "public-surface-allow"
BLOCKED_TRACKED_PATHS = (
    re.compile(r"(^|/)AGENTS\.md$"),
    re.compile(r"^docs/(checkpoints|superpowers|internal)/"),
    re.compile(r"^resume/"),
    re.compile(r"^dist/"),
)
GENERIC_TEXT_RULES = {
    "absolute-home-path": re.compile(r"/home/[A-Za-z0-9._-]+(?:/|\b)"),
    "tilde-projects-path": re.compile(r"~/projects(?:/|\b)"),
    "windows-user-path": re.compile(r"/mnt/c/Users/[A-Za-z0-9._-]+(?:/|\b)"),
    "internal-agent-file": re.compile(r"\bAGENTS\.md\b"),
    "internal-doc-path": re.compile(r"docs/(?:checkpoints|superpowers|internal)/"),
}


@dataclass(frozen=True)
class Rule:
    rule_id: str
    pattern: re.Pattern[str]


@dataclass(frozen=True)
class Hit:
    path: Path
    line_no: int
    rule_id: str


def git_files(*args: str) -> list[Path]:
    output = subprocess.check_output(("git", *args), text=True)
    return [Path(line) for line in output.splitlines() if line]


def candidate_files(staged: bool) -> list[Path]:
    if staged:
        return git_files("diff", "--cached", "--name-only", "--diff-filter=ACMR")
    tracked = git_files("ls-files")
    untracked = git_files("ls-files", "--others", "--exclude-standard")
    return sorted(set(tracked + untracked))


def private_rules(path: Path, required: bool) -> list[Rule]:
    if not path.exists():
        if required:
            raise FileNotFoundError(f"required private policy file missing: {path}")
        return []
    rules: list[Rule] = []
    for index, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        rules.append(Rule(f"private-policy-{index}", re.compile(stripped, re.IGNORECASE)))
    return rules


def scan_file(path: Path, rules: list[Rule]) -> list[Hit]:
    if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip"}:
        return []
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []

    hits: list[Hit] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        if PRIVATE_ALLOW_MARKER in line:
            continue
        for rule in rules:
            if rule.pattern.search(line):
                hits.append(Hit(path, line_no, rule.rule_id))
    return hits


def tracked_path_errors(paths: list[Path]) -> list[str]:
    errors: list[str] = []
    for path in paths:
        path_text = path.as_posix()
        for pattern in BLOCKED_TRACKED_PATHS:
            if pattern.search(path_text):
                errors.append(f"{path_text}: tracked internal/generated path")
                break
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--staged", action="store_true", help="scan staged files")
    parser.add_argument("--private-rules", type=Path, default=Path(".private/policy.txt"))
    parser.add_argument("--require-private-rules", action="store_true")
    args = parser.parse_args()

    files = candidate_files(args.staged)
    tracked = git_files("diff", "--cached", "--name-only") if args.staged else git_files("ls-files")

    rules = [Rule(rule_id, pattern) for rule_id, pattern in GENERIC_TEXT_RULES.items()]
    rules.extend(private_rules(args.private_rules, args.require_private_rules))

    errors = tracked_path_errors(tracked)
    for path in files:
        if path.as_posix() in PUBLIC_FILES or path.suffix.lower() in {".md", ".yml", ".yaml"}:
            for hit in scan_file(path, rules):
                errors.append(f"{hit.path}:{hit.line_no}: [{hit.rule_id}] redacted policy hit")

    for error in errors:
        print(error, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
