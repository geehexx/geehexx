#!/usr/bin/env python3
"""Small README lint checks for the public profile surface."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def lint(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    errors: list[str] = []

    if text.count("<details>") != text.count("</details>"):
        errors.append("details tags are unbalanced")
    if "<details>" in text and "<summary>" not in text:
        errors.append("details block is missing a summary")
    if len(re.findall(r"^# ", text, flags=re.MULTILINE)) != 1:
        errors.append("README must have exactly one H1 heading")
    if "<!--" in text or "-->" in text:
        errors.append("README must not contain hidden HTML comments")

    for index, line in enumerate(lines, start=1):
        if line.rstrip() != line:
            errors.append(f"line {index}: trailing whitespace")
        if "\t" in line:
            errors.append(f"line {index}: tab character")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    args = parser.parse_args()

    errors = lint(args.path)
    for error in errors:
        print(f"{args.path}: {error}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
