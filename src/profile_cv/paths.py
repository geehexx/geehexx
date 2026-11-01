from __future__ import annotations

import json
from pathlib import Path


def project_root(start: Path | None = None) -> Path:
    """Find the repository root by looking for pyproject.toml and resume.yaml."""
    candidates: list[Path] = []
    if start is not None:
        candidates.append(start.resolve())
    candidates.extend([Path.cwd().resolve(), Path(__file__).resolve().parents[2]])

    for candidate in candidates:
        for current in [candidate, *candidate.parents]:
            if (current / "pyproject.toml").exists() and (current / "resume.yaml").exists():
                return current
    raise FileNotFoundError(
        "Could not locate repository root containing pyproject.toml and resume.yaml"
    )


OUTPUT_MARKER = ".profile-cv-output"
_OUTPUT_MARKER_CONTENT = "profile-cv generated output\n"
_SOURCE_DIRECTORIES = {
    ".git",
    ".github",
    ".venv",
    "docs",
    "schemas",
    "scripts",
    "src",
    "styles",
    "templates",
    "tests",
    "vendor",
}


def paths_overlap(left: Path, right: Path) -> bool:
    left, right = left.resolve(), right.resolve()
    return left == right or left in right.parents or right in left.parents


def reject_symlink_path(path: Path) -> None:
    """Reject aliases before resolving; resolving first would hide the link."""
    absolute = path.absolute()
    if any(part.is_symlink() for part in (absolute, *absolute.parents)):
        raise ValueError(f"Output/source path must not contain symlinks: {path}")


def _is_owned_output(path: Path) -> bool:
    marker = path / OUTPUT_MARKER
    if (
        marker.is_file()
        and not marker.is_symlink()
        and marker.read_text(encoding="utf-8") == _OUTPUT_MARKER_CONTENT
    ):
        return True
    manifest = path / "manifest.json"
    if manifest.is_file() and not manifest.is_symlink():
        try:
            payload = json.loads(manifest.read_text(encoding="utf-8"))
        except (ValueError, UnicodeError):
            return False
        return isinstance(payload, dict) and payload.get("generator") == "profile-cv review-package"
    return False


def mark_output(path: Path) -> None:
    (path / OUTPUT_MARKER).write_text(_OUTPUT_MARKER_CONTENT, encoding="utf-8")


def validate_output_directory(
    path: Path,
    *,
    root: Path,
    known_outputs: tuple[Path, ...] = (),
    protected: tuple[Path, ...] = (),
) -> None:
    """Check output ownership and source boundaries without changing the filesystem.

    Explicit relative paths retain their normal current-working-directory meaning.
    Custom output directories must be new, empty, or marked by a prior build.
    """
    reject_symlink_path(path)
    resolved = path.resolve()
    repo = root.resolve()
    if resolved == repo or resolved in repo.parents:
        raise ValueError(f"Output directory must not contain repository root: {path}")
    # A default output alias must never turn its source target into a trusted
    # generated root (for example, dist -> src).
    for output in known_outputs:
        reject_symlink_path(output)
    generated = {item.resolve() for item in known_outputs}
    source_paths = list(protected)
    if repo.is_dir():
        for child in repo.iterdir():
            if child.resolve() in generated:
                continue
            if child.name not in _SOURCE_DIRECTORIES and child.is_dir():
                if _is_owned_output(child):
                    continue
                if child.resolve() == resolved and not any(child.iterdir()):
                    continue
            source_paths.append(child)
    for source in source_paths:
        if paths_overlap(resolved, source):
            raise ValueError(f"Output directory overlaps repository source {source}: {path}")
    if path.exists():
        if not path.is_dir():
            raise ValueError(f"Output path is not a directory: {path}")
        if resolved not in generated and any(path.iterdir()) and not _is_owned_output(path):
            raise ValueError(f"Refusing to replace unowned nonempty output directory: {path}")
        # Existing file links can redirect ordinary write_text/copy2 operations.
        if any(item.is_symlink() for item in path.rglob("*")):
            raise ValueError(f"Output directory contains symlinks: {path}")
