from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_DIR = ROOT / ".github" / "workflows"
DEPENDABOT = ROOT / ".github" / "dependabot.yml"
EXPECTED_UV_VERSION = "0.10.0"
SETUP_UV_REF = "astral-sh/setup-uv@08807647e7069bb48b6ef5acd8ec9567f424441b"
CHECKOUT_REF = "actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0"
UPLOAD_ARTIFACT_REF = "actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a"


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.load(path.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    if not isinstance(data, dict):
        raise AssertionError(f"{path} must contain a YAML mapping")
    return data


def workflow_paths() -> list[Path]:
    return sorted(WORKFLOW_DIR.glob("*.yml"))


def assert_workflow_policy(path: Path) -> list[str]:
    data = load_yaml(path)
    errors = _top_level_errors(path, data)
    jobs = data.get("jobs")
    if not isinstance(jobs, dict) or not jobs:
        return [*errors, f"{path}: missing jobs"]
    for job_name, job in jobs.items():
        errors.extend(_job_errors(path, str(job_name), job))
    if data.get("env", {}).get("UV_VERSION") != EXPECTED_UV_VERSION:
        errors.append(f"{path}: env.UV_VERSION must be {EXPECTED_UV_VERSION}")
    return errors


def _top_level_errors(path: Path, data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if "permissions" not in data:
        errors.append(f"{path}: missing top-level permissions")
    if "concurrency" not in data:
        errors.append(f"{path}: missing top-level concurrency")
    defaults = data.get("defaults", {})
    if not isinstance(defaults, dict) or defaults.get("run", {}).get("shell") != "bash":
        errors.append(f"{path}: defaults.run.shell must be bash")
    return errors


def _job_errors(path: Path, job_name: str, job: object) -> list[str]:
    if not isinstance(job, dict):
        return [f"{path}: job {job_name} must be a mapping"]
    errors: list[str] = []
    if "timeout-minutes" not in job:
        errors.append(f"{path}: job {job_name} missing timeout-minutes")
    steps = job.get("steps", [])
    if not isinstance(steps, list):
        return [*errors, f"{path}: job {job_name} steps must be a list"]
    for index, step in enumerate(steps, start=1):
        if isinstance(step, dict):
            errors.extend(_step_errors(path, index, step))
    return errors


def _step_errors(path: Path, index: int, step: dict[str, Any]) -> list[str]:
    uses = str(step.get("uses", ""))
    if uses.startswith("actions/checkout@"):
        return _checkout_errors(path, index, uses, step)
    if uses.startswith("astral-sh/setup-uv@"):
        return _setup_uv_errors(path, index, uses, step)
    if uses.startswith("actions/upload-artifact@"):
        return _upload_artifact_errors(path, index, uses, step)
    return []


def _checkout_errors(path: Path, index: int, uses: str, step: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if uses != CHECKOUT_REF:
        errors.append(f"{path}: checkout step {index} must remain SHA-pinned")
    with_block = step.get("with", {})
    if not isinstance(with_block, dict):
        return [*errors, f"{path}: checkout step {index} missing with block"]
    if with_block.get("persist-credentials") != "false":
        errors.append(f"{path}: checkout step {index} must set persist-credentials: false")
    return errors


def _setup_uv_errors(path: Path, index: int, uses: str, step: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if uses != SETUP_UV_REF:
        errors.append(f"{path}: setup-uv step {index} must remain SHA-pinned")
    with_block = step.get("with", {})
    if not isinstance(with_block, dict):
        return [*errors, f"{path}: setup-uv step {index} missing with block"]
    if with_block.get("version") != "${{ env.UV_VERSION }}":
        errors.append(f"{path}: setup-uv step {index} must use env-pinned uv version")
    if with_block.get("enable-cache") != "true":
        errors.append(f"{path}: setup-uv step {index} must enable cache")
    return errors


def _upload_artifact_errors(path: Path, index: int, uses: str, step: dict[str, Any]) -> list[str]:
    with_block = step.get("with", {})
    if not isinstance(with_block, dict):
        return [f"{path}: upload-artifact step {index} missing with block"]
    errors: list[str] = []
    if uses != UPLOAD_ARTIFACT_REF:
        errors.append(f"{path}: upload-artifact step {index} must remain SHA-pinned")
    if with_block.get("if-no-files-found") != "error":
        errors.append(f"{path}: upload-artifact step {index} must fail on missing files")
    if "retention-days" not in with_block:
        errors.append(f"{path}: upload-artifact step {index} missing retention-days")
    return errors


def assert_dependabot_policy() -> list[str]:
    data = load_yaml(DEPENDABOT)
    updates = data.get("updates")
    if not isinstance(updates, list):
        return [f"{DEPENDABOT}: missing updates list"]
    ecosystems = {item.get("package-ecosystem") for item in updates if isinstance(item, dict)}
    if "github-actions" not in ecosystems:
        return [f"{DEPENDABOT}: must update GitHub Actions dependencies"]
    return []


def main() -> int:
    errors: list[str] = []
    paths = workflow_paths()
    if not paths:
        errors.append(f"{WORKFLOW_DIR}: no workflows found")
    for path in paths:
        errors.extend(assert_workflow_policy(path))
    if DEPENDABOT.exists():
        errors.extend(assert_dependabot_policy())
    else:
        errors.append(f"{DEPENDABOT}: missing Dependabot config")

    for error in errors:
        print(error, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
