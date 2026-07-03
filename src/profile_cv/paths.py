from __future__ import annotations

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
