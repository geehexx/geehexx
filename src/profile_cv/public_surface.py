from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from .quality_policy import (
    DEFAULT_POLICY_PATH,
    QualityPolicy,
    TextRule,
    default_policy,
    load_policy,
)

__all__ = [
    "GENERIC_TEXT_RULES",
    "Rule",
    "is_public_surface",
    "load_policy",
    "scan_file",
    "tracked_path_errors",
]

PRIVATE_ALLOW_MARKER = "public-surface-allow"
_DEFAULT_POLICY = default_policy()
GENERIC_TEXT_RULES = {rule.rule_id: rule.pattern for rule in _DEFAULT_POLICY.text_rules}
Rule = TextRule


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


def is_public_surface(path: Path, policy: QualityPolicy = _DEFAULT_POLICY) -> bool:
    path_text = path.as_posix()
    return path_text in policy.public_files or any(
        path_text.startswith(prefix) for prefix in policy.public_dir_prefixes
    )


def scan_file(path: Path, rules: list[Rule], policy: QualityPolicy = _DEFAULT_POLICY) -> list[Hit]:
    if path.as_posix() in policy.scan_excluded_files:
        return []
    if path.suffix.lower() in policy.binary_suffixes:
        return []
    if not path.exists() or not is_public_surface(path, policy):
        return []
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []
    hits: list[Hit] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        if policy.private_allow_marker in line:
            continue
        for rule in rules:
            if rule.pattern.search(line):
                hits.append(Hit(path, line_no, rule.rule_id))
    return hits


def tracked_path_errors(paths: list[Path], policy: QualityPolicy = _DEFAULT_POLICY) -> list[str]:
    errors: list[str] = []
    for path in paths:
        path_text = path.as_posix()
        for pattern in policy.blocked_tracked_paths:
            if pattern.search(path_text):
                errors.append(f"{path_text}: tracked internal/generated path")
                break
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate the public profile repository surface.")
    parser.add_argument("--staged", action="store_true", help="scan staged files")
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY_PATH)
    parser.add_argument("--private-rules", type=Path, default=Path(".private/policy.txt"))
    parser.add_argument("--require-private-rules", action="store_true")
    args = parser.parse_args(argv)

    files = candidate_files(args.staged)
    tracked = git_files("diff", "--cached", "--name-only") if args.staged else git_files("ls-files")
    policy = load_policy(args.policy)
    rules = list(policy.text_rules)
    rules.extend(private_rules(args.private_rules, args.require_private_rules))

    errors = tracked_path_errors(tracked, policy)
    for path in files:
        for hit in scan_file(path, rules, policy):
            errors.append(f"{hit.path}:{hit.line_no}: [{hit.rule_id}] redacted policy hit")

    for error in errors:
        print(error, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
