# Maintainer Guide

This repository owns the public `geehexx` GitHub profile README and reviewed CV
artifacts. Source data, templates, tests, policy, and workflow configuration are
tracked; generated distribution files stay under ignored output directories.

## Source Model

`resume.yaml` is the canonical source. It keeps JSON Resume-compatible sections
(`basics`, `work`, `education`, `skills`, `projects`, `languages`, `meta`) plus
repo-owned `x_` fields for profile copy, RenderCV design settings, output names,
and per-surface inclusion flags.

Generated files must not become secondary sources. Regenerate instead of
hand-editing `README.md`, `dist/`, `site/`, RenderCV YAML, DOCX, PDF, HTML, or
JSON-LD output.

## Commands

```bash
uv sync --extra dev
uv run profile-cv validate
uv run profile-cv render-profile --check
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest
uv run python scripts/check_public_surface.py
uv run python scripts/check_workflows.py
uv run profile-cv compare-themes
uv run profile-cv build --clean --no-profile-check
uv run profile-cv qa
```

`profile-cv build` emits reviewed artifacts under `dist/` and a publishable site
under `site/`. CI installs Pandoc, Poppler, and LibreOffice before artifact
generation because DOCX metadata and visual QA depend on those system tools.

## Quality Gates

`quality-gates.yaml` owns repo-specific policy:

- public/tracked file allowlists and generated/private path blocks;
- secret and tool-citation leak patterns;
- source-required tokens and known fact-risk tokens;
- artifact text, ATS, and README expectations.

General syntax/format checks should use standard tools such as pre-commit hooks,
Ruff, mypy, pytest, and GitHub push protection. Keep custom Python gates narrow
and repo-specific.

## Rendering Decisions

RenderCV stays the PDF/Typst renderer because it keeps CV content in text and
handles consistent typography. The default theme is `engineeringresumes`; only
change theme, font, margins, contact separators, or spacing after comparing
generated artifacts and confirming no ATS downside.

ATS surfaces should remain single-column, text-based, standard-heading documents
with readable 10-12pt body text, simple bullets, no icons, no tables used for
layout, no text boxes, and contact details in the main body.

DOCX output is generated from Markdown through Pandoc and finalized by the
metadata normalizer. Keep the normalizer only while tests prove Pandoc leaves
stale or incomplete core/extended properties.

## Manual Release Review

Before distributing a CV/profile build:

- compare `README.md`, ATS Markdown, PDF text, and DOCX text for aligned dates,
  titles, project descriptions, skills, and contact/privacy boundaries;
- review every PDF and DOCX page rendered to PNG for clipping, overlap, missing
  glyphs, broken visible links, and unexpected pagination drift;
- keep generated artifacts ignored unless the user explicitly asks to publish
  them elsewhere.
