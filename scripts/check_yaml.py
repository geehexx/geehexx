#!/usr/bin/env python3
"""Validate tracked YAML files when present."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def git_files(staged: bool) -> list[Path]:
    if staged:
        cmd = ("git", "diff", "--cached", "--name-only", "--diff-filter=ACMR")
    else:
        cmd = ("git", "ls-files")
    output = subprocess.check_output(cmd, text=True)
    return [
        Path(line)
        for line in output.splitlines()
        if line.endswith((".yaml", ".yml"))
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--staged", action="store_true")
    args = parser.parse_args()

    yaml_files = git_files(args.staged)
    if not yaml_files:
        return 0

    try:
        import yaml
    except ImportError:
        print("YAML files are present but PyYAML is not installed.", file=sys.stderr)
        return 1

    errors: list[str] = []
    for path in yaml_files:
        text = path.read_text(encoding="utf-8")
        for line_no, line in enumerate(text.splitlines(), start=1):
            if "\t" in line:
                errors.append(f"{path}:{line_no}: tab character")
        try:
            yaml.safe_load(text)
        except yaml.YAMLError as exc:
            errors.append(f"{path}: invalid YAML: {exc}")

    for error in errors:
        print(error, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
