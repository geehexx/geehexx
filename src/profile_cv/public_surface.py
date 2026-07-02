from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from .quality_policy import (
    DEFAULT_POLICY_PATH,
    QualityPolicy,
    default_policy,
    load_policy,
)

__all__ = [
    "is_public_surface",
    "load_policy",
    "tracked_path_errors",
]

_DEFAULT_POLICY = default_policy()


def git_files(*args: str) -> list[Path]:
    output = subprocess.check_output(("git", *args), text=True)
    return [Path(line) for line in output.splitlines() if line]


def is_public_surface(path: Path, policy: QualityPolicy = _DEFAULT_POLICY) -> bool:
    path_text = path.as_posix()
    return path_text in policy.public_files or any(
        path_text.startswith(prefix) for prefix in policy.public_dir_prefixes
    )


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
    args = parser.parse_args(argv)

    tracked = git_files("diff", "--cached", "--name-only") if args.staged else git_files("ls-files")
    policy = load_policy(args.policy)
    errors = tracked_path_errors(tracked, policy)

    for error in errors:
        print(error, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
