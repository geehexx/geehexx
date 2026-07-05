#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REQUIRED_HEADINGS = (
    "# Andrew Crozier",
    "## Now",
    "## Selected Public Work",
    "## Career Snapshot",
    "## Toolbox",
    "## Engineering Biases",
    "## Reach Me",
)
FORBIDDEN = ("{{", "}}", "TODO", "andrewcrozier86@gmail.com")


def lint(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    if sum(1 for line in text.splitlines() if line.startswith("# ")) != 1:
        errors.append("README must have exactly one H1 heading")
    for heading in REQUIRED_HEADINGS:
        if heading not in text:
            errors.append(f"missing required heading: {heading}")
    for token in FORBIDDEN:
        if token in text:
            errors.append(f"forbidden token present: {token}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Lint the generated profile README.")
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    errors = lint(args.path)
    for error in errors:
        print(f"{args.path}: {error}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
