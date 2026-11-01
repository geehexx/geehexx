from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _run(script: str, *args: Path, seed: str) -> str:
    env = {**os.environ, "PYTHONHASHSEED": seed}
    return subprocess.run(
        [sys.executable, "-c", script, *(str(arg) for arg in args)],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    ).stdout


def test_serialized_surfaces_are_stable_across_process_hash_seeds(tmp_path: Path) -> None:
    script = """
import json, sys
from pathlib import Path
from profile_cv.adapters import render_template, to_json_ld, to_rendercv, write_yaml
from profile_cv.source import load_source, serialize_source, write_json
root, output = map(Path, sys.argv[1:])
output.mkdir()
resume = load_source(root / "resume.yaml")
(output / "source.yaml").write_text(serialize_source(resume), encoding="utf-8")
write_yaml(output / "rendercv.yaml", to_rendercv(resume))
write_json(output / "resume.json", resume)
write_json(output / "schema.json", to_json_ld(resume))
for name in ("README.md", "resume.md"):
    text = render_template(resume, root / "templates", name + ".j2")
    (output / name).write_text(text, encoding="utf-8")
assert list(to_rendercv(resume)["cv"]["sections"]) == [
    "Summary", "Experience", "Technologies", "Selected Projects", "Education"
]
assert [p["name"] for p in resume["projects"]][:3] == [
    "hitl-mcp-cli", "llm-bedrock-converse", "library-ops"
]
"""
    snapshots = []
    for seed in ("1", "2", "123", "random"):
        output = tmp_path / seed
        _run(script, ROOT, output, seed=seed)
        snapshots.append({p.name: p.read_bytes() for p in output.iterdir()})
    assert all(snapshot == snapshots[0] for snapshot in snapshots[1:])


@pytest.mark.integration
def test_full_outputs_repeat_across_processes_and_hash_seeds(tmp_path: Path) -> None:
    root = tmp_path / "source"
    root.mkdir()
    for name in ("resume.yaml", "pyproject.toml"):
        shutil.copy2(ROOT / name, root / name)
    for name in ("templates", "styles", "schemas", "vendor"):
        shutil.copytree(ROOT / name, root / name)
    script = """
import sys
from pathlib import Path
from profile_cv.adapters import to_rendercv, write_yaml
from profile_cv.build import build_all, build_review_package
from profile_cv.source import load_source
root = Path(sys.argv[1])
expected = root / "expected.yaml"
write_yaml(expected, to_rendercv(load_source(root / "resume.yaml")))
build_all(root=root, clean=True, update_profile=False, profile_check=False)
assert (root / "dist/rendercv/Andrew_Crozier_Resume.yaml").read_bytes() == expected.read_bytes()
build_review_package(root=root)
"""
    snapshots = []
    for seed in ("1", "123", "random"):
        _run(script, root, seed=seed)
        snapshots.append(
            {
                p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                for directory in (root / "dist", root / "site")
                for p in sorted(directory.rglob("*"))
                if p.is_file()
            }
        )
        time.sleep(2)  # Cross ZIP DOS timestamp resolution, not just the same clock tick.
    baseline = snapshots[0]
    assert len(baseline) > 30
    for snapshot in snapshots[1:]:
        changed = sorted(
            path
            for path in baseline.keys() | snapshot.keys()
            if baseline.get(path) != snapshot.get(path)
        )
        assert not changed, f"Non-reproducible outputs: {changed}"
    manifest = json.loads((root / "dist/review-package/manifest.json").read_text())
    assert "branch" not in manifest["source"]
    assert "generated_at_utc" not in manifest
    assert manifest["source_modified_at_utc"] == "2026-11-01T00:00:00Z"
