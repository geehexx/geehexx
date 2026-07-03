from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .build import (
    build_all,
    build_review_package,
    compare_themes,
    render_profile,
    run_quality_gates,
)
from .paths import project_root
from .qa import doctor
from .source import load_repo_schema, load_source, validate_source


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="profile-cv")
    parser.add_argument(
        "--root", type=Path, default=None, help="Repository root. Defaults to auto-detect."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("doctor", help="Check external tool availability.")
    sub.add_parser("validate", help="Validate canonical resume.yaml.")

    profile_parser = sub.add_parser("render-profile", help="Render README.md from resume.yaml.")
    profile_parser.add_argument("--check", action="store_true", help="Fail if README.md is stale.")

    build_parser = sub.add_parser("build", help="Build README and resume artifacts.")
    build_parser.add_argument("--clean", action="store_true", help="Remove dist/ before building.")
    build_parser.add_argument(
        "--no-qa", action="store_true", help="Skip post-build quality checks."
    )
    build_parser.add_argument(
        "--no-profile-check",
        action="store_true",
        help="Overwrite README.md instead of checking whether it was already current.",
    )

    compare_parser = sub.add_parser("compare-themes", help="Render configured RenderCV themes.")
    compare_parser.add_argument("--json", action="store_true", help="Emit machine-readable rows.")

    sub.add_parser("qa", help="Run artifact quality gates against dist/ and README.md.")

    review_parser = sub.add_parser(
        "review-package", help="Assemble the ignored PR review package under dist/."
    )
    review_parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Review package directory. Defaults to dist/review-package.",
    )

    args = parser.parse_args(argv)
    root = project_root(args.root)

    try:
        if args.command == "doctor":
            status = doctor()
            for name, ok in status.items():
                print(f"{name}: {'ok' if ok else 'missing'}")
            return 0 if all(status.values()) else 1

        if args.command == "validate":
            validate_source(
                load_source(root / "resume.yaml"),
                schema=load_repo_schema(root),
            )
            print("resume.yaml: ok")
            return 0

        if args.command == "render-profile":
            path = render_profile(root=root, check=args.check)
            print(path)
            return 0

        if args.command == "build":
            metrics = build_all(
                root=root,
                clean=args.clean,
                run_qa=not args.no_qa,
                profile_check=not args.no_profile_check,
            )
            print(json.dumps(metrics, indent=2))
            return 0

        if args.command == "compare-themes":
            rows = compare_themes(root=root)
            if args.json:
                print(json.dumps(rows, indent=2))
            else:
                for row in rows:
                    print(
                        f"{row['theme']}: pages={row['pages']} "
                        f"chars={row['text_chars']} pdf={row['pdf']}"
                    )
            return 0

        if args.command == "qa":
            print(json.dumps(run_quality_gates(root=root), indent=2))
            return 0

        if args.command == "review-package":
            print(
                json.dumps(
                    build_review_package(root=root, package_dir=args.output_dir),
                    indent=2,
                )
            )
            return 0

    except Exception as exc:  # noqa: BLE001 - CLI boundary should return a clear non-zero code.
        print(f"error: {exc}", file=sys.stderr)
        return 1

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
