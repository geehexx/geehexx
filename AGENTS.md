# Geehexx Repository Instructions

## Repository Scope

- Treat this repository as the public profile and CV source workspace.
- Keep `resume.yaml`, `uv.lock`, templates, tests, styles, workflow
  configuration, and maintainer documentation as the tracked source of truth.
- Keep generated artifacts out of git unless a future publishing change
  explicitly requires a reviewed artifact to be tracked.

## Source And Artifacts

- `resume.yaml` is canonical. Generated JSON, Markdown, DOCX, PDF, Typst, HTML,
  review packages, previews, and site output are derived artifacts.
- Public profile output must not expose the direct resume email. Resume artifacts
  may include resume contact details.
- Do not publish GitHub Pages unless a future reviewed change explicitly
  redefines the public contact boundary.
- Do not hand-edit generated output to fix source or template issues.

## Implementation Standards

- Prefer small typed helpers and source-backed rendering over broad dictionaries
  crossing template, adapter, and build boundaries.
- Keep custom gates narrow. Use standard tools for syntax, formatting, typing,
  tests, workflow linting/security, YAML validation, and secret detection when
  available.
- Keep repo policy data limited to repository surface boundaries.

## Verification

- Use targeted tests for behavior changes, then run the relevant full gate set
  before publishing: `profile-cv validate`, `profile-cv render-profile --check`,
  Ruff, mypy, pytest, actionlint, check-jsonschema, yamllint, zizmor,
  public-surface checks, workflow checks, README lint, and artifact QA where
  local system tools are available.
- For PR review, build `dist/review-package/` with `profile-cv review-package`
  after rendering PDF/DOCX previews, then attach it through the CI
  `resume-artifacts` GitHub Actions artifact rather than committing it.
- For final CV/profile review, compare README, ATS Markdown, PDF text, and DOCX
  text for aligned dates, titles, project descriptions, skills, and contact
  boundaries.
